import streamlit as st

from crm.data import clear_all_caches
from crm.utils import display_df, filter_df, format_currency, safe_number, short_id, value_label
from crm.ui.layout import section_title, badge_html, divider


def render(ctx):
    projects_df = ctx.dfs["projects_df"]
    equipment_df = ctx.dfs["equipment_df"]
    customers_df = ctx.dfs["customers_df"]

    section_title("Drift", "Prosjekter, timer og vedlikehold")

    tab1, tab2 = st.tabs(["🏗️ Oppdrag", "🔧 Utstyr"])

    with tab1:
        search = st.text_input(
            "🔎 Søk i oppdrag",
            placeholder="Kunde, adresse, type...",
            key="operations_projects_search",
        )
        view = filter_df(projects_df, ctx.global_search, ["customer_name", "project_type", "address", "status"])
        view = filter_df(view, search, ["customer_name", "project_type", "address", "status"])

        st.markdown("### 📊 Oppdragsoversikt")
        if view.empty:
            st.info("Ingen oppdrag registrert.")
        else:
            cols = [c for c in ["customer_name", "project_type", "address", "status", "price", "total_logged_hours", "start_date"] if c in view.columns]
            st.dataframe(display_df(view[cols], ctx.show_internal_ids), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### ➕ Nytt oppdrag")

        customer_options = {
            f"{row.get('name', 'Ukjent')} • {short_id(row['id'])}": row
            for _, row in customers_df.iterrows()
        } if not customers_df.empty and "id" in customers_df.columns else {}

        if not customer_options:
            st.info("Opprett en kunde under «Kunder» før du kan registrere oppdrag.")
        else:
            with st.form("new_project_form", clear_on_submit=True):
                customer_label = st.selectbox("Kunde *", list(customer_options.keys()))
                project_type = st.selectbox("Oppdragstype", ["Installasjon", "Vedlikehold", "Reparasjon", "Konsultasjon", "Annet"])
                address = st.text_input("Adresse", placeholder="Oppdragssted")
                price = st.number_input("Pris", min_value=0.0, step=500.0)
                status = st.selectbox("Status", ["Planlagt", "Pågår", "Fullført", "Avsluttet"])
                note = st.text_area("Notat", placeholder="Tilleggsinformasjon...")

                submitted = st.form_submit_button("✅ Lagre oppdrag", use_container_width=True)
                if submitted:
                    selected_customer = customer_options[customer_label]
                    try:
                        ctx.client.table("projects").insert({
                            "user_id": ctx.user_id,
                            "company_id": ctx.company_id,
                            "customer_id": selected_customer["id"],
                            "project_type": project_type,
                            "address": address.strip() or None,
                            "price": price,
                            "status": status,
                            "note": note.strip() or None,
                        }).execute()
                    except Exception as err:
                        st.error(f"Kunne ikke lagre oppdrag: {err}")
                    else:
                        clear_all_caches()
                        st.success("✅ Oppdrag lagret.")
                        st.rerun()

    with tab2:
        search = st.text_input(
            "🔎 Søk i utstyr",
            placeholder="Navn, kategori...",
            key="operations_equipment_search",
        )
        view = filter_df(equipment_df, ctx.global_search, ["name", "category", "maintenance_status"])
        view = filter_df(view, search, ["name", "category", "maintenance_status"])

        st.markdown("### 📋 Utstyrsoversikt")
        if view.empty:
            st.info("Ingen utstyr registrert.")
        else:
            cols = [c for c in ["name", "category", "hours_used", "service_interval", "remaining_hours_to_service", "maintenance_status"] if c in view.columns]
            st.dataframe(display_df(view[cols], ctx.show_internal_ids), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### ➕ Nytt utstyr")
        with st.form("new_equipment_form", clear_on_submit=True):
            name = st.text_input("Utstyrnavn *", placeholder="F.eks. Boremaskine XYZ")
            category = st.selectbox("Kategori", ["Verktøy", "Maskin", "Kjøretøy", "Verneutstyr", "Annet"])
            hours_used = st.number_input("Timer brukt", min_value=0.0, step=1.0, value=0.0)
            service_interval = st.number_input("Serviceintervall (timer)", min_value=0, step=50)
            note = st.text_area("Notat", placeholder="Vedlikeholdshistorikk...")

            submitted = st.form_submit_button("✅ Lagre utstyr", use_container_width=True)
            if submitted:
                if not name.strip():
                    st.warning("Utstyrnavn må fylles ut.")
                else:
                    try:
                        ctx.client.table("equipment").insert({
                            "user_id": ctx.user_id,
                            "company_id": ctx.company_id,
                            "name": name.strip(),
                            "category": category,
                            "hours_used": hours_used,
                            "service_interval": service_interval if service_interval > 0 else None,
                            "note": note.strip() or None,
                        }).execute()
                    except Exception as err:
                        st.error(f"Kunne ikke lagre utstyr: {err}")
                    else:
                        clear_all_caches()
                        st.success("✅ Utstyr lagret.")
                        st.rerun()
