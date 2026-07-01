import streamlit as st
import pandas as pd

from crm.data import clear_all_caches
from crm.utils import display_df, filter_df, scoped_key, short_id
from crm.ui.layout import badge_html, section_title


def _set_customer_navigation(customer_id: str | None):
    if not customer_id:
        return
    st.session_state["selected_customer_id"] = customer_id
    st.session_state["active_area"] = "Kunder"


def render_leads_workspace(ctx, show_title: bool = True):
    leads_df = ctx.dfs.get("leads_df", pd.DataFrame())
    customers_df = ctx.dfs.get("customers_df", pd.DataFrame())

    if show_title:
        section_title("Leads", "Lead-oversikt og oppfølging")

    left, right = st.columns([1.15, 0.85])

    with left:
        search = st.text_input(
            "🔎 Søk i leads",
            placeholder="Kunde, status, kilde...",
            key=scoped_key("leads", "search"),
        )
        view = filter_df(leads_df, ctx.global_search, ["customer_name", "status", "source", "title", "note"])
        view = filter_df(view, search, ["customer_name", "status", "source", "title", "note"])

        st.markdown("### 📌 Lead-liste")
        if view.empty:
            st.info("Ingen leads registrert.")
        else:
            for _, row in view.iterrows():
                customer_name = row.get("customer_name", "Ukjent")
                status = row.get("status", "Ny")
                status_variant = "warning" if str(status).lower() in {"ny", "åpen", "open"} else "success"

                st.markdown(
                    f"""
                    <div class="tf-list-card" style="margin-bottom: .75rem;">
                        <div style="padding: 1rem;">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <div class="tf-title">{row.get('title') or row.get('source') or 'Lead'}</div>
                                {badge_html(str(status), status_variant)}
                            </div>
                            <div class="tf-muted" style="margin-top:.35rem;">Kunde: {customer_name}</div>
                            <div class="tf-muted" style="margin-top:.2rem;">Kilde: {row.get('source', '-')}</div>
                            <div class="tf-muted" style="margin-top:.2rem;">Notat: {row.get('note', '-')}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    f"Åpne kundekort: {customer_name}",
                    key=scoped_key("leads:open_customer", str(row.get("id") or customer_name)),
                    use_container_width=False,
                ):
                    _set_customer_navigation(row.get("customer_id"))
                    st.rerun()

            with st.expander("📊 Vis leadtabell"):
                cols = [
                    col
                    for col in ["customer_name", "title", "status", "source", "note", "created_at"]
                    if col in view.columns
                ]
                st.dataframe(display_df(view[cols], ctx.show_internal_ids), use_container_width=True, hide_index=True)

    with right:
        st.markdown("### ➕ Ny lead")
        customer_options = {
            f"{row.get('name', 'Ukjent')} • {short_id(row['id'])}": row
            for _, row in customers_df.iterrows()
        } if not customers_df.empty and "id" in customers_df.columns else {}

        with st.form(scoped_key("leads", "new_lead_form"), clear_on_submit=True):
            if not customer_options:
                st.info("Opprett en kunde før du registrerer leads.")
                st.form_submit_button("✅ Lagre lead", disabled=True, use_container_width=True)
            else:
                customer_label = st.selectbox("Kunde *", list(customer_options.keys()))
                title = st.text_input("Lead-tittel", placeholder="F.eks. Ønsker befaring")
                source = st.selectbox("Kilde", ["Nettside", "Telefon", "E-post", "Møte", "Annet"])
                status = st.selectbox("Status", ["Ny", "Pågår", "Kvalifisert", "Lukket"])
                note = st.text_area("Notat", placeholder="Detaljer om henvendelsen...")
                submitted = st.form_submit_button("✅ Lagre lead", use_container_width=True)

                if submitted:
                    selected_customer = customer_options.get(customer_label)
                    payload = {
                        "user_id": ctx.user_id,
                        "company_id": ctx.company_id,
                        "customer_id": selected_customer["id"],
                        "title": title.strip() or None,
                        "source": source,
                        "status": status,
                        "note": note.strip() or None,
                    }
                    try:
                        ctx.client.table("leads").insert(payload).execute()
                    except Exception as err:
                        st.error(f"Kunne ikke lagre lead: {err}")
                    else:
                        clear_all_caches()
                        st.success("✅ Lead lagret.")
                        st.rerun()


def render(ctx):
    render_leads_workspace(ctx, show_title=True)
