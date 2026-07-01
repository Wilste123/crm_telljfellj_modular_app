from __future__ import annotations

from html import escape

import streamlit as st

from .auth import logout
from .data import clear_all_caches


def inject_css():
    st.markdown(
        """
        <style>
        :root {
            --crm-bg: #eef1f5;
            --crm-card: #ffffff;
            --crm-border: #d9e1ea;
            --crm-text: #0f172a;
            --crm-muted: #58708f;
            --crm-dark: #01092b;
            --crm-accent: #09bb7c;
            --crm-accent-soft: #d8f2e7;
        }
        html, body, .stApp {
            background: var(--crm-bg) !important;
            color: var(--crm-text);
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        }
        [data-testid="stMainBlockContainer"] {
            max-width: 1480px;
            padding-top: 2.1rem;
            padding-left: 2.6rem;
            padding-right: 2.6rem;
            padding-bottom: 2.8rem;
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #01092b 0%, #000720 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.08) !important;
        }
        section[data-testid="stSidebar"] * { color: #ecf2ff !important; }
        .tf-sidebar-brand {
            display: flex;
            gap: .75rem;
            align-items: center;
            margin-bottom: 1.1rem;
        }
        .tf-logo {
            width: 56px;
            height: 56px;
            border-radius: 18px;
            background: linear-gradient(135deg, #09bb7c, #00d4a0);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 1.5rem;
            font-weight: 900;
        }
        .tf-brand-title {
            font-weight: 800;
            font-size: 1.82rem;
            color: #f8fbff;
            line-height: 1;
        }
        .tf-brand-sub {
            font-size: 1rem;
            color: #9db0ce;
            margin-top: .2rem;
        }
        .tf-nav-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: .9rem 1rem;
            border-radius: 20px;
            margin-bottom: .6rem;
            border: 1px solid transparent;
            background: transparent;
            color: #dce6f9;
            font-size: 1.45rem;
            font-weight: 650;
        }
        .tf-nav-item.active {
            background: #ffffff;
            color: #0f172a;
            border-color: #ffffff;
        }
        .tf-company-card {
            margin-top: 1.3rem;
            background: rgba(19, 33, 71, 0.78);
            border: 1px solid rgba(146, 166, 205, 0.25);
            border-radius: 24px;
            padding: 1rem;
        }
        .tf-company-status {
            display: inline-flex;
            border-radius: 14px;
            padding: .45rem .7rem;
            margin-top: .8rem;
            color: #6ff2ca;
            background: rgba(3, 90, 87, 0.6);
            border: 1px solid rgba(31, 183, 168, .45);
        }
        .crm-topbar {
            display: flex;
            justify-content: space-between;
            gap: 1.4rem;
            margin-bottom: 1.2rem;
        }
        .crm-kicker {
            letter-spacing: .36em;
            text-transform: uppercase;
            color: #0b9967;
            font-weight: 900;
            font-size: .95rem;
            margin-bottom: .2rem;
        }
        .crm-title {
            font-size: 3.55rem;
            font-weight: 860;
            line-height: 1.02;
            margin: 0;
            letter-spacing: -.04em;
        }
        .crm-subtitle {
            margin-top: .65rem;
            font-size: 2rem;
            color: #5f7593;
            font-weight: 500;
        }
        .crm-actions {
            display: flex;
            align-items: center;
            gap: .7rem;
        }
        .crm-search {
            background: #ffffff;
            border: 1px solid var(--crm-border);
            border-radius: 24px;
            color: #8ea0ba;
            font-size: 1.08rem;
            padding: .75rem 1rem;
            min-width: 360px;
        }
        .crm-bell {
            width: 56px;
            height: 56px;
            border-radius: 18px;
            border: 1px solid var(--crm-border);
            background: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            color: #0f172a;
            font-size: 1.2rem;
        }
        .crm-bell-badge {
            position: absolute;
            top: -6px;
            right: -6px;
            width: 28px;
            height: 28px;
            border-radius: 999px;
            background: #09bb7c;
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: .83rem;
            font-weight: 800;
            border: 2px solid #ffffff;
        }
        .crm-kpi-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1.2rem;
            margin: 1.1rem 0 1.7rem;
        }
        .crm-kpi {
            background: var(--crm-card);
            border: 1px solid var(--crm-border);
            border-radius: 30px;
            padding: 1.35rem 1.45rem;
            box-shadow: 8px 8px 0 rgba(15,23,42,0.08);
        }
        .crm-kpi-label {
            color: #5f7593;
            font-weight: 560;
            font-size: 1.95rem;
            margin-bottom: .65rem;
        }
        .crm-kpi-value {
            font-size: 3.15rem;
            letter-spacing: -.04em;
            font-weight: 880;
            color: #0f1733;
        }
        .crm-kpi-sub {
            display: inline-flex;
            margin-top: .65rem;
            padding: .35rem .65rem;
            border-radius: 999px;
            background: var(--crm-accent-soft);
            color: #007453;
            font-weight: 700;
            font-size: 1.03rem;
        }
        div[data-testid="stDataFrame"], div[data-testid="stTable"] {
            background: #ffffff;
            border: 1px solid var(--crm-border);
            border-radius: 28px;
            overflow: hidden;
        }
        .block-container hr {
            border-color: #d7e0ea;
        }
        @media (max-width: 1200px) {
            .crm-title { font-size: 2.4rem; }
            .crm-subtitle { font-size: 1.24rem; }
            .crm-search { min-width: 220px; }
            .crm-kpi-grid { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(user: dict):
    user_name = escape((user.get("email", "bruker").split("@")[0] or "bruker").replace(".", " ").title())
    st.markdown(
        f"""
        <div class="crm-topbar">
            <div>
                <div class="crm-kicker">Dashboard</div>
                <h1 class="crm-title">God oversikt, {user_name}</h1>
                <div class="crm-subtitle">Tilbud, oppdrag og varsler samlet i én ryddig flate.</div>
            </div>
            <div class="crm-actions">
                <div class="crm-search">🔎 Søk i kunder, tilbud, oppdrag...</div>
                <div class="crm-bell">🔔<div class="crm-bell-badge">3</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(user: dict):
    with st.sidebar:
        user_email = escape(user.get("email", "-"))
        st.markdown(
            """
            <div class="tf-sidebar-brand">
                <div class="tf-logo">🏢</div>
                <div>
                    <div class="tf-brand-title">Telljfellj CRM</div>
                    <div class="tf-brand-sub">Modulær bedriftsapp</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="tf-nav-item active"><span>Dashboard</span><span>›</span></div>
            <div class="tf-nav-item"><span>Kunder</span></div>
            <div class="tf-nav-item"><span>Tilbud</span></div>
            <div class="tf-nav-item"><span>Oppdrag</span></div>
            <div class="tf-nav-item"><span>Utstyr</span></div>
            <div class="tf-nav-item"><span>Innstillinger</span></div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div style="height: .6rem;"></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:#8ea2c5;font-size: .9rem;">Innlogget: {user_email}</div>', unsafe_allow_html=True)

        st.markdown('<div style="height: .5rem;"></div>', unsafe_allow_html=True)
        global_search = st.text_input("Globalt søk", placeholder="Søk i kunder, tilbud, oppdrag...")
        show_internal_ids = st.toggle("Vis tekniske ID-er", value=False)

        st.markdown(
            """
            <div class="tf-company-card">
                <div style="font-weight:800;font-size:1.35rem;">Bedrift</div>
                <div style="margin-top:.3rem;color:#a8b9d7;">Telljfellj AS</div>
                <div class="tf-company-status">Admin-tilgang aktiv</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Oppdater data"):
            
            clear_all_caches()
            st.rerun()
        if st.button("Logg ut"):
            logout()
            st.rerun()
    return global_search, show_internal_ids


def render_kpis(customers_df, leads_df, projects_df, quotes_df):
    accepted_quotes = 0
    accepted_total = 0.0
    if not quotes_df.empty:
        statuses = quotes_df["status"].astype(str).str.lower() if "status" in quotes_df.columns else None
        accepted_mask = statuses.eq("akseptert") if statuses is not None else None
        accepted_quotes = int(accepted_mask.sum()) if accepted_mask is not None else 0
        if accepted_mask is not None and "total_price" in quotes_df.columns:
            accepted_total = float(quotes_df.loc[accepted_mask, "total_price"].fillna(0).sum())
    open_projects = len(projects_df)
    urgent_open_projects = (
        int((projects_df["maintenance_status"].astype(str).str.contains("forfalt|snart", case=False, na=False)).sum())
        if not projects_df.empty and "maintenance_status" in projects_df.columns
        else 0
    )
    st.markdown(
        f"""
        <div class="crm-kpi-grid">
            <div class="crm-kpi">
                <div class="crm-kpi-label">Aktive tilbud</div>
                <div class="crm-kpi-value">{len(quotes_df)}</div>
                <div class="crm-kpi-sub">+{accepted_quotes} akseptert</div>
            </div>
            <div class="crm-kpi">
                <div class="crm-kpi-label">Akseptert verdi</div>
                <div class="crm-kpi-value">{int(accepted_total):,} kr</div>
                <div class="crm-kpi-sub">Siste 30 dager</div>
            </div>
            <div class="crm-kpi">
                <div class="crm-kpi-label">Åpne oppdrag</div>
                <div class="crm-kpi-value">{open_projects}</div>
                <div class="crm-kpi-sub">{urgent_open_projects} haster</div>
            </div>
        </div>
        """.replace(",", " "),
        unsafe_allow_html=True,
    )
