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

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from pyrogram.listeners import (
    LISTENER_GROUP,
    CallbackQueryListenerHandler,
    Listener,
    ListenerStopped,
    ListenerTimeout,
    ListenerTypes,
    MessageListenerHandler,
    _Target,
)

if TYPE_CHECKING:
    import pyrogram
    from pyrogram.filters import Filter
    from pyrogram.types import CallbackQuery, Message


class Listeners:
    """One-shot update waiting (``listen`` / ``ask``) implemented natively.

    See :mod:`pyrogram.listeners` for the matching rules and exceptions.
    """

    def _ensure_listener_infra(self: pyrogram.Client) -> None:
        """Create the listener registry and (re)register the internal handlers.

        Safe to call repeatedly: handlers are only added when they are actually
        missing, which also covers a ``dispatcher.stop(clear_handlers=True)``.
        """
        if not hasattr(self, "listeners"):
            self.listeners = {listener_type: [] for listener_type in ListenerTypes}

        present = any(
            isinstance(handler, (MessageListenerHandler, CallbackQueryListenerHandler))
            for handlers in self.dispatcher.groups.values()
            for handler in handlers
        )
        if not present:
            self.dispatcher.add_handler(MessageListenerHandler(), LISTENER_GROUP)
            self.dispatcher.add_handler(CallbackQueryListenerHandler(), LISTENER_GROUP)

    def get_many_listeners_matching_with_data(
        self: pyrogram.Client,
        data: _Target,
        listener_type: ListenerTypes,
        ignore_user: bool = False,
    ) -> list[Listener]:
        """Every pending listener for ``listener_type`` whose target matches ``data``."""
        return [
            listener
            for listener in getattr(self, "listeners", {}).get(listener_type, ())
            if listener.target.matches(data, ignore_user=ignore_user)
        ]

    def get_listener_matching_with_data(
        self: pyrogram.Client,
        data: _Target,
        listener_type: ListenerTypes,
        ignore_user: bool = False,
    ) -> Listener | None:
        """The most specific pending listener matching ``data``, or ``None``."""
        matching = self.get_many_listeners_matching_with_data(
            data, listener_type, ignore_user=ignore_user
        )
        return max(matching, key=lambda item: item.target.specificity(), default=None)

    def remove_listener(self: pyrogram.Client, listener: Listener) -> None:
        """Drop ``listener`` from the registry (no-op if it is already gone)."""
        try:
            self.listeners[listener.listener_type].remove(listener)
        except (AttributeError, KeyError, ValueError):
            pass

    async def stop_listener(self: pyrogram.Client, listener: Listener) -> None:
        """Cancel a pending listener; a coroutine waiting on it gets :class:`ListenerStopped`."""
        self.remove_listener(listener)
        if listener.future is not None and not listener.future.done():
            listener.future.set_exception(ListenerStopped())

    async def stop_listening(
        self: pyrogram.Client,
        listener_type: ListenerTypes = ListenerTypes.MESSAGE,
        chat_id: Any = None,
        user_id: Any = None,
        message_id: Any = None,
        inline_message_id: Any = None,
    ) -> None:
        """Cancel every pending listener of ``listener_type`` matching the given ids."""
        pattern = _Target.from_ids(
            chat_id=chat_id,
            user_id=user_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
        )
        # Snapshot first: stop_listener() mutates the registry while we walk it.
        listeners = [
            listener
            for listener in getattr(self, "listeners", {}).get(listener_type, ())
            if pattern.matches(listener.target)
        ]
        for listener in listeners:
            await self.stop_listener(listener)

    def register_next_step_handler(
        self: pyrogram.Client,
        callback: Any,
        filters: Filter | None = None,
        listener_type: ListenerTypes = ListenerTypes.MESSAGE,
        unallowed_click_alert: bool | str = True,
        chat_id: Any = None,
        user_id: Any = None,
        message_id: Any = None,
        inline_message_id: Any = None,
    ) -> None:
        """Register ``callback`` to run on the next matching update (fire-and-forget)."""
        self._ensure_listener_infra()
        listener = Listener(
            listener_type=listener_type,
            target=_Target.from_ids(
                chat_id=chat_id,
                user_id=user_id,
                message_id=message_id,
                inline_message_id=inline_message_id,
            ),
            filters=filters,
            unallowed_click_alert=unallowed_click_alert,
            callback=callback,
        )
        self.listeners[listener_type].append(listener)

    async def listen(
        self: pyrogram.Client,
        filters: Filter | None = None,
        listener_type: ListenerTypes = ListenerTypes.MESSAGE,
        timeout: float | None = None,
        unallowed_click_alert: bool | str = True,
        chat_id: Any = None,
        user_id: Any = None,
        message_id: Any = None,
        inline_message_id: Any = None,
    ) -> Message | CallbackQuery:
        """Wait for the next update that matches the given ids and filters.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Only resume on updates this filter accepts.

            listener_type (:obj:`~pyrogram.listeners.ListenerTypes`, *optional*):
                Whether to wait for a message or a callback query. Defaults to messages.

            timeout (``float``, *optional*):
                Seconds to wait before raising :class:`~pyrogram.listeners.ListenerTimeout`.
                ``None`` waits indefinitely.

            unallowed_click_alert (``bool`` | ``str``, *optional*):
                For callback-query listeners, whether (and with which text) to alert a
                user that presses the awaited button but does not pass ``filters``.

            chat_id / user_id / message_id / inline_message_id:
                Optional ids to restrict the listener. Accepts a single id or a group of ids.

        Returns:
            The matched :obj:`~pyrogram.types.Message` or :obj:`~pyrogram.types.CallbackQuery`.
        """
        self._ensure_listener_infra()
        future: asyncio.Future[Any] = asyncio.get_running_loop().create_future()
        listener = Listener(
            listener_type=listener_type,
            target=_Target.from_ids(
                chat_id=chat_id,
                user_id=user_id,
                message_id=message_id,
                inline_message_id=inline_message_id,
            ),
            filters=filters,
            unallowed_click_alert=unallowed_click_alert,
            future=future,
        )
        future.add_done_callback(lambda _future: self.remove_listener(listener))
        self.listeners[listener_type].append(listener)
        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError as exc:
            raise ListenerTimeout(timeout) from exc

    async def ask(
        self: pyrogram.Client,
        chat_id: Any,
        text: str,
        filters: Filter | None = None,
        listener_type: ListenerTypes = ListenerTypes.MESSAGE,
        timeout: float | None = None,
        unallowed_click_alert: bool | str = True,
        user_id: Any = None,
        message_id: Any = None,
        inline_message_id: Any = None,
        *args: Any,
        **kwargs: Any,
    ) -> Message | CallbackQuery:
        """Send ``text`` and wait for the next matching update.

        The sent prompt (if any) is attached to the returned object as
        ``sent_message`` so callers can clean it up afterwards.

        Returns:
            The matched :obj:`~pyrogram.types.Message` or :obj:`~pyrogram.types.CallbackQuery`.
        """
        sent_message = None
        if text and text.strip():
            target_chat = chat_id[0] if isinstance(chat_id, (list, tuple)) else chat_id
            sent_message = await self.send_message(target_chat, text, *args, **kwargs)

        response = await self.listen(
            filters=filters,
            listener_type=listener_type,
            timeout=timeout,
            unallowed_click_alert=unallowed_click_alert,
            chat_id=chat_id,
            user_id=user_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
        )
        if response is not None:
            try:
                response.sent_message = sent_message
            except Exception:  # noqa: BLE001 - not every update type allows extra attributes
                pass
        return response
