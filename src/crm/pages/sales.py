import streamlit as st

from crm.data import clear_all_caches
from crm.pages.leads import render_leads_workspace
from crm.quotes import render_quotes_module
from crm.utils import display_df, filter_df, format_currency, scoped_key, short_id
from crm.ui.layout import section_title, badge_html


def build_pricing_payload(
    ctx,
    customer_id: str,
    job_type: str,
    calculated_price: float,
    note: str | None = None,
) -> dict:
    if not customer_id:
        raise ValueError("Kunde må velges.")
    if not (job_type or "").strip():
        raise ValueError("Kalkyletittel må fylles ut.")

    return {
        "user_id": ctx.user_id,
        "company_id": ctx.company_id,
        "customer_id": customer_id,
        "job_type": job_type.strip(),
        "calculated_price": float(calculated_price),
        "note": (note or "").strip() or None,
    }


def render_kalkyle_submodule(ctx):
    customers_df = ctx.dfs["customers_df"]
    pricing_df = ctx.dfs["pricing_df"]

    st.markdown("### 📐 Kalkyler")

    with st.form(scoped_key("sales:kalkyle", "new_calculation_form"), clear_on_submit=True):
        st.markdown("#### ➕ Ny kalkyle")

        customer_options = {
            f"{row.get('name', 'Ukjent')} • {short_id(row['id'])}": row
            for _, row in customers_df.iterrows()
        } if not customers_df.empty and "id" in customers_df.columns else {}

        if not customer_options:
            st.info("Du må ha minst én kunde før du kan opprette kalkyle.")
        else:
            customer_label = st.selectbox("Kunde *", list(customer_options.keys()))
            job_type = st.text_input("Kalkyletittel *", placeholder="F.eks. Nytt tak")
            calculated_price = st.number_input("Kalkulert pris", min_value=0.0, step=500.0)
            note = st.text_area("Notat", placeholder="Valgfri notattekst")

            submitted = st.form_submit_button("✅ Opprett kalkyle", use_container_width=True)

            if submitted:
                selected_customer = customer_options.get(customer_label)
                try:
                    payload = build_pricing_payload(
                        ctx=ctx,
                        customer_id=selected_customer["id"],
                        job_type=job_type,
                        calculated_price=calculated_price,
                        note=note,
                    )
                except ValueError as err:
                    st.warning(str(err))
                else:
                    try:
                        ctx.client.table("pricing_calculations").insert(payload).execute()
                    except Exception as err:
                        st.error(f"Kunne ikke opprette kalkyle: {err}")
                    else:
                        clear_all_caches()
                        st.success("✅ Kalkyle opprettet.")
                        st.rerun()

    st.markdown("---")
    st.markdown("#### 📋 Eksisterende kalkyler")

    search = st.text_input(
        "🔎 Søk i kalkyler",
        placeholder="Kunde, kalkyle, notat...",
        key=scoped_key("sales:kalkyle", "search"),
    )
    view = filter_df(pricing_df, ctx.global_search, ["customer_name", "job_type", "note"])
    view = filter_df(view, search, ["customer_name", "job_type", "note"])

    cols_to_show = [
        c
        for c in ["customer_name", "job_type", "calculated_price", "note", "created_at", "updated_at"]
        if c in view.columns
    ]

    if not cols_to_show or view.empty:
        st.info("Ingen kalkyler registrert.")
    else:
        shown = view[cols_to_show].copy()
        if "calculated_price" in shown.columns:
            shown["calculated_price"] = shown["calculated_price"].map(format_currency)
        st.dataframe(
            display_df(shown, ctx.show_internal_ids),
            use_container_width=True,
            hide_index=True,
        )


def render_tilbud_submodule(ctx):
    quotes_df = ctx.dfs["quotes_df"]

    left, right = st.columns([1.05, 0.95])

    with left:
        search = st.text_input(
            "🔎 Søk i tilbud",
            placeholder="Kunde, tilbudsnummer...",
            key=scoped_key("sales:quotes", "search"),
        )
        view = filter_df(quotes_df, ctx.global_search, ["customer_name", "quote_number", "status", "note"])
        view = filter_df(view, search, ["customer_name", "quote_number", "status", "note"])

        st.markdown("### 💼 Tilbudsliste")
        if view.empty:
            st.info("Ingen tilbud registrert.")
        else:
            for _, row in view.iterrows():
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
        st.markdown("### 📋 Tilbudsadministrasjon")
        render_quotes_module(ctx, key_namespace="sales:quotes")


SALES_SUBMODULES = (
    ("Kalkyle", render_kalkyle_submodule),
    ("Tilbud", render_tilbud_submodule),
    ("Leads", lambda ctx: render_leads_workspace(ctx, show_title=False)),
)


def render(ctx):
    section_title("Salg", "Tilbud og salgsprosess")

    tabs = st.tabs([label for label, _ in SALES_SUBMODULES])

    for tab, (_, renderer) in zip(tabs, SALES_SUBMODULES):
        with tab:
            renderer(ctx)
