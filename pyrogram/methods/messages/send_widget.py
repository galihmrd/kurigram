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
from typing import TYPE_CHECKING

import pyrogram
from pyrogram import enums, raw, types, utils

if TYPE_CHECKING:
    from datetime import datetime, timedelta

log = logging.getLogger(__name__)


class SendWidget:
    async def send_widget(
        self: pyrogram.Client,
        chat_id: int | str,
        html: str,
        width: int = 0,
        height: int = 0,
        public_data: str | None = None,
        chat_data: str | None = None,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        show_caption_above_media: bool | None = None,
        allow_queries: bool | None = None,
        is_shared: bool | None = None,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        effect_id: int | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | timedelta | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        business_connection_id: str | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: (
            types.InlineKeyboardMarkup
            | types.ReplyKeyboardMarkup
            | types.ReplyKeyboardRemove
            | types.ForceReply
            | None
        ) = None,
    ) -> types.Message | None:
        """Send a message with an HTML widget.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            html (``str``):
                HTML code of the widget, 1-32768 bytes.
                The code must not exceed 4096 bytes when compressed with zlib at the maximum compression level.

            width (``int``, *optional*):
                Width of the widget in logical pixels.
                Pass 0 to make the widget occupy the whole width of the message bubble.

            height (``int``, *optional*):
                Height of the widget in logical pixels.
                Pass 0 to let the height depend on the widget content.

            public_data (``str``, *optional*):
                Public data of the widget, 0-1024 bytes, which will be available wherever the widget is shown.
                If the widget is shared, then all messages with it will have the same public data.

            chat_data (``str``, *optional*):
                Data of the widget, which is specific to the message, 0-1024 bytes.

            caption (``str``, *optional*):
                Widget caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            show_caption_above_media (``bool``, *optional*):
                Pass True if the caption must be shown above the widget.

            allow_queries (``bool``, *optional*):
                Pass True to allow the widget to send queries to the bot.

            is_shared (``bool``, *optional*):
                Pass True to create a shared widget, which can be sent again using
                :meth:`~pyrogram.Client.send_shared_widget`.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For direct chats only.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime` | :py:obj:`~datetime.timedelta`, *optional*):
                Date when the message will be automatically sent.
                A :py:obj:`~datetime.timedelta` is counted from now.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the message will be sent.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :obj:`~pyrogram.types.Message` | ``None``: On success, the sent message is returned.

        Example:
            .. code-block:: python

                await app.send_widget(
                    chat_id="me",
                    html="<h3>Order #1042</h3><p>Total: $23.50</p>",
                    caption="Order #1042",
                )
        """
        media = raw.types.InputMediaWidget(
            allow_queries=allow_queries,
            shared_widget=is_shared,
            width=width,
            height=height,
            html=html,
            public_data=public_data,
            chat_data=chat_data,
        )

        rpc = raw.functions.messages.SendMedia(
            peer=await self.resolve_peer(chat_id),
            media=media,
            silent=disable_notification,
            invert_media=show_caption_above_media,
            reply_to=await utils.get_reply_to(
                self, reply_parameters, message_thread_id, direct_messages_topic_id
            ),
            random_id=self.rnd_id(),
            schedule_date=utils.datetime_to_timestamp(schedule_date),
            schedule_repeat_period=repeat_period,
            noforwards=protect_content,
            allow_paid_floodskip=allow_paid_broadcast,
            allow_paid_stars=paid_message_star_count,
            suggested_post=suggested_post_parameters.write() if suggested_post_parameters else None,
            reply_markup=await reply_markup.write(self) if reply_markup else None,
            effect=effect_id,
            **await utils.parse_text_entities(self, caption, parse_mode, caption_entities),
        )

        r = await self.invoke(rpc, business_connection_id=business_connection_id)

        messages = await utils.parse_messages(client=self, messages=r)

        return messages[0] if messages else None
