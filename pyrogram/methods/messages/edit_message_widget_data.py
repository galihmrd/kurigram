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

import logging

import pyrogram
from pyrogram import raw, utils

log = logging.getLogger(__name__)


class EditMessageWidgetData:
    async def edit_message_widget_data(
        self: pyrogram.Client,
        chat_id: int | str | None = None,
        message_id: int | None = None,
        inline_message_id: str | None = None,
        public_data: str | None = None,
        chat_data: str | None = None,
    ) -> bool:
        """Edit data of a widget in a message sent by the bot or via the bot.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``, *optional*):
                Required if *inline_message_id* is not specified.
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            message_id (``int``, *optional*):
                Required if *inline_message_id* is not specified.
                Identifier of the message with the widget.

            inline_message_id (``str``, *optional*):
                Required if *chat_id* and *message_id* are not specified.
                Identifier of the inline message.

            public_data (``str``, *optional*):
                New public data of the widget, 0-1024 bytes.
                Pass an empty string to remove the public data.
                If omitted, then the public data isn't changed.

            chat_data (``str``, *optional*):
                New data of the widget, which is specific to the message, 0-1024 bytes.
                Pass an empty string to remove the data.
                If omitted, then the data isn't changed.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.edit_message_widget_data(
                    chat_id=chat_id,
                    message_id=message_id,
                    chat_data='{"turn": "x"}',
                )
        """
        if inline_message_id is not None:
            unpacked = utils.unpack_inline_message_id(inline_message_id)
            session = await self.get_session(unpacked.dc_id, is_media=True)

            await session.invoke(
                raw.functions.messages.EditInlineBotMessageWidgetData(
                    id=unpacked,
                    public_data=public_data,
                    chat_data=chat_data,
                ),
                sleep_threshold=self.sleep_threshold,
            )
        else:
            if chat_id is None or message_id is None:
                raise ValueError("chat_id and message_id are required")

            await self.invoke(
                raw.functions.messages.EditMessageWidgetData(
                    peer=await self.resolve_peer(chat_id),
                    id=message_id,
                    public_data=public_data,
                    chat_data=chat_data,
                )
            )

        return True
