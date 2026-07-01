from __future__ import annotations

import pandas as pd
import streamlit as st

from .auth import get_client_with_session
from .utils import as_df, safe_number


@st.cache_data(ttl=60, max_entries=200, show_spinner=False)
def fetch_table(
    _cache_key: str,
    table_name: str,
    order_by: str | None = None,
    ascending: bool = True,
    company_id: str | None = None,
):
    client = get_client_with_session()
    query = client.table(table_name).select("*")
    if company_id:
        query = query.eq("company_id", company_id)
    if order_by:
        query = query.order(order_by, desc=not ascending)
    result = query.execute()
    return result.data or []


def clear_all_caches():
    fetch_table.clear()


def make_cache_key(user_id: str, company_id: str | None = None) -> str:
    if company_id:
        return f"{user_id}:{company_id}"
    return user_id


def fetch_all_data(user_id: str, company_id: str | None = None):
    cache_key = make_cache_key(user_id, company_id)
    return {
        "customers": fetch_table(cache_key, "customers", "created_at", ascending=False, company_id=company_id),
        "leads": fetch_table(cache_key, "leads", "created_at", ascending=False, company_id=company_id),
        "projects": fetch_table(cache_key, "projects", "created_at", ascending=False, company_id=company_id),
        "pricing": fetch_table(cache_key, "pricing_calculations", "created_at", ascending=False, company_id=company_id),
        "quotes": fetch_table(cache_key, "quotes", "created_at", ascending=False, company_id=company_id),
        "project_logs": fetch_table(cache_key, "project_logs", "created_at", ascending=False, company_id=company_id),
        "equipment": fetch_table(cache_key, "equipment", "created_at", ascending=False, company_id=company_id),
        "courses": fetch_table(cache_key, "courses", "created_at", ascending=False, company_id=company_id),
        "project_log_equipment": fetch_table(cache_key, "project_log_equipment", "created_at", ascending=False, company_id=company_id),
        "equipment_service_logs": fetch_table(cache_key, "equipment_service_logs", "service_date", ascending=False, company_id=company_id),
        "documents": fetch_table(cache_key, "documents", "uploaded_at", ascending=False, company_id=company_id),
    }

def fetch_user_companies(user_id: str):
    client = get_client_with_session()

    res = (
        client.table("company_members")
        .select("company_id, role, companies(id, name)")
        .eq("user_id", user_id)
        .execute()
    )

    return res.data or []

def prepare_data(data: dict):
    dfs = {key + "_df": as_df(value) for key, value in data.items()}

    customers_df = dfs.get("customers_df", pd.DataFrame())
    leads_df = dfs.get("leads_df", pd.DataFrame())
    projects_df = dfs.get("projects_df", pd.DataFrame())
    pricing_df = dfs.get("pricing_df", pd.DataFrame())
    quotes_df = dfs.get("quotes_df", pd.DataFrame())
    project_logs_df = dfs.get("project_logs_df", pd.DataFrame())
    equipment_df = dfs.get("equipment_df", pd.DataFrame())
    project_log_equipment_df = dfs.get("project_log_equipment_df", pd.DataFrame())

    customer_lookup = {}
    if not customers_df.empty and "id" in customers_df.columns:
        for _, row in customers_df.iterrows():
            customer_lookup[row["id"]] = row.to_dict()

    for df_name in ["quotes_df", "pricing_df", "leads_df", "projects_df"]:
        df = locals().get(df_name)
        if df is not None and not df.empty and "customer_id" in df.columns:
            df["customer_name"] = df["customer_id"].map(
                lambda x: customer_lookup.get(x, {}).get("name", "Ukjent")
            )

    if not project_logs_df.empty and "project_id" in project_logs_df.columns and not projects_df.empty:
        project_map = {
            row["id"]: f"{row.get('customer_name', 'Ukjent')} • {row.get('project_type', '')}"
            for _, row in projects_df.iterrows()
        }
        project_logs_df["project_label"] = project_logs_df["project_id"].map(
            lambda x: project_map.get(x, "Ukjent oppdrag")
        )

    if not projects_df.empty:
        log_hours = {}
        log_count = {}
        if not project_logs_df.empty and "project_id" in project_logs_df.columns:
            for _, row in project_logs_df.iterrows():
                pid = row["project_id"]
                log_hours[pid] = log_hours.get(pid, 0) + safe_number(row.get("hours", 0))
                log_count[pid] = log_count.get(pid, 0) + 1
        projects_df["total_logged_hours"] = projects_df["id"].map(lambda x: log_hours.get(x, 0.0))
        projects_df["log_entries"] = projects_df["id"].map(lambda x: log_count.get(x, 0))

    if not equipment_df.empty:
        def maintenance_status(row):
            category = row.get("category")
            interval = row.get("service_interval")
            hours_used = safe_number(row.get("hours_used", 0))
            if category == "Verneutstyr":
                return "Årlig kontroll", None
            if interval in (None, ""):
                return "Ingen intervall", None
            remaining = safe_number(interval) - hours_used
            if remaining <= 0:
                return "Service forfalt", remaining
            if remaining <= 10:
                return "Service snart", remaining
            return "OK", remaining

        equipment_df[["maintenance_status", "remaining_hours_to_service"]] = equipment_df.apply(
            lambda row: pd.Series(maintenance_status(row)), axis=1
        )

    dfs.update({
        "customers_df": customers_df,
        "leads_df": leads_df,
        "projects_df": projects_df,
        "pricing_df": pricing_df,
        "quotes_df": quotes_df,
        "project_logs_df": project_logs_df,
        "equipment_df": equipment_df,
        "project_log_equipment_df": project_log_equipment_df,
    })
    return dfs
