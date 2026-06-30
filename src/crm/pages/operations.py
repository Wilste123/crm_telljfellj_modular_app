from datetime import date, datetime

import pandas as pd
import streamlit as st

from crm.data import clear_all_caches
from crm.utils import dataframe_to_excel_bytes, display_df, filter_df, format_currency, pdf_from_lines, safe_number, short_id, value_label


def render(ctx):
    projects_df = ctx.dfs["projects_df"]
    project_logs_df = ctx.dfs["project_logs_df"]
    equipment_df = ctx.dfs["equipment_df"]
    project_log_equipment_df = ctx.dfs["project_log_equipment_df"]
    equipment_service_logs_df = ctx.dfs["equipment_service_logs_df"]

    tab_project_card, tab_project_logs, tab_equipment = st.tabs(["Oppdragskort", "Oppdragslogg", "Utstyr"])

    with tab_project_card:
        left, right = st.columns([1.05, 0.95])
        with left:
            search = st.text_input("Søk i oppdrag")
            status_filter = st.selectbox("Oppdragsstatus", ["Alle", "Planlagt", "Pågår", "Fullført", "Fakturert", "Avsluttet"])
            view = filter_df(projects_df, ctx.global_search, ["customer_name", "project_type", "address", "status", "note"])
            view = filter_df(view, search, ["customer_name", "project_type", "address", "status", "note"])
            if status_filter != "Alle" and not view.empty and "status" in view.columns:
                view = view[view["status"] == status_filter]
            if view.empty:
                st.info("Ingen oppdrag.")
            else:
                st.dataframe(display_df(view, ctx.show_internal_ids), use_container_width=True, hide_index=True)
        with right:
            project_opts = {f"{row.get('customer_name', 'Ukjent')} • {row.get('project_type', '')} • {short_id(row['id'])}": row for _, row in projects_df.iterrows()} if not projects_df.empty else {}
            if not project_opts:
                st.info("Ingen oppdrag tilgjengelig.")
            else:
                label = st.selectbox("Velg oppdrag", list(project_opts.keys()))
                row = project_opts[label]
                project_id = row["id"]
                related_logs = project_logs_df[project_logs_df["project_id"] == project_id] if not project_logs_df.empty and "project_id" in project_logs_df.columns else pd.DataFrame()
                total_hours = float(related_logs["hours"].fillna(0).sum()) if not related_logs.empty and "hours" in related_logs.columns else 0.0
                related_links = project_log_equipment_df[project_log_equipment_df["project_log_id"].isin(related_logs["id"].tolist())] if not project_log_equipment_df.empty and not related_logs.empty and "id" in related_logs.columns else pd.DataFrame()
                st.markdown(f"**Kunde:** {row.get('customer_name', '-')}")
                st.markdown(f"**Oppdragstype:** {row.get('project_type', '-')}")
                st.markdown(f"**Adresse:** {value_label(row.get('address'))}")
                st.markdown(f"**Status:** {value_label(row.get('status'))}")
                st.markdown(f"**Pris:** {format_currency(row.get('price', 0))}")
                st.markdown(f"**Timer logget:** {total_hours}")
                st.markdown(f"**Loggposter:** {len(related_logs)}")
                st.markdown(f"**Utstyrskoblinger:** {len(related_links)}")
                if not related_logs.empty:
                    st.dataframe(display_df(related_logs, ctx.show_internal_ids), use_container_width=True, hide_index=True)
                pdf_data = pdf_from_lines("Oppdragskort", [
                    f"Kunde: {row.get('customer_name', '-')}",
                    f"Oppdrag-ID: {row.get('id', '-')}",
                    f"Oppdragstype: {row.get('project_type', '-')}",
                    f"Adresse: {value_label(row.get('address'))}",
                    f"Status: {value_label(row.get('status'))}",
                    f"Pris: {format_currency(row.get('price', 0))}",
                    f"Timer logget: {total_hours}",
                    f"Loggposter: {len(related_logs)}",
                    f"Utstyrskoblinger: {len(related_links)}",
                    f"Fakturanummer: {value_label(row.get('invoice_number'))}",
                ])
                xlsx_data = dataframe_to_excel_bytes(pd.DataFrame([row]), sheet_name="Oppdragskort")
                a, b = st.columns(2)
                with a:
                    st.download_button("Oppdragskort PDF", data=pdf_data, file_name=f"oppdragskort_{short_id(project_id)}.pdf", mime="application/pdf")
                with b:
                    st.download_button("Oppdragskort Excel", data=xlsx_data, file_name=f"oppdragskort_{short_id(project_id)}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with tab_project_logs:
        left, right = st.columns([1.05, 0.95])
        with left:
            search = st.text_input("Søk i oppdragslogg")
            view = filter_df(project_logs_df, ctx.global_search, ["project_label", "task", "performed_by", "deviation", "next_step", "note"])
            view = filter_df(view, search, ["project_label", "task", "performed_by", "deviation", "next_step", "note"])
            if view.empty:
                st.info("Ingen loggposter.")
            else:
                st.dataframe(display_df(view, ctx.show_internal_ids), use_container_width=True, hide_index=True)
            st.markdown("### Utstyr koblet til loggposter")
            if not project_log_equipment_df.empty:
                st.dataframe(display_df(project_log_equipment_df, ctx.show_internal_ids), use_container_width=True, hide_index=True)
            else:
                st.caption("Ingen koblinger ennå.")
        with right:
            project_opts = {f"{row.get('customer_name', 'Ukjent')} • {row.get('project_type', '')} • {short_id(row['id'])}": row["id"] for _, row in projects_df.iterrows()} if not projects_df.empty else {}
            equipment_opts = {f"{row.get('name')} • {row.get('category', '')} • {short_id(row['id'])}": row["id"] for _, row in equipment_df.iterrows()} if not equipment_df.empty else {}
            with st.form("new_log_form", clear_on_submit=True):
                project_label = st.selectbox("Oppdrag *", list(project_opts.keys()) if project_opts else [])
                log_date_value = st.date_input("Dato", value=date.today())
                hours = st.number_input("Timer", min_value=0.0, value=1.0, step=0.5)
                performed_by = st.text_input("Utført av", value="William")
                task = st.text_input("Hva ble gjort *")
                equipment_used = st.text_input("Utstyr brukt (fritekst)")
                deviation = st.text_input("Avvik / hendelser")
                next_step = st.text_input("Neste steg")
                note = st.text_area("Notat")
                eq1 = st.selectbox("Utstyr 1", ["Ingen"] + list(equipment_opts.keys())) if equipment_opts else st.selectbox("Utstyr 1", ["Ingen"])
                eq1_hours = st.number_input("Timer utstyr 1", min_value=0.0, value=0.0, step=0.5)
                submitted = st.form_submit_button("Lagre loggpost")
                if submitted:
                    if not project_opts:
                        st.warning("Du må ha minst ett oppdrag.")
                    elif not task.strip():
                        st.warning("Du må skrive hva som ble gjort.")
                    else:
                        inserted = ctx.client.table("project_logs").insert({
                            "user_id": ctx.user_id,
                            "company_id": ctx.company_id,
                            "project_id": project_opts[project_label],
                            "log_date": log_date_value.isoformat(),
                            "hours": float(hours),
                            "performed_by": performed_by.strip() or None,
                            "task": task.strip(),
                            "equipment_used": equipment_used.strip() or None,
                            "deviation": deviation.strip() or None,
                            "next_step": next_step.strip() or None,
                            "note": note.strip() or None,
                        }).execute()
                        new_log = inserted.data[0]
                        if eq1 != "Ingen":
                            ctx.client.table("project_log_equipment").insert({
                                "user_id": ctx.user_id,
                                "company_id": ctx.company_id,
                                "project_log_id": new_log["id"],
                                "equipment_id": equipment_opts[eq1],
                                "hours_used": float(eq1_hours),
                                "note": f"Registrert fra app {datetime.now().isoformat()}",
                            }).execute()
                        clear_all_caches()
                        st.success("Loggpost lagret.")
                        st.rerun()

    with tab_equipment:
        left, right = st.columns([1.05, 0.95])
        with left:
            search = st.text_input("Søk i utstyr")
            view = filter_df(equipment_df, ctx.global_search, ["name", "category", "status", "note", "maintenance_status"])
            view = filter_df(view, search, ["name", "category", "status", "note", "maintenance_status"])
            if view.empty:
                st.info("Ingen utstyr.")
            else:
                st.dataframe(display_df(view, ctx.show_internal_ids), use_container_width=True, hide_index=True)
            st.markdown("### Servicehistorikk")
            if not equipment_service_logs_df.empty:
                st.dataframe(display_df(equipment_service_logs_df, ctx.show_internal_ids), use_container_width=True, hide_index=True)
            else:
                st.caption("Ingen servicehistorikk.")
        with right:
            with st.form("new_equipment_form", clear_on_submit=True):
                name = st.text_input("Navn *")
                category = st.selectbox("Kategori", ["Motorsag", "Henger", "Vinsj", "Verneutstyr", "Annet"])
                hours_used = st.number_input("Timer brukt", min_value=0.0, value=0.0, step=1.0)
                service_interval = st.number_input("Serviceintervall", min_value=0.0, value=50.0, step=5.0)
                last_service = st.date_input("Sist service", value=date.today())
                status = st.selectbox("Status", ["I drift", "Service", "Ute"])
                note = st.text_area("Notat")
                submitted = st.form_submit_button("Legg til utstyr")
                if submitted:
                    if not name.strip():
                        st.warning("Navn må fylles ut.")
                    else:
                        ctx.client.table("equipment").insert({
                            "user_id": ctx.user_id,
                            "company_id": ctx.company_id,
                            "name": name.strip(),
                            "category": category,
                            "hours_used": float(hours_used),
                            "service_interval": float(service_interval),
                            "last_service": last_service.isoformat(),
                            "status": status,
                            "note": note.strip() or None,
                        }).execute()
                        clear_all_caches()
                        st.success("Utstyr lagret.")
                        st.rerun()
            st.markdown("---")
            equipment_opts = {f"{row.get('name')} • {short_id(row['id'])}": row["id"] for _, row in equipment_df.iterrows()} if not equipment_df.empty else {}
            with st.form("service_form", clear_on_submit=True):
                equipment_label = st.selectbox("Velg utstyr", list(equipment_opts.keys()) if equipment_opts else [])
                service_date = st.date_input("Servicedato", value=date.today())
                hours_at_service = st.number_input("Timer ved service", min_value=0.0, value=0.0, step=0.5)
                description = st.text_input("Beskrivelse", value="Service registrert")
                cost = st.number_input("Kostnad", min_value=0.0, value=0.0, step=100.0)
                performed_by = st.text_input("Utført av", value="William")
                submitted = st.form_submit_button("Registrer service")
                if submitted:
                    if not equipment_opts:
                        st.warning("Ingen utstyr å registrere service på.")
                    else:
                        ctx.client.table("equipment_service_logs").insert({
                            "user_id": ctx.user_id,
                            "company_id": ctx.company_id,
                            "equipment_id": equipment_opts[equipment_label],
                            "service_date": service_date.isoformat(),
                            "hours_at_service": float(hours_at_service),
                            "description": description.strip() or None,
                            "cost": float(cost),
                            "performed_by": performed_by.strip() or None,
                        }).execute()
                        clear_all_caches()
                        st.success("Service registrert.")
                        st.rerun()
                ctx.client.table("equipment").update({
                     "last_service": service_date.isoformat(),
                    "hours_used": float(hours_at_service),
                    "status": "I drift",
                }).eq("id", equipment_opts[equipment_label]).execute()