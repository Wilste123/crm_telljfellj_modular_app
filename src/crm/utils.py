from __future__ import annotations

from datetime import date
from io import BytesIO

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def as_df(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def safe_number(value, default=0.0) -> float:
    try:
        if value in (None, ""):
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def value_label(value) -> str:
    return "-" if value in (None, "") else str(value)


def format_currency(value) -> str:
    return f"{safe_number(value):,.0f} kr".replace(",", " ")


def short_id(value: str | None) -> str:
    if not value:
        return "-"
    return str(value)[:8]


def filter_df(df: pd.DataFrame, search: str, columns: list[str] | None = None) -> pd.DataFrame:
    if df.empty or not search or not search.strip():
        return df
    columns = columns or list(df.columns)
    s = search.strip().lower()
    mask = pd.Series([False] * len(df), index=df.index)
    for col in columns:
        if col in df.columns:
            mask = mask | df[col].astype(str).str.lower().str.contains(s, na=False)
    return df[mask]


def display_df(df: pd.DataFrame, show_internal_ids: bool = False) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if not show_internal_ids:
        hide_cols = [
            c for c in out.columns
            if c == "id" or c.endswith("_id") or c in {"created_at", "updated_at", "user_id"}
        ]
        out = out.drop(columns=hide_cols, errors="ignore")
    return out


def dataframe_to_excel_bytes(df: pd.DataFrame, sheet_name: str = "Data") -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    output.seek(0)
    return output.getvalue()


def pdf_from_lines(title: str, lines: list[str]) -> bytes:
    output = BytesIO()
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(output, pagesize=A4)
    story = [Paragraph(title, styles["Title"]), Spacer(1, 12)]
    for line in lines:
        story.append(Paragraph(str(line).replace("\n", "<br/>") , styles["BodyText"]))
        story.append(Spacer(1, 6))
    doc.build(story)
    output.seek(0)
    return output.getvalue()


def safe_date_input(value, fallback=None):
    if fallback is None:
        fallback = date.today()
    if value in (None, "", pd.NaT):
        return fallback
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return fallback
