import streamlit as st

from crm.utils import display_df, filter_df
from crm.ui.layout import section_title, divider


def render(ctx):
    project_logs_df = ctx.dfs["project_logs_df"]
    equipment_df = ctx.dfs["equipment_df"]
    quotes_df = ctx.dfs["quotes_df"]
    
    section_title("Siste tilbud", "Status på tilbud sendt fra appen")
    
    left, right = st.columns([1.55, 0.75])
    with left:
        quotes_view = filter_df(quotes_df, ctx.global_search, ["customer_name", "quote_number", "status", "description", "note"])
        if quotes_view.empty:
            st.info("Ingen tilbud registrert.")
        else:
            cols = [c for c in ["customer_name", "quote_number", "status", "total_price", "created_at"] if c in quotes_view.columns]
            st.dataframe(display_df(quotes_view[cols].head(8), ctx.show_internal_ids), use_container_width=True, hide_index=True)
            if st.button("Nytt tilbud →", use_container_width=False, key="dashboard_new_quote"):
                st.session_state["active_area"] = "Salg"
                st.rerun()

        st.markdown("### 📋 Nyeste aktivitet")
        dashboard_logs = filter_df(project_logs_df, ctx.global_search, ["project_label", "task", "performed_by", "note"])
        if dashboard_logs.empty:
            st.info("Ingen aktivitet registrert.")
        else:
            cols = [c for c in ["project_label", "log_date", "hours", "performed_by", "task", "next_step"] if c in dashboard_logs.columns]
            st.dataframe(display_df(dashboard_logs[cols].head(10), ctx.show_internal_ids), use_container_width=True, hide_index=True)

    with right:
        st.markdown("### 🔔 Varsler")
        accepted_count = 0
        if not quotes_df.empty and "status" in quotes_df.columns:
            accepted_count = int(quotes_df["status"].astype(str).str.lower().eq("akseptert").sum())
        st.success(f"Tilbud akseptert: {accepted_count}")

        upcoming_tasks = filter_df(project_logs_df, ctx.global_search, ["task", "next_step", "project_label"])
        if upcoming_tasks.empty:
            st.info("Ingen planlagte aktiviteter.")
        else:
            first_task = upcoming_tasks.iloc[0]
            task_label = first_task.get("next_step") or first_task.get("task") or "Oppfølging planlagt"
            st.info(f"Nytt oppdrag planlagt: {task_label}")

        divider()
        st.markdown("### ⚙️ Stilretning")
        st.markdown(
            "Proff SaaS-følelse: mørk sidebar, lyse kort, grønn aksent, tydelige statuser og mye luft."
        )

        st.markdown("### 🛠️ Vedlikeholdsstatus")
        equip_view = filter_df(equipment_df, ctx.global_search, ["name", "category", "maintenance_status", "note"])
        if equip_view.empty:
            st.info("Ingen utstyr.")
        else:
            cols = [c for c in ["name", "category", "hours_used", "service_interval", "remaining_hours_to_service", "maintenance_status"] if c in equip_view.columns]
            st.dataframe(display_df(equip_view[cols].head(8), ctx.show_internal_ids), use_container_width=True, hide_index=True)
