import streamlit as st

from crm.data import clear_all_caches
from crm.documents import render_documents_module
from crm.utils import display_df, filter_df, short_id, value_label


def render(ctx):
    customers_df = ctx.dfs["customers_df"]
    left, right = st.columns([1.05, 0.95])
    with left:
        search = st.text_input("Søk i kunder")
        view = filter_df(customers_df, ctx.global_search, ["name", "phone", "email", "address", "customer_type", "note"])
        view = filter_df(view, search, ["name", "phone", "email", "address", "customer_type", "note"])
        st.markdown("### Kundeliste")
        if view.empty:
            st.info("Ingen kunder.")
        else:
            cols = st.columns(2)
            for idx, (_, row) in enumerate(view.iterrows()):
                with cols[idx % 2]:
                    st.markdown(
                        f"""
                        **{row.get('name', '-')}**  
                        Type: {value_label(row.get('customer_type'))}  
                        Telefon: {value_label(row.get('phone'))}  
                        E-post: {value_label(row.get('email'))}  
                        Adresse: {value_label(row.get('address'))}  
                        Notat: {value_label(row.get('note'))}
                        """
                    )
            with st.expander("Vis kundetabell"):
                st.dataframe(display_df(view, ctx.show_internal_ids), use_container_width=True, hide_index=True)

    with right:
        st.markdown("### Ny kunde")
        with st.form("new_customer_form", clear_on_submit=True):
            name = st.text_input("Navn *")
            phone = st.text_input("Telefon")
            email = st.text_input("E-post")
            address = st.text_input("Adresse")
            customer_type = st.selectbox("Kundetype", ["Privat", "Bedrift", "Borettslag", "Annet"])
            note = st.text_area("Notat")
            submitted = st.form_submit_button("Lagre kunde")
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
                    st.success("Kunde lagret.")
                    st.rerun()

        st.markdown("---")
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
