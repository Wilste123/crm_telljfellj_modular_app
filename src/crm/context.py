from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AppContext:
    client: Any
    user: dict
    user_id: str
    company_id: str
    company_role: str
    data: dict
    dfs: dict
    global_search: str
    show_internal_ids: bool