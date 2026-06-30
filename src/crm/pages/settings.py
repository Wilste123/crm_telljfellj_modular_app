import streamlit as st

from crm.data import clear_all_caches


def fetch_quote_terms(ctx):
    res = (
        ctx.client.table("quote_terms")
        .select("*")
        .eq("company_id", ctx.company_id)
        .eq("is_default", True)
        .limit(1)
        .execute()
    )

    rows = res.data or []

    if rows:
        return rows[0]

    return None


def render_quote_terms_settings(ctx):
    st.markdown("### Standard tilbudsvilkår")

    terms = fetch_quote_terms(ctx)

    if terms:
        current_title = terms.get("title") or "Standard vilkår"
        current_terms = terms.get("terms_text") or ""
        terms_id = terms.get("id")
    else:
        current_title = "Standard vilkår"
        current_terms = (
            "Tilbudet er basert på opplysninger tilgjengelig på tilbudstidspunktet. "
            "Eventuelle endringer i omfang, tilgjengelighet, grunnforhold eller andre "
            "forutsetninger kan påvirke pris og fremdrift."
        )
        terms_id = None

    with st.form("quote_terms_form"):
        title = st.text_input("Tittel", value=current_title)

        terms_text = st.text_area(
            "Vilkårstekst",
            value=current_terms,
            height=260,
        )

        submitted = st.form_submit_button("Lagre vilkår", type="primary")

        if submitted:
            if not terms_text.strip():
                st.warning("Vilkårstekst kan ikke være tom.")
                return

            if terms_id:
                ctx.client.table("quote_terms").update({
                    "title": title.strip() or "Standard vilkår",
                    "terms_text": terms_text.strip(),
                }).eq("id", terms_id).execute()

                st.success("Standardvilkår oppdatert.")
            else:
                ctx.client.table("quote_terms").insert({
                    "company_id": ctx.company_id,
                    "title": title.strip() or "Standard vilkår",
                    "terms_text": terms_text.strip(),
                    "is_default": True,
                }).execute()

                st.success("Standardvilkår opprettet.")

            clear_all_caches()
            st.rerun()


def render(ctx):
    st.markdown("## Innstillinger")

    tab_terms, tab_notifications = st.tabs(
        [
            "Tilbudsvilkår",
            "Varsler",
        ]
    )

    with tab_terms:
        render_quote_terms_settings(ctx)

    with tab_notifications:
        render_notifications_settings(ctx)


def render_notifications_settings(ctx):
    st.markdown("### Varsler")

    st.info(
        "Nivå 1-varsler vises foreløpig inne i appen. "
        "Senere kan vi legge til ekte push/e-post/Telegram-varsel."
    )

    st.markdown(
        """
        Foreløpig varsles aksepterte tilbud på Dashboard og i Salg/Tilbud.
        """
    )