"""
UI Styling Module for Telljfellj CRM
Provides comprehensive CSS styling for modern SaaS dashboard
"""

import streamlit as st


def apply_style():
    """Apply modern SaaS styling to the Streamlit app"""
    st.markdown(
        """
        <style>
        :root {
            --tf-bg: #f2f6fa;
            --tf-card: #ffffff;
            --tf-card-soft: #f8fafc;
            --tf-border: #e2e8f0;
            --tf-text: #0f172a;
            --tf-muted: #64748b;
            --tf-sidebar: #07111f;
            --tf-sidebar-soft: #0f172a;
            --tf-green: #10b981;
            --tf-green-dark: #047857;
            --tf-green-soft: #ecfdf5;
            --tf-blue: #38bdf8;
            --tf-blue-soft: #eff6ff;
            --tf-yellow-soft: #fffbeb;
            --tf-red-soft: #fef2f2;
            --tf-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
            --tf-shadow-soft: 0 8px 24px rgba(15, 23, 42, 0.06);
        }

        html, body, .stApp {
            background: var(--tf-bg) !important;
            color: var(--tf-text) !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        }

        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #f8fafc 0%, #eef5f7 38%, #f2f6fa 100%) !important;
        }

        header[data-testid="stHeader"] {
            background: rgba(255,255,255,0.88) !important;
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(226, 232, 240, 0.9) !important;
        }

        div[data-testid="stMainBlockContainer"] {
            max-width: 1540px;
            padding-top: 2rem;
            padding-left: 2.8rem;
            padding-right: 2.8rem;
            padding-bottom: 4rem;
        }

        section[data-testid="stSidebar"] {
            background:
                radial-gradient(circle at top left, rgba(16,185,129,0.18), transparent 16rem),
                linear-gradient(180deg, #050b16 0%, #07111f 55%, #081827 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.08) !important;
        }

        section[data-testid="stSidebar"] > div {
            background: transparent !important;
        }

        section[data-testid="stSidebar"] * {
            color: #e5edf7 !important;
        }

        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #ffffff !important;
            font-weight: 700 !important;
        }

        section[data-testid="stSidebar"] input,
        section[data-testid="stSidebar"] textarea,
        section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
            background: #ffffff !important;
            color: #0f172a !important;
            border-radius: 15px !important;
            border: 1px solid rgba(255,255,255,0.55) !important;
            box-shadow: 0 8px 18px rgba(0,0,0,0.12) !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="select"] span {
            color: #0f172a !important;
        }

        h1 {
            color: var(--tf-text) !important;
            font-size: 2.28rem !important;
            font-weight: 850 !important;
            letter-spacing: -0.05em !important;
            line-height: 1.05 !important;
            margin-bottom: 0.35rem !important;
        }

        h2 {
            color: var(--tf-text) !important;
            font-size: 1.45rem !important;
            font-weight: 800 !important;
            letter-spacing: -0.035em !important;
        }

        h3 {
            color: var(--tf-text) !important;
            font-weight: 760 !important;
        }

        .stButton button,
        .stDownloadButton button {
            border-radius: 14px !important;
            background: var(--tf-sidebar) !important;
            color: #ffffff !important;
            border: 1px solid var(--tf-sidebar) !important;
            font-weight: 750 !important;
            min-height: 2.65rem;
            padding: 0.55rem 1.1rem !important;
            box-shadow: var(--tf-shadow-soft) !important;
            transition: 0.15s ease-in-out;
        }

        .stButton button:hover,
        .stDownloadButton button:hover {
            background: #111827 !important;
            transform: translateY(-1px);
            box-shadow: var(--tf-shadow) !important;
        }

        input,
        textarea,
        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div,
        div[data-baseweb="select"] > div {
            background: #ffffff !important;
            color: var(--tf-text) !important;
            border: 1px solid var(--tf-border) !important;
            border-radius: 14px !important;
        }

        input:focus,
        textarea:focus,
        div[data-baseweb="select"] > div:focus-within {
            border-color: var(--tf-green) !important;
            box-shadow: 0 0 0 3px rgba(16,185,129,0.13) !important;
        }

        div[data-testid="stForm"],
        details[data-testid="stExpander"] {
            background: rgba(255,255,255,0.94) !important;
            border: 1px solid var(--tf-border) !important;
            border-radius: 22px !important;
            box-shadow: var(--tf-shadow-soft) !important;
            overflow: hidden !important;
        }

        div[data-testid="stForm"] {
            padding: 1.35rem !important;
        }

        div[data-testid="stMetric"] {
            background: var(--tf-card) !important;
            border: 1px solid var(--tf-border) !important;
            border-radius: 22px !important;
            box-shadow: var(--tf-shadow-soft) !important;
            padding: 1.15rem 1.2rem !important;
            min-height: 118px;
        }

        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {
            background: #ffffff !important;
            border: 1px solid var(--tf-border) !important;
            border-radius: 22px !important;
            box-shadow: var(--tf-shadow-soft) !important;
            overflow: hidden !important;
        }

        .tf-topbar {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
            margin-bottom: 1.55rem;
        }

        .tf-kicker {
            color: var(--tf-green-dark);
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.23em;
            font-weight: 900;
            margin-bottom: 0.2rem;
        }

        .tf-subtitle {
            color: var(--tf-muted);
            font-size: 1.02rem;
            font-weight: 600;
            margin-top: 0.25rem;
        }

        .tf-search-pill {
            background: #ffffff;
            border: 1px solid var(--tf-border);
            border-radius: 18px;
            padding: 0.75rem 1rem;
            min-width: 280px;
            color: var(--tf-muted);
            box-shadow: var(--tf-shadow-soft);
        }

        .tf-bell {
            position: relative;
            width: 48px;
            height: 48px;
            border-radius: 18px;
            background: #ffffff;
            border: 1px solid var(--tf-border);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--tf-shadow-soft);
            font-size: 1.1rem;
        }

        .tf-bell-badge {
            position: absolute;
            top: -7px;
            right: -7px;
            width: 24px;
            height: 24px;
            border-radius: 999px;
            background: var(--tf-green);
            color: #ffffff;
            font-size: 0.75rem;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            border: 2px solid #ffffff;
        }

        .tf-kpi-grid {
            display: grid;
            grid-template-columns: repeat(6, minmax(0, 1fr));
            gap: 1.15rem;
            margin: 1.2rem 0 2rem;
        }

        .tf-kpi {
            background: #ffffff;
            border: 1px solid var(--tf-border);
            border-radius: 22px;
            padding: 1.25rem;
            min-height: 122px;
            box-shadow: var(--tf-shadow-soft);
            transition: 0.15s ease-in-out;
        }

        .tf-kpi:hover {
            transform: translateY(-2px);
            box-shadow: var(--tf-shadow);
        }

        .tf-kpi-label {
            color: var(--tf-text);
            font-size: 0.96rem;
            font-weight: 670;
            margin-bottom: 0.65rem;
        }

        .tf-kpi-value {
            color: var(--tf-text);
            font-size: 2.25rem;
            font-weight: 900;
            letter-spacing: -0.055em;
            line-height: 1;
        }

        .tf-divider {
            height: 1px;
            background: rgba(148,163,184,0.38);
            margin: 1.8rem 0;
        }

        .tf-list-card {
            background: #ffffff;
            border: 1px solid var(--tf-border);
            border-radius: 22px;
            box-shadow: var(--tf-shadow-soft);
            overflow: hidden;
        }

        .tf-list-header {
            padding: 1.1rem 1.2rem;
            border-bottom: 1px solid var(--tf-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .tf-list-row {
            padding: 1rem 1.2rem;
            border-bottom: 1px solid #f1f5f9;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
        }

        .tf-list-row:last-child {
            border-bottom: none;
        }

        .tf-list-row:hover {
            background: #f8fafc;
        }

        .tf-title {
            font-weight: 820;
            color: var(--tf-text);
        }

        .tf-muted {
            color: var(--tf-muted);
            font-size: 0.9rem;
        }

        .tf-badge {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.3rem 0.72rem;
            font-size: 0.76rem;
            font-weight: 850;
            white-space: nowrap;
        }

        .tf-badge-success {
            background: #ecfdf5;
            color: #047857;
            border: 1px solid #a7f3d0;
        }

        .tf-badge-info {
            background: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
        }

        .tf-badge-neutral {
            background: #f1f5f9;
            color: #475569;
            border: 1px solid #e2e8f0;
        }

        .tf-badge-warning {
            background: #fffbeb;
            color: #b45309;
            border: 1px solid #fde68a;
        }

        .tf-badge-danger {
            background: #fef2f2;
            color: #b91c1c;
            border: 1px solid #fecaca;
        }

        .tf-nav-label {
            color: #cbd5e1;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-weight: 850;
            margin: 0.7rem 0 0.55rem;
        }

        .tf-sidebar-brand {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin-bottom: 1.4rem;
        }

        .tf-logo {
            width: 44px;
            height: 44px;
            border-radius: 17px;
            background: linear-gradient(135deg, var(--tf-green), #22d3ee);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 950;
            box-shadow: 0 12px 28px rgba(16,185,129,0.24);
        }

        .felt-logo-image {
            width: 44px;
            height: 44px;
            border-radius: 17px;
            background: rgba(255,255,255,0.96);
            padding: 5px;
            object-fit: contain;
            box-sizing: border-box;
            display: block;
            box-shadow: 0 12px 28px rgba(15,23,42,0.24);
        }

        .tf-brand-title {
            color: white;
            font-weight: 900;
            font-size: 1.05rem;
            line-height: 1.1;
        }

        .tf-brand-sub {
            color: #93a4b8;
            font-size: 0.78rem;
            margin-top: 0.1rem;
        }

        .tf-side-card {
            background: rgba(255,255,255,0.055);
            border: 1px solid rgba(255,255,255,0.09);
            border-radius: 20px;
            padding: 1rem;
            margin-top: 1rem;
        }

        @media(max-width: 1200px) {
            .tf-kpi-grid {
                grid-template-columns: repeat(3, minmax(0, 1fr));
            }
        }

        @media(max-width: 760px) {
            div[data-testid="stMainBlockContainer"] {
                padding: 1rem;
            }

            .tf-kpi-grid {
                grid-template-columns: 1fr;
            }

            .tf-search-pill {
                display: none;
            }

            .tf-topbar {
                flex-direction: column;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
