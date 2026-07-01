from __future__ import annotations

import secrets
from datetime import date, datetime
from io import BytesIO
from urllib.parse import quote

import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from crm.config import DOC_BUCKET
from crm.data import clear_all_caches
from crm.utils import display_df, format_currency, safe_number, short_id


AUTHOR_NAME = "William Berg Steffenak"
COPYRIGHT_LINE = "William Berg Steffenak - copyright"


# =========================================================
# HELPERS
# =========================================================

def generate_quote_number() -> str:
    return f"TILBUD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def generate_public_token() -> str:
    return secrets.token_urlsafe(32)


def get_app_public_url() -> str:
    return st.secrets.get("APP_PUBLIC_URL", "http://localhost:8501").rstrip("/")


def build_accept_link(public_token: str) -> str:
    if not public_token:
        return ""
    return f"{get_app_public_url()}/?accept_quote={quote(public_token)}"


def build_mailto_link(to_email: str, subject: str, body: str) -> str:
    return f"mailto:{quote(to_email or '')}?subject={quote(subject or '')}&body={quote(body or '')}"


def build_sms_link(phone: str, body: str) -> str:
    phone = (phone or "").replace(" ", "")
    return f"sms:{phone}?body={quote(body or '')}"


def build_email_body(
    customer_name: str,
    title: str,
    quote_number: str,
    accept_link: str,
) -> str:
    return f"""Hei {customer_name},

Vedlagt finner du tilbud på: {title}

Tilbudsnummer: {quote_number}

Du kan godta tilbudet her:
{accept_link}

Gi gjerne beskjed dersom du har spørsmål, eller ønsker justeringer i tilbudet.

Vennlig hilsen
William Berg Steffenak
"""


def build_sms_body(
    customer_name: str,
    title: str,
    quote_number: str,
    accept_link: str,
) -> str:
    return f"""Hei {customer_name}. Her er tilbud {quote_number} på {title}. Du kan godta tilbudet her: {accept_link} Mvh William"""


def fetch_default_quote_terms(ctx) -> str:
    try:
        res = (
            ctx.client.table("quote_terms")
            .select("terms_text")
            .eq("company_id", ctx.company_id)
            .eq("is_default", True)
            .limit(1)
            .execute()
        )

        rows = res.data or []

        if rows:
            return rows[0].get("terms_text") or ""

    except Exception:
        pass

    return (
        "Tilbudet er basert på opplysninger tilgjengelig på tilbudstidspunktet. "
        "Eventuelle endringer i omfang, tilgjengelighet, grunnforhold eller andre "
        "forutsetninger kan påvirke pris og fremdrift."
    )

# =========================================================
# PDF
# =========================================================

def build_quote_pdf(
    quote_number: str,
    customer_name: str,
    customer_email: str | None,
    title: str,
    description: str,
    amount: float,
    vat_rate: float,
    vat_amount: float,
    total_amount: float,
    valid_until,
    terms_text: str,
) -> bytes:
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Tilbud", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"<b>Tilbudsnummer:</b> {quote_number}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Dato:</b> {date.today().isoformat()}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Gyldig til:</b> {valid_until}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Kunde</b>", styles["Heading2"]))
    story.append(Paragraph(customer_name or "-", styles["BodyText"]))

    if customer_email:
        story.append(Paragraph(customer_email, styles["BodyText"]))

    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Oppdrag</b>", styles["Heading2"]))
    story.append(Paragraph(f"<b>{title}</b>", styles["BodyText"]))

    if description:
        story.append(Paragraph(description.replace("\n", "<br/>"), styles["BodyText"]))

    story.append(Spacer(1, 16))

    data = [
        ["Beskrivelse", "Beløp"],
        ["Tilbudssum eks. mva", format_currency(amount)],
        [f"MVA ({vat_rate:.0f} %)", format_currency(vat_amount)],
        ["Total inkl. mva", format_currency(total_amount)],
    ]

    table = Table(data, colWidths=[330, 140])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(table)
    story.append(Spacer(1, 18))

    story.append(Paragraph("<b>Vilkår</b>", styles["Heading2"]))
    story.append(
        Paragraph(
            str(terms_text).replace("\n", "<br/>"),
            styles["BodyText"],
        )
    )

    story.append(Spacer(1, 28))
    story.append(Paragraph("Vennlig hilsen", styles["BodyText"]))
    story.append(Paragraph(AUTHOR_NAME, styles["BodyText"]))

    story.append(Spacer(1, 20))
    story.append(Paragraph(COPYRIGHT_LINE, styles["Normal"]))

    doc.build(story)
    output.seek(0)

    return output.getvalue()


# =========================================================
# TOKEN
# =========================================================

def ensure_quote_public_token(ctx, quote_row: dict) -> str:
    existing_token = quote_row.get("public_token")

    if existing_token:
        return existing_token

    new_token = generate_public_token()

    ctx.client.table("quotes").update({
        "public_token": new_token,
        "public_token_expires_at": None,
        "updated_at": datetime.now().isoformat(),
    }).eq("id", quote_row["id"]).execute()

    quote_row["public_token"] = new_token

    return new_token


# =========================================================
# DIALOG: SEND EMAIL / SMS
# =========================================================

@st.dialog("Send tilbud", width="large")
def send_quote_dialog(ctx, quote_row: dict, pdf_bytes: bytes | None):
    customer_name = quote_row.get("customer_name", "-")
    customer_email = quote_row.get("customer_email") or ""
    customer_phone = quote_row.get("customer_phone") or ""

    quote_number = quote_row.get("quote_number", "-")
    title = quote_row.get("title") or quote_row.get("job_type") or "Tilbud"

    public_token = ensure_quote_public_token(ctx, quote_row)
    accept_link = build_accept_link(public_token)

    st.write(f"**Tilbud:** {quote_number}")
    st.write(f"**Kunde:** {customer_name}")

    st.markdown("---")
    st.markdown("### E-post")

    to_email = st.text_input(
        "Til",
        value=customer_email,
        key=f"email_to_{quote_row['id']}",
    )

    subject = st.text_input(
        "Emne",
        value=f"Tilbud {quote_number} - {title}",
        key=f"email_subject_{quote_row['id']}",
    )

    default_body = build_email_body(
        customer_name=customer_name,
        title=title,
        quote_number=quote_number,
        accept_link=accept_link,
    )

    body = st.text_area(
        "E-posttekst",
        value=default_body,
        height=230,
        key=f"email_body_{quote_row['id']}",
    )

    if pdf_bytes:
        st.download_button(
            "Last ned tilbudsvedlegg",
            data=pdf_bytes,
            file_name=f"{quote_number}.pdf",
            mime="application/pdf",
            key=f"download_quote_attachment_{quote_row['id']}",
        )
        st.caption("Last ned PDF-en og legg den ved i e-posten som åpnes.")
    else:
        st.warning("PDF mangler. E-post kan åpnes, men vedlegg må eventuelt lastes opp/genereres på nytt.")

    mailto = build_mailto_link(to_email, subject, body)

    if to_email:
        st.link_button("Åpne e-postklient", mailto)
    else:
        st.warning("Fyll inn mottakeradresse først.")

    st.markdown("---")
    st.markdown("### SMS")

    sms_to = st.text_input(
        "Mobilnummer",
        value=customer_phone,
        key=f"sms_to_{quote_row['id']}",
    )

    default_sms = build_sms_body(
        customer_name=customer_name,
        title=title,
        quote_number=quote_number,
        accept_link=accept_link,
    )

    sms_text = st.text_area(
        "SMS-tekst",
        value=default_sms,
        height=140,
        key=f"sms_body_{quote_row['id']}",
    )

    if sms_to:
        st.link_button(
            "Åpne SMS",
            build_sms_link(sms_to, sms_text),
        )
    else:
        st.warning("Fyll inn mobilnummer for SMS.")

    st.markdown("---")
    st.markdown("### Godkjenningslenke")

    st.code(accept_link)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Marker som sendt", key=f"mark_sent_dialog_{quote_row['id']}"):
            ctx.client.table("quotes").update({
                "status": "Sendt",
                "sent_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }).eq("id", quote_row["id"]).execute()

            clear_all_caches()
            st.success("Tilbud markert som sendt.")
            st.rerun()

    with col2:
        if st.button("Lukk", key=f"close_send_dialog_{quote_row['id']}"):
            st.rerun()


# =========================================================
# MAIN RENDER
# =========================================================

def render_quotes_module(ctx):
    return render_quotes_area(
        ctx,
        ctx.dfs.get("customers_df", pd.DataFrame()),
        ctx.dfs.get("pricing_df", pd.DataFrame()),
        ctx.dfs.get("quotes_df", pd.DataFrame()),
    )


def render_quotes_area(
    ctx,
    customers_df: pd.DataFrame,
    pricing_df: pd.DataFrame,
    quotes_df: pd.DataFrame,
):
    st.markdown("### Tilbud")

    tab_new, tab_existing = st.tabs(["Nytt tilbud", "Eksisterende tilbud"])

    # =====================================================
    # NYTT TILBUD
    # =====================================================
    with tab_new:
        if customers_df.empty:
            st.info("Du må ha minst én kunde før du kan lage tilbud.")
            return

        customer_options = {
            f"{row.get('name', 'Ukjent')} • {short_id(row['id'])}": row
            for _, row in customers_df.iterrows()
        }

        pricing_options = {}

        if not pricing_df.empty:
            for _, row in pricing_df.iterrows():
                label = (
                    f"{row.get('customer_name', 'Ukjent')} • "
                    f"{row.get('job_type', 'Kalkyle')} • "
                    f"{format_currency(row.get('calculated_price', 0))} • "
                    f"{short_id(row['id'])}"
                )
                pricing_options[label] = row

        with st.form("new_quote_form", clear_on_submit=False):
            customer_label = st.selectbox(
                "Kunde",
                list(customer_options.keys()),
                key="quote_customer_select",
            )

            selected_customer = customer_options[customer_label]

            pricing_label = st.selectbox(
                "Kalkyle (valgfri)",
                ["Ingen"] + list(pricing_options.keys()),
                key="quote_pricing_select",
            )

            selected_pricing = None

            if pricing_label != "Ingen":
                selected_pricing = pricing_options[pricing_label]

            default_title = "Tilbud"
            default_description = ""
            default_amount = 0.0

            if selected_pricing is not None:
                default_title = selected_pricing.get("job_type") or "Tilbud"
                default_description = selected_pricing.get("note") or selected_pricing.get("job_type") or ""
                default_amount = safe_number(selected_pricing.get("calculated_price", 0))

            title = st.text_input(
                "Tittel",
                value=default_title,
                key="quote_title_input",
            )

            description = st.text_area(
                "Beskrivelse",
                value=default_description,
                height=140,
                key="quote_description_input",
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                amount = st.number_input(
                    "Beløp eks. mva",
                    min_value=0.0,
                    value=float(default_amount),
                    step=500.0,
                    key="quote_amount_input",
                )

            with col2:
                vat_rate = st.number_input(
                    "MVA %",
                    min_value=0.0,
                    value=25.0,
                    step=1.0,
                    key="quote_vat_rate_input",
                )

            with col3:
                valid_until = st.date_input(
                    "Gyldig til",
                    value=date.today(),
                    key="quote_valid_until_input",
                )

            vat_amount = float(amount) * float(vat_rate) / 100
            total_amount = float(amount) + vat_amount

            st.info(f"Total inkl. mva: {format_currency(total_amount)}")

            submitted = st.form_submit_button("Opprett tilbud")

            if submitted:
                if not title.strip():
                    st.warning("Tittel må fylles ut.")
                    return

                quote_number = generate_quote_number()
                public_token = generate_public_token()

                customer_name = selected_customer.get("name", "Ukjent")
                customer_email = selected_customer.get("email")

                job_type_value = title.strip()

                if selected_pricing is not None:
                    job_type_value = selected_pricing.get("job_type") or title.strip()

                terms_text = fetch_default_quote_terms(ctx)

                pdf_bytes = build_quote_pdf(
                    quote_number=quote_number,
                    customer_name=customer_name,
                    customer_email=customer_email,
                    title=title.strip(),
                    description=description.strip(),
                    amount=float(amount),
                    vat_rate=float(vat_rate),
                    vat_amount=float(vat_amount),
                    total_amount=float(total_amount),
                    valid_until=valid_until.isoformat(),
                    terms_text=terms_text,
                )


                storage_path = (
                    f"customers/{selected_customer['id']}/quotes/"
                    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{quote_number}.pdf"
                )

                try:
                    ctx.client.storage.from_(DOC_BUCKET).upload(
                        storage_path,
                        pdf_bytes,
                        {"content-type": "application/pdf"},
                    )

                    quote_payload = {
                        "company_id": ctx.company_id,
                        "user_id": ctx.user_id,
                        "customer_id": selected_customer["id"],
                        "pricing_calculation_id": None if selected_pricing is None else selected_pricing["id"],

                        # VIKTIG: eksisterende quotes-tabell krever denne
                        "job_type": job_type_value,

                        "quote_number": quote_number,
                        "title": title.strip(),
                        "description": description.strip(),
                        "amount": float(amount),
                        "vat_rate": float(vat_rate),
                        "vat_amount": float(vat_amount),
                        "total_amount": float(total_amount),
                        "status": "Utkast",
                        "valid_until": valid_until.isoformat(),
                        "pdf_storage_path": storage_path,

                        "public_token": public_token,
                        "public_token_expires_at": None,
                        "terms_text": terms_text,
                    }

                    inserted_quote = ctx.client.table("quotes").insert(quote_payload).execute()
                    quote_row = inserted_quote.data[0]

                    document_payload = {
                        "company_id": ctx.company_id,
                        "customer_id": selected_customer["id"],
                        "project_id": None,
                        "file_name": f"{quote_number}.pdf",
                        "file_type": "application/pdf",
                        "file_size": len(pdf_bytes),
                        "category": "Tilbud",
                        "storage_path": storage_path,
                        "created_by": ctx.user_id,
                        "author_name": AUTHOR_NAME,
                        "copyright_line": COPYRIGHT_LINE,
                    }

                    ctx.client.table("documents").insert(document_payload).execute()

                    st.success("Tilbud opprettet ✅")
                    st.caption(f"Tilbudsnummer: {quote_number}")

                    clear_all_caches()

                    st.session_state["new_quote_pdf_bytes"] = pdf_bytes
                    st.session_state["new_quote_pdf_name"] = f"{quote_number}.pdf"
                    st.session_state["new_quote_number"] = quote_number
                    st.session_state["new_quote_id"] = quote_row["id"]
                    st.info("Tilbudet er opprettet. Nedlasting vises under skjemaet.")

                except Exception as e:
                    st.error(f"Kunne ikke opprette tilbud: {e}")

    # =====================================================
    # EKSISTERENDE TILBUD
    # =====================================================
    with tab_existing:
        if quotes_df.empty:
            st.info("Ingen tilbud registrert.")
            return

        view = quotes_df.copy()

        if "customer_id" in view.columns and not customers_df.empty:
            customer_lookup = {
                row["id"]: {
                    "name": row.get("name", "Ukjent"),
                    "email": row.get("email"),
                    "phone": row.get("phone"),
                }
                for _, row in customers_df.iterrows()
            }

            view["customer_name"] = view["customer_id"].map(
                lambda x: customer_lookup.get(x, {}).get("name", "Ukjent")
            )

            view["customer_email"] = view["customer_id"].map(
                lambda x: customer_lookup.get(x, {}).get("email")
            )

            view["customer_phone"] = view["customer_id"].map(
                lambda x: customer_lookup.get(x, {}).get("phone")
            )

        st.dataframe(
            display_df(view, ctx.show_internal_ids),
            use_container_width=True,
            hide_index=True,
        )

        quote_options = {
            (
                f"{row.get('quote_number', 'Tilbud')} • "
                f"{row.get('customer_name', 'Ukjent')} • "
                f"{format_currency(row.get('total_amount', 0))}"
            ): row
            for _, row in view.iterrows()
        }

        if not quote_options:
            return

        selected_quote_label = st.selectbox(
            "Velg tilbud",
            list(quote_options.keys()),
            key="existing_quote_select",
        )

        selected_quote = quote_options[selected_quote_label]

        col1, col2, col3, col4 = st.columns(4)

        pdf_bytes = None

        if selected_quote.get("pdf_storage_path"):
            try:
                pdf_bytes = ctx.client.storage.from_(DOC_BUCKET).download(
                    selected_quote["pdf_storage_path"]
                )
            except Exception:
                pdf_bytes = None

        with col1:
            if pdf_bytes:
                st.download_button(
                    "Last ned PDF",
                    data=pdf_bytes,
                    file_name=f"{selected_quote.get('quote_number', 'tilbud')}.pdf",
                    mime="application/pdf",
                    key=f"quote_download_{selected_quote['id']}",
                )
            else:
                st.caption("PDF mangler")

        with col2:
            if st.button("Send e-post/SMS", key=f"quote_send_{selected_quote['id']}"):
                send_quote_dialog(ctx, selected_quote, pdf_bytes)

        with col3:
            if st.button("Marker som sendt", key=f"quote_mark_sent_{selected_quote['id']}"):
                ctx.client.table("quotes").update({
                    "status": "Sendt",
                    "sent_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }).eq("id", selected_quote["id"]).execute()

                clear_all_caches()

                st.success("Tilbud markert som sendt.")
                st.rerun()

        with col4:
            public_token = selected_quote.get("public_token")

            if not public_token:
                if st.button("Lag godkjenningslenke", key=f"quote_create_link_{selected_quote['id']}"):
                    token = ensure_quote_public_token(ctx, selected_quote)
                    st.success("Godkjenningslenke opprettet.")
                    st.code(build_accept_link(token))
            else:
                st.caption("Godkjenningslenke")
                st.code(build_accept_link(public_token))