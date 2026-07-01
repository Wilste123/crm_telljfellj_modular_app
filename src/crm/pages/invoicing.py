import pandas as pd
import streamlit as st

from crm.data import clear_all_caches
from crm.utils import dataframe_to_excel_bytes, display_df, filter_df, format_currency, pdf_from_lines, safe_number, short_id, value_label
from crm.ui.layout import section_title, badge_html, divider


def render(ctx):
    projects_df = ctx.dfs["projects_df"]
    
    section_title("Fakturering", "Fakturagrunnlag og betalingsstatus")
    
    invoice_view = projects_df.copy()
    if not invoice_view.empty:
        search = st.text_input("🔎 Søk i oppdrag", placeholder="Kunde, fakturanummer...")
        invoice_view = filter_df(invoice_view, ctx.global_search, ["customer_name", "project_type", "status", "invoice_number"])
        invoice_view = filter_df(invoice_view, search, ["customer_name", "project_type", "status", "invoice_number"])

    left, right = st.columns([1.05, 0.95])
    with left:
        st.markdown("### 📊 Oppdrag til fakturering")
        if invoice_view.empty:
            st.info("Ingen oppdrag tilgjengelig.")
        else:
            cols = [c for c in ["customer_name", "project_type", "address", "status", "price", "total_logged_hours", "ready_for_invoice", "invoiced", "invoice_number", "start_date"] if c in invoice_view.columns]
            st.dataframe(display_df(invoice_view[cols], ctx.show_internal_ids), use_container_width=True, hide_index=True)

    with right:
        project_opts = {f"{row.get('customer_name', 'Ukjent')} • {row.get('project_type', '')} • {short_id(row['id'])}": row for _, row in projects_df.iterrows()} if not projects_df.empty else {}
        if not project_opts:
            st.info("Ingen oppdrag tilgjengelig.")
            return
        
        project_label = st.selectbox("Velg oppdrag", list(project_opts.keys()))
        selected = project_opts[project_label]

        st.markdown("### 📄 Fakturagrunnlag")
        faktura_pdf = pdf_from_lines("Fakturagrunnlag", [
            f"Kunde: {selected.get('customer_name', '-')}",
            f"Oppdrag-ID: {selected.get('id', '-')}",
            f"Oppdragstype: {selected.get('project_type', '-')}",
            f"Adresse: {value_label(selected.get('address'))}",
            f"Status: {value_label(selected.get('status'))}",
            f"Pris: {format_currency(selected.get('price', 0))}",
            f"Timer logget: {safe_number(selected.get('total_logged_hours', 0))}",
            f"Klar for fakturering: {value_label(selected.get('ready_for_invoice'))}",
            f"Fakturert: {value_label(selected.get('invoiced'))}",
            f"Fakturanummer: {value_label(selected.get('invoice_number'))}",
        ])
        faktura_xlsx = dataframe_to_excel_bytes(pd.DataFrame([selected]), sheet_name="Fakturagrunnlag")
        
        a, b = st.columns(2)
        with a:
            st.download_button("📥 PDF", data=faktura_pdf, file_name=f"fakturagrunnlag_{short_id(selected['id'])}.pdf", mime="application/pdf", use_container_width=True)
        with b:
            st.download_button("📊 Excel", data=faktura_xlsx, file_name=f"fakturagrunnlag_{short_id(selected['id'])}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

        divider()
        st.markdown("### ✏️ Oppdater fakturastatus")
        with st.form("invoice_update_form"):
            ready_for_invoice = st.checkbox("✅ Klar for fakturering", value=bool(selected.get("ready_for_invoice", False)))
            invoiced = st.checkbox("✅ Fakturert", value=bool(selected.get("invoiced", False)))
            invoice_number = st.text_input("Fakturanummer", value=selected.get("invoice_number") or "", placeholder="F.eks. FAK-001-2026")
            invoice_note = st.text_area("Notat", placeholder="Tilleggsinformasjon...")
            submitted = st.form_submit_button("✅ Oppdater status", use_container_width=True)
            if submitted:
                payload = {
                    "ready_for_invoice": ready_for_invoice,
                    "invoiced": invoiced,
                    "invoice_number": invoice_number.strip() or None,
                }
                if invoice_note.strip():
                    existing_note = selected.get("note") or ""
                    payload["note"] = (existing_note + "\n" + invoice_note.strip()).strip()
                ctx.client.table("projects").update(payload).eq("id", selected["id"]).execute()
                clear_all_caches()
                st.success("✅ Fakturastatus oppdatert.")
                st.rerun()
