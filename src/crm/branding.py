from __future__ import annotations

from base64 import b64encode
from functools import lru_cache
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
ASSET_DIR = ROOT_DIR / ".streamlit" / "assets"
FULL_LOGO_PATH = ASSET_DIR / "felt-logo-full.png"
SQUARE_LOGO_PATH = ASSET_DIR / "felt-logo-square.png"
TRANSPARENT_LOGO_PATH = ASSET_DIR / "felt-logo-transparent.png"
FAVICON_PATH = ASSET_DIR / "favicon.png"


@lru_cache(maxsize=None)
def asset_data_uri(path: Path) -> str | None:
    if not path.exists():
        return None

    mime_type = "image/png"
    encoded = b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"
