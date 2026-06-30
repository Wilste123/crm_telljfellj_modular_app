from __future__ import annotations

import streamlit as st

from .auth import logout
from .data import clear_all_caches


def inject_css():
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
        .crm-title {font-size: 1.8rem; font-weight: 750; margin-bottom: .1rem;}
        .crm-subtitle {color: #667085; margin-bottom: 1rem;}
        div[data-testid="stMetric"] {background: #fff; border: 1px solid #eef0f3; padding: .8rem; border-radius: 14px;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(user: dict):
    st.markdown(
        f"""
        <div class="crm-title">Lokal CRM</div>
        <div class="crm-subtitle">Innlogget som: {user.get('email', '-')}</div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(user: dict):
    with st.sidebar:
        st.write(f"Bruker: **{user.get('email', '-')}**")
        global_search = st.text_input("Globalt søk")
        show_internal_ids = st.toggle("Vis tekniske ID-er", value=False)
        if st.button("Oppdater data"):
            
            clear_all_caches()
            st.rerun()
        if st.button("Logg ut"):
            logout()
            st.rerun()
    return global_search, show_internal_ids


def render_kpis(customers_df, leads_df, projects_df, quotes_df):
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Kunder", len(customers_df))
    k2.metric("Leads", len(leads_df))
    k3.metric("Oppdrag", len(projects_df))
    k4.metric("Tilbud", len(quotes_df))
    k5.metric(
        "Klar for fakturering",
        int(projects_df["ready_for_invoice"].fillna(False).sum())
        if not projects_df.empty and "ready_for_invoice" in projects_df.columns else 0,
    )
    k6.metric(
        "Fakturert",
        int(projects_df["invoiced"].fillna(False).sum())
        if not projects_df.empty and "invoiced" in projects_df.columns else 0,
    )
    st.markdown("---")
