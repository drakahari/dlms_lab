"""Read-only Omarchy palette adapter with a readable built-in fallback."""
from pathlib import Path
import re
import tomllib

FALLBACK = {"background": "#101827", "surface": "#1b293c", "foreground": "#eef4fc",
            "muted": "#b3c2d6", "accent": "#97beff", "success": "#9adfb2", "danger": "#ffb4ab"}


def luminance(color):
    values = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in values]
    return sum(v * w for v, w in zip(linear, (.2126, .7152, .0722)))


def contrast(a, b):
    lighter, darker = sorted((luminance(a), luminance(b)), reverse=True)
    return (lighter + .05) / (darker + .05)


def read_theme(path=None, force_fallback=False):
    path = Path(path) if path else Path.home() / ".local/state/omarchy/current/theme/colors.toml"
    if force_fallback:
        return dict(FALLBACK), "Built-in palette"
    try:
        with path.open("rb") as stream:
            raw = stream.read(65537)
        if len(raw) > 65536:
            raise ValueError("Theme is too large")
        values = tomllib.loads(raw.decode())
        mapping = {"background": "background", "surface": "lighter_background", "foreground": "foreground",
                   "muted": "light_foreground", "accent": "accent", "success": "green", "danger": "red"}
        palette = {}
        for role, key in mapping.items():
            value = values.get(key)
            if not isinstance(value, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
                raise ValueError("Missing or invalid color")
            palette[role] = value
        for role in ("foreground", "muted", "accent", "success", "danger"):
            if min(contrast(palette[role], palette[bg]) for bg in ("background", "surface")) < 4.5:
                palette[role] = palette["foreground"]
        if min(contrast(palette["foreground"], palette[bg]) for bg in ("background", "surface")) < 4.5:
            raise ValueError("Insufficient text contrast")
        return palette, "Omarchy palette"
    except (OSError, ValueError, UnicodeError, tomllib.TOMLDecodeError):
        return dict(FALLBACK), "Built-in palette · theme unavailable or unreadable"
