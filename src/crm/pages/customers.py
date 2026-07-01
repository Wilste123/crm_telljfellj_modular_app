import streamlit as st

from crm.data import clear_all_caches
from crm.documents import render_documents_module
from crm.utils import display_df, filter_df, short_id, value_label
from crm.ui.layout import section_title, divider, badge_html


def _find_customer_by_id(customers_df, customer_id: str | None):
    if not customer_id or customers_df.empty or "id" not in customers_df.columns:
        return None
    matches = customers_df[customers_df["id"] == customer_id]
    if matches.empty:
        return None
    return matches.iloc[0].to_dict()


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
                    customer_name = row.get("name", "-")
                    customer_id = row.get("id")
                    customer_type_variant = "info" if row.get('customer_type') == "Bedrift" else "neutral"
                    st.markdown(
                        f"""
                        <div class="tf-list-card" style="padding: 1rem;">
                            <div class="tf-title">{customer_name}</div>
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
                    if st.button(
                        "Åpne kundekort",
                        key=f"open_customer_profile_{customer_id}",
                        use_container_width=True,
                    ):
                        st.session_state["selected_customer_id"] = customer_id
                        st.rerun()
            
            with st.expander("📊 Vis kundetabell"):
                st.dataframe(display_df(view, ctx.show_internal_ids), use_container_width=True, hide_index=True)

    with right:
        st.markdown("### 🗂️ Kundekort")
        customer_options = {
            f"{row.get('name', 'Ukjent')} • {short_id(row['id'])}": row
            for _, row in customers_df.iterrows()
        } if not customers_df.empty and "id" in customers_df.columns else {}

        selected_customer = None
        if customer_options:
            selected_customer_id = st.session_state.get("selected_customer_id")
            selected_customer = _find_customer_by_id(customers_df, selected_customer_id)
            labels = list(customer_options.keys())
            default_index = 0
            if selected_customer is not None:
                for index, label in enumerate(labels):
                    if customer_options[label].get("id") == selected_customer["id"]:
                        default_index = index
                        break
            selected_label = st.selectbox("Velg kunde", labels, index=default_index)
            selected_customer = customer_options[selected_label]
            st.session_state["selected_customer_id"] = selected_customer["id"]

            with st.form(f"customer_profile_form_{selected_customer['id']}", clear_on_submit=False):
                name = st.text_input("Navn *", value=selected_customer.get("name") or "")
                phone = st.text_input("Telefon", value=selected_customer.get("phone") or "")
                email = st.text_input("E-post", value=selected_customer.get("email") or "")
                address = st.text_input("Adresse", value=selected_customer.get("address") or "")
                customer_type = st.selectbox(
                    "Kundetype",
                    ["Privat", "Bedrift", "Borettslag", "Annet"],
                    index=["Privat", "Bedrift", "Borettslag", "Annet"].index(
                        selected_customer.get("customer_type")
                    ) if selected_customer.get("customer_type") in ["Privat", "Bedrift", "Borettslag", "Annet"] else 0,
                )
                note = st.text_area("Notat", value=selected_customer.get("note") or "")
                submitted = st.form_submit_button("💾 Lagre endringer", use_container_width=True)
                if submitted:
                    if not name.strip():
                        st.warning("Navn må fylles ut.")
                    else:
                        try:
                            ctx.client.table("customers").update({
                                "name": name.strip(),
                                "phone": phone.strip() or None,
                                "email": email.strip() or None,
                                "address": address.strip() or None,
                                "customer_type": customer_type,
                                "note": note.strip() or None,
                            }).eq("id", selected_customer["id"]).execute()
                        except Exception as err:
                            st.error(f"Kunne ikke lagre kundekort: {err}")
                        else:
                            clear_all_caches()
                            st.success("✅ Kundekort oppdatert.")
                            st.rerun()
        else:
            st.info("Ingen kunder registrert ennå.")

        divider()
        with st.expander("➕ Opprett ny kunde"):
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
                        try:
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
                        except Exception as err:
                            st.error(f"Kunne ikke lagre kunde: {err}")
                        else:
                            clear_all_caches()
                            st.success("✅ Kunde lagret.")
                            st.rerun()

        divider()
        st.markdown("### 📄 Dokumenter")
        if selected_customer is not None:
            render_documents_module(
                ctx.client,
                selected_customer["id"],
                selected_customer.get("name"),
                ctx.user_id,
            )
        else:
            st.info("Opprett en kunde før du bruker dokumenter.")
