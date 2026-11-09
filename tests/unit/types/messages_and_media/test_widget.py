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
from typing import Final

from pyrogram import raw, types

_HTML: Final[str] = "<h3>Order #1042</h3>"


def media(*, payload: bytes) -> raw.types.MessageMediaWidget:
    return raw.types.MessageMediaWidget(
        width=320,
        height=200,
        payload=payload,
        public_data='{"price": 5.47}',
        chat_data='{"seen": false}',
        widget_id=1234567890123456789,
        can_query=True,
        is_copy=False,
        background_query=True,
    )


def test_a_widget_inflates_its_zlib_payload() -> None:
    widget = types.Widget._parse(media(payload=zlib.compress(_HTML.encode(), 9)))

    assert widget.html == _HTML
    assert widget.payload == zlib.compress(_HTML.encode(), 9)
    assert widget.width == 320
    assert widget.height == 200
    assert widget.id == 1234567890123456789
    assert widget.public_data == '{"price": 5.47}'
    assert widget.chat_data == '{"seen": false}'
    assert widget.can_query is True
    assert widget.is_copy is False
    assert widget.background_query is True


def test_a_widget_with_a_corrupt_payload_keeps_the_raw_bytes() -> None:
    widget = types.Widget._parse(media(payload=b"not a zlib stream"))

    assert widget.html is None
    assert widget.payload == b"not a zlib stream"
