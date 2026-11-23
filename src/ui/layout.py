"""Shared Streamlit layout, typography, hero banner, sidebar, and UI cards.

Presentation layer only: delegates data/model/service logic to src modules.
"""
import base64
from pathlib import Path
from typing import Optional

import streamlit as st

from config import settings

C = settings.COLORS

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: {C["text"]};
}}

.stApp {{
    background-color: {C["background"]};
}}

.block-container {{
    padding-top: 4.25rem;
    padding-bottom: 3rem;
    padding-left: 2.25rem;
    padding-right: 2.25rem;
    max-width: 1360px;
}}

/* Hide anchor link chains next to Markdown headings */
[data-testid="stHeaderActionElements"] {{
    display: none !important;
}}

/* Typography hierarchy */
h1 {{
    color: {C["primary"]};
    font-size: clamp(1.9rem, 2.5vw, 2.45rem);
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.18;
}}
h2 {{
    color: {C["primary"]};
    font-size: clamp(1.45rem, 1.8vw, 1.75rem);
    font-weight: 700;
    letter-spacing: -0.015em;
    margin-top: 1.5rem;
    margin-bottom: 0.6rem;
}}
h3 {{
    color: {C["primary"]};
    font-size: 1.2rem;
    font-weight: 700;
}}
p, li, .stMarkdown p {{
    font-size: 1rem;
    line-height: 1.6;
    color: {C["text"]};
}}
label, .stSelectbox label, .stNumberInput label, .stSlider label, .stMultiSelect label, .stRadio label {{
    font-size: 0.96rem !important;
    font-weight: 600 !important;
    color: {C["text"]} !important;
}}

/* Sidebar styling */
[data-testid="stSidebar"] {{
    background-color: #FFFFFF;
    border-right: 1px solid {C["border"]};
}}
[data-testid="stSidebar"] .block-container {{
    padding-top: 1.5rem;
    padding-left: 1rem;
    padding-right: 1rem;
}}
.sidebar-brand {{
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.7rem 0.8rem;
    background: {C["soft_green"]};
    border: 1px solid {C["border"]};
    border-radius: 12px;
    margin-bottom: 0.9rem;
}}
.sidebar-brand-icon {{
    font-size: 1.65rem;
    line-height: 1;
}}
.sidebar-brand-title {{
    font-size: 1.08rem;
    font-weight: 800;
    color: {C["primary"]};
    line-height: 1.2;
}}
.sidebar-brand-sub {{
    font-size: 0.82rem;
    color: {C["muted"]};
    margin-top: 0.12rem;
}}
.sidebar-section-label {{
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {C["muted"]};
    margin: 0.9rem 0 0.45rem 0.25rem;
}}
.sidebar-info-box {{
    background: {C["background"]};
    border: 1px solid {C["border"]};
    border-radius: 10px;
    padding: 0.75rem 0.85rem;
    font-size: 0.88rem;
    line-height: 1.5;
    color: {C["text"]};
    margin-bottom: 0.6rem;
}}
.sidebar-info-box strong {{
    color: {C["primary"]};
}}

/* Sidebar page links */
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {{
    border-radius: 9px;
    padding: 0.55rem 0.75rem;
    margin-bottom: 0.25rem;
    font-size: 0.98rem;
    font-weight: 500;
    color: {C["text"]};
    border: 1px solid transparent;
    transition: background-color 0.15s ease, border-color 0.15s ease;
}}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] p {{
    font-size: 0.98rem !important;
    font-weight: 500 !important;
    margin: 0 !important;
}}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {{
    background-color: {C["soft_green"]};
    border-color: {C["border"]};
}}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"],
[data-testid="stSidebar"] .nav-active a[data-testid="stPageLink-NavLink"] {{
    background-color: {C["primary"]} !important;
    color: #FFFFFF !important;
    border-color: {C["primary"]} !important;
}}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] p,
[data-testid="stSidebar"] .nav-active a[data-testid="stPageLink-NavLink"] p,
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] span,
[data-testid="stSidebar"] .nav-active a[data-testid="stPageLink-NavLink"] span {{
    color: #FFFFFF !important;
    font-weight: 600 !important;
}}

/* Hero banner */
.hero-banner {{
    position: relative;
    width: 100%;
    min-height: 335px;
    border-radius: 16px !important;
    overflow: hidden !important;
    background-clip: padding-box;
    display: flex;
    align-items: center;
    padding: 2.3rem 2.75rem;
    margin-top: 0.25rem;
    margin-bottom: 1.85rem;
    border: 1px solid {C["border"]};
    background-size: cover;
    background-position: center right;
    background-repeat: no-repeat;
}}
.hero-content {{
    max-width: 610px;
    z-index: 2;
}}
.hero-badge {{
    display: inline-block;
    background: rgba(132, 204, 22, 0.22);
    border: 1px solid rgba(163, 230, 53, 0.55);
    color: #ECFCCB;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    padding: 0.32rem 0.8rem;
    border-radius: 999px;
    margin-bottom: 0.85rem;
    text-transform: uppercase;
}}
.hero-title {{
    color: #FFFFFF !important;
    font-size: clamp(2rem, 3vw, 2.75rem) !important;
    font-weight: 800 !important;
    line-height: 1.14 !important;
    margin: 0 0 0.65rem 0 !important;
    letter-spacing: -0.02em;
}}
.hero-subtitle {{
    display: inline-block;
    background: rgba(34, 139, 34, 0.88);
    color: #FFFFFF;
    font-size: 1.02rem;
    font-weight: 600;
    padding: 0.38rem 0.95rem;
    border-radius: 999px;
    margin-bottom: 0.85rem;
}}
.hero-description {{
    color: #E2E8F0 !important;
    font-size: 1.02rem !important;
    line-height: 1.55 !important;
    margin: 0 !important;
    max-width: 540px;
}}

/* Page header for subpages */
.page-header {{
    background: #FFFFFF;
    border: 1px solid {C["border"]};
    border-left: 6px solid {C["primary"]};
    border-radius: 12px;
    padding: 1.35rem 1.6rem;
    margin-bottom: 1.5rem;
}}
.page-badge {{
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: {C["primary"]};
    background: {C["soft_green"]};
    padding: 0.22rem 0.65rem;
    border-radius: 999px;
    margin-bottom: 0.45rem;
}}
.page-header h1 {{
    margin: 0;
    font-size: clamp(1.85rem, 2.4vw, 2.3rem);
    color: {C["primary"]};
}}
.page-header p {{
    margin: 0.35rem 0 0 0;
    color: {C["muted"]};
    font-size: 1.02rem;
}}

/* Section headings */
.section-head {{
    margin-top: 2rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid {C["border"]};
}}
.section-head h2 {{
    margin: 0;
    font-size: 1.58rem;
    font-weight: 700;
    color: {C["primary"]};
}}
.section-head p {{
    margin: 0.25rem 0 0 0;
    color: {C["muted"]};
    font-size: 0.98rem;
}}

/* KPI cards - uniform minimum height for horizontal alignment */
.kpi-card {{
    background: {C["card"]};
    border: 1px solid {C["border"]};
    border-top: 4px solid {C["secondary"]};
    border-radius: 12px;
    padding: 1.15rem 1.25rem;
    min-height: 152px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    margin-bottom: 0.75rem;
    box-sizing: border-box;
}}
.kpi-card.seasonal-card {{
    min-height: 176px;
}}
.kpi-top {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    margin-bottom: 0.45rem;
}}
.kpi-title {{
    font-size: 0.94rem;
    font-weight: 600;
    color: {C["muted"]};
}}
.kpi-icon {{
    background: {C["soft_green"]};
    color: {C["primary"]};
    width: 36px;
    height: 36px;
    flex-shrink: 0;
    border-radius: 9px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1.15rem;
}}
.kpi-value {{
    font-size: 2rem;
    font-weight: 800;
    color: {C["primary"]};
    line-height: 1.15;
    margin-bottom: 0.35rem;
}}
.kpi-desc {{
    font-size: 0.89rem;
    color: {C["muted"]};
    line-height: 1.45;
}}

/* Model summary cards */
.model-card {{
    background: #FFFFFF;
    border: 1px solid {C["border"]};
    border-radius: 12px;
    padding: 1.25rem 1.3rem;
    min-height: 204px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    margin-bottom: 0.85rem;
    box-sizing: border-box;
}}
.model-card.best-rmse {{
    border: 2px solid {C["primary"]};
    background: #FAFDFA;
}}
.model-card-head {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
}}
.model-card h3 {{
    margin: 0;
    font-size: 1.2rem;
    color: {C["primary"]};
}}
.model-pill {{
    font-size: 0.74rem;
    font-weight: 700;
    padding: 0.22rem 0.62rem;
    border-radius: 999px;
    white-space: nowrap;
}}
.pill-rmse {{
    background: {C["primary"]};
    color: #FFFFFF;
}}
.pill-mae {{
    background: #ECFCCB;
    color: {C["primary"]};
    border: 1px solid #BEF264;
}}
.model-fullname {{
    font-size: 0.9rem;
    color: {C["muted"]};
    margin-bottom: 0.9rem;
}}
.metric-grid {{
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.55rem;
}}
.metric-tile {{
    background: {C["background"]};
    border: 1px solid {C["border"]};
    border-radius: 8px;
    padding: 0.55rem 0.65rem;
    min-width: 0;
}}
.metric-tile-label {{
    font-size: 0.78rem;
    font-weight: 600;
    color: {C["muted"]};
}}
.metric-tile-val {{
    font-size: 1.12rem;
    font-weight: 700;
    color: {C["text"]};
    margin-top: 0.1rem;
}}

/* Quick nav cards */
.nav-card {{
    background: #FFFFFF;
    border: 1px solid {C["border"]};
    border-left: 4px solid {C["secondary"]};
    border-radius: 12px;
    padding: 1.15rem 1.2rem;
    height: 158px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    margin-bottom: 0.55rem;
    box-sizing: border-box;
}}
.nav-card-icon {{
    font-size: 1.45rem;
    margin-bottom: 0.45rem;
    line-height: 1;
}}
.nav-card h4 {{
    margin: 0 0 0.35rem 0;
    font-size: 1.1rem;
    font-weight: 700;
    color: {C["primary"]};
}}
.nav-card p {{
    margin: 0;
    font-size: 0.93rem;
    color: {C["muted"]};
    line-height: 1.45;
}}
.nav-link-wrap a[data-testid="stPageLink-NavLink"] {{
    background-color: #FFFFFF;
    border: 1px solid {C["border"]};
    border-radius: 9px;
    padding: 0.45rem 0.85rem;
    justify-content: center;
    transition: background-color 0.15s ease, border-color 0.15s ease;
}}
.nav-link-wrap a[data-testid="stPageLink-NavLink"]:hover {{
    background-color: {C["soft_green"]};
    border-color: {C["primary"]};
}}
.nav-link-wrap a[data-testid="stPageLink-NavLink"] p {{
    color: {C["primary"]} !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
}}

/* Prediction result card */
.pred-result-card {{
    background: #FFFFFF;
    border: 2px solid {C["primary"]};
    border-radius: 14px;
    padding: 1.65rem 1.8rem;
    margin: 0.25rem 0 1rem 0;
}}
.pred-result-label {{
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: {C["secondary"]};
    margin-bottom: 0.35rem;
}}
.pred-result-value {{
    font-size: clamp(2.1rem, 3vw, 2.8rem);
    font-weight: 800;
    color: {C["primary"]};
    line-height: 1.1;
    margin-bottom: 0.85rem;
}}
.pred-meta-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 0.75rem;
    padding-top: 0.9rem;
    border-top: 1px solid {C["border"]};
}}
.pred-meta-item span {{
    display: block;
    font-size: 0.8rem;
    color: {C["muted"]};
    font-weight: 600;
}}
.pred-meta-item strong {{
    font-size: 1.02rem;
    color: {C["text"]};
}}

/* Buttons */
.stButton > button[kind="primary"] {{
    background-color: {C["primary"]};
    border-color: {C["primary"]};
    font-size: 1rem;
    font-weight: 600;
    padding: 0.6rem 1.25rem;
    border-radius: 9px;
}}
.stButton > button[kind="primary"]:hover {{
    background-color: {C["secondary"]};
    border-color: {C["secondary"]};
}}

/* Footer */
.app-footer {{
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid {C["border"]};
    color: {C["muted"]};
    font-size: 0.88rem;
    text-align: center;
}}

/* Responsive hero & spacing */
@media (max-width: 900px) {{
    .nav-card {{
        height: auto;
        min-height: 132px;
    }}
}}
@media (max-width: 768px) {{
    .block-container {{
        padding-top: 3.5rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }}
    .hero-banner {{
        min-height: 260px;
        padding: 1.5rem 1.35rem;
        background-position: center;
    }}
    .metric-grid {{
        grid-template-columns: 1fr;
    }}
}}
</style>
"""

NAV_ITEMS = [
    ("Home / Dashboard", "app.py", "🏠"),
    ("Dataset Overview", "pages/1_Dataset_Overview.py", "📊"),
    ("Exploratory Analysis", "pages/2_Exploratory_Analysis.py", "📈"),
    ("Model Comparison", "pages/3_Model_Comparison.py", "⚖️"),
    ("Production Prediction", "pages/4_Production_Prediction.py", "🌾"),
]


def render_html(markup: str) -> None:
    """Render HTML via st.markdown after stripping indentation so CommonMark never parses it as code."""
    compact = "\n".join(line.strip() for line in markup.splitlines() if line.strip())
    st.markdown(compact, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def _load_image_data_uri(image_path: str) -> Optional[str]:
    path = Path(image_path)
    if not path.is_file():
        return None
    suffix = path.suffix.lower().lstrip(".") or "png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/{suffix};base64,{encoded}"


def setup_page(page_title: Optional[str] = None, icon: str = "🌾") -> None:
    """Configure Streamlit page settings and inject global design system CSS."""
    full_title = f"{page_title} · {settings.APP_TITLE}" if page_title else settings.APP_TITLE
    st.set_page_config(
        page_title=full_title,
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(_CSS, unsafe_allow_html=True)


def render_sidebar(active_page: str = "app.py") -> None:
    """Render branded agricultural navigation sidebar with active link highlight."""
    with st.sidebar:
        render_html(
            f"""
            <div class="sidebar-brand">
                <div class="sidebar-brand-icon">🌾</div>
                <div>
                    <div class="sidebar-brand-title">{settings.APP_SHORT_NAME}</div>
                    <div class="sidebar-brand-sub">{settings.APP_TAGLINE}</div>
                </div>
            </div>
            """
        )

        render_html('<div class="sidebar-section-label">Navigation</div>')
        for label, path, icon in NAV_ITEMS:
            is_active = path == active_page
            if is_active:
                render_html('<div class="nav-active">')
            st.page_link(path, label=label, icon=icon, width="stretch")
            if is_active:
                render_html("</div>")

        render_html('<div class="sidebar-section-label">About</div>')
        render_html(
            """
            <div class="sidebar-info-box">
                Ensemble machine learning analytics predicting Sri Lankan paddy production
                using pre-trained <strong>Bagging</strong>, <strong>Boosting</strong>, and
                <strong>Stacking</strong> regressors.
            </div>
            """
        )

        render_html('<div class="sidebar-section-label">Dataset &amp; Target</div>')
        render_html(
            f"""
            <div class="sidebar-info-box">
                <strong>Dataset:</strong> 25 districts &middot; Maha &amp; Yala<br/>
                <strong>Coverage:</strong> {settings.TRAIN_START_YEAR}&ndash;{settings.TEST_END_YEAR}<br/>
                <strong>Target:</strong> <code>{settings.TARGET_COLUMN}</code> (000 MT)<br/>
                <strong>Inputs:</strong> {', '.join(settings.PREDICTION_FEATURES)}
            </div>
            """
        )


def render_hero() -> None:
    """Render homepage hero banner using assets/paddy_hero.png with a safe fallback."""
    data_uri = _load_image_data_uri(str(settings.HERO_IMAGE_PATH))
    overlay = (
        "linear-gradient(90deg, rgba(14, 56, 28, 0.94) 0%, "
        "rgba(20, 83, 45, 0.84) 44%, rgba(20, 83, 45, 0.32) 72%, "
        "rgba(20, 83, 45, 0.06) 100%)"
    )
    if data_uri:
        bg_style = f"background-image: {overlay}, url('{data_uri}');"
    else:
        bg_style = (
            "background: linear-gradient(125deg, #0F3D1E 0%, #14532D 55%, #228B22 100%);"
        )

    render_html(
        f"""
        <div class="hero-banner" style="{bg_style}">
            <div class="hero-content">
                <div class="hero-badge">AGRICULTURE ANALYTICS | SRI LANKA</div>
                <h1 class="hero-title">Sri Lankan Paddy Production Prediction</h1>
                <div class="hero-subtitle">Ensemble Learning Analytics for Agricultural Production</div>
                <p class="hero-description">
                    Predict paddy production using historical Sri Lankan agricultural statistics
                    and ensemble machine learning models.
                </p>
            </div>
        </div>
        """
    )


def render_page_header(title: str, subtitle: str, badge: str = "") -> None:
    badge_html = f'<div class="page-badge">{badge}</div>' if badge else ""
    render_html(
        f"""
        <div class="page-header">
            {badge_html}
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """
    )


def render_section_heading(title: str, subtitle: str = "") -> None:
    sub_html = f"<p>{subtitle}</p>" if subtitle else ""
    render_html(f'<div class="section-head"><h2>{title}</h2>{sub_html}</div>')


def render_kpi_card(
    title: str,
    value: str,
    description: str,
    icon: str = "🌾",
    extra_class: str = "",
) -> None:
    cls = f"kpi-card {extra_class}".strip()
    render_html(
        f"""
        <div class="{cls}">
            <div>
                <div class="kpi-top">
                    <div class="kpi-title">{title}</div>
                    <div class="kpi-icon">{icon}</div>
                </div>
                <div class="kpi-value">{value}</div>
            </div>
            <div class="kpi-desc">{description}</div>
        </div>
        """
    )


def render_model_card(
    name: str,
    full_name: str,
    mae: float,
    rmse: float,
    r2: float,
    is_best_rmse: bool = False,
    is_best_mae: bool = False,
) -> None:
    card_cls = "model-card best-rmse" if is_best_rmse else "model-card"
    pill = ""
    if is_best_rmse:
        pill = '<span class="model-pill pill-rmse">Best RMSE &amp; R²</span>'
    elif is_best_mae:
        pill = '<span class="model-pill pill-mae">Lowest MAE</span>'

    render_html(
        f"""
        <div class="{card_cls}">
            <div>
                <div class="model-card-head">
                    <h3>{name}</h3>
                    {pill}
                </div>
                <div class="model-fullname">{full_name}</div>
            </div>
            <div class="metric-grid">
                <div class="metric-tile">
                    <div class="metric-tile-label">MAE</div>
                    <div class="metric-tile-val">{mae:.4f}</div>
                </div>
                <div class="metric-tile">
                    <div class="metric-tile-label">RMSE</div>
                    <div class="metric-tile-val">{rmse:.4f}</div>
                </div>
                <div class="metric-tile">
                    <div class="metric-tile-label">R²</div>
                    <div class="metric-tile-val">{r2:.4f}</div>
                </div>
            </div>
        </div>
        """
    )


def render_nav_card(
    title: str,
    description: str,
    icon: str,
    page_path: str,
) -> None:
    render_html(
        f"""
        <div class="nav-card">
            <div class="nav-card-icon">{icon}</div>
            <h4>{title}</h4>
            <p>{description}</p>
        </div>
        """
    )
    render_html('<div class="nav-link-wrap">')
    st.page_link(page_path, label=f"Open {title} →", width="stretch")
    render_html("</div>")


def render_footer() -> None:
    render_html(
        f'<div class="app-footer">{settings.APP_TITLE} &middot; Ensemble Learning Project &middot; '
        "Sri Lankan Agricultural Statistics (1978&ndash;2025) &middot; Built with Streamlit</div>"
    )
