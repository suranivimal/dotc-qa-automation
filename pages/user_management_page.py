"""
=============================================================================
DOTC Admin Panel — User Management Page Object
=============================================================================
Covers the full User Management module:
  • Sidebar navigation to User Management
  • User listing table — column validation, row parsing, pagination
  • Filters — Status, Location, Dating Mode (single + combined)
  • Search — by name, by email
  • User Detail — navigate via eye-icon, validate detail fields
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import allure
from playwright.sync_api import Page, Locator, TimeoutError as PwTimeout

from pages.base_page import BasePage
from utils.config import (
    USER_MANAGEMENT_URL,
    DEFAULT_TIMEOUT,
    SHORT_TIMEOUT,
    LONG_TIMEOUT,
    EXPECTED_TABLE_COLUMNS,
)
from utils.logger import get_logger

log = get_logger("user_mgmt_page")


# ─── Data class for a parsed user row ──────────────────────────────────────
UUID_RE = re.compile(
    r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
    re.IGNORECASE,
)


@dataclass
class UserRow:
    name: str
    email: str
    location: str
    status: str
    dating_mode: str
    id: str = ""


class UserManagementPage(BasePage):
    """Page Object for the DOTC Admin User Management section."""

    # ═══════════════════════════════════════════════════════════════════
    #  LOCATORS
    # ═══════════════════════════════════════════════════════════════════

    # --- Sidebar / Navigation ---
    SIDEBAR_NAV = 'nav, aside, [class*="sidebar"], [class*="side-bar"]'
    USER_MGMT_LINK = (
        'a:has-text("User Management"), '
        'a:has-text("Users"), '
        '[class*="sidebar"] a[href*="user"], '
        'nav a[href*="user"]'
    )
    PAGE_HEADING = 'h1, h2, [class*="page-title"], [class*="heading"]'

    # --- User Table ---
    TABLE = 'table, [class*="table"], [role="table"], [class*="data-table"]'
    TABLE_HEADER_ROW = 'thead tr, [class*="table-header"] tr, [role="table"] [role="row"]:first-child'
    TABLE_HEADER_CELLS = 'thead th, thead td, [class*="table-header"] th, [role="columnheader"]'
    TABLE_BODY_ROWS = 'tbody tr:not(:has([data-slot="skeleton"]))'
    TABLE_CELLS = 'td, [role="cell"]'
    NO_DATA_MESSAGE = (
        'p:has-text("No users"), td:has-text("No users"), '
        'p:has-text("No data"), p:has-text("No results"), '
        '[class*="empty"], [class*="no-data"]'
    )

    # --- Filters (Radix UI combobox — app uses custom dropdowns, not <select>) ---
    # Status = first combobox, Dating Mode = second combobox on the page
    COMBOBOX_TRIGGERS = 'button[role="combobox"][data-slot="select-trigger"]'
    COMBOBOX_OPTION   = '[role="option"][data-slot="select-item"]'
    _STATUS_COMBOBOX_IDX      = 0
    _DATING_MODE_COMBOBOX_IDX = 1

    # Location uses a plain text input (autocomplete)
    LOCATION_FILTER_INPUT = 'input[placeholder*="location" i]'

    # --- Search (single box: name / ID / email) ---
    SEARCH_INPUT = 'input[placeholder*="Search" i], input[placeholder*="name" i]'

    # --- User Detail (Actions column) ---
    VIEW_BUTTON = (
        'button:has(svg), a:has(svg), '
        '[class*="action"] button:first-child, '
        'button[title*="View" i], a[title*="View" i], '
        'button:has([class*="eye"]), a:has([class*="eye"]), '
        '[data-testid*="view"], '
        'td:last-child button:first-child, td:last-child a:first-child'
    )

    # --- User Detail Page ---
    # Detection indicator: "BACK TO MEMBERS" button is unique to the detail page
    DETAIL_PAGE_INDICATOR = (
        'button:has-text("Back to Members"), '
        'button:has-text("Back To Members"), '
        'a:has-text("Back to Members"), '
        'a:has-text("Back To Members"), '
        'button:has-text("BACK TO MEMBERS")'
    )
    USER_DETAIL_CONTAINER = (
        '[class*="user-detail"], [class*="user-profile"], '
        '[class*="detail-page"], .profile-card, '
        'main [class*="detail"], [class*="userDetail"], '
        '[class*="member-detail"], [class*="memberDetail"]'
    )
    # Page-level fallback selectors used when container isn't found
    DETAIL_NAME        = 'h1, h2, h3, [class*="name"], [class*="title"]'
    DETAIL_EMAIL       = '[class*="email"], [data-field="email"], a[href*="mailto:"]'
    DETAIL_LOCATION    = '[class*="location"], [data-field="location"]'
    DETAIL_STATUS      = '[class*="status"], [data-field="status"], .badge, [class*="badge"]'
    DETAIL_DATING_MODE = '[class*="dating"], [class*="mode"], [data-field="datingMode"]'
    BACK_BUTTON = (
        'button:has-text("Back to Members"), '
        'button:has-text("Back To Members"), '
        'button:has-text("BACK TO MEMBERS"), '
        'a:has-text("Back to Members"), '
        'button:has-text("Back"), a:has-text("Back"), '
        'button[class*="back"], [class*="breadcrumb"] a'
    )

    # --- Loading / Spinners ---
    TABLE_LOADING = (
        '.table-loading, [class*="spinner"], '
        '[data-slot="skeleton"], [class*="skeleton"]'
    )
    # Pagination uses aria-labels (confirmed via DOM inspection)
    PAGINATION_NEXT = 'button[aria-label="Next page"]'
    PAGINATION_PREV = 'button[aria-label="Previous page"]'

    # --- Pagination Count Summary (e.g. "Showing 1–10 of 189 Members") ---
    PAGINATION_SUMMARY = (
        'p:has-text("Showing"), span:has-text("Showing"), '
        '[class*="showing"], [class*="page-info"], [class*="pagination-info"]'
    )

    # --- Page Subtitle / Description beneath the main heading ---
    PAGE_SUBTITLE = (
        '[class*="subtitle"], [class*="sub-title"], [class*="page-subtitle"], '
        '[class*="text-muted-foreground"], h1 + p, h2 + p, header > p'
    )

    # --- Clear All Button ---
    CLEAR_ALL_BUTTON = (
        'button:has-text("Clear All"), button:has-text("Clear all"), '
        'button:has-text("CLEAR ALL")'
    )

    # --- Cancel/Clear icon inside the search input (×) ---
    SEARCH_CANCEL_ICON = (
        '[class*="search"] button[aria-label*="clear" i], '
        '[class*="search"] [aria-label*="cancel" i], '
        '[class*="search"] [data-testid*="clear"], '
        'input[placeholder*="Search" i] ~ button[type="button"]'
    )

    # ═══════════════════════════════════════════════════════════════════
    #  CONSTRUCTOR
    # ═══════════════════════════════════════════════════════════════════

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ═══════════════════════════════════════════════════════════════════
    #  NAVIGATION
    # ═══════════════════════════════════════════════════════════════════

    @allure.step("Navigate to User Management via sidebar")
    def navigate_to_user_management(self) -> "UserManagementPage":
        """Click the sidebar link and wait for the table to render."""
        log.info("Navigating to User Management section")
        try:
            self.safe_click(self.USER_MGMT_LINK, description="User Management sidebar link")
        except Exception:
            # Fallback: direct URL navigation
            log.warning("Sidebar link click failed — navigating via URL")
            self.navigate_to(USER_MANAGEMENT_URL)

        self._wait_for_table_loaded()
        log.info("User Management page loaded successfully")
        return self

    @allure.step("Open User Management page directly")
    def open_user_management_page(self) -> "UserManagementPage":
        self.navigate_to(USER_MANAGEMENT_URL)
        self._wait_for_table_loaded()
        return self

    # ═══════════════════════════════════════════════════════════════════
    #  TABLE — VALIDATION & PARSING
    # ═══════════════════════════════════════════════════════════════════

    @allure.step("Validate user table is visible")
    def is_table_visible(self) -> bool:
        return self.element_is_visible(self.TABLE)

    @allure.step("Get table column headers")
    def get_table_column_headers(self) -> list[str]:
        """Return the visible text of each <th> in the table header."""
        self._wait_for_table_loaded()
        headers = self.get_all_texts(self.TABLE_HEADER_CELLS)
        clean = [h.strip() for h in headers if h.strip()]
        log.info(f"Table columns found: {clean}")
        return clean

    @allure.step("Validate expected columns are present")
    def validate_table_columns(self, expected: list[str] | None = None) -> bool:
        """Case-insensitive check that every expected column exists."""
        expected = expected or EXPECTED_TABLE_COLUMNS
        actual = [h.lower() for h in self.get_table_column_headers()]
        missing = [col for col in expected if col.lower() not in actual]
        if missing:
            log.error(f"Missing columns: {missing} — found: {actual}")
            return False
        log.info("All expected columns present ✓")
        return True

    @allure.step("Get total visible row count")
    def get_table_row_count(self) -> int:
        self._wait_for_table_loaded()
        count = self.get_element_count(self.TABLE_BODY_ROWS)
        log.info(f"Visible table rows: {count}")
        return count

    @allure.step("Parse user rows from table")
    def get_all_user_rows(self) -> list[UserRow]:
        """Parse each <tr> in tbody into a UserRow dataclass."""
        self._wait_for_table_loaded()
        rows: list[UserRow] = []
        row_locators = self.page.locator(self.TABLE_BODY_ROWS)

        for i in range(row_locators.count()):
            cells = row_locators.nth(i).locator(self.TABLE_CELLS)
            cell_texts = [cells.nth(j).inner_text().strip() for j in range(cells.count())]

            if len(cell_texts) >= 5:
                rows.append(UserRow(
                    name=cell_texts[0],
                    email=cell_texts[1],
                    location=cell_texts[2],
                    status=cell_texts[3],
                    dating_mode=cell_texts[4],
                ))
        log.info(f"Parsed {len(rows)} user rows")
        return rows

    @allure.step("Check if no-data message is shown")
    def is_no_data_message_displayed(self) -> bool:
        try:
            return self.page.locator(self.NO_DATA_MESSAGE).first.is_visible(timeout=SHORT_TIMEOUT)
        except Exception:
            return False

    # ═══════════════════════════════════════════════════════════════════
    #  FILTERS
    # ═══════════════════════════════════════════════════════════════════

    @allure.step("Apply Status filter: {label}")
    def apply_status_filter(self, *, value: str = "", label: str = "") -> "UserManagementPage":
        opt = label or value
        log.info(f"Applying Status filter: '{opt}'")
        self._select_combobox_option(self._STATUS_COMBOBOX_IDX, opt)
        self._wait_after_filter()
        return self

    @allure.step("Apply Location filter: {label}")
    def apply_location_filter(self, *, value: str = "", label: str = "") -> "UserManagementPage":
        loc = label or value
        log.info(f"Applying Location filter (text input): '{loc}'")
        try:
            inp = self.page.locator(self.LOCATION_FILTER_INPUT)
            inp.fill(loc, timeout=DEFAULT_TIMEOUT)
        except Exception as exc:
            log.warning(f"Location filter fill failed: {exc}")
        self._wait_after_filter()
        return self

    @allure.step("Apply Dating Mode filter: {label}")
    def apply_dating_mode_filter(self, *, value: str = "", label: str = "") -> "UserManagementPage":
        opt = label or value
        log.info(f"Applying Dating Mode filter: '{opt}'")
        self._select_combobox_option(self._DATING_MODE_COMBOBOX_IDX, opt)
        self._wait_after_filter()
        return self

    @allure.step("Apply multiple filters together")
    def apply_combined_filters(
        self,
        status: str = "",
        location: str = "",
        dating_mode: str = "",
    ) -> "UserManagementPage":
        log.info(f"Applying combined filters — status='{status}', location='{location}', dating_mode='{dating_mode}'")
        if status:
            self._select_combobox_option(self._STATUS_COMBOBOX_IDX, status)
        if location:
            try:
                self.page.locator(self.LOCATION_FILTER_INPUT).fill(location)
            except Exception as exc:
                log.warning(f"Location fill failed: {exc}")
        if dating_mode:
            self._select_combobox_option(self._DATING_MODE_COMBOBOX_IDX, dating_mode)
        self._wait_after_filter()
        return self

    @allure.step("Reset all filters to default")
    def reset_filters(self) -> "UserManagementPage":
        log.info("Resetting all filters")
        # Reset Status to "All Status"
        status_opts = self._get_combobox_options(self._STATUS_COMBOBOX_IDX)
        all_status = next((o for o in status_opts if "all" in o.lower()), "")
        if all_status:
            self._select_combobox_option(self._STATUS_COMBOBOX_IDX, all_status)

        # Reset Dating Mode to "All Dating Modes"
        mode_opts = self._get_combobox_options(self._DATING_MODE_COMBOBOX_IDX)
        all_mode = next((o for o in mode_opts if "all" in o.lower()), "")
        if all_mode:
            self._select_combobox_option(self._DATING_MODE_COMBOBOX_IDX, all_mode)

        # Clear location text input
        try:
            inp = self.page.locator(self.LOCATION_FILTER_INPUT)
            if inp.is_visible(timeout=SHORT_TIMEOUT):
                inp.fill("")
        except Exception:
            pass

        self._wait_after_filter()
        return self

    @allure.step("Get available Status filter options")
    def get_status_filter_options(self) -> list[str]:
        return self._get_combobox_options(self._STATUS_COMBOBOX_IDX)

    @allure.step("Get available Location filter options")
    def get_location_filter_options(self) -> list[str]:
        return []  # Location uses a free-text input, not a dropdown

    @allure.step("Get available Dating Mode filter options")
    def get_dating_mode_filter_options(self) -> list[str]:
        return self._get_combobox_options(self._DATING_MODE_COMBOBOX_IDX)

    # ═══════════════════════════════════════════════════════════════════
    #  SEARCH
    # ═══════════════════════════════════════════════════════════════════

    @allure.step("Search for: {query}")
    def search_users(self, query: str) -> "UserManagementPage":
        """Type into the search box and wait for results."""
        log.info(f"Searching for: '{query}'")
        self.safe_clear_and_fill(self.SEARCH_INPUT, query, description="Search input")
        self.page.locator(self.SEARCH_INPUT).first.press("Enter")
        self._wait_after_filter()
        return self

    @allure.step("Clear search input")
    def clear_search(self) -> "UserManagementPage":
        log.info("Clearing search input")
        search = self.page.locator(self.SEARCH_INPUT)
        search.click(click_count=3)
        search.fill("")
        search.press("Enter")
        self._wait_after_filter()
        return self

    @allure.step("Validate search results contain '{expected_text}'")
    def validate_search_results_contain(self, expected_text: str) -> bool:
        """Every visible row should contain the expected text (name or email)."""
        rows = self.get_all_user_rows()
        if not rows:
            log.warning("No rows found after search")
            return False

        pattern = re.compile(re.escape(expected_text), re.IGNORECASE)
        for row in rows:
            combined = f"{row.name} {row.email}"
            if not pattern.search(combined):
                log.error(f"Row does not match search '{expected_text}': {row}")
                return False
        log.info(f"All {len(rows)} rows match search term '{expected_text}' ✓")
        return True

    # ═══════════════════════════════════════════════════════════════════
    #  USER DETAIL
    # ═══════════════════════════════════════════════════════════════════

    @allure.step("Click View (eye icon) on row #{row_index}")
    def click_view_user(self, row_index: int = 0) -> "UserManagementPage":
        """Click the View action on the Nth row (0-based)."""
        log.info(f"Clicking View on row index {row_index}")
        rows = self.page.locator(self.TABLE_BODY_ROWS)
        if rows.count() <= row_index:
            raise AssertionError(
                f"Cannot view row {row_index} — only {rows.count()} rows visible"
            )
        target_row = rows.nth(row_index)

        # Find the eye / view button inside that row
        view_btn = target_row.locator(self.VIEW_BUTTON).first
        view_btn.click(timeout=DEFAULT_TIMEOUT)

        # Wait for navigation or modal
        self._wait_for_detail_page()
        return self

    @allure.step("Validate user detail page is loaded")
    def is_user_detail_displayed(self) -> bool:
        current_url = self.get_current_url()
        # Query-param style IDs (e.g. ?userId=...)
        if "userId" in current_url or "user_id" in current_url:
            return True
        # UUID path segment (e.g. /user-management/<uuid>)
        if UUID_RE.search(current_url):
            return True
        # URL changed to a sub-path of the list page
        if current_url.startswith(USER_MANAGEMENT_URL + "/"):
            return True
        # "Back to Members" button — use the same locator that _wait_for_detail_page uses
        try:
            back_btn = self.page.locator(self.DETAIL_PAGE_INDICATOR)
            if back_btn.first.is_visible(timeout=SHORT_TIMEOUT):
                return True
        except Exception:
            pass
        # Last resort: CSS container selector
        return self.element_is_visible(self.USER_DETAIL_CONTAINER, timeout=SHORT_TIMEOUT)

    @allure.step("Get user detail — name")
    def get_detail_name(self) -> str:
        # Name is rendered as <h2> — the only h2 in main content
        for selector in ["main h2", "main h1", "h2", "h1"]:
            try:
                text = self.page.locator(selector).first.inner_text(
                    timeout=SHORT_TIMEOUT
                ).strip()
                if text:
                    return text
            except Exception:
                continue
        return ""

    @allure.step("Get user detail — email")
    def get_detail_email(self) -> str:
        for selector in [
            "main a[href*='mailto:']",
            "main p",
            "main span",
            "main li",
            "main [class*='email']",
            "main div[class*='info']",
            "body p",
            "body span",
        ]:
            try:
                for el in self.page.locator(selector).all():
                    try:
                        txt = el.inner_text(timeout=2_000).strip()
                        if "@" in txt and "." in txt and " " not in txt.split("@")[0][-5:]:
                            return txt
                    except Exception:
                        continue
            except Exception:
                continue
        return ""

    @allure.step("Get user detail — status")
    def get_detail_status(self) -> str:
        # Status badge is a <span> with text like ACTIVE or SUSPENDED
        # It appears BEFORE the DATING MODE badge in DOM order
        status_keywords = {"active", "suspended", "inactive", "blocked", "banned"}
        for selector in ["main span", "main .badge", "main [class*='badge']"]:
            try:
                for el in self.page.locator(selector).all():
                    try:
                        txt = el.inner_text(timeout=2_000).strip()
                        if txt.lower() in status_keywords:
                            return txt
                    except Exception:
                        continue
            except Exception:
                continue
        return ""

    @allure.step("Navigate back from detail page")
    def go_back_to_list(self) -> "UserManagementPage":
        log.info("Navigating back to user list")
        if self.element_is_visible(self.BACK_BUTTON, timeout=SHORT_TIMEOUT):
            self.safe_click(self.BACK_BUTTON, description="Back button")
        else:
            self.page.go_back()
        self._wait_for_table_loaded()
        return self

    # ═══════════════════════════════════════════════════════════════════
    #  PAGINATION
    # ═══════════════════════════════════════════════════════════════════

    @allure.step("Check if pagination component is visible")
    def is_pagination_visible(self) -> bool:
        try:
            return self.page.locator(self.PAGINATION_NEXT).is_visible(timeout=SHORT_TIMEOUT)
        except Exception:
            return False

    @allure.step("Check if page number buttons are visible")
    def is_page_numbers_visible(self) -> bool:
        """Return True if any numeric page buttons are rendered in the pagination bar."""
        try:
            # Numeric page buttons: aria-label="Page N" or button containing a digit inside nav/pagination
            selectors = [
                'button[aria-label^="Page "]',
                'nav button:has-text("1")',
                '[class*="pagination"] button:has-text("1")',
                '[class*="page-item"]',
            ]
            for sel in selectors:
                loc = self.page.locator(sel)
                if loc.count() > 0 and loc.first.is_visible(timeout=SHORT_TIMEOUT):
                    return True
            return False
        except Exception:
            return False

    @allure.step("Check if next page button is available")
    def is_next_page_available(self) -> bool:
        try:
            btn = self.page.locator(self.PAGINATION_NEXT)
            return btn.is_visible(timeout=SHORT_TIMEOUT) and btn.is_enabled()
        except Exception:
            return False

    @allure.step("Check if previous page button is available")
    def is_prev_page_available(self) -> bool:
        try:
            btn = self.page.locator(self.PAGINATION_PREV)
            return btn.is_visible(timeout=SHORT_TIMEOUT) and btn.is_enabled()
        except Exception:
            return False

    @allure.step("Click next page")
    def click_next_page(self) -> "UserManagementPage":
        self.page.locator(self.PAGINATION_NEXT).click(timeout=DEFAULT_TIMEOUT)
        self._wait_after_filter()
        return self

    @allure.step("Click previous page")
    def click_prev_page(self) -> "UserManagementPage":
        self.page.locator(self.PAGINATION_PREV).click(timeout=DEFAULT_TIMEOUT)
        self._wait_after_filter()
        return self

    @allure.step("Snapshot current page rows (name|email)")
    def get_first_row_snapshot(self) -> list[str]:
        """Return a fingerprint of visible rows for before/after comparisons."""
        return [f"{r.name}|{r.email}" for r in self.get_all_user_rows()]

    @allure.step("Extract user ID from current URL")
    def get_user_id_from_url(self) -> str:
        url = self.get_current_url()
        match = re.search(r'/(\d+)/?(?:\?|#|$)', url)
        return match.group(1) if match else ""

    # ═══════════════════════════════════════════════════════════════════
    #  UI / BUG-VERIFICATION HELPERS
    # ═══════════════════════════════════════════════════════════════════

    @allure.step("Get pagination count summary text")
    def get_pagination_summary_text(self) -> str:
        """Return text like 'Showing 1–10 of 189 Members', or '' if not found."""
        try:
            for selector in [self.PAGINATION_SUMMARY, '[class*="pagination"] p', 'nav ~ p']:
                loc = self.page.locator(selector)
                if loc.count() and loc.first.is_visible(timeout=SHORT_TIMEOUT):
                    return loc.first.inner_text().strip()
        except Exception:
            pass
        return ""

    @allure.step("Get page subtitle text")
    def get_page_subtitle(self) -> str:
        """Return the subtitle/description text beneath the main page heading."""
        try:
            for selector in [
                '[class*="text-muted-foreground"]', '[class*="subtitle"]',
                'h1 + p', 'h2 + p', 'header p',
            ]:
                for el in self.page.locator(selector).all():
                    try:
                        txt = el.inner_text(timeout=2_000).strip()
                        if txt and len(txt) > 5:
                            log.debug(f"Subtitle from '{selector}': {txt!r}")
                            return txt
                    except Exception:
                        continue
        except Exception:
            pass
        return ""

    @allure.step("Check if 'Clear All' button is visible")
    def is_clear_all_button_visible(self) -> bool:
        try:
            return self.page.locator(self.CLEAR_ALL_BUTTON).first.is_visible(timeout=SHORT_TIMEOUT)
        except Exception:
            return False

    @allure.step("Get placeholder text of location filter input")
    def get_location_filter_placeholder(self) -> str:
        try:
            return self.page.locator(self.LOCATION_FILTER_INPUT).first.get_attribute("placeholder") or ""
        except Exception:
            return ""

    @allure.step("Get computed cursor style of filter combobox #{idx}")
    def get_filter_combobox_cursor_style(self, idx: int = 0) -> str:
        """Return the computed CSS 'cursor' property for the Nth filter combobox trigger."""
        try:
            trigger = self.page.locator(self.COMBOBOX_TRIGGERS).nth(idx)
            return trigger.evaluate("el => window.getComputedStyle(el).cursor") or ""
        except Exception:
            return ""

    @allure.step("Check if search cancel icon is visible inside search field")
    def is_search_cancel_icon_visible(self) -> bool:
        try:
            return self.page.locator(self.SEARCH_CANCEL_ICON).first.is_visible(timeout=SHORT_TIMEOUT)
        except Exception:
            return False

    @allure.step("Check if a server error is displayed on the page")
    def has_server_error(self) -> bool:
        """Return True if an internal server error message is visible on the page."""
        try:
            body_text = self.page.inner_text("body")
            return bool(re.search(r'internal\s+server\s+error', body_text, re.IGNORECASE))
        except Exception:
            return False

    @allure.step("Set browser viewport to {width}x{height}")
    def set_viewport_size(self, width: int, height: int) -> None:
        self.page.set_viewport_size({"width": width, "height": height})
        try:
            self.page.wait_for_load_state("networkidle", timeout=3_000)
        except PwTimeout:
            pass

    @allure.step("Get bounding boxes of all filter section elements")
    def get_filter_element_bounding_boxes(self) -> dict:
        """Return bounding boxes for all combobox triggers and the location input."""
        boxes: dict = {"comboboxes": [], "location_input": []}
        for trigger in self.page.locator(self.COMBOBOX_TRIGGERS).all():
            try:
                box = trigger.bounding_box()
                if box:
                    boxes["comboboxes"].append(box)
            except Exception:
                pass
        try:
            box = self.page.locator(self.LOCATION_FILTER_INPUT).first.bounding_box()
            if box:
                boxes["location_input"].append(box)
        except Exception:
            pass
        return boxes

    # ═══════════════════════════════════════════════════════════════════
    #  INTERNAL HELPERS
    # ═══════════════════════════════════════════════════════════════════

    def _wait_for_table_loaded(self) -> None:
        """Wait for the table to render and skeleton rows to disappear."""
        try:
            self.page.wait_for_selector(self.TABLE, state="visible", timeout=LONG_TIMEOUT)
            # Wait for Radix skeleton rows to detach (app uses data-slot="skeleton")
            try:
                self.page.wait_for_selector(
                    '[data-slot="skeleton"]', state="detached", timeout=LONG_TIMEOUT
                )
            except PwTimeout:
                pass  # no skeletons present or already gone
            log.debug("Table is visible and loaded")
        except PwTimeout:
            self._capture_screenshot("table_load_timeout")
            raise AssertionError("User table did not load within timeout")

    def _wait_after_filter(self) -> None:
        """After any filter/search action, wait for the table to refresh."""
        # Wait for skeletons to appear then disappear (Radix loading state)
        try:
            self.page.wait_for_selector(
                '[data-slot="skeleton"]', state="attached", timeout=2_000
            )
            self.page.wait_for_selector(
                '[data-slot="skeleton"]', state="detached", timeout=LONG_TIMEOUT
            )
        except PwTimeout:
            pass  # no skeleton cycle — filter result was instant
        # Settle trailing network activity
        try:
            self.page.wait_for_load_state("networkidle", timeout=5_000)
        except PwTimeout:
            pass

    def _wait_for_detail_page(self) -> None:
        """Wait for the detail page to load — detected via URL change and Back to Members button."""
        # Wait for URL to change away from the list page
        try:
            self.page.wait_for_url(
                lambda url: url != USER_MANAGEMENT_URL,
                timeout=DEFAULT_TIMEOUT,
            )
        except PwTimeout:
            pass

        # Primary indicator: "Back to Members" button appears on the detail page
        try:
            self.page.wait_for_selector(
                self.DETAIL_PAGE_INDICATOR, state="visible", timeout=DEFAULT_TIMEOUT
            )
            log.debug("Detail page loaded — 'Back to Members' indicator found")
            return
        except PwTimeout:
            pass

        # Fallback: try generic container selectors
        if not self.element_is_visible(self.USER_DETAIL_CONTAINER, timeout=SHORT_TIMEOUT):
            self._capture_screenshot("detail_page_not_loaded")
            log.warning("User detail container not detected — may need locator tuning")

    def _get_combobox_options(self, combobox_index: int) -> list[str]:
        """Open a Radix UI combobox by position index and return its option texts."""
        try:
            trigger = self.page.locator(self.COMBOBOX_TRIGGERS).nth(combobox_index)
            trigger.click(timeout=DEFAULT_TIMEOUT)
            self.page.wait_for_timeout(300)
            options = self.page.locator(self.COMBOBOX_OPTION).all()
            texts = [o.inner_text().strip() for o in options if o.is_visible()]
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(200)
            log.info(f"Combobox[{combobox_index}] options: {texts}")
            return texts
        except Exception as exc:
            log.warning(f"Could not read combobox[{combobox_index}] options: {exc}")
            try:
                self.page.keyboard.press("Escape")
            except Exception:
                pass
            return []

    def _select_combobox_option(self, combobox_index: int, option_text: str) -> None:
        """Click a Radix UI combobox trigger then click the matching option."""
        if not option_text:
            return
        log.info(f"Selecting combobox[{combobox_index}] → '{option_text}'")
        try:
            trigger = self.page.locator(self.COMBOBOX_TRIGGERS).nth(combobox_index)
            trigger.click(timeout=DEFAULT_TIMEOUT)
            self.page.wait_for_timeout(300)
            option = self.page.locator(
                f'{self.COMBOBOX_OPTION}:has-text("{option_text}")'
            ).first
            option.click(timeout=DEFAULT_TIMEOUT)
            self.page.wait_for_timeout(200)
        except Exception as exc:
            log.warning(f"Combobox option '{option_text}' click failed: {exc}")
            try:
                self.page.keyboard.press("Escape")
            except Exception:
                pass
            raise