from datetime import date

import streamlit as st

from crm.quotes import render_quotes_area
from crm.data import clear_all_caches
from crm.utils import display_df, filter_df, format_currency, short_id


def render(ctx):
    customers_df = ctx.dfs["customers_df"]
    leads_df = ctx.dfs["leads_df"]
    pricing_df = ctx.dfs["pricing_df"]
    quotes_df = ctx.dfs["quotes_df"]

    tab_leads, tab_pricing, tab_quotes = st.tabs(["Leads", "Kalkyle", "Tilbud"])

    with tab_leads:
        left, right = st.columns([1.05, 0.95])
        with left:
            search = st.text_input("Søk i leads")
            status_filter = st.selectbox("Status", ["Alle", "Ny", "Kontaktet", "Tilbud sendt", "Vunnet", "Tapt"])
            view = filter_df(leads_df, ctx.global_search, ["description", "source", "status", "note"])
            view = filter_df(view, search, ["description", "source", "status", "note"])
            if status_filter != "Alle" and not view.empty:
                view = view[view["status"] == status_filter]
            if view.empty:
                st.info("Ingen leads.")
            else:
                st.dataframe(display_df(view, ctx.show_internal_ids), use_container_width=True, hide_index=True)
        with right:
            customers_opts = {f"{row['name']} • {short_id(row['id'])}": row["id"] for _, row in customers_df.iterrows()} if not customers_df.empty else {}
            with st.form("new_lead_form", clear_on_submit=True):
                customer_label = st.selectbox("Kunde *", list(customers_opts.keys()) if customers_opts else [])
                description = st.text_input("Beskrivelse *")
                source = st.text_input("Kilde", value="Tips")
                status = st.selectbox("Status", ["Ny", "Kontaktet", "Tilbud sendt", "Vunnet", "Tapt"])
                estimated_value = st.number_input("Estimert verdi", min_value=0.0, value=0.0, step=500.0)
                follow_up_date = st.date_input("Neste oppfølging", value=date.today())
                note = st.text_area("Notat")
                submitted = st.form_submit_button("Legg til lead")
                if submitted:
                    if not customers_opts:
                        st.warning("Du må ha minst én kunde.")
                    elif not description.strip():
                        st.warning("Beskrivelse må fylles ut.")
                    else:
                        ctx.client.table("leads").insert({
                            "user_id": ctx.user_id,
                            "company_id": ctx.company_id,
                            "customer_id": customers_opts[customer_label],
                            "description": description.strip(),
                            "source": source.strip() or None,
                            "status": status,
                            "estimated_value": float(estimated_value),
                            "follow_up_date": follow_up_date.isoformat(),
                            "note": note.strip() or None,
                        }).execute()
                        clear_all_caches()
                        st.success("Lead lagret.")
                        st.rerun()

    with tab_pricing:
        left, right = st.columns([1.05, 0.95])
        with left:
            search = st.text_input("Søk i kalkyler")
            view = filter_df(pricing_df, ctx.global_search, ["job_type", "complexity", "note"])
            view = filter_df(view, search, ["job_type", "complexity", "note"])
            if view.empty:
                st.info("Ingen kalkyler.")
            else:
                st.dataframe(display_df(view, ctx.show_internal_ids), use_container_width=True, hide_index=True)
        with right:
            customers_opts = {f"{row['name']} • {short_id(row['id'])}": row["id"] for _, row in customers_df.iterrows()} if not customers_df.empty else {}
            lead_opts = {f"{row['description']} • {short_id(row['id'])}": row["id"] for _, row in leads_df.iterrows()} if not leads_df.empty else {}
            with st.form("new_pricing_form", clear_on_submit=True):
                customer_label = st.selectbox("Kunde *", list(customers_opts.keys()) if customers_opts else [])
                lead_label = st.selectbox("Lead (valgfri)", ["Ingen"] + list(lead_opts.keys()))
                job_type = st.text_input("Oppdragstype *", value="Trefelling")
                travel_km = st.number_input("Reise km", min_value=0.0, value=20.0, step=1.0)
                complexity = st.selectbox("Kompleksitet", ["Lav", "Middels", "Høy"])
                estimated_hours = st.number_input("Estimerte timer", min_value=0.0, value=6.0, step=0.5)
                hourly_rate = st.number_input("Timepris", min_value=0.0, value=850.0, step=50.0)
                extra_equipment_cost = st.number_input("Ekstra utstyr", min_value=0.0, value=500.0, step=100.0)
                disposal_cost = st.number_input("Bortkjøring / avfall", min_value=0.0, value=0.0, step=100.0)
                minimum_price = st.number_input("Minstepris", min_value=0.0, value=3500.0, step=100.0)
                valid_until = st.date_input("Gyldig til", value=date.today())
                note = st.text_area("Notat")
                travel_cost = travel_km * 8
                base_labor = estimated_hours * hourly_rate
                multiplier = {"Lav": 1.0, "Middels": 1.2, "Høy": 1.45}[complexity]
                calculated_price = max(minimum_price, round((base_labor + travel_cost + extra_equipment_cost + disposal_cost) * multiplier / 100) * 100)
                st.info(f"Beregnet pris: {format_currency(calculated_price)}")
                submitted = st.form_submit_button("Lagre kalkyle")
                if submitted:
                    if not customers_opts:
                        st.warning("Du må ha minst én kunde.")
                    elif not job_type.strip():
                        st.warning("Oppdragstype må fylles ut.")
                    else:
                        ctx.client.table("pricing_calculations").insert({
                            "user_id": ctx.user_id,
                            "company_id": ctx.company_id,
                            "customer_id": customers_opts[customer_label],
                            "lead_id": None if lead_label == "Ingen" else lead_opts[lead_label],
                            "job_type": job_type.strip(),
                            "travel_km": float(travel_km),
                            "complexity": complexity,
                            "estimated_hours": float(estimated_hours),
                            "hourly_rate": float(hourly_rate),
                            "extra_equipment_cost": float(extra_equipment_cost),
                            "disposal_cost": float(disposal_cost),
                            "minimum_price": float(minimum_price),
                            "calculated_price": float(calculated_price),
                            "valid_until": valid_until.isoformat(),
                            "note": note.strip() or None,
                        }).execute()
                        clear_all_caches()
                        st.success("Kalkyle lagret.")
                        st.rerun()

    with tab_quotes:
        render_quotes_area(ctx, customers_df, pricing_df, quotes_df)