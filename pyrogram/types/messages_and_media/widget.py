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

import zlib
from typing import TYPE_CHECKING

from ..object import Object

if TYPE_CHECKING:
    from pyrogram import raw


class Widget(Object):
    """Describes an HTML widget.

    Parameters:
        id (``int``, *optional*):
            Unique identifier of the shared widget, which can be used to send the widget again using
            :meth:`~pyrogram.Client.send_shared_widget`.
            Omitted if the widget isn't shared.

        width (``int``):
            Width of the widget in logical pixels.
            Zero means that the widget occupies the whole width of the message bubble.

        height (``int``):
            Height of the widget in logical pixels.
            Zero means that the height of the widget isn't fixed.

        html (``str``, *optional*):
            HTML code of the widget.

        payload (``bytes``, *optional*):
            Raw zlib-compressed HTML code of the widget, as stored in the message.

        public_data (``str``, *optional*):
            Public data of the widget, which is available wherever the widget is shown.
            All messages with a shared widget have the same public data.

        chat_data (``str``, *optional*):
            Data of the widget, which is specific to the message.

        can_query (``bool``, *optional*):
            True, if the widget may send queries to the bot.

        is_copy (``bool``, *optional*):
            True, if the widget is a copy of another widget.

        background_query (``bool``, *optional*):
            True, if the widget may send queries to the bot in the background.
    """

    def __init__(
        self,
        *,
        width: int,
        height: int,
        id: int | None = None,
        html: str | None = None,
        payload: bytes | None = None,
        public_data: str | None = None,
        chat_data: str | None = None,
        can_query: bool | None = None,
        is_copy: bool | None = None,
        background_query: bool | None = None,
    ):
        super().__init__()

        self.id = id
        self.width = width
        self.height = height
        self.html = html
        self.payload = payload
        self.public_data = public_data
        self.chat_data = chat_data
        self.can_query = can_query
        self.is_copy = is_copy
        self.background_query = background_query

    @staticmethod
    def _parse(media: raw.types.MessageMediaWidget) -> Widget:
        html = None

        if media.payload:
            try:
                html = zlib.decompress(media.payload).decode("utf-8")
            except (UnicodeDecodeError, zlib.error):
                html = None

        return Widget(
            id=media.widget_id,
            width=media.width,
            height=media.height,
            html=html,
            payload=media.payload,
            public_data=media.public_data,
            chat_data=media.chat_data,
            can_query=media.can_query,
            is_copy=media.is_copy,
            background_query=media.background_query,
        )
