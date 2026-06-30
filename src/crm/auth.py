from __future__ import annotations

import streamlit as st
from supabase import Client, create_client

from .config import dev_login_email, dev_login_password, dev_mode, get_supabase_key, get_supabase_url


def normalize_supabase_url(raw_url: str) -> str:
    url = raw_url.strip().rstrip("/")
    for suffix in ("/rest/v1", "/auth/v1", "/storage/v1"):
        if url.endswith(suffix):
            url = url[: -len(suffix)]
    return url


@st.cache_resource
def get_base_client() -> Client:
    return create_client(normalize_supabase_url(get_supabase_url()), get_supabase_key())


def get_client_with_session() -> Client:
    client = get_base_client()
    session_data = st.session_state.get("supabase_session")
    if session_data:
        try:
            client.auth.set_session(
                session_data["access_token"],
                session_data["refresh_token"],
            )
        except Exception:
            st.session_state.pop("supabase_session", None)
            st.session_state.pop("auth_user", None)
    return client


def current_user():
    return st.session_state.get("auth_user")


def login(email: str, password: str):
    client = get_base_client()
    response = client.auth.sign_in_with_password({"email": email, "password": password})
    if not response or not response.user or not response.session:
        raise RuntimeError("Innlogging feilet.")
    st.session_state["auth_user"] = {
        "id": response.user.id,
        "email": response.user.email,
    }
    st.session_state["supabase_session"] = {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
    }


def logout():
    try:
        client = get_client_with_session()
        client.auth.sign_out()
    except Exception:
        pass
    finally:
        st.session_state.pop("supabase_session", None)
        st.session_state.pop("auth_user", None)


def ensure_dev_autologin():
    if not dev_mode():
        return
    if current_user():
        return
    email = dev_login_email()
    password = dev_login_password()
    if not email or not password:
        st.error("DEV_MODE er aktiv, men DEV_LOGIN_EMAIL / DEV_LOGIN_PASSWORD mangler i secrets.")
        st.stop()
    try:
        login(email, password)
        st.rerun()
    except Exception as e:
        st.error(f"Auto-login i DEV_MODE feilet: {e}")
        st.stop()


def render_login_screen():
    ensure_dev_autologin()

    if current_user():
        return

    st.markdown(
        """
        <div class="hero">
            <h1>📋 Lokal CRM</h1>
            <p>Logg inn med Supabase Auth for å få tilgang til dine egne data.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    left, right = st.columns([0.8, 1.2])
    with left:
        st.markdown("### Innlogging")
        with st.form("login_form"):
            email = st.text_input("E-post")
            password = st.text_input("Passord", type="password")
            submitted = st.form_submit_button("Logg inn")
            if submitted:
                try:
                    login(email, password)
                    st.success("Innlogging ok.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Innlogging feilet: {e}")
    with right:
        st.markdown("### Viktig")
        st.write(
            "- Appen bruker Supabase Auth + RLS.\n"
            "- Brukeren ser kun sine egne rader.\n"
            "- Nye rader lagres med brukerens `user_id`."
        )
    st.stop()
