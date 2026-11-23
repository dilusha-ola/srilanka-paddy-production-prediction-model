"""Smoke tests verifying the Streamlit dashboard and all multipages render without errors."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent


def test_dashboard_and_pages_start_without_errors():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=90).run()
    assert not at.exception
    assert not at.error

    for rel_path in [
        "pages/1_Dataset_Overview.py",
        "pages/2_Exploratory_Analysis.py",
        "pages/3_Model_Comparison.py",
        "pages/4_Production_Prediction.py",
    ]:
        page = at.switch_page(str(ROOT / rel_path)).run()
        assert not page.exception, f"Exception in {rel_path}: {page.exception}"
        assert not page.error, f"Error in {rel_path}: {page.error}"

    # Submit a live prediction from page 4
    pred_page = at.switch_page(str(ROOT / "pages/4_Production_Prediction.py")).run()
    pred_page.button[0].click().run()
    assert not pred_page.exception
    assert not pred_page.error
    assert len(pred_page.dataframe) >= 1
