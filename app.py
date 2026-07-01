# =========================================
# Dato skrevet: 30.06.2026
# Forfatter: William Berg Steffenak - copyright
# Fil: app.py
# Beskrivelse: Modulær CRM-app med Supabase Auth + RLS
# =========================================
from __future__ import annotations
from crm.public_quote import render_public_quote_accept_page

from pathlib import Path
import sys

# Gjør src/-mappen importbar når appen kjøres direkte med Streamlit
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import streamlit as st

from crm.auth import current_user, get_client_with_session, render_login_screen
from crm.config import APP_ICON, APP_TITLE
from crm.context import AppContext
from crm.data import fetch_all_data, prepare_data, fetch_user_companies, clear_all_caches
from crm.ui.style import apply_style
from crm.ui.layout import render_topbar, kpi_row, render_sidebar as render_ui_sidebar
from crm.pages import courses, customers, dashboard, invoicing, operations, sales, settings

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")
apply_style()

if "accept_quote" in st.query_params:
    render_public_quote_accept_page(st.query_params["accept_quote"])
    st.stop()

render_login_screen()

user = current_user()
user_id = user["id"]
client = get_client_with_session()

# Hent bedrifter brukeren er medlem av
memberships = fetch_user_companies(user_id)

if not memberships:
    st.error("Brukeren er ikke koblet til noen bedrift.")
    st.stop()

company_options = {
    row["companies"]["name"]: {
        "company_id": row["company_id"],
        "role": row["role"],
    }
    for row in memberships
    if row.get("companies")
}

selected_company_name = st.sidebar.selectbox(
    "Bedrift",
    list(company_options.keys()),
    key="active_company_select"
)

active_company_id = company_options[selected_company_name]["company_id"]
active_company_role = company_options[selected_company_name]["role"]

# Render modern sidebar
with st.sidebar:
    st.markdown(
        """
        <div class="tf-sidebar-brand">
            <div class="tf-logo">TF</div>
            <div>
                <div class="tf-brand-title">Telljfellj CRM</div>
                <div class="tf-brand-sub">Modulær bedriftsapp</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown('<div class="tf-nav-label">Bedrift</div>', unsafe_allow_html=True)
    st.selectbox("Bedrift", [selected_company_name], label_visibility="collapsed", key="company_display")
    
    st.markdown(f"**Bruker:** {user.get('email', '-')}")
    
    st.markdown('<div class="tf-nav-label">Søk</div>', unsafe_allow_html=True)
    global_search = st.text_input(
        "Globalt søk",
        label_visibility="collapsed",
        placeholder="Søk i kunder, tilbud, oppdrag...",
    )
    
    st.markdown('<div class="tf-nav-label">Verktøy</div>', unsafe_allow_html=True)
    show_internal_ids = st.toggle("Vis tekniske ID-er", value=False)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Oppdater", use_container_width=True):
            clear_all_caches()
            st.rerun()
    with col2:
        if st.button("🚪 Logg ut", use_container_width=True):
            from crm.auth import logout
            logout()
            st.rerun()
    
    st.markdown(
        f"""
        <div class="tf-side-card">
            <div style="font-weight:800;color:white;">Bedrift</div>
            <div style="font-size:.86rem;color:#93a4b8;margin-top:.2rem;">{selected_company_name}</div>
            <div style="margin-top:.7rem;">
                <span class="tf-badge tf-badge-success">Admin-tilgang aktiv</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Behold eksisterende funksjonalitet først: hent alt.
# Neste ytelsessteg er å bytte dette til områdebasert henting.
data = fetch_all_data(user_id)
dfs = prepare_data(data)

# Render modern topbar
render_topbar(
    title="Telljfellj CRM",
    subtitle="Bedriftsadministrasjon og salgsmodul",
    kicker="Oversikt",
    notification_count=0
)

# Render KPIs in modern style
kpi_row([
    {"label": "Kunder", "value": str(len(dfs["customers_df"]))},
    {"label": "Leads", "value": str(len(dfs["leads_df"]))},
    {"label": "Oppdrag", "value": str(len(dfs["projects_df"]))},
    {"label": "Tilbud", "value": str(len(dfs["quotes_df"]))},
    {
        "label": "Klar for fakturering",
        "value": str(
            int(dfs["projects_df"]["ready_for_invoice"].fillna(False).sum())
            if not dfs["projects_df"].empty and "ready_for_invoice" in dfs["projects_df"].columns else 0
        ),
    },
    {
        "label": "Fakturert",
        "value": str(
            int(dfs["projects_df"]["invoiced"].fillna(False).sum())
            if not dfs["projects_df"].empty and "invoiced" in dfs["projects_df"].columns else 0
        ),
    },
])

area = st.segmented_control(
    "Arbeidsområde",
    options=["Dashboard", "Kunder", "Salg", "Drift", "Fakturering", "Kursing", "Innstillinger"],
    default="Dashboard",
)

ctx = AppContext(
    client=client,
    user=user,
    user_id=user_id,
    company_id=active_company_id,
    company_role=active_company_role,
    data=data,
    dfs=dfs,
    global_search=global_search,
    show_internal_ids=show_internal_ids,
)

if area == "Dashboard":
    dashboard.render(ctx)
elif area == "Kunder":
    customers.render(ctx)
elif area == "Salg":
    sales.render(ctx)
elif area == "Drift":
    operations.render(ctx)
elif area == "Fakturering":
    invoicing.render(ctx)
elif area == "Kursing":
    courses.render(ctx)
elif area == "Innstillinger":
    settings.render(ctx)

st.markdown("---")
st.caption("Denne versjonen bruker Supabase Auth + RLS. Alle nye rader lagres med user_id, og hver bruker ser kun egne data.")
