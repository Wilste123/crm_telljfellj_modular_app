from __future__ import annotations

from io import BytesIO

import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from crm.auth import get_base_client
from crm.utils import format_currency


def fetch_public_quote(client, token: str) -> dict | None:
    res = client.rpc(
        "get_quote_public",
        {"p_token": token},
    ).execute()

    rows = res.data or []

    if not rows:
        return None

    return rows[0]


def build_signed_quote_pdf(quote: dict) -> bytes:
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    quote_number = quote.get("quote_number") or "-"
    title = quote.get("title") or quote.get("job_type") or "Tilbud"
    job_type = quote.get("job_type") or title
    description = quote.get("description") or ""

    amount = quote.get("amount") or 0
    vat_rate = quote.get("vat_rate") or 25
    vat_amount = quote.get("vat_amount") or 0
    total_amount = quote.get("total_amount") or 0
    valid_until = quote.get("valid_until") or "-"
    terms_text = quote.get("terms_text") or (
    "Tilbudet er basert på opplysninger tilgjengelig på tilbudstidspunktet. "
    "Eventuelle endringer i omfang, tilgjengelighet, grunnforhold eller andre "
    "forutsetninger kan påvirke pris og fremdrift."
)
    accepted_at = quote.get("accepted_at") or "-"
    accepted_by_name = quote.get("accepted_by_name") or "-"
    accepted_by_email = quote.get("accepted_by_email") or "-"
    accepted_phone = quote.get("accepted_phone") or "-"
    accepted_signature = quote.get("accepted_signature") or "-"
    customer_comment = quote.get("customer_comment") or "-"

    # -----------------------------------------------------
    # HOVEDTILBUD
    # -----------------------------------------------------
    story.append(Paragraph("Signert tilbud", styles["Title"]))
    story.append(Spacer(1, 14))

    story.append(Paragraph("<b>Tilbudsinformasjon</b>", styles["Heading2"]))
    story.append(Paragraph(f"<b>Tilbudsnummer:</b> {quote_number}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Tittel:</b> {title}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Oppdragstype:</b> {job_type}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Gyldig til:</b> {valid_until}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    if description:
        story.append(Paragraph("<b>Beskrivelse / omfang</b>", styles["Heading2"]))
        story.append(Paragraph(str(description).replace("\n", "<br/>"), styles["BodyText"]))
        story.append(Spacer(1, 14))

    # -----------------------------------------------------
    # PRISTABELL
    # -----------------------------------------------------
    story.append(Paragraph("<b>Pris</b>", styles["Heading2"]))

    price_data = [
        ["Beskrivelse", "Beløp"],
        ["Tilbudssum eks. mva", format_currency(amount)],
        [f"MVA ({float(vat_rate):.0f} %)", format_currency(vat_amount)],
        ["Total inkl. mva", format_currency(total_amount)],
    ]

    price_table = Table(price_data, colWidths=[330, 140])
    price_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story.append(price_table)
    story.append(Spacer(1, 16))

    # -----------------------------------------------------
    # VILKÅR
    # -----------------------------------------------------
    story.append(Paragraph("<b>Vilkår</b>", styles["Heading2"]))
    story.append(
        Paragraph(
            str(terms_text).replace("\n", "<br/>"),
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 16))

    story.append(Spacer(1, 20))

    # -----------------------------------------------------
    # SIGNATUR / AKSEPT
    # -----------------------------------------------------
    story.append(Paragraph("<b>Elektronisk aksept/signatur</b>", styles["Heading2"]))

    sign_data = [
        ["Felt", "Verdi"],
        ["Status", "Akseptert"],
        ["Akseptert tidspunkt", str(accepted_at)],
        ["Navn", accepted_by_name],
        ["E-post", accepted_by_email],
        ["Telefon", accepted_phone],
        ["Signatur", accepted_signature],
        ["Kommentar", customer_comment],
    ]

    sign_table = Table(sign_data, colWidths=[150, 330])
    sign_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story.append(sign_table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("<b>Aksepttekst</b>", styles["Heading2"]))
    story.append(
        Paragraph(
            "Kunden har elektronisk bekreftet at kunden har lest tilbudet og godtar pris, "
            "vilkår og omfang slik det fremgår av dette dokumentet. Aksepten er registrert "
            "elektronisk med navn, e-post, telefon, signatur og tidspunkt.",
            styles["BodyText"],
        )
    )

    story.append(Spacer(1, 24))
    story.append(Paragraph("Vennlig hilsen", styles["BodyText"]))
    story.append(Paragraph("William Berg Steffenak", styles["BodyText"]))

    story.append(Spacer(1, 20))
    story.append(Paragraph("William Berg Steffenak - copyright", styles["Normal"]))

    doc.build(story)
    output.seek(0)

    return output.getvalue()


def render_signed_quote_download(quote: dict):
    if quote.get("status") != "Akseptert":
        return

    signed_pdf = build_signed_quote_pdf(quote)
    quote_number = quote.get("quote_number") or "signert_tilbud"

    st.download_button(
        "Last ned signert tilbud",
        data=signed_pdf,
        file_name=f"{quote_number}_signert.pdf",
        mime="application/pdf",
        key=f"signed_quote_download_{quote.get('id')}",
    )


def render_public_quote_accept_page(token: str):
    client = get_base_client()

    st.title("📝 Godta og signer tilbud")

    if not token:
        st.error("Mangler tilbudslenke.")
        st.stop()

    try:
        quote = fetch_public_quote(client, token)
    except Exception as e:
        st.error(f"Kunne ikke hente tilbud: {e}")
        st.stop()

    if not quote:
        st.error("Tilbudet finnes ikke, eller lenken er utløpt.")
        st.stop()

    quote_number = quote.get("quote_number") or "-"
    title = quote.get("title") or quote.get("job_type") or "Tilbud"
    description = quote.get("description") or ""
    total_amount = quote.get("total_amount") or 0
    status = quote.get("status") or "-"
    valid_until = quote.get("valid_until") or "-"

    st.markdown("### Tilbudsinformasjon")
    st.write(f"**Tilbudsnummer:** {quote_number}")
    st.write(f"**Tittel:** {title}")
    st.write(f"**Status:** {status}")
    st.write(f"**Gyldig til:** {valid_until}")
    st.write(f"**Total inkl. mva:** {format_currency(total_amount)}")

    if description:
        st.markdown("#### Beskrivelse")
        st.write(description)

    st.markdown("---")

    if status == "Akseptert":
        st.success("Dette tilbudet er allerede godkjent og signert.")
        render_signed_quote_download(quote)
        st.stop()

    st.markdown("### Godkjenning og signatur")

    st.info(
        "Fyll inn informasjonen under for å godta tilbudet. "
        "Aksepten registreres elektronisk."
    )

    with st.form("accept_quote_form"):
        name = st.text_input(
            "Navn *",
            placeholder="Fullt navn",
        )

        email = st.text_input(
            "E-post *",
            placeholder="navn@eksempel.no",
        )

        phone = st.text_input(
            "Telefon",
            placeholder="+47 ...",
        )

        comment = st.text_area(
            "Kommentar (valgfritt)",
            placeholder="Eventuelle kommentarer til tilbudet",
        )

        signature = st.text_input(
            "Signatur - skriv fullt navn *",
            placeholder="Fullt navn",
        )

        accepted_terms = st.checkbox(
            "Jeg har lest tilbudet og godtar pris, vilkår og omfang. "
            "Jeg forstår at dette registreres som en bindende aksept."
        )

        submitted = st.form_submit_button(
            "Godta og signer tilbud",
            type="primary",
        )

    if submitted:
        if not name.strip():
            st.warning("Navn må fylles ut.")
            st.stop()

        if not email.strip():
            st.warning("E-post må fylles ut.")
            st.stop()

        if "@" not in email:
            st.warning("E-postadressen ser ikke gyldig ut.")
            st.stop()

        if not signature.strip():
            st.warning("Signatur må fylles ut.")
            st.stop()

        if signature.strip().lower() != name.strip().lower():
            st.warning("Signatur må samsvare med navnet.")
            st.stop()

        if not accepted_terms:
            st.warning("Du må bekrefte at du godtar tilbudet.")
            st.stop()

        try:
            result = client.rpc(
                "accept_quote_public",
                {
                    "p_token": token,
                    "p_name": name.strip(),
                    "p_email": email.strip(),
                    "p_phone": phone.strip() or None,
                    "p_signature": signature.strip(),
                    "p_comment": comment.strip() or None,
                },
            ).execute()

            data = result.data or []

            if data and data[0].get("success"):
                st.success("Tilbudet er godkjent og signert. Takk!")
                st.balloons()

                updated_quote = fetch_public_quote(client, token)

                st.markdown("---")
                st.markdown("### Kvittering")
                st.write(f"**Tilbudsnummer:** {quote_number}")
                st.write(f"**Signert av:** {name.strip()}")
                st.write(f"**E-post:** {email.strip()}")

                if phone.strip():
                    st.write(f"**Telefon:** {phone.strip()}")

                if updated_quote:
                    render_signed_quote_download(updated_quote)

                st.info("Du kan nå lukke denne siden.")

            else:
                message = "Kunne ikke godta tilbudet."

                if data and data[0].get("message"):
                    message = data[0]["message"]

                st.error(message)

        except Exception as e:
            st.error(f"Kunne ikke godta tilbudet: {e}")