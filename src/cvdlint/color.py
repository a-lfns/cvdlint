"""Colour parsing, conversion, simulation, and difference functions."""

from __future__ import annotations

import math
import re

import numpy as np
from numpy.typing import NDArray

RGBArray = NDArray[np.float64]

_HEX = re.compile(r"^#?([0-9a-fA-F]{6})$")

# Machado, Oliveira & Fernandes (2009), full dichromacy matrices.
_CVD_MATRICES = {
    "protanopia": np.array(
        [
            [0.152286, 1.052583, -0.204868],
            [0.114503, 0.786281, 0.099216],
            [-0.003882, -0.048116, 1.051998],
        ]
    ),
    "deuteranopia": np.array(
        [
            [0.367322, 0.860646, -0.227968],
            [0.280085, 0.672501, 0.047413],
            [-0.011820, 0.042940, 0.968881],
        ]
    ),
    "tritanopia": np.array(
        [
            [1.255528, -0.076749, -0.178779],
            [-0.078411, 0.930809, 0.147602],
            [0.004733, 0.691367, 0.303900],
        ]
    ),
}


def normalize_hex(color: str) -> str:
    """Return a canonical uppercase ``#RRGGBB`` colour."""
    match = _HEX.fullmatch(color.strip())
    if match is None:
        raise ValueError(f"Unsupported colour {color!r}; expected #RRGGBB")
    return f"#{match.group(1).upper()}"


def hex_to_rgb(colors: list[str] | tuple[str, ...]) -> RGBArray:
    """Convert hex colours to sRGB values in [0, 1]."""
    normalized = [normalize_hex(color)[1:] for color in colors]
    return np.array(
        [[int(value[i : i + 2], 16) / 255 for i in (0, 2, 4)] for value in normalized],
        dtype=float,
    )


def rgb_to_hex(rgb: RGBArray) -> tuple[str, ...]:
    """Convert sRGB values in [0, 1] to canonical hex colours."""
    values = np.rint(np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    return tuple(f"#{r:02X}{g:02X}{b:02X}" for r, g, b in values)


def simulate(rgb: RGBArray, condition: str, severity: float = 1.0) -> RGBArray:
    """Simulate a colour-vision deficiency using the Machado model."""
    if condition not in _CVD_MATRICES:
        raise ValueError(f"Unknown CVD condition: {condition!r}")
    if not 0 <= severity <= 1:
        raise ValueError("severity must be between 0 and 1")
    matrix = np.eye(3) + severity * (_CVD_MATRICES[condition] - np.eye(3))
    linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    transformed = np.clip(linear @ matrix.T, 0, 1)
    return np.where(
        transformed <= 0.0031308,
        12.92 * transformed,
        1.055 * transformed ** (1 / 2.4) - 0.055,
    )


def srgb_to_lab(rgb: RGBArray) -> RGBArray:
    """Convert sRGB/D65 to CIE Lab/D65."""
    linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    xyz = (
        linear
        @ np.array(
            [
                [0.4124564, 0.3575761, 0.1804375],
                [0.2126729, 0.7151522, 0.0721750],
                [0.0193339, 0.1191920, 0.9503041],
            ]
        ).T
    )
    xyz /= np.array([0.95047, 1.0, 1.08883])
    delta = 6 / 29
    f = np.where(xyz > delta**3, np.cbrt(xyz), xyz / (3 * delta**2) + 4 / 29)
    return np.column_stack(
        (116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2]))
    )


def delta_e_76(first: RGBArray, second: RGBArray) -> float:
    return float(np.linalg.norm(first - second))


def delta_e_94(first: RGBArray, second: RGBArray) -> float:
    """Compute CIE94 colour difference with graphic-arts parameters."""
    dl = first[0] - second[0]
    c1 = math.hypot(first[1], first[2])
    c2 = math.hypot(second[1], second[2])
    dc = c1 - c2
    da = first[1] - second[1]
    db = first[2] - second[2]
    dh_squared = max(0.0, da**2 + db**2 - dc**2)
    return math.sqrt(
        dl**2 + (dc / (1 + 0.045 * c1)) ** 2 + dh_squared / (1 + 0.015 * c1) ** 2
    )


def delta_e_2000(first: RGBArray, second: RGBArray) -> float:
    """Compute CIEDE2000 for two Lab colours."""
    l1, a1, b1 = first
    l2, a2, b2 = second
    c1, c2 = math.hypot(a1, b1), math.hypot(a2, b2)
    cbar = (c1 + c2) / 2
    g = 0.5 * (1 - math.sqrt(cbar**7 / (cbar**7 + 25**7)))
    ap1, ap2 = (1 + g) * a1, (1 + g) * a2
    cp1, cp2 = math.hypot(ap1, b1), math.hypot(ap2, b2)
    hp1 = math.degrees(math.atan2(b1, ap1)) % 360
    hp2 = math.degrees(math.atan2(b2, ap2)) % 360
    dl = l2 - l1
    dc = cp2 - cp1
    dh_angle = hp2 - hp1
    if cp1 * cp2 == 0:
        dh_angle = 0
    elif dh_angle > 180:
        dh_angle -= 360
    elif dh_angle < -180:
        dh_angle += 360
    dh = 2 * math.sqrt(cp1 * cp2) * math.sin(math.radians(dh_angle / 2))
    lbar = (l1 + l2) / 2
    cpbar = (cp1 + cp2) / 2
    if cp1 * cp2 == 0:
        hpbar = hp1 + hp2
    elif abs(hp1 - hp2) <= 180:
        hpbar = (hp1 + hp2) / 2
    elif hp1 + hp2 < 360:
        hpbar = (hp1 + hp2 + 360) / 2
    else:
        hpbar = (hp1 + hp2 - 360) / 2
    t = (
        1
        - 0.17 * math.cos(math.radians(hpbar - 30))
        + 0.24 * math.cos(math.radians(2 * hpbar))
        + 0.32 * math.cos(math.radians(3 * hpbar + 6))
        - 0.20 * math.cos(math.radians(4 * hpbar - 63))
    )
    sl = 1 + 0.015 * (lbar - 50) ** 2 / math.sqrt(20 + (lbar - 50) ** 2)
    sc = 1 + 0.045 * cpbar
    sh = 1 + 0.015 * cpbar * t
    rt = (
        -2
        * math.sqrt(cpbar**7 / (cpbar**7 + 25**7))
        * math.sin(math.radians(60 * math.exp(-(((hpbar - 275) / 25) ** 2))))
    )
    return math.sqrt(
        (dl / sl) ** 2 + (dc / sc) ** 2 + (dh / sh) ** 2 + rt * (dc / sc) * (dh / sh)
    )
