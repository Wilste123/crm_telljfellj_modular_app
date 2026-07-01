from datetime import date

import streamlit as st

from crm.data import clear_all_caches
from crm.utils import display_df, filter_df
from crm.ui.layout import section_title, badge_html, divider


def render(ctx):
    courses_df = ctx.dfs["courses_df"]
    
    section_title("Kursing", "Sertifiseringer og opplæring")
    
    left, right = st.columns([1.05, 0.95])
    
    with left:
        search = st.text_input("🔎 Søk i kurs", placeholder="Kurstittel, tilbyder...")
        view = filter_df(courses_df, ctx.global_search, ["title", "course_type", "provider", "documentation", "note"])
        view = filter_df(view, search, ["title", "course_type", "provider", "documentation", "note"])
        
        st.markdown("### 📚 Kursoversikt")
        if view.empty:
            st.info("Ingen kurs registrert.")
        else:
            cols = [c for c in ["title", "course_type", "provider", "course_date", "duration"] if c in view.columns]
            st.dataframe(display_df(view[cols], ctx.show_internal_ids), use_container_width=True, hide_index=True)
    
    with right:
        st.markdown("### ➕ Nytt kurs")
        with st.form("new_course_form", clear_on_submit=True):
            title = st.text_input("Kurstittel *", placeholder="F.eks. Python Grunnkurs")
            course_type = st.selectbox("Type", ["Kurs", "Sertifisering", "Opplæring", "Annet"])
            provider = st.text_input("Tilbyder", placeholder="F.eks. Udemy")
            course_date = st.date_input("Dato", value=date.today())
            duration = st.text_input("Varighet", value="1 dag", placeholder="F.eks. 5 dager")
            documentation = st.text_input("Dokumentasjon / lenke", placeholder="https://example.com")
            note = st.text_area("Notat", placeholder="Ekstra informasjon...")
            
            submitted = st.form_submit_button("✅ Lagre kurs", use_container_width=True)
            if submitted:
                if not title.strip():
                    st.warning("Kurstittel må fylles ut.")
                else:
                    ctx.client.table("courses").insert({
                        "company_id": ctx.company_id,
                        "user_id": ctx.user_id,
                        "title": title.strip(),
                        "course_type": course_type,
                        "provider": provider.strip() or None,
                        "course_date": course_date.isoformat(),
                        "duration": duration.strip() or None,
                        "documentation": documentation.strip() or None,
                        "note": note.strip() or None,
                    }).execute()
                    clear_all_caches()
                    st.success("✅ Kurs lagret.")
                    st.rerun()
