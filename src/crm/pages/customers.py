import streamlit as st

from crm.data import clear_all_caches
from crm.documents import render_documents_module
from crm.utils import display_df, filter_df, short_id, value_label
from crm.ui.layout import section_title, divider, badge_html


def render(ctx):
    customers_df = ctx.dfs["customers_df"]
    
    section_title("Kunder", "Administrer kunderegister")
    
    left, right = st.columns([1.05, 0.95])
    with left:
        search = st.text_input("🔎 Søk i kunder", placeholder="Navn, telefon, e-post...")
        view = filter_df(customers_df, ctx.global_search, ["name", "phone", "email", "address", "customer_type", "note"])
        view = filter_df(view, search, ["name", "phone", "email", "address", "customer_type", "note"])
        
        st.markdown("### 👥 Kundeliste")
        if view.empty:
            st.info("Ingen kunder funnet.")
        else:
            cols = st.columns(2)
            for idx, (_, row) in enumerate(view.iterrows()):
                with cols[idx % 2]:
                    customer_type_variant = "info" if row.get('customer_type') == "Bedrift" else "neutral"
                    st.markdown(
                        f"""
                        <div class="tf-list-card" style="padding: 1rem;">
                            <div class="tf-title">{row.get('name', '-')}</div>
                            <div class="tf-muted" style="margin-top: 0.5rem;">
                                {badge_html(row.get('customer_type', 'Ukjent'), customer_type_variant)}
                            </div>
                            <div style="font-size: 0.85rem; color: #64748b; margin-top: 0.5rem;">
                                📱 {value_label(row.get('phone'))}<br>
                                📧 {value_label(row.get('email'))}<br>
                                📍 {value_label(row.get('address'))}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            with st.expander("📊 Vis kundetabell"):
                st.dataframe(display_df(view, ctx.show_internal_ids), use_container_width=True, hide_index=True)

    with right:
        st.markdown("### ➕ Ny kunde")
        with st.form("new_customer_form", clear_on_submit=True):
            name = st.text_input("Navn *", placeholder="Kundens navn")
            phone = st.text_input("Telefon", placeholder="+47 12345678")
            email = st.text_input("E-post", placeholder="kunde@example.com")
            address = st.text_input("Adresse", placeholder="Gateadresse")
            customer_type = st.selectbox("Kundetype", ["Privat", "Bedrift", "Borettslag", "Annet"])
            note = st.text_area("Notat", placeholder="Tilleggsinformasjon...")
            submitted = st.form_submit_button("✅ Lagre kunde", use_container_width=True)
            if submitted:
                if not name.strip():
                    st.warning("Navn må fylles ut.")
                else:
                    ctx.client.table("customers").insert({
                        "user_id": ctx.user_id,
                        "company_id": ctx.company_id,
                        "name": name.strip(),
                        "phone": phone.strip() or None,
                        "email": email.strip() or None,
                        "address": address.strip() or None,
                        "customer_type": customer_type,
                        "note": note.strip() or None,
                    }).execute()
                    clear_all_caches()
                    st.success("✅ Kunde lagret.")
                    st.rerun()

        divider()
        st.markdown("### 📄 Dokumenter")
        customer_options = {
            f"{row.get('name', 'Ukjent')} • {short_id(row['id'])}": row
            for _, row in customers_df.iterrows()
        } if not customers_df.empty and "id" in customers_df.columns else {}
        if customer_options:
            label = st.selectbox("Velg kunde for dokumenter", list(customer_options.keys()))
            row = customer_options[label]
            render_documents_module(ctx.client, row["id"], row.get("name"), ctx.user_id)
        else:
            st.info("Opprett en kunde før du bruker dokumenter.")
