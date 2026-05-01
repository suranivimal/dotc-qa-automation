"""
conftest.py — Shared pytest fixtures for DOTC QA Automation Suite.

Provides:
  • browser_type_launch_args  — headless / slow_mo from config
  • browser_context_args      — viewport from config
  • authenticated_page        — page already logged in to admin panel
  • pytest_runtest_makereport — screenshot + Allure attachment on failure
"""

from __future__ import annotations

import os
import re
import shutil

import allure
import pytest
from playwright.sync_api import Page, BrowserContext

from pages.login_page import LoginPage
from utils.bug_reporter import report_bug_on_failure
from utils.config import (
    HEADLESS,
    SLOW_MO,
    VIEWPORT_WIDTH,
    VIEWPORT_HEIGHT,
    VALID_EMAIL,
    VALID_PASSWORD,
)
from utils.excel_reporter import reporter
from utils.logger import get_logger

log = get_logger("conftest")

VIDEO_DIR = "reports/videos"

_FUNC_TC_MAP: dict[str, str] = {
    # Login
    "test_valid_login_redirects_to_dashboard": "TC-LOGIN-001",
    "test_invalid_email_shows_error":          "TC-LOGIN-002",
    "test_wrong_password_shows_error":         "TC-LOGIN-003",
    "test_empty_email_validation":             "TC-LOGIN-004",
    "test_empty_password_validation":          "TC-LOGIN-005",
    "test_both_empty_validation":              "TC-LOGIN-006",
    "test_login_page_elements_visible":        "TC-LOGIN-007",
    "test_sql_injection_does_not_crash":       "TC-LOGIN-008",
    "test_xss_attempt_sanitized":             "TC-LOGIN-009",
    # Advanced Login Tests (TC-LOGIN-010 to TC-LOGIN-020)
    "test_email_format_validation_realtime":   "TC-LOGIN-010",
    "test_password_visibility_toggle":         "TC-LOGIN-011",
    "test_keyboard_navigation_tab_support":    "TC-LOGIN-012",
    "test_validation_clears_on_input":         "TC-LOGIN-013",
    "test_special_chars_in_password":          "TC-LOGIN-014",
    "test_email_whitespace_trimming":          "TC-LOGIN-015",
    "test_very_long_email":                    "TC-LOGIN-016",
    "test_uppercase_email":                    "TC-LOGIN-017",
    "test_form_labels_association":            "TC-LOGIN-018",
    "test_page_meta_description":              "TC-LOGIN-019",
    "test_no_sensitive_data_in_storage":       "TC-LOGIN-020",
    # User Management
    "test_navigate_to_user_management":        "TC-UM-001",
    "test_page_heading_visible":               "TC-UM-002",
    "test_table_is_visible":                   "TC-UM-003",
    "test_table_columns":                      "TC-UM-004",
    "test_at_least_one_row":                   "TC-UM-005",
    "test_row_data_non_empty":                 "TC-UM-006",
    "test_status_filter":                      "TC-UM-007",
    "test_location_filter":                    "TC-UM-008",
    "test_dating_mode_filter":                 "TC-UM-009",
    "test_combined_filters":                   "TC-UM-010",
    "test_no_result_filter":                   "TC-UM-011",
    "test_reset_filters":                      "TC-UM-012",
    "test_search_by_name":                     "TC-UM-013",
    "test_search_by_email":                    "TC-UM-014",
    "test_search_no_match":                    "TC-UM-015",
    "test_clear_search":                       "TC-UM-016",
    "test_view_user_detail":                   "TC-UM-017",
    "test_user_detail_fields":                 "TC-UM-018",
    "test_back_to_list":                       "TC-UM-019",
    "test_special_chars_search":               "TC-UM-020",
    "test_long_search_string":                 "TC-UM-021",
    "test_rapid_filter_switching":             "TC-UM-022",
    # TC-UM-023 to TC-UM-028 — extended filter tests (already in test file)
    "test_status_filter_active":              "TC-UM-023",
    "test_status_filter_deactive":            "TC-UM-024",
    "test_status_filter_suspended":           "TC-UM-025",
    "test_location_filter_all_options":       "TC-UM-026",
    "test_dating_mode_filter_all_options":    "TC-UM-027",
    "test_clear_all_button":                  "TC-UM-028",
    # TC-UM-029 to TC-UM-036 — new ScoutQA scenario coverage
    "test_status_filter_all":                 "TC-UM-029",
    "test_dating_mode_filter_active":         "TC-UM-030",
    "test_dating_mode_filter_inactive":       "TC-UM-031",
    "test_search_by_id":                      "TC-UM-032",
    "test_table_data_completeness":           "TC-UM-033",
    "test_pagination_visible":                "TC-UM-034",
    "test_pagination_next_page":              "TC-UM-035",
    "test_pagination_prev_page":              "TC-UM-036",
    # TC-LOGIN-021 to TC-LOGIN-023 — session & logout tests
    "test_login_via_enter_key":              "TC-LOGIN-021",
    "test_session_persists_on_refresh":      "TC-LOGIN-022",
    "test_logout_redirects_to_login":        "TC-LOGIN-023",
    # TC-UM-037 to TC-UM-043 — extended user detail tests
    "test_detail_name_matches_list":         "TC-UM-037",
    "test_detail_email_matches_list":        "TC-UM-038",
    "test_detail_status_matches_list":       "TC-UM-039",
    "test_detail_page_url_changes":          "TC-UM-040",
    "test_admin_actions_visible_on_detail":  "TC-UM-041",
    "test_back_from_detail_shows_list":      "TC-UM-042",
    "test_different_users_show_different_detail": "TC-UM-043",
}


def _extract_tc_id(item: pytest.Item) -> str | None:
    return _FUNC_TC_MAP.get(item.function.__name__)


# ── Excel reporter lifecycle ─────────────────────────────────────────────────

def pytest_sessionstart(session: pytest.Session) -> None:
    reporter.setup()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    reporter.save()
    log.info(f"Excel test report saved → reports/test_cases.xlsx")


# ── Browser configuration ────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
    return {
        **browser_type_launch_args,
        "headless": HEADLESS,
        "slow_mo": SLOW_MO,
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {
        **browser_context_args,
        "viewport": {"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
    }


@pytest.fixture
def context(browser, browser_context_args, request) -> BrowserContext:
    """Override pytest-playwright context to record a video per test."""
    # Sanitise test name for use as a filename (handles [chromium] brackets etc.)
    safe_name = re.sub(r'[^\w\-]', '_', request.node.name)[:100]
    test_video_dir = os.path.join(VIDEO_DIR, safe_name)
    os.makedirs(test_video_dir, exist_ok=True)

    ctx = browser.new_context(
        **browser_context_args,
        record_video_dir=test_video_dir,
        record_video_size={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
    )
    yield ctx

    # Collect video paths BEFORE closing (path is known, file not yet written)
    video_paths: list[str] = []
    for p in ctx.pages:
        if p.video:
            try:
                video_paths.append(p.video.path())
            except Exception:
                pass

    ctx.close()  # Video files are flushed and written after this call

    # Move each video to a named file and store on node for Allure attachment
    os.makedirs(VIDEO_DIR, exist_ok=True)
    for idx, vp in enumerate(video_paths):
        if not os.path.exists(vp):
            log.warning(f"Video file not found after context close: {vp}")
            continue
        suffix = f"_{idx}" if idx > 0 else ""
        named_path = os.path.join(VIDEO_DIR, f"{safe_name}{suffix}.webm")
        try:
            shutil.move(vp, named_path)
            vp = named_path
        except Exception as exc:
            log.warning(f"Could not rename video: {exc}")

        try:
            with open(vp, "rb") as f:
                video_bytes = f.read()
            if not hasattr(request.node, "_video_attachments"):
                request.node._video_attachments = []
            request.node._video_attachments.append((video_bytes, safe_name))
            log.info(f"Video recorded → {vp}")
        except Exception as exc:
            log.warning(f"Could not read video for Allure: {exc}")

    # Remove the now-empty temp subdirectory
    try:
        if os.path.isdir(test_video_dir) and not os.listdir(test_video_dir):
            os.rmdir(test_video_dir)
    except Exception:
        pass


# ── Authentication fixture ───────────────────────────────────────────────────

@pytest.fixture
def authenticated_page(page: Page) -> Page:
    """Return a Playwright Page that is already logged in to the admin panel."""
    log.info(f"Authenticating as {VALID_EMAIL}")
    lp = LoginPage(page)
    lp.open_login_page()
    lp.login(VALID_EMAIL, VALID_PASSWORD)
    lp.wait_for_dashboard()
    log.info("Authentication complete — page is ready")
    return page


# ── Screenshot-on-failure hook ───────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call):
    """Capture a full-page screenshot and attach it to Allure on test failure."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        tc_id = _extract_tc_id(item)
        if tc_id:
            if report.passed:
                reporter.update_result(tc_id, "PASS")
            elif report.failed:
                reporter.update_result(tc_id, "FAIL")
            elif report.skipped:
                reporter.update_result(tc_id, "SKIP")

        if report.failed:
            page: Page | None = (
                item.funcargs.get("page")
                or item.funcargs.get("authenticated_page")
            )
            screenshot_path = None
            if page:
                try:
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    screenshot_filename = f"failure_{item.name}_{timestamp}.png"
                    screenshot_dir = "reports/screenshots"
                    os.makedirs(screenshot_dir, exist_ok=True)
                    screenshot_path = f"{screenshot_dir}/{screenshot_filename}"
                    screenshot = page.screenshot(full_page=True, path=screenshot_path)
                    allure.attach(
                        screenshot,
                        name=f"failure_{item.name}",
                        attachment_type=allure.attachment_type.PNG,
                    )
                    log.warning(f"Failure screenshot captured and attached: {item.name}")
                except Exception as exc:
                    log.warning(f"Could not capture failure screenshot: {exc}")

            # Create bug report
            tc_id = tc_id or "UNKNOWN"
            failure_message = str(call.excinfo.value) if call.excinfo else "Unknown failure"
            report_bug_on_failure(tc_id, item.name, failure_message, screenshot_path)

    elif report.when == "setup" and report.skipped:
        tc_id = _extract_tc_id(item)
        if tc_id:
            reporter.update_result(tc_id, "SKIP")

    elif report.when == "teardown":
        for video_bytes, safe_name in getattr(item, "_video_attachments", []):
            try:
                allure.attach(
                    video_bytes,
                    name=f"Video — {safe_name}",
                    attachment_type=allure.attachment_type.WEBM,
                )
            except Exception as exc:
                log.warning(f"Could not attach video to Allure report: {exc}")
