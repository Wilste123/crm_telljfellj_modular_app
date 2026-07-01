from __future__ import annotations

import streamlit as st

from .branding import FAVICON_PATH

APP_TITLE = "Lokal CRM"
APP_ICON = str(FAVICON_PATH) if FAVICON_PATH.exists() else "📋"
APP_AUTHOR = "William Berg Steffenak - copyright"
DOC_BUCKET = "crm-files"


def get_supabase_url() -> str:
    return st.secrets["SUPABASE_URL"]


def get_supabase_key() -> str:
    return st.secrets.get("SUPABASE_PUBLISHABLE_KEY") or st.secrets.get("SUPABASE_KEY")


def dev_mode() -> bool:
    return bool(st.secrets.get("DEV_MODE", False))


def dev_login_email() -> str:
    return st.secrets.get("DEV_LOGIN_EMAIL", "")


def dev_login_password() -> str:
    return st.secrets.get("DEV_LOGIN_PASSWORD", "")
