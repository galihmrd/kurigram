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
from pyrogram import raw

log = logging.getLogger(__name__)


class EditSharedWidgetData:
    async def edit_shared_widget_data(
        self: pyrogram.Client,
        widget_id: int | str,
        public_data: str,
        cache_time: int | None = None,
    ) -> bool:
        """Edit public data of a shared widget created by the bot.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            widget_id (``int`` | ``str``):
                Unique identifier of the shared widget.
                You can get it from the ``id`` field of :obj:`~pyrogram.types.Widget`.

            public_data (``str``):
                New public data of the widget, 0-1024 bytes.
                Pass an empty string to remove the public data.

            cache_time (``int``, *optional*):
                The maximum amount of time in seconds that the public data of the widget may be cached client-side,
                5-3600. If omitted, then the current value is kept, which is 30 by default.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.edit_shared_widget_data(
                    widget_id=widget_id,
                    public_data='{"price": 5.47}',
                    cache_time=10,
                )
        """
        return bool(
            await self.invoke(
                raw.functions.messages.EditWidgetData(
                    widget_id=int(widget_id),
                    public_data=public_data,
                    cache_time=cache_time,
                )
            )
        )
