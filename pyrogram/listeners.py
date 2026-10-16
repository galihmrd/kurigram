#  Kurigram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#  Copyright (C) 2024-present KurimuzonAkuma <https://github.com/KurimuzonAkuma>
#
#  This file is part of Kurigram.
#
#  Kurigram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Kurigram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Kurigram. If not, see <https://www.gnu.org/licenses/>.

"""One-shot update listeners (``Client.listen`` / ``Client.ask``).

A *listener* is a pending expectation: a coroutine registers it and is resumed
with the first incoming update that satisfies it.  It is matched on a
:class:`_Target` (chat / user / message / inline-message id, ``None`` acting as
a wildcard) plus an optional Pyrogram :obj:`~pyrogram.filters.Filter`.

Dispatch happens through two internal handlers that live in a dedicated
high-priority group (:data:`LISTENER_GROUP`), so a waiting listener consumes the
update it was waiting for and regular handlers never see it.  When no listener
matches, the handlers stay out of the way and dispatch proceeds as usual.
"""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, cast

import pyrogram
from pyrogram.handlers import CallbackQueryHandler, MessageHandler

if TYPE_CHECKING:
    from pyrogram.filters import Filter
    from pyrogram.raw.base import Update as RawUpdate
    from pyrogram.types import CallbackQuery, Message, Update


#: Dispatch group of the internal listener handlers. Kept well below the usual
#: ``0`` (and the ``-1`` some applications use for guard handlers) so a pending
#: listener always gets first refusal on the update it waits for.
LISTENER_GROUP = -1000

#: Text shown when a button that belongs to a listener is pressed by the wrong
#: user. Overridable per listener by passing a string as ``unallowed_click_alert``.
DEFAULT_CLICK_ALERT = "This button isn't for you."

MatchValue = int | str
MatchInput = MatchValue | Iterable[MatchValue] | None


def _to_set(value: MatchInput) -> set[Any] | None:
    """Normalize an id (or a group of ids) to a set, dropping ``None``."""
    if value is None:
        return None
    if isinstance(value, (str, bytes)) or not isinstance(value, Iterable):
        return {value}
    return {item for item in value if item is not None} or None


@dataclass
class _Target:
    """The concrete ids a listener is allowed to be triggered by.

    Each field is either ``None`` (wildcard, matches anything) or a set of
    accepted values.  A listener target is matched against the target of an
    incoming update with :meth:`matches`.
    """

    chat: set[Any] | None = None
    user: set[Any] | None = None
    message: set[Any] | None = None
    inline: set[Any] | None = None

    @classmethod
    def from_ids(
        cls,
        *,
        chat_id: MatchInput = None,
        user_id: MatchInput = None,
        message_id: MatchInput = None,
        inline_message_id: MatchInput = None,
    ) -> _Target:
        return cls(
            chat=_to_set(chat_id),
            user=_to_set(user_id),
            message=_to_set(message_id),
            inline=_to_set(inline_message_id),
        )

    def matches(self, update: _Target, *, ignore_user: bool = False) -> bool:
        """True when every populated field here is also present in ``update``."""
        pairs = (
            (self.chat, update.chat),
            (None if ignore_user else self.user, update.user),
            (self.message, update.message),
            (self.inline, update.inline),
        )
        for wanted, actual in pairs:
            if wanted is None:
                continue
            if not actual or not (wanted & actual):
                return False
        return True

    def specificity(self) -> int:
        """Number of constrained fields; a higher value is a more precise match."""
        return sum(part is not None for part in (self.chat, self.user, self.message, self.inline))


class ListenerTypes(Enum):
    """The kind of update a listener waits for."""

    MESSAGE = "message"
    CALLBACK_QUERY = "callback_query"


class ListenerTimeout(asyncio.TimeoutError):
    """No matching update arrived within the listener's ``timeout``."""


class ListenerStopped(Exception):
    """A pending listener was cancelled through :meth:`Client.stop_listening`."""


@dataclass
class Listener:
    """A pending expectation registered by :meth:`Client.listen`."""

    listener_type: ListenerTypes
    target: _Target
    filters: Filter | None = None
    unallowed_click_alert: bool | str = True
    future: asyncio.Future[Any] | None = None
    callback: Callable[..., Any] | None = None


def message_target(message: Message) -> _Target:
    """Build the :class:`_Target` describing an incoming :obj:`~pyrogram.types.Message`."""
    sender = getattr(message, "from_user", None)
    chat = getattr(message, "chat", None)
    message_id = getattr(message, "id", None)
    return _Target(
        chat=_to_set([getattr(chat, "id", None), getattr(chat, "username", None)]),
        user=_to_set([getattr(sender, "id", None), getattr(sender, "username", None)]),
        message=None if message_id is None else {message_id},
    )


def callback_query_target(query: CallbackQuery) -> _Target:
    """Build the :class:`_Target` describing an incoming :obj:`~pyrogram.types.CallbackQuery`."""
    sender = getattr(query, "from_user", None)
    message = getattr(query, "message", None)
    chat = getattr(message, "chat", None) if message is not None else None
    message_id = getattr(message, "id", None) if message is not None else None
    inline_message_id = getattr(query, "inline_message_id", None)
    return _Target(
        chat=_to_set([getattr(chat, "id", None), getattr(chat, "username", None)]),
        user=_to_set([getattr(sender, "id", None), getattr(sender, "username", None)]),
        message=None if message_id is None else {message_id},
        inline=_to_set(inline_message_id),
    )


async def _filter_passes(client: pyrogram.Client, listener: Listener, update: Any) -> bool:
    """Run the listener's filter against ``update`` (accepting sync or async filters)."""
    filt = listener.filters
    if not callable(filt):
        return True
    # A filter is normally a Pyrogram object with an ``async def __call__``, but a
    # plain coroutine function is accepted too; everything else runs off-loop.
    if inspect.iscoroutinefunction(filt) or inspect.iscoroutinefunction(filt.__call__):
        return bool(await filt(client, update))
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(client.executor, filt, client, update)
    if inspect.isawaitable(result):
        result = await result
    return bool(result)


async def _deliver(client: pyrogram.Client, listener: Listener, update: Any) -> None:
    """Resolve a matched listener and stop the update from reaching other handlers."""
    client.remove_listener(listener)
    if listener.future is not None and not listener.future.done():
        listener.future.set_result(update)
    elif listener.callback is not None:
        result = listener.callback(client, update)
        if inspect.isawaitable(result):
            await result
    else:
        return
    raise pyrogram.StopPropagation


class MessageListenerHandler(MessageHandler):
    """Internal handler that feeds matching messages to pending listeners."""

    def __init__(self) -> None:
        super().__init__(_consume_message)

    async def check(self, client: pyrogram.Client, update: Update | RawUpdate) -> bool:
        message = cast("Message", update)
        listener = client.get_listener_matching_with_data(
            message_target(message), ListenerTypes.MESSAGE
        )
        if listener is None:
            return False
        return await _filter_passes(client, listener, message)


class CallbackQueryListenerHandler(CallbackQueryHandler):
    """Internal handler that feeds matching callback queries to pending listeners."""

    def __init__(self) -> None:
        super().__init__(_consume_callback_query)

    async def check(self, client: pyrogram.Client, update: Update | RawUpdate) -> bool:
        query = cast("CallbackQuery", update)
        data = callback_query_target(query)
        listener = client.get_listener_matching_with_data(data, ListenerTypes.CALLBACK_QUERY)
        if listener is not None and await _filter_passes(client, listener, query):
            return True

        # The button belongs to a pending listener but this click was rejected
        # (wrong user, or the filter said no): warn the clicker when asked to,
        # then let the update fall through to the regular handlers.
        owner = listener or client.get_listener_matching_with_data(
            data, ListenerTypes.CALLBACK_QUERY, ignore_user=True
        )
        if owner is not None and owner.unallowed_click_alert:
            alert = (
                owner.unallowed_click_alert
                if isinstance(owner.unallowed_click_alert, str)
                else DEFAULT_CLICK_ALERT
            )
            try:
                await query.answer(alert)
            except Exception:  # noqa: BLE001 - answering is best-effort
                pass
        return False


async def _consume_message(client: pyrogram.Client, message: Message, *args: Any) -> None:
    listener = client.get_listener_matching_with_data(
        message_target(message), ListenerTypes.MESSAGE
    )
    if listener is not None:
        await _deliver(client, listener, message)


async def _consume_callback_query(
    client: pyrogram.Client, query: CallbackQuery, *args: Any
) -> None:
    listener = client.get_listener_matching_with_data(
        callback_query_target(query), ListenerTypes.CALLBACK_QUERY
    )
    if listener is not None:
        await _deliver(client, listener, query)
