"""Shared Streamlit layout helpers (page setup, styling, sidebar, footer).

Presentation only: no data loading or model logic lives here.
"""
import streamlit as st

from config import settings

PRIMARY = "#1B5E20"

_CSS = f"""
<style>
.block-container {{ padding-top: 2rem; padding-bottom: 3rem; max-width: 1200px; }}
h1, h2, h3 {{ color: {PRIMARY}; font-weight: 700; letter-spacing: -0.01em; }}
[data-testid="stSidebar"] {{ border-right: 1px solid #DCE6DC; }}
.app-header {{ border-bottom: 3px solid {PRIMARY}; padding-bottom: .5rem; margin-bottom: 1.25rem; }}
.app-header h1 {{ margin: 0; font-size: 2rem; }}
.app-header p {{ margin: .25rem 0 0 0; color: #52606D; }}
.app-card {{ background: #F1F6F1; border: 1px solid #DCE6DC; border-left: 4px solid {PRIMARY};
            border-radius: 6px; padding: 1rem 1.25rem; height: 100%; }}
.app-card h4 {{ margin: 0 0 .35rem 0; color: {PRIMARY}; }}
.app-card p {{ margin: 0; color: #3E4C59; font-size: .93rem; }}
.app-footer {{ margin-top: 3rem; padding-top: .75rem; border-top: 1px solid #DCE6DC;
              color: #7B8794; font-size: .8rem; text-align: center; }}
</style>
"""


def setup_page(icon: str = "🌾") -> None:
    """Configure the page. Must be the first Streamlit call on every page."""
    st.set_page_config(
        page_title=settings.APP_TITLE,
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(_CSS, unsafe_allow_html=True)


def render_header(title: str, subtitle: str = "") -> None:
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f'<div class="app-header"><h1>{title}</h1>{sub}</div>',
        unsafe_allow_html=True,
    )


def render_card(title: str, body: str) -> None:
    st.markdown(
        f'<div class="app-card"><h4>{title}</h4><p>{body}</p></div>',
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    """Sidebar project info. Page navigation is provided by Streamlit's
    multipage support (files in the pages/ directory)."""
    with st.sidebar:
        st.markdown(f"### 🌾 {settings.APP_TITLE}")
        st.caption("Ensemble learning dashboard")
        st.divider()
        st.markdown("**About**")
        st.caption(
            "Predicts Sri Lankan paddy production (thousand MT) with "
            "Bagging, Boosting and Stacking regressors."
        )
        st.markdown("**Prediction inputs**")
        st.caption(", ".join(settings.PREDICTION_FEATURES))
        st.markdown("**Target**")
        st.caption(settings.TARGET_COLUMN)


def render_footer() -> None:
    st.markdown(
        f'<div class="app-footer">{settings.APP_TITLE} · Ensemble Learning Project · '
        f"Built with Streamlit</div>",
        unsafe_allow_html=True,
    )
