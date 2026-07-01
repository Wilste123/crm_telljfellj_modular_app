"""
Layout Components Module for Telljfellj CRM
Provides reusable UI components for modern SaaS dashboard
"""

import streamlit as st

from crm.branding import SQUARE_LOGO_PATH, asset_data_uri


def render_sidebar(
    company_name: str = "Telljfellj",
    user_email: str | None = None,
    active_page: str = "Dashboard",
):
    """Render the professional dark sidebar with navigation"""
    logo_src = asset_data_uri(SQUARE_LOGO_PATH)
    logo_markup = (
        f'<img class="tf-logo-image" src="{logo_src}" alt="FELT logo" />'
        if logo_src
        else '<div class="tf-logo">TF</div>'
    )

    with st.sidebar:
        st.markdown(
            f"""
            <div class="tf-sidebar-brand">
                {logo_markup}
                <div>
                    <div class="tf-brand-title">FELT</div>
                    <div class="tf-brand-sub">Kunder. Tilbud. Oppdrag.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="tf-nav-label">Bedrift</div>', unsafe_allow_html=True)
        st.selectbox("Bedrift", [company_name], label_visibility="collapsed")

        if user_email:
            st.markdown(f"**Bruker:** {user_email}")

        st.markdown('<div class="tf-nav-label">Search</div>', unsafe_allow_html=True)
        st.text_input(
            "Global search",
            label_visibility="collapsed",
            placeholder="Search customers, quotes, tasks...",
        )

        st.markdown('<div class="tf-nav-label">Navigation</div>', unsafe_allow_html=True)

        pages = [
            "Dashboard",
            "Customers",
            "Sales",
            "Operations",
            "Invoicing",
            "Courses",
            "Settings",
        ]

        if active_page not in pages:
            active_page = "Dashboard"

        selected_page = st.radio(
            "Work Area",
            pages,
            index=pages.index(active_page),
            label_visibility="collapsed",
        )

        st.session_state.active_page = selected_page

        st.markdown(
            f"""
            <div class="tf-side-card">
                <div style="font-weight:800;color:white;">Company</div>
                <div style="font-size:.86rem;color:#93a4b8;margin-top:.2rem;">{company_name}</div>
                <div style="margin-top:.7rem;">
                    <span class="tf-badge tf-badge-success">Admin Access Active</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        return selected_page


def render_topbar(
    title: str,
    subtitle: str = "",
    kicker: str = "Dashboard",
    notification_count: int = 0,
):
    """Render the professional topbar with title, search, and notifications"""
    st.markdown(
        f"""
        <div class="tf-topbar">
            <div>
                <div class="tf-kicker">{kicker}</div>
                <h1>{title}</h1>
                <div class="tf-subtitle">{subtitle}</div>
            </div>
            <div style="display:flex;align-items:center;gap:.75rem;">
                <div class="tf-search-pill">Search customers, quotes, tasks...</div>
                <div class="tf-bell">
                    Alert
                    <div class="tf-bell-badge">{notification_count}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_row(items: list[dict]):
    """Render a grid of KPI cards"""
    html = '<div class="tf-kpi-grid">'

    for item in items:
        html += f"""
        <div class="tf-kpi">
            <div class="tf-kpi-label">{item.get("label", "")}</div>
            <div class="tf-kpi-value">{item.get("value", "")}</div>
        </div>
        """

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def section_title(title: str, subtitle: str = ""):
    """Render a section title with optional subtitle"""
    st.markdown(
        f"""
        <div class="tf-section-head">
            <div>
                <h2 style="margin-bottom:.15rem;">{title}</h2>
                <div class="tf-muted">{subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge_html(label: str, variant: str = "neutral"):
    """Generate HTML for a status badge"""
    if variant not in {"success", "info", "neutral", "warning", "danger"}:
        variant = "neutral"

    return f'<span class="tf-badge tf-badge-{variant}">{label}</span>'


def list_card(
    title: str,
    subtitle: str,
    rows: list[dict],
    action_label: str | None = None,
):
    """
    Render a list card with rows.
    
    Args:
        title: Card title
        subtitle: Card subtitle
        rows: List of dicts with keys:
            - "left": main row text
            - "sub": secondary row text (muted)
            - "right": badge/action text
            - "variant": badge variant (success, info, neutral, warning, danger)
        action_label: Optional action badge at header
    """
    action = badge_html(action_label, "info") if action_label else ""

    html = f"""
    <div class="tf-list-card">
        <div class="tf-list-header">
            <div>
                <div class="tf-title">{title}</div>
                <div class="tf-muted">{subtitle}</div>
            </div>
            {action}
        </div>
    """

    for row in rows:
        html += f"""
        <div class="tf-list-row">
            <div>
                <div class="tf-title">{row.get("left", "")}</div>
                <div class="tf-muted">{row.get("sub", "")}</div>
            </div>
            <div>
                {badge_html(row.get("right", ""), row.get("variant", "neutral")) if row.get("right") else ""}
            </div>
        </div>
        """

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


def divider():
    """Render a subtle divider"""
    st.markdown('<div class="tf-divider"></div>', unsafe_allow_html=True)
