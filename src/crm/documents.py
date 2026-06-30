from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import streamlit as st

from .config import DOC_BUCKET

AUTHOR_NAME = "William Berg Steffenak"
COPYRIGHT_LINE = "William Berg Steffenak - copyright"
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".png", ".jpg", ".jpeg", ".webp", ".txt", ".csv"}
MAX_FILE_SIZE_MB = 25


def _safe_filename(filename: str) -> str:
    filename = filename.strip().replace(" ", "_")
    filename = re.sub(r"[^A-Za-z0-9._-]", "", filename)
    return filename or "fil"


def _ext(filename: str) -> str:
    return Path(filename).suffix.lower()


def _category_folder(category: str) -> str:
    return category.strip().lower().replace("æ", "ae").replace("ø", "o").replace("å", "a").replace(" ", "_")


def _format_size(num_bytes) -> str:
    if not num_bytes:
        return "-"
    size = float(num_bytes)
    units = ["B", "KB", "MB", "GB"]
    idx = 0
    while size >= 1024 and idx < len(units) - 1:
        size /= 1024
        idx += 1
    return f"{int(size)} {units[idx]}" if idx == 0 else f"{size:.1f} {units[idx]}"


def render_documents_module(supabase, customer_id: str, customer_name: Optional[str] = None, current_user_id: Optional[str] = None):
    st.subheader("📁 Dokumenter")
    if not customer_id:
        st.info("Velg en kunde først for å bruke dokumentmodulen.")
        return
    if customer_name:
        st.caption(f"Kunde: {customer_name}")

    with st.expander("Last opp nytt dokument", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            category = st.selectbox("Kategori", ["Kontrakt", "Tilbud", "Faktura", "Bilde", "Rapport", "Annet"], key=f"doc_category_{customer_id}")
        with c2:
            project_id = st.text_input("Prosjekt-ID (valgfritt)", key=f"doc_project_id_{customer_id}")
        custom_title = st.text_input("Visningsnavn (valgfritt)", key=f"doc_custom_title_{customer_id}")
        uploaded_file = st.file_uploader("Velg fil", type=[e.replace(".", "") for e in sorted(ALLOWED_EXTENSIONS)], key=f"doc_upload_{customer_id}")

        if st.button("Last opp dokument", key=f"doc_upload_btn_{customer_id}", type="primary"):
            if not uploaded_file:
                st.warning("Velg en fil først.")
            else:
                try:
                    file_ext = _ext(uploaded_file.name)
                    if file_ext not in ALLOWED_EXTENSIONS:
                        st.error(f"Filtype {file_ext} er ikke tillatt.")
                        st.stop()
                    file_bytes = uploaded_file.getvalue()
                    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
                        st.error(f"Filen er for stor. Maks størrelse er {MAX_FILE_SIZE_MB} MB.")
                        st.stop()
                    final_name = f"{_safe_filename(custom_title)}{file_ext}" if custom_title.strip() else _safe_filename(uploaded_file.name)
                    mime_type = uploaded_file.type or "application/octet-stream"
                    storage_path = f"customers/{customer_id}/{_category_folder(category)}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{final_name}"
                    supabase.storage.from_(DOC_BUCKET).upload(storage_path, file_bytes, {"content-type": mime_type})
                    payload = {
                        "customer_id": customer_id,
                        "project_id": project_id or None,
                        "file_name": final_name,
                        "file_type": mime_type,
                        "file_size": len(file_bytes),
                        "category": category,
                        "storage_path": storage_path,
                        "author_name": AUTHOR_NAME,
                        "copyright_line": COPYRIGHT_LINE,
                    }
                    if current_user_id:
                        payload["created_by"] = current_user_id
                    supabase.table("documents").insert(payload).execute()
                    st.success("Dokument lastet opp ✅")
                    st.rerun()
                except Exception as e:
                    st.error(f"Opplasting feilet: {e}")

    try:
        res = supabase.table("documents").select("*").eq("customer_id", customer_id).order("uploaded_at", desc=True).execute()
        docs = res.data or []
    except Exception as e:
        st.error(f"Kunne ikke hente dokumenter: {e}")
        return

    if not docs:
        st.info("Ingen dokumenter registrert på denne kunden ennå.")
        return

    categories = ["Alle"] + sorted({d.get("category", "Annet") for d in docs})
    f1, f2 = st.columns([1, 2])
    with f1:
        category_filter = st.selectbox("Filter kategori", categories, key=f"doc_filter_{customer_id}")
    with f2:
        search = st.text_input("Søk i dokumenter", key=f"doc_search_{customer_id}").strip().lower()

    if category_filter != "Alle":
        docs = [d for d in docs if d.get("category") == category_filter]
    if search:
        docs = [d for d in docs if search in (d.get("file_name") or "").lower()]

    for doc in docs:
        left, mid, right = st.columns([5, 1.2, 1])
        with left:
            st.write(f"📄 **{doc.get('file_name', '-')}**")
            st.caption(f"Kategori: {doc.get('category', '-')} | Størrelse: {_format_size(doc.get('file_size'))}")
            st.caption(f"Forfatter: {doc.get('author_name') or '-'}")
            st.caption(doc.get("copyright_line") or "-")
        with mid:
            try:
                file_bytes = supabase.storage.from_(DOC_BUCKET).download(doc["storage_path"])
                st.download_button("Last ned", data=file_bytes, file_name=doc.get("file_name", "dokument"), mime=doc.get("file_type") or "application/octet-stream", key=f"download_{doc['id']}")
            except Exception:
                st.caption("Mangler fil")
        with right:
            if st.button("Slett", key=f"delete_doc_{doc['id']}"):
                try:
                    try:
                        supabase.storage.from_(DOC_BUCKET).remove([doc["storage_path"]])
                    except Exception:
                        pass
                    supabase.table("documents").delete().eq("id", doc["id"]).execute()
                    st.success("Dokument slettet ✅")
                    st.rerun()
                except Exception as e:
                    st.error(f"Sletting feilet: {e}")
