# =========================================
# Dato skrevet: 30.06.2026
# Forfatter: William Berg Steffenak - copyright
# Fil: app.py
# Beskrivelse: Modulær CRM-app med Supabase Auth + RLS
# =========================================
from __future__ import annotations

from pathlib import Path
import sys

# Gjør src/-mappen importbar når appen kjøres direkte med Streamlit
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Nå kan vi importere fra crm
from crm.public_quote import render_public_quote_accept_page

import streamlit as st

from crm.auth import current_user, get_client_with_session, render_login_screen
from crm.config import APP_ICON, APP_TITLE
from crm.context import AppContext
from crm.data import fetch_all_data, fetch_user_companies, prepare_data
from crm.layout import inject_css, render_header, render_kpis, render_sidebar
from crm.pages import courses, customers, dashboard, invoicing, leads, operations, sales, settings
from crm.ui.style import apply_style

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")
inject_css()
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
    key="active_company_select",
)

active_company_id = company_options[selected_company_name]["company_id"]
active_company_role = company_options[selected_company_name]["role"]

# Hent all data tidlig slik at varselteller er klar før headeren tegnes
data = fetch_all_data(user_id, active_company_id)
dfs = prepare_data(data)

# Beregn varselantall (aksepterte tilbud) og lagre i session_state for headeren
_quotes_df = dfs.get("quotes_df")
if _quotes_df is not None and not _quotes_df.empty and "status" in _quotes_df.columns:
    st.session_state["notification_count"] = int(
        _quotes_df["status"].astype(str).str.lower().eq("akseptert").sum()
    )
else:
    st.session_state["notification_count"] = 0

render_header(user)
area, global_search, show_internal_ids = render_sidebar(user)

render_kpis(dfs["customers_df"], dfs["leads_df"], dfs["projects_df"], dfs["quotes_df"])

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
elif area == "Leads":
    leads.render(ctx)
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
