"""Internal display calibration for the reconstructed mass coordinate."""

from __future__ import annotations

import base64
import struct
import zlib
from functools import lru_cache


_PAYLOAD = b"c$~BUzyJmgo)8)U77qcr"


@lru_cache(maxsize=1)
def _mass_axis_parameters():
    raw = zlib.decompress(base64.b85decode(_PAYLOAD))
    return struct.unpack(">dd", raw)


def mass_coordinate(mass):
    """Map a reconstructed mass to the blinded display coordinate."""
    scale, shift = _mass_axis_parameters()
    return scale * float(mass) + shift
