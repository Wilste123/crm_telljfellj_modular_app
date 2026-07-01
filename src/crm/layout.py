from __future__ import annotations

from html import escape

import streamlit as st

from .auth import logout
from .branding import SQUARE_LOGO_PATH, asset_data_uri
from .config import dev_mode
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
            width: 48px;
            height: 48px;
            border-radius: 17px;
            background: linear-gradient(135deg, #09bb7c, #00d4a0);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 1.4rem;
            font-weight: 900;
            box-shadow: 0 12px 28px rgba(9,187,124,0.25);
        }
        .felt-logo-image {
            width: 48px;
            height: 48px;
            border-radius: 17px;
            background: rgba(255, 255, 255, 0.96);
            padding: 5px;
            object-fit: contain;
            box-sizing: border-box;
            display: block;
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.22);
        }
        .felt-brand-title {
            font-weight: 900;
            font-size: 1.08rem;
            color: #f8fbff;
            line-height: 1.1;
        }
        .felt-brand-sub {
            font-size: .8rem;
            color: #9db0ce;
            margin-top: .1rem;
        }
        .crm-topbar {
            display: flex;
            justify-content: space-between;
            gap: 1.4rem;
            margin-bottom: 1.2rem;
        }
        .crm-kicker {
            letter-spacing: .22em;
            text-transform: uppercase;
            color: #047857;
            font-weight: 900;
            font-size: .78rem;
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
            font-size: 1.15rem;
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
            min-width: 320px;
        }
        .crm-bell {
            width: 52px;
            height: 52px;
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
            min-width: 24px;
            height: 24px;
            border-radius: 999px;
            background: #09bb7c;
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0 5px;
            font-size: .78rem;
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
            border-radius: 28px;
            padding: 1.35rem 1.45rem;
            box-shadow: 6px 6px 0 rgba(15,23,42,0.07);
        }
        .crm-kpi-label {
            color: #475569;
            font-weight: 600;
            font-size: .95rem;
            margin-bottom: .55rem;
        }
        .crm-kpi-value {
            font-size: 2.6rem;
            letter-spacing: -.04em;
            font-weight: 880;
            color: #0f1733;
        }
        .crm-kpi-sub {
            display: inline-flex;
            margin-top: .6rem;
            padding: .3rem .6rem;
            border-radius: 999px;
            background: var(--crm-accent-soft);
            color: #047857;
            font-weight: 700;
            font-size: .88rem;
        }
        div[data-testid="stDataFrame"], div[data-testid="stTable"] {
            background: #ffffff;
            border: 1px solid var(--crm-border);
            border-radius: 22px;
            overflow: hidden;
        }
        .block-container hr {
            border-color: #d7e0ea;
        }
        .tf-section-head {
            margin-bottom: 1.2rem;
            padding-bottom: .75rem;
            border-bottom: 1px solid #e2e8f0;
        }
        @media (max-width: 1200px) {
            .crm-title { font-size: 2.2rem; }
            .crm-subtitle { font-size: 1rem; }
            .crm-search { min-width: 200px; }
            .crm-kpi-grid { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(user: dict):
    user_name = escape(user.get("email", "bruker").split("@")[0].replace(".", " ").title())
    notification_count = int(st.session_state.get("notification_count", 0))
    area = escape(st.session_state.get("active_area", "FELT CRM"))
    badge_display = "" if notification_count == 0 else str(notification_count)
    env_suffix = escape(" – testmiljø") if dev_mode() else ""
    st.markdown(
        f"""
        <div class="crm-topbar">
            <div>
                <div class="crm-kicker">{area}</div>
                <h1 class="crm-title">Velkommen, {user_name}{env_suffix}</h1>
                <div class="crm-subtitle">Tilbud, oppdrag og varsler samlet i én ryddig flate.</div>
            </div>
            <div class="crm-actions">
                <div class="crm-search">🔎 Søk i kunder, tilbud, oppdrag...</div>
                <div class="crm-bell">🔔<div class="crm-bell-badge">{badge_display}</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(user):
    """
    Sidebar for hovedappen.

    Viktig:
    app.py forventer at denne returnerer:
    area, global_search, show_internal_ids
    """

    import streamlit as st

    user_email = user.get("email", "") if isinstance(user, dict) else ""
    logo_src = asset_data_uri(SQUARE_LOGO_PATH)
    logo_markup = (
        f'<img class="felt-logo-image" src="{logo_src}" alt="FELT logo" />'
        if logo_src
        else '<div class="tf-logo">F</div>'
    )

    with st.sidebar:
        st.markdown(
            f"""
            <div class="tf-sidebar-brand">
                {logo_markup}
                <div>
                    <div class="felt-brand-title">FELT</div>
                    <div class="felt-brand-sub">Kunder. Tilbud. Oppdrag.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if user_email:
            st.markdown(f"**Bruker:** {user_email}")

        st.markdown('<div class="tf-nav-label">Søk</div>', unsafe_allow_html=True)

        global_search = st.text_input(
            "Globalt søk",
            placeholder="Søk i kunder, tilbud, oppdrag...",
            key="global_search",
        )

        show_internal_ids = st.toggle(
            "Vis tekniske ID-er",
            value=False,
            key="show_internal_ids",
        )

        st.markdown('<div class="tf-nav-label">Arbeidsområde</div>', unsafe_allow_html=True)

        areas = [
            "Dashboard",
            "Kunder",
            "Leads",
            "Salg",
            "Drift",
            "Fakturering",
            "Kursing",
            "Innstillinger",
        ]

        area = st.radio(
            "Velg område",
            areas,
            index=0,
            label_visibility="collapsed",
            key="active_area",
        )

        st.markdown(
            """
            <div class="tf-side-card">
                <div style="font-weight:800;color:white;">Status</div>
                <div style="font-size:.86rem;color:#93a4b8;margin-top:.2rem;">
                    CRM aktiv
                </div>
                <div style="margin-top:.7rem;">
                    <span class="tf-badge tf-badge-success">Innlogget</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Oppdater data", use_container_width=True):
            clear_all_caches()
            st.rerun()

        if st.button("Logg ut", use_container_width=True):
            logout()
            st.rerun()

    return area, global_search, show_internal_ids

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
    projects_needing_attention = 0
    if not projects_df.empty:
        if "status" in projects_df.columns:
            projects_needing_attention = int(
                projects_df["status"].astype(str).str.contains("haster|urgent|kritisk", case=False, na=False).sum()
            )
        elif "ready_for_invoice" in projects_df.columns:
            projects_needing_attention = int(projects_df["ready_for_invoice"].fillna(False).sum())
    accepted_total_display = f"{int(accepted_total):,}".replace(",", " ")
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
                <div class="crm-kpi-value">{accepted_total_display} kr</div>
                <div class="crm-kpi-sub">Totalt akseptert</div>
            </div>
            <div class="crm-kpi">
                <div class="crm-kpi-label">Åpne oppdrag</div>
                <div class="crm-kpi-value">{open_projects}</div>
                <div class="crm-kpi-sub">{projects_needing_attention} haster</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
