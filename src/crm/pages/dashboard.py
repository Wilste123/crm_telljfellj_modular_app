import streamlit as st

from crm.utils import display_df, filter_df


def render(ctx):
    project_logs_df = ctx.dfs["project_logs_df"]
    equipment_df = ctx.dfs["equipment_df"]
    left, right = st.columns([1.2, 0.8])
    with left:
        st.markdown("### Nyeste aktivitet")
        dashboard_logs = filter_df(project_logs_df, ctx.global_search, ["project_label", "task", "performed_by", "note"])
        if dashboard_logs.empty:
            st.info("Ingen aktivitet registrert.")
        else:
            cols = [c for c in ["project_label", "log_date", "hours", "performed_by", "task", "next_step"] if c in dashboard_logs.columns]
            st.dataframe(display_df(dashboard_logs[cols], ctx.show_internal_ids), use_container_width=True, hide_index=True)
    with right:
        st.markdown("### Vedlikeholdsstatus")
        equip_view = filter_df(equipment_df, ctx.global_search, ["name", "category", "maintenance_status", "note"])
        if equip_view.empty:
            st.info("Ingen utstyr.")
        else:
            cols = [c for c in ["name", "category", "hours_used", "service_interval", "remaining_hours_to_service", "maintenance_status"] if c in equip_view.columns]
            st.dataframe(display_df(equip_view[cols], ctx.show_internal_ids), use_container_width=True, hide_index=True)
