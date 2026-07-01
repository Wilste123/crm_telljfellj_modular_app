import streamlit as st

from crm.data import clear_all_caches
from crm.utils import display_df, filter_df, format_currency, safe_number, short_id, value_label
from crm.ui.layout import section_title, badge_html, divider


def render(ctx):
    projects_df = ctx.dfs["projects_df"]
    equipment_df = ctx.dfs["equipment_df"]
    
    section_title("Drift", "Prosjekter, timer og vedlikehold")
    
    tab1, tab2 = st.tabs(["🏗️ Oppdrag", "🔧 Utstyr"])
    
    with tab1:
        search = st.text_input("🔎 Søk i oppdrag", placeholder="Kunde, adresse, type...")
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
        with st.form("new_project_form", clear_on_submit=True):
            customer_name = st.text_input("Kundenavn *", placeholder="Kunde")
            project_type = st.selectbox("Oppdragstype", ["Installasjon", "Vedlikehold", "Reparasjon", "Konsultasjon", "Annet"])
            address = st.text_input("Adresse", placeholder="Oppdragssted")
            price = st.number_input("Pris", min_value=0.0, step=500.0)
            status = st.selectbox("Status", ["Planlagt", "Pågår", "Fullført", "Avsluttet"])
            note = st.text_area("Notat", placeholder="Tilleggsinformasjon...")
            
            submitted = st.form_submit_button("✅ Lagre oppdrag", use_container_width=True)
            if submitted:
                if not customer_name.strip():
                    st.warning("Kundenavn må fylles ut.")
                else:
                    ctx.client.table("projects").insert({
                        "user_id": ctx.user_id,
                        "company_id": ctx.company_id,
                        "customer_name": customer_name.strip(),
                        "project_type": project_type,
                        "address": address.strip() or None,
                        "price": price,
                        "status": status,
                        "note": note.strip() or None,
                    }).execute()
                    clear_all_caches()
                    st.success("✅ Oppdrag lagret.")
                    st.rerun()
    
    with tab2:
        search = st.text_input("🔎 Søk i utstyr", placeholder="Navn, kategori...")
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
            category = st.selectbox("Kategori", ["Verktøy", "Maskin", "Kjøretøy", "Annet"])
            service_interval = st.number_input("Servicintervall (timer)", min_value=0, step=50)
            maintenance_status = st.selectbox("Status", ["God", "Varsling", "Service nødvendig", "Ute av drift"])
            note = st.text_area("Notat", placeholder="Vedlikeholdshistorikk...")
            
            submitted = st.form_submit_button("✅ Lagre utstyr", use_container_width=True)
            if submitted:
                if not name.strip():
                    st.warning("Utstyrnavn må fylles ut.")
                else:
                    ctx.client.table("equipment").insert({
                        "user_id": ctx.user_id,
                        "company_id": ctx.company_id,
                        "name": name.strip(),
                        "category": category,
                        "service_interval": service_interval,
                        "maintenance_status": maintenance_status,
                        "note": note.strip() or None,
                    }).execute()
                    clear_all_caches()
                    st.success("✅ Utstyr lagret.")
                    st.rerun()
