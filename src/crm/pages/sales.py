import streamlit as st

from crm.quotes import render_quotes_module
from crm.utils import display_df, filter_df, scoped_key
from crm.ui.layout import section_title, badge_html


def render_kalkyle_submodule(ctx):
    pricing_df = ctx.dfs["pricing_df"]

    st.markdown("### 📐 Kalkyler")

    if pricing_df.empty:
        st.info("Ingen kalkyler registrert.")
        return

    search = st.text_input(
        "🔎 Søk i kalkyler",
        placeholder="Kunde, kalkyle, notat...",
        key=scoped_key("sales:kalkyle", "search"),
    )
    view = filter_df(pricing_df, ctx.global_search, ["customer_name", "job_type", "note"])
    view = filter_df(view, search, ["customer_name", "job_type", "note"])

    cols_to_show = [
        c
        for c in ["customer_name", "job_type", "calculated_price", "note", "created_at"]
        if c in view.columns
    ]

    st.dataframe(
        display_df(view[cols_to_show], ctx.show_internal_ids),
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
)


def render(ctx):
    section_title("Salg", "Tilbud og salgsprosess")

    tabs = st.tabs([label for label, _ in SALES_SUBMODULES])

    for tab, (_, renderer) in zip(tabs, SALES_SUBMODULES):
        with tab:
            renderer(ctx)
