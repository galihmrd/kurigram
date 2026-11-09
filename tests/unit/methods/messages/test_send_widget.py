#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations as _annotations

from typing import TYPE_CHECKING, Final

import pytest

from pyrogram import raw
from pyrogram.methods.messages.edit_message_widget_data import EditMessageWidgetData
from pyrogram.methods.messages.edit_shared_widget_data import EditSharedWidgetData
from pyrogram.methods.messages.send_shared_widget import SendSharedWidget
from pyrogram.methods.messages.send_widget import SendWidget
from pyrogram.parser import Parser

if TYPE_CHECKING:
    from pyrogram.raw.core import TLObject

_WIDGET_ID: Final[int] = 1234567890123456789
_HTML: Final[str] = "<h3>Order #1042</h3>"


class FakeClient(SendWidget, SendSharedWidget, EditMessageWidgetData, EditSharedWidgetData):
    """A client that records the query handed to `invoke`, without touching the network."""

    def __init__(self) -> None:
        self.parser = Parser(None)
        self.captured_query: TLObject | None = None
        self.inline_calls: list[TLObject] = []

    def rnd_id(self) -> int:
        return 1

    async def resolve_peer(self, peer_id: int | str) -> raw.base.InputPeer:
        return raw.types.InputPeerUser(
            user_id=int(peer_id),
            access_hash=0,
        )

    async def invoke(
        self,
        query: TLObject,
        business_connection_id: str | None = None,
    ) -> raw.base.messages.Messages | bool:
        self.captured_query = query

        return raw.types.messages.Messages(
            messages=[],
            chats=[],
            users=[],
            topics=[],
        )


@pytest.mark.asyncio
async def test_send_widget_builds_an_input_media_widget() -> None:
    client = FakeClient()

    result = await client.send_widget(
        chat_id=7,
        html=_HTML,
        width=320,
        height=200,
        public_data='{"price": 5.47}',
        chat_data='{"seen": false}',
        caption="Order #1042",
        show_caption_above_media=True,
        allow_queries=True,
        is_shared=True,
        disable_notification=True,
        protect_content=True,
    )

    assert result is None
    assert isinstance(client.captured_query, raw.functions.messages.SendMedia)
    assert client.captured_query.media == raw.types.InputMediaWidget(
        allow_queries=True,
        shared_widget=True,
        width=320,
        height=200,
        html=_HTML,
        public_data='{"price": 5.47}',
        chat_data='{"seen": false}',
    )
    assert client.captured_query.message == "Order #1042"
    assert client.captured_query.invert_media is True
    assert client.captured_query.silent is True
    assert client.captured_query.noforwards is True


@pytest.mark.asyncio
async def test_send_shared_widget_builds_an_input_media_widget_id() -> None:
    client = FakeClient()

    result = await client.send_shared_widget(
        chat_id=7,
        widget_id=str(_WIDGET_ID),
        chat_data='{"seen": false}',
        caption="Order #1042",
    )

    assert result is None
    assert isinstance(client.captured_query, raw.functions.messages.SendMedia)
    assert client.captured_query.media == raw.types.InputMediaWidgetId(
        widget_id=_WIDGET_ID,
        chat_data='{"seen": false}',
    )
    assert client.captured_query.message == "Order #1042"


@pytest.mark.asyncio
async def test_edit_message_widget_data_targets_the_message() -> None:
    client = FakeClient()

    result = await client.edit_message_widget_data(
        chat_id=7,
        message_id=11,
        public_data='{"price": 5.47}',
        chat_data='{"seen": true}',
    )

    assert result is True
    assert isinstance(client.captured_query, raw.functions.messages.EditMessageWidgetData)
    assert client.captured_query.id == 11
    assert client.captured_query.public_data == '{"price": 5.47}'
    assert client.captured_query.chat_data == '{"seen": true}'


@pytest.mark.asyncio
async def test_edit_shared_widget_data_targets_the_widget() -> None:
    client = FakeClient()

    result = await client.edit_shared_widget_data(
        widget_id=_WIDGET_ID,
        public_data='{"price": 5.47}',
        cache_time=10,
    )

    assert result is True
    assert isinstance(client.captured_query, raw.functions.messages.EditWidgetData)
    assert client.captured_query.widget_id == _WIDGET_ID
    assert client.captured_query.public_data == '{"price": 5.47}'
    assert client.captured_query.cache_time == 10
