import streamlit as st

from crm.data import clear_all_caches
from crm.quotes import render_quotes_module
from crm.utils import display_df, filter_df, short_id
from crm.ui.layout import section_title, badge_html


def render(ctx):
    quotes_df = ctx.dfs["quotes_df"]
    projects_df = ctx.dfs["projects_df"]
    customers_df = ctx.dfs["customers_df"]
    
    section_title("Salg", "Tilbud og salgsprosess")
    
    left, right = st.columns([1.05, 0.95])
    
    with left:
        search = st.text_input("🔎 Søk i tilbud", placeholder="Kunde, tilbudsnummer...")
        view = filter_df(quotes_df, ctx.global_search, ["customer_name", "quote_number", "status", "note"])
        view = filter_df(view, search, ["customer_name", "quote_number", "status", "note"])
        
        st.markdown("### 💼 Tilbudsliste")
        if view.empty:
            st.info("Ingen tilbud registrert.")
        else:
            cols = st.columns(1)
            for idx, (_, row) in enumerate(view.iterrows()):
                status = row.get('status', 'Utkast')
                status_variant = "success" if status == "Akseptert" else "warning" if status == "Sendt" else "neutral"
                
                st.markdown(
                    f"""
                    <div class="tf-list-card" style="margin-bottom: 0.75rem;">
                        <div style="padding: 1rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div class="tf-title">{row.get('customer_name', 'Ukjent')} • {row.get('quote_number', '-')}</div>
                                    <div class="tf-muted" style="margin-top: 0.25rem;">Dato: {row.get('created_at', '-')}</div>
                                </div>
                                {badge_html(status, status_variant)}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with st.expander("📊 Vis tilbudstabell"):
                cols_to_show = [c for c in ["customer_name", "quote_number", "created_at", "status", "total_price"] if c in view.columns]
                st.dataframe(display_df(view[cols_to_show], ctx.show_internal_ids), use_container_width=True, hide_index=True)
    
    with right:
        st.markdown("### ➕ Nytt tilbud")
        
        customer_options = {
            f"{row.get('name', 'Ukjent')} • {short_id(row['id'])}": row['id']
            for _, row in customers_df.iterrows()
        } if not customers_df.empty else {}
        
        if customer_options:
            selected_customer = st.selectbox("Velg kunde", list(customer_options.keys()))
            selected_customer_id = customer_options[selected_customer]
            
            with st.form("new_quote_form", clear_on_submit=True):
                quote_number = st.text_input("Tilbudsnummer", placeholder="F.eks. TLF-001-2026")
                total_price = st.number_input("Totalbeløp", min_value=0.0, step=100.0)
                description = st.text_area("Tilbudsbeskrivelse", placeholder="Detaljert beskrivelse av tilbudet...")
                
                submitted = st.form_submit_button("✅ Opprett tilbud", use_container_width=True)
                if submitted:
                    if not quote_number.strip():
                        st.warning("Tilbudsnummer må fylles ut.")
                    else:
                        ctx.client.table("quotes").insert({
                            "user_id": ctx.user_id,
                            "company_id": ctx.company_id,
                            "customer_id": selected_customer_id,
                            "customer_name": selected_customer.split(" • ")[0],
                            "quote_number": quote_number.strip(),
                            "total_price": total_price,
                            "description": description.strip() or None,
                            "status": "Utkast",
                        }).execute()
                        clear_all_caches()
                        st.success("✅ Tilbud opprettet.")
                        st.rerun()
        else:
            st.info("📌 Opprett minst en kunde før du kan lage tilbud.")
        
        st.markdown("---")
        st.markdown("### 📋 Tilbudsadministrasjon")
        render_quotes_module(ctx)
