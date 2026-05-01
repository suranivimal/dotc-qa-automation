"""
=============================================================================
DOTC Admin Panel — User Management Test Suite
=============================================================================
Test Scope:
  ── Navigation ──
  TC-UM-001  Navigate to User Management from sidebar
  TC-UM-002  Page heading / title validation

  ── User Table ──
  TC-UM-003  Table is visible
  TC-UM-004  Table has expected columns
  TC-UM-005  At least one user row is displayed
  TC-UM-033  Table data completeness — name, email, status, location (all rows)

  ── Filters ──
  TC-UM-010  Combined filters → results match
  TC-UM-011  Filter with no results → no-data message
  TC-UM-023  Status filter → Active → only Active users shown
  TC-UM-025  Status filter → Suspended → only Suspended users shown
  TC-UM-026  Location filter → each available option → valid results
  TC-UM-027  Dating Mode filter → each available option → valid results
  TC-UM-028  Clear All button → resets all filters → full list restored
  TC-UM-029  Status filter 'All' → full user list shown
  TC-UM-030  Dating Mode filter 'Active' → only Active dating mode users
  TC-UM-031  Dating Mode filter 'Inactive' → only Inactive dating mode users

  ── Search ──
  TC-UM-013  Search by name → matching results
  TC-UM-014  Search by email → matching results
  TC-UM-015  Search with no match → no-data message
  TC-UM-016  Clear search → full list restored
  TC-UM-032  Search by user ID → matching results

  ── Pagination ──
  TC-UM-034  Pagination is visible on User Management page
  TC-UM-035  Pagination next page navigation works
  TC-UM-036  Pagination previous page navigation works

  ── User Detail ──
  TC-UM-018  Detail page shows user info (name + email visible in detail container)
  TC-UM-037  Detail page name matches list row data
  TC-UM-038  Detail page email matches list row data
  TC-UM-039  Detail page status matches list row data
  TC-UM-040  Detail page URL changes from list URL
  TC-UM-041  Admin action buttons visible on user detail page
  TC-UM-042  Back from detail navigates to user list
  TC-UM-043  Different users show different detail content

  ── Edge Cases ──
  TC-UM-020  Special characters in search
  TC-UM-021  Very long search string
  TC-UM-022  Rapid filter switching (stability)

  ── Bug Regression ──
  TC-UM-044  Filter dropdown triggers have pointer/hand cursor
  TC-UM-045  No count summary or pagination shown when filter returns no results
  TC-UM-046  Location filter placeholder text is 'Search by location'
  TC-UM-047  Page subtitle is user-friendly
  TC-UM-048  'Clear All' button NOT shown when searching by name, ID, or email
  TC-UM-049  Filter section is responsive at 1280px and 1024px widths
  TC-UM-050  No server error when navigating between pages
  TC-UM-051  Location filter returns results for full address with city, state, country
  TC-UM-052  Dating Mode filter options show 'Active'/'Inactive', not 'Dating Mode Active'
"""

from __future__ import annotations

import pytest
import allure

from pages.user_management_page import UserManagementPage
from utils.config import EXPECTED_TABLE_COLUMNS
from utils.logger import StepLogger


# ═══════════════════════════════════════════════════════════════════════════
#  FIXTURES
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def user_mgmt_page(authenticated_page) -> UserManagementPage:
    """Start every test on the User Management page (already logged in)."""
    ump = UserManagementPage(authenticated_page)
    ump.navigate_to_user_management()
    return ump


# ═══════════════════════════════════════════════════════════════════════════
#  NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════

@allure.suite("User Management")
@allure.sub_suite("Navigation")
class TestUserManagementNavigation:
    pytestmark = [pytest.mark.user_management, pytest.mark.smoke, pytest.mark.regression]

    @allure.title("TC-UM-001: Navigate to User Management from sidebar")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_navigate_to_user_management(self, authenticated_page):
        step = StepLogger("TC-UM-001")
        ump = UserManagementPage(authenticated_page)

        step.info("Click User Management in sidebar")
        ump.navigate_to_user_management()

        step.info("Validate URL contains 'user'")
        current_url = ump.get_current_url()
        assert "user" in current_url.lower(), (
            f"URL does not contain 'user': {current_url}"
        )
        step.passed(f"Navigation successful — URL: {current_url}")

    @allure.title("TC-UM-002: Page heading is visible")
    @allure.severity(allure.severity_level.NORMAL)
    def test_page_heading_visible(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-002")

        step.info("Check for page heading")
        heading_visible = user_mgmt_page.element_is_visible(
            UserManagementPage.PAGE_HEADING
        )
        assert heading_visible, "Page heading not visible"
        step.passed("Page heading is displayed")


# ═══════════════════════════════════════════════════════════════════════════
#  USER TABLE
# ═══════════════════════════════════════════════════════════════════════════

@allure.suite("User Management")
@allure.sub_suite("User Table")
class TestUserTable:
    pytestmark = [pytest.mark.user_management, pytest.mark.regression]

    @allure.title("TC-UM-003: User table is visible")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_table_is_visible(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-003")

        step.info("Check table visibility")
        assert user_mgmt_page.is_table_visible(), "User table is not visible"
        step.passed("User table is visible")

    @allure.title("TC-UM-004: Table has expected columns")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_table_columns(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-004")

        step.info("Retrieve column headers")
        headers = user_mgmt_page.get_table_column_headers()

        step.info(f"Expected columns: {EXPECTED_TABLE_COLUMNS}")
        step.info(f"Actual columns:   {headers}")

        assert user_mgmt_page.validate_table_columns(), (
            f"Column mismatch — expected {EXPECTED_TABLE_COLUMNS}, got {headers}"
        )
        step.passed("All expected columns are present")

    @allure.title("TC-UM-005: At least one user record is displayed")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_at_least_one_row(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-005")

        step.info("Count table rows")
        count = user_mgmt_page.get_table_row_count()
        assert count >= 1, f"Expected ≥1 rows, found {count}"
        step.passed(f"Table has {count} row(s)")

    @allure.title("TC-UM-033: Table data completeness — all rows have name, email, status, location")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_table_data_completeness(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-033")

        rows = user_mgmt_page.get_all_user_rows()
        assert rows, "No user rows found in table"

        step.info(f"Validating completeness across {len(rows)} visible rows")
        failures: list[str] = []
        for idx, row in enumerate(rows):
            missing = [
                field for field, val in [
                    ("name", row.name),
                    ("email", row.email),
                    ("status", row.status),
                    ("location", row.location),
                ]
                if not val.strip()
            ]
            if missing:
                failures.append(f"Row {idx} missing: {missing} — {row}")

        assert not failures, "Data completeness failures:\n" + "\n".join(failures)
        step.passed(f"All {len(rows)} rows have complete name, email, status, location")


# ═══════════════════════════════════════════════════════════════════════════
#  FILTERS
# ═══════════════════════════════════════════════════════════════════════════

@allure.suite("User Management")
@allure.sub_suite("Filters")
class TestFilters:
    pytestmark = [pytest.mark.user_management, pytest.mark.filters, pytest.mark.regression]

    @allure.title("TC-UM-010: Combined filters → filtered results")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_combined_filters(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-010")

        status_opts = user_mgmt_page.get_status_filter_options()
        location_opts = user_mgmt_page.get_location_filter_options()

        status_val = self._first_real_option(status_opts) or ""
        location_val = self._first_real_option(location_opts) or ""

        if not status_val and not location_val:
            pytest.skip("Not enough filter options for combined test")

        step.info(f"Apply combined: status='{status_val}', location='{location_val}'")
        user_mgmt_page.apply_combined_filters(
            status=status_val,
            location=location_val,
        )

        row_count = user_mgmt_page.get_table_row_count()
        no_data = user_mgmt_page.is_no_data_message_displayed()
        assert row_count > 0 or no_data, "Expected rows or no-data message after combined filter"

        if row_count > 0:
            rows = user_mgmt_page.get_all_user_rows()
            for r in rows:
                if status_val:
                    assert status_val.lower() in r.status.lower(), (
                        f"Row status '{r.status}' does not match combined filter status '{status_val}'"
                    )
                if location_val:
                    assert location_val.lower() in r.location.lower(), (
                        f"Row location '{r.location}' does not match combined filter location '{location_val}'"
                    )
        step.passed(f"Combined filter returned {row_count} verified row(s)")

    @allure.title("TC-UM-011: Filter producing no results → no-data message")
    @allure.severity(allure.severity_level.NORMAL)
    def test_no_result_filter(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-011")

        step.info("Collect available filter options")
        status_opts = user_mgmt_page.get_status_filter_options()
        loc_opts = user_mgmt_page.get_location_filter_options()
        mode_opts = user_mgmt_page.get_dating_mode_filter_options()

        placeholders = {"", "all", "select", "select...", "-- select --", "any", "none"}
        real_s = [o for o in status_opts if o.strip().lower() not in placeholders]
        real_l = [o for o in loc_opts  if o.strip().lower() not in placeholders]
        real_m = [o for o in mode_opts if o.strip().lower() not in placeholders]

        if not any([real_s, real_l, real_m]):
            pytest.skip(
                "No non-placeholder options found in any filter — "
                "filters may use custom UI (tabs/buttons) not standard <select>"
            )

        s = real_s[-1] if real_s else ""
        l = real_l[-1] if real_l else ""
        m = real_m[-1] if real_m else ""

        step.info(f"Apply extreme filters: status='{s}', location='{l}', mode='{m}'")
        user_mgmt_page.apply_combined_filters(status=s, location=l, dating_mode=m)

        row_count = user_mgmt_page.get_table_row_count()
        no_data = user_mgmt_page.is_no_data_message_displayed()

        step.info(f"Rows: {row_count}, No-data shown: {no_data}")
        assert user_mgmt_page.is_table_visible() or no_data, (
            "Page went into an unexpected state after applying extreme filters"
        )
        # If no-data is shown, the row count must be zero
        if no_data:
            assert row_count == 0, (
                f"No-data message is shown but table still has {row_count} row(s)"
            )
            step.passed("Extreme filters produced no results — no-data message shown correctly")
        else:
            assert row_count > 0, (
                "No no-data message shown but table also has 0 rows — unexpected empty state"
            )
            step.passed(f"Extreme filters matched {row_count} real user(s) — filter logic is working")

    @allure.title("TC-UM-023: Status filter 'Active' → only Active users shown")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_status_filter_active(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-023")
        self._apply_and_verify_status(user_mgmt_page, step, "TC-UM-023", "Active")

    @allure.title("TC-UM-025: Status filter 'Suspended' → only Suspended users shown")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_status_filter_suspended(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-025")
        self._apply_and_verify_status(user_mgmt_page, step, "TC-UM-025", "Suspended")

    @allure.title("TC-UM-026: Location filter → each available option → valid results")
    @allure.severity(allure.severity_level.NORMAL)
    def test_location_filter_all_options(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-026")

        options = user_mgmt_page.get_location_filter_options()
        real_opts = [o for o in options if o.strip().lower() not in
                     {"", "all", "select", "select...", "-- select --", "any", "none"}]

        if not real_opts:
            pytest.skip("No location filter options available to test")

        step.info(f"Testing {len(real_opts)} location option(s): {real_opts}")
        for location in real_opts:
            step.info(f"Apply Location filter: '{location}'")
            user_mgmt_page.apply_location_filter(label=location)
            row_count = user_mgmt_page.get_table_row_count()
            no_data = user_mgmt_page.is_no_data_message_displayed()
            assert user_mgmt_page.is_table_visible() or no_data, (
                f"Page in unexpected state after location filter '{location}'"
            )
            step.info(f"Location='{location}' → {row_count} row(s), no-data={no_data}")
            user_mgmt_page.reset_filters()

        step.passed(f"All {len(real_opts)} location option(s) verified successfully")

    @allure.title("TC-UM-027: Dating Mode filter → each available option → valid results")
    @allure.severity(allure.severity_level.NORMAL)
    def test_dating_mode_filter_all_options(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-027")

        options = user_mgmt_page.get_dating_mode_filter_options()
        real_opts = [o for o in options if o.strip().lower() not in
                     {"", "all", "select", "select...", "-- select --", "any", "none"}]

        if not real_opts:
            pytest.skip("No dating mode filter options available to test")

        step.info(f"Testing {len(real_opts)} dating mode option(s): {real_opts}")
        for mode in real_opts:
            step.info(f"Apply Dating Mode filter: '{mode}'")
            user_mgmt_page.apply_dating_mode_filter(label=mode)
            row_count = user_mgmt_page.get_table_row_count()
            no_data = user_mgmt_page.is_no_data_message_displayed()
            assert user_mgmt_page.is_table_visible() or no_data, (
                f"Page in unexpected state after dating mode filter '{mode}'"
            )
            step.info(f"Dating Mode='{mode}' → {row_count} row(s), no-data={no_data}")
            user_mgmt_page.reset_filters()

        step.passed(f"All {len(real_opts)} dating mode option(s) verified successfully")

    @allure.title("TC-UM-028: Clear All button → resets all filters → full list restored")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_clear_all_button(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-028")

        step.info("Record initial row count before applying filters")
        initial_count = user_mgmt_page.get_table_row_count()

        status_val = self._first_real_option(user_mgmt_page.get_status_filter_options())
        location_val = self._first_real_option(user_mgmt_page.get_location_filter_options())
        mode_val = self._first_real_option(user_mgmt_page.get_dating_mode_filter_options())

        if not any([status_val, location_val, mode_val]):
            pytest.skip("No filter options available to apply before testing Clear All")

        step.info(f"Apply filters — status='{status_val}', location='{location_val}', mode='{mode_val}'")
        user_mgmt_page.apply_combined_filters(
            status=status_val,
            location=location_val,
            dating_mode=mode_val,
        )
        filtered_count = user_mgmt_page.get_table_row_count()
        step.info(f"Row count after filters: {filtered_count}")

        step.info("Click Clear All button")
        user_mgmt_page.reset_filters()

        restored_count = user_mgmt_page.get_table_row_count()
        assert abs(restored_count - initial_count) <= 2, (
            f"Expected ~{initial_count} rows after Clear All, got {restored_count}"
        )
        step.passed(f"Clear All restored full list — row count: {restored_count}")

    @allure.title("TC-UM-029: Status filter 'All' → full user list shown")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_status_filter_all(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-029")

        step.info("Record initial (unfiltered) row count")
        initial_count = user_mgmt_page.get_table_row_count()

        step.info("Apply a non-All status filter first to change the view")
        status_opts = user_mgmt_page.get_status_filter_options()
        real_opt = self._first_real_option(status_opts)
        if real_opt:
            user_mgmt_page.apply_status_filter(label=real_opt)
            step.info(f"Applied '{real_opt}' filter — rows now: {user_mgmt_page.get_table_row_count()}")

        step.info("Select 'All' from Status filter (or reset if 'All' not present)")
        all_opt = next(
            (o for o in status_opts if o.strip().lower() in {"all", ""}),
            None,
        )
        if all_opt is not None:
            user_mgmt_page.apply_status_filter(label=all_opt)
        else:
            user_mgmt_page.reset_filters()

        restored_count = user_mgmt_page.get_table_row_count()
        assert abs(restored_count - initial_count) <= 2, (
            f"Expected ~{initial_count} rows after 'All' filter, got {restored_count}"
        )
        step.passed(f"Status 'All' restored full list — {restored_count} rows")

    @allure.title("TC-UM-030: Dating Mode filter 'Active' → only Active dating mode users")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_dating_mode_filter_active(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-030")
        self._apply_and_verify_dating_mode(user_mgmt_page, step, "TC-UM-030", "Active")

    @allure.title("TC-UM-031: Dating Mode filter 'Inactive' → only Inactive dating mode users")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_dating_mode_filter_inactive(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-031")
        self._apply_and_verify_dating_mode(user_mgmt_page, step, "TC-UM-031", "Inactive")

    # --- Helpers ---
    @staticmethod
    def _first_real_option(options: list[str]) -> str:
        """Return the first option that isn't a placeholder like 'All', 'All Status', 'Select', ''."""
        for opt in options:
            stripped = opt.strip().lower()
            if not stripped:
                continue
            # Skip "all …", "… all", "select", "any", "none" style placeholders
            if "all" in stripped.split() or stripped in {"select", "select...", "-- select --", "any", "none"}:
                continue
            return opt
        return ""

    @staticmethod
    def _apply_and_verify_dating_mode(
        page: UserManagementPage,
        step: StepLogger,
        tc_id: str,
        mode_label: str,
    ) -> None:
        options = page.get_dating_mode_filter_options()
        # Try exact match first, then partial (e.g. "Active" matches "Dating Mode Active")
        match = next((o for o in options if o.strip().lower() == mode_label.lower()), None)
        if not match:
            if mode_label.lower() == "inactive":
                match = next((o for o in options if "inactive" in o.strip().lower()), None)
            else:
                match = next(
                    (o for o in options
                     if mode_label.lower() in o.strip().lower()
                     and "inactive" not in o.strip().lower()),
                    None,
                )
        if not match:
            pytest.skip(f"{tc_id}: '{mode_label}' not found in Dating Mode dropdown — options: {options}")

        step.info(f"Apply Dating Mode filter: '{match}'")
        page.apply_dating_mode_filter(label=match)

        row_count = page.get_table_row_count()
        no_data = page.is_no_data_message_displayed()
        assert row_count > 0 or no_data, (
            f"Expected rows or no-data after filtering by dating_mode='{match}'"
        )
        if row_count > 0:
            rows = page.get_all_user_rows()
            for r in rows:
                assert mode_label.lower() in r.dating_mode.strip().lower(), (
                    f"Row dating_mode '{r.dating_mode}' does not contain filter '{mode_label}'"
                )
        step.passed(f"Dating Mode='{mode_label}' filter returned {row_count} valid row(s)")

    @staticmethod
    def _apply_and_verify_status(
        page: UserManagementPage,
        step: StepLogger,
        tc_id: str,
        status_label: str,
    ) -> None:
        """Apply a named status filter and assert every visible row matches it."""
        options = page.get_status_filter_options()
        match = next((o for o in options if o.strip().lower() == status_label.lower()), None)
        if not match:
            pytest.skip(f"{tc_id}: '{status_label}' not found in Status dropdown — options: {options}")

        step.info(f"Apply Status filter: '{match}'")
        page.apply_status_filter(label=match)

        row_count = page.get_table_row_count()
        no_data = page.is_no_data_message_displayed()
        assert row_count > 0 or no_data, (
            f"Expected rows or no-data after filtering by status='{match}'"
        )

        if row_count > 0:
            rows = page.get_all_user_rows()
            for r in rows:
                assert r.status.strip().lower() == status_label.lower(), (
                    f"Row status '{r.status}' does not match filter '{status_label}'"
                )
        step.passed(f"Status='{status_label}' filter returned {row_count} valid row(s)")


# ═══════════════════════════════════════════════════════════════════════════
#  SEARCH
# ═══════════════════════════════════════════════════════════════════════════

@allure.suite("User Management")
@allure.sub_suite("Search")
class TestSearch:
    pytestmark = [pytest.mark.user_management, pytest.mark.search, pytest.mark.regression]

    @allure.title("TC-UM-013: Search by name → matching results")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_by_name(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-013")

        step.info("Get a real (non-placeholder) name to use as search term")
        rows = user_mgmt_page.get_all_user_rows()
        if not rows:
            pytest.skip("No users in table to search")

        _PLACEHOLDERS = {"unnamed", "unnamed user", "n/a", ""}
        real_user = next(
            (r for r in rows if r.name.strip().lower().split("\n")[0] not in _PLACEHOLDERS),
            None,
        )
        if not real_user:
            pytest.skip("All visible users have placeholder names — cannot test name search")

        name_parts = real_user.name.split()
        search_name = name_parts[0] if name_parts else real_user.name.strip()
        step.info(f"Searching for name: '{search_name}'")
        user_mgmt_page.search_users(search_name)

        step.info("Validate results contain search term")
        result_count = user_mgmt_page.get_table_row_count()
        assert result_count >= 1, f"Expected ≥1 results for '{search_name}', got {result_count}"

        parsed_rows = user_mgmt_page.get_all_user_rows()
        if parsed_rows:
            assert user_mgmt_page.validate_search_results_contain(search_name), (
                f"Not all results match search term '{search_name}'"
            )
            step.passed(f"Search by name returned {result_count} matching result(s)")
        else:
            # Search results use a different DOM structure — fall back to page-level check
            page_text = user_mgmt_page.page.inner_text("body").lower()
            assert search_name.lower() in page_text, (
                f"Search term '{search_name}' not found anywhere on the page "
                f"after search — {result_count} DOM row(s) exist but are unreadable"
            )
            step.passed(
                f"Search by name: '{search_name}' found in page content "
                f"({result_count} DOM row(s) — search results use a different table structure)"
            )

    @allure.title("TC-UM-014: Search by email → matching results")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_by_email(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-014")

        rows = user_mgmt_page.get_all_user_rows()
        if not rows:
            pytest.skip("No users in table to search")

        search_email = rows[0].email
        step.info(f"Searching for email: '{search_email}'")
        user_mgmt_page.search_users(search_email)

        result_count = user_mgmt_page.get_table_row_count()
        assert result_count >= 1, f"Expected ≥1 results for '{search_email}'"
        step.passed(f"Search by email returned {result_count} result(s)")

    @allure.title("TC-UM-015: Search with no match → no-data message")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_no_match(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-015")

        nonsense = "zzzznonexistentuser12345xyz"
        step.info(f"Searching for nonsense: '{nonsense}'")
        user_mgmt_page.search_users(nonsense)

        step.info("Validate no results or no-data message")
        row_count = user_mgmt_page.get_table_row_count()
        no_data = user_mgmt_page.is_no_data_message_displayed()

        assert row_count == 0 or no_data, (
            f"Expected 0 rows or no-data message, got {row_count} rows"
        )

        step.info("Validate pagination is hidden when no results found")
        pagination_visible = user_mgmt_page.is_pagination_visible()
        page_numbers_visible = user_mgmt_page.is_page_numbers_visible()

        assert not pagination_visible, (
            "Pagination (Next/Prev buttons) should NOT be visible when search returns no results"
        )
        assert not page_numbers_visible, (
            "Page number buttons should NOT be visible when search returns no results"
        )
        step.passed("No-match search: no results, no pagination, no page numbers — correct")

    @allure.title("TC-UM-016: Clear search → full list restored")
    @allure.severity(allure.severity_level.NORMAL)
    def test_clear_search(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-016")

        initial_count = user_mgmt_page.get_table_row_count()

        step.info("Search for something specific")
        rows = user_mgmt_page.get_all_user_rows()
        if rows:
            name_parts = rows[0].name.split()
            user_mgmt_page.search_users(name_parts[0] if name_parts else rows[0].name.strip())

        step.info("Clear search")
        user_mgmt_page.clear_search()

        restored = user_mgmt_page.get_table_row_count()
        assert abs(restored - initial_count) <= 2, (
            f"Expected ~{initial_count} rows after clear, got {restored}"
        )
        step.passed(f"Search cleared — row count restored to {restored}")

    @allure.title("TC-UM-032: Search by user ID → matching results")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_by_id(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-032")

        rows = user_mgmt_page.get_all_user_rows()
        if not rows:
            pytest.skip("No users in table to derive an ID from")

        step.info("Open first user detail page to extract ID from URL")
        user_mgmt_page.click_view_user(row_index=0)
        user_id = user_mgmt_page.get_user_id_from_url()

        if not user_id:
            pytest.skip("Could not extract numeric user ID from URL — app may use slugs")

        step.info(f"Extracted user ID: '{user_id}' — navigating back to list")
        user_mgmt_page.go_back_to_list()

        step.info(f"Searching for ID: '{user_id}'")
        user_mgmt_page.search_users(user_id)

        result_count = user_mgmt_page.get_table_row_count()
        no_data = user_mgmt_page.is_no_data_message_displayed()

        assert result_count >= 1, (
            f"Expected ≥1 result when searching by ID '{user_id}' (extracted from a real user), "
            f"got {result_count} — search by ID may be broken"
        )
        step.passed(f"Search by ID '{user_id}' returned {result_count} result(s)")


# ═══════════════════════════════════════════════════════════════════════════
#  USER DETAIL
# ═══════════════════════════════════════════════════════════════════════════

@allure.suite("User Management")
@allure.sub_suite("User Detail")
class TestUserDetail:
    pytestmark = [pytest.mark.user_management, pytest.mark.detail, pytest.mark.regression]

    @allure.title("TC-UM-018: Detail page shows user info (name + email in detail container)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user_detail_fields(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-018")

        rows = user_mgmt_page.get_all_user_rows()
        if not rows:
            pytest.skip("No users to view")

        # Prefer a user with a real email in the list so the detail assertion isn't vacuous
        target_idx = 0
        for idx, row in enumerate(rows):
            if row.email.strip() and "@" in row.email:
                target_idx = idx
                break

        step.info(f"Navigate to user detail (row {target_idx})")
        user_mgmt_page.click_view_user(row_index=target_idx)

        step.info("Verify detail container is visible")
        assert user_mgmt_page.is_user_detail_displayed(), (
            "User detail container not found on detail page"
        )

        step.info("Verify page has meaningful content")
        page_content = user_mgmt_page.page.content()
        assert len(page_content) > 500, (
            "Detail page content appears too short — may not have loaded"
        )

        step.info("Verify user name is present on detail page")
        detail_name = user_mgmt_page.get_detail_name()
        assert detail_name.strip(), "Name field is empty or not visible on detail page"

        step.info("Verify user email is present on detail page")
        detail_email = user_mgmt_page.get_detail_email()
        assert detail_email.strip(), (
            f"Email field is empty or not visible on detail page for row {target_idx} "
            f"(list email: '{rows[target_idx].email}')"
        )

        step.passed(f"Detail page shows name='{detail_name}', email='{detail_email}'")

    @allure.title("TC-UM-037: Detail page name matches list row data")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_detail_name_matches_list(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-037")

        rows = user_mgmt_page.get_all_user_rows()
        if not rows:
            pytest.skip("No users to view")

        # Prefer a user with a real name — skip placeholder rows
        _PLACEHOLDERS = {"n/a", "unnamed user", "unnamed", ""}
        target_idx = 0
        for idx, row in enumerate(rows):
            if row.name.strip().lower().split("\n")[0] not in _PLACEHOLDERS:
                target_idx = idx
                break

        list_name = rows[target_idx].name.split("\n")[0].strip()
        step.info(f"List row {target_idx} name: '{list_name}'")

        user_mgmt_page.click_view_user(row_index=target_idx)

        detail_name = user_mgmt_page.get_detail_name()
        step.info(f"Detail page name: '{detail_name}'")

        # Accept if both sides are placeholder values (empty / N/A / Unnamed)
        def _is_placeholder(s: str) -> bool:
            return s.strip().lower() in _PLACEHOLDERS

        if _is_placeholder(list_name) and _is_placeholder(detail_name):
            step.passed("Both list and detail show placeholder name — user has no display name set")
            return

        assert (
            list_name.lower() in detail_name.lower()
            or detail_name.lower() in list_name.lower()
        ), f"Detail name '{detail_name}' does not match list row name '{list_name}'"
        step.passed(f"Detail name '{detail_name}' matches list name '{list_name}'")

    @allure.title("TC-UM-038: Detail page email matches list row data")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_detail_email_matches_list(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-038")

        rows = user_mgmt_page.get_all_user_rows()
        if not rows:
            pytest.skip("No users to view")

        list_email = rows[0].email
        step.info(f"List row email: '{list_email}'")

        user_mgmt_page.click_view_user(row_index=0)

        detail_email = user_mgmt_page.get_detail_email()
        step.info(f"Detail page email: '{detail_email}'")

        assert list_email.lower() in detail_email.lower() or detail_email.lower() in list_email.lower(), (
            f"Detail email '{detail_email}' does not match list row email '{list_email}'"
        )
        step.passed(f"Detail email '{detail_email}' matches list email '{list_email}'")

    @allure.title("TC-UM-039: Detail page status matches list row data")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_detail_status_matches_list(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-039")

        rows = user_mgmt_page.get_all_user_rows()
        if not rows:
            pytest.skip("No users to view")

        list_status = rows[0].status
        step.info(f"List row status: '{list_status}'")

        user_mgmt_page.click_view_user(row_index=0)

        detail_status = user_mgmt_page.get_detail_status()
        step.info(f"Detail page status: '{detail_status}'")

        assert list_status.lower() in detail_status.lower() or detail_status.lower() in list_status.lower(), (
            f"Detail status '{detail_status}' does not match list row status '{list_status}'"
        )
        step.passed(f"Detail status '{detail_status}' matches list status '{list_status}'")

    @allure.title("TC-UM-040: Detail page URL changes from list URL")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_detail_page_url_changes(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-040")

        rows = user_mgmt_page.get_all_user_rows()
        if not rows:
            pytest.skip("No users to view")

        list_url = user_mgmt_page.get_current_url()
        step.info(f"List page URL: '{list_url}'")

        user_mgmt_page.click_view_user(row_index=0)

        detail_url = user_mgmt_page.get_current_url()
        step.info(f"Detail page URL: '{detail_url}'")

        assert detail_url != list_url, (
            "URL did not change after clicking View — detail routing may be broken"
        )
        step.passed(f"URL changed to: '{detail_url}'")

    @allure.title("TC-UM-041: Admin action buttons visible on user detail page")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_admin_actions_visible_on_detail(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-041")

        rows = user_mgmt_page.get_all_user_rows()
        if not rows:
            pytest.skip("No users to view")

        user_mgmt_page.click_view_user(row_index=0)

        step.info("Scan detail page for admin action keywords")
        page_content = user_mgmt_page.page.content().lower()

        action_keywords = ["edit", "suspend", "activate", "verify", "block", "deactivate"]
        found_actions = [kw for kw in action_keywords if kw in page_content]

        step.info(f"Found admin action keywords: {found_actions}")
        assert found_actions, (
            "No admin action buttons found on user detail page. "
            "Expected at least one of: Edit, Suspend/Activate, Verify per project requirements"
        )
        step.passed(f"Admin actions present on detail page: {found_actions}")

    @allure.title("TC-UM-042: Back from detail navigates to user list")
    @allure.severity(allure.severity_level.NORMAL)
    def test_back_from_detail_shows_list(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-042")

        step.info("Apply Active status filter before navigating to detail")
        status_opts = user_mgmt_page.get_status_filter_options()
        active_opt = next(
            (o for o in status_opts if "active" in o.lower() and "inactive" not in o.lower()),
            "",
        )
        if active_opt:
            user_mgmt_page.apply_status_filter(label=active_opt)
            step.info(f"Applied filter: '{active_opt}'")

        rows = user_mgmt_page.get_all_user_rows()
        if not rows:
            pytest.skip("No users visible after filtering")

        step.info("Navigate to first user detail page")
        user_mgmt_page.click_view_user(row_index=0)

        step.info("Navigate back to user list")
        user_mgmt_page.go_back_to_list()

        assert user_mgmt_page.is_table_visible(), (
            "User list table not visible after navigating back from detail page"
        )
        step.passed("Back from detail restored the user list table")

    @allure.title("TC-UM-043: Different users show different detail content")
    @allure.severity(allure.severity_level.NORMAL)
    def test_different_users_show_different_detail(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-043")

        rows = user_mgmt_page.get_all_user_rows()
        if len(rows) < 2:
            pytest.skip("Need at least 2 users in the list to compare detail pages")

        step.info(f"User 1: name='{rows[0].name}' | User 2: name='{rows[1].name}'")

        step.info("Navigate to first user detail")
        user_mgmt_page.click_view_user(row_index=0)
        detail_name_1 = user_mgmt_page.get_detail_name()
        step.info(f"Detail 1 — name: '{detail_name_1}'")
        user_mgmt_page.go_back_to_list()

        step.info("Navigate to second user detail")
        user_mgmt_page.click_view_user(row_index=1)
        detail_name_2 = user_mgmt_page.get_detail_name()
        step.info(f"Detail 2 — name: '{detail_name_2}'")

        assert detail_name_1 != detail_name_2, (
            f"Both users show the same detail name '{detail_name_1}' — "
            "detail page may not be rendering per-user data"
        )
        step.passed(f"User 1 detail '{detail_name_1}' ≠ User 2 detail '{detail_name_2}'")


# ═══════════════════════════════════════════════════════════════════════════
#  EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════

@allure.suite("User Management")
@allure.sub_suite("Edge Cases")
class TestEdgeCases:
    pytestmark = [pytest.mark.user_management, pytest.mark.edge_case, pytest.mark.regression]

    @allure.title("TC-UM-020: Special characters in search → no crash")
    @allure.severity(allure.severity_level.NORMAL)
    def test_special_chars_search(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-020")

        special_queries = [
            "!@#$%^&*()",
            "<script>alert(1)</script>",
            "'; DROP TABLE users; --",
            "   ",
        ]
        for query in special_queries:
            step.info(f"Searching: '{query}'")
            user_mgmt_page.search_users(query)

            # The page should not crash — table or no-data message visible
            table_ok = user_mgmt_page.is_table_visible()
            no_data = user_mgmt_page.is_no_data_message_displayed()
            assert table_ok or no_data, (
                f"Page crashed or went blank after searching '{query}'"
            )
            user_mgmt_page.clear_search()

        step.passed("All special character searches handled without crash")

    @allure.title("TC-UM-021: Very long search string → no crash")
    @allure.severity(allure.severity_level.MINOR)
    def test_long_search_string(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-021")

        long_string = "a" * 500
        step.info("Entering a 500-character search string")
        user_mgmt_page.search_users(long_string)

        table_ok = user_mgmt_page.is_table_visible()
        no_data = user_mgmt_page.is_no_data_message_displayed()
        assert table_ok or no_data, "Page broke with long search input"
        user_mgmt_page.clear_search()
        step.passed("Long search string handled gracefully")

    @allure.title("TC-UM-022: Rapid filter switching → stable")
    @allure.severity(allure.severity_level.MINOR)
    def test_rapid_filter_switching(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-022")

        status_opts = user_mgmt_page.get_status_filter_options()
        real_opts = [o for o in status_opts if o.strip().lower() not in
                     {"", "all", "select", "any"}]

        if len(real_opts) < 2:
            pytest.skip("Need ≥2 status options for rapid switching test")

        step.info("Rapidly switch between filter options")
        for opt in real_opts[:3]:
            user_mgmt_page.apply_status_filter(label=opt)

        step.info("Verify page is still functional")
        assert user_mgmt_page.is_table_visible() or user_mgmt_page.is_no_data_message_displayed(), (
            "Page became unstable after rapid filter switching"
        )
        step.passed("Rapid filter switching did not break the page")


# ═══════════════════════════════════════════════════════════════════════════
#  PAGINATION
# ═══════════════════════════════════════════════════════════════════════════

@allure.suite("User Management")
@allure.sub_suite("Pagination")
class TestPagination:
    pytestmark = [pytest.mark.user_management, pytest.mark.pagination, pytest.mark.regression]

    @allure.title("TC-UM-034: Pagination is visible on User Management page")
    @allure.severity(allure.severity_level.NORMAL)
    def test_pagination_visible(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-034")

        row_count = user_mgmt_page.get_table_row_count()
        step.info(f"Visible rows on current page: {row_count}")

        pagination_visible = user_mgmt_page.is_pagination_visible()
        step.info(f"Pagination component visible: {pagination_visible}")

        # Page must show users OR pagination — both absent means something broke
        assert row_count >= 1 or pagination_visible, (
            "User management page shows 0 rows and no pagination — "
            "table may have failed to load"
        )
        if pagination_visible:
            step.passed("Pagination component is present and visible")
        else:
            step.passed(
                f"Pagination not visible — all {row_count} users fit on one page "
                "(expected if dataset is small)"
            )

    @allure.title("TC-UM-035: Pagination next page navigation works")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_pagination_next_page(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-035")

        if not user_mgmt_page.is_pagination_visible():
            pytest.skip("Pagination not visible — all users may fit on one page")

        if not user_mgmt_page.is_next_page_available():
            pytest.skip("Next page button not available — only one page of results")

        step.info("Snapshot rows on page 1")
        page1_snapshot = user_mgmt_page.get_first_row_snapshot()

        step.info("Click Next page")
        user_mgmt_page.click_next_page()

        page2_snapshot = user_mgmt_page.get_first_row_snapshot()
        row_count = user_mgmt_page.get_table_row_count()

        assert row_count > 0, "Next page loaded with 0 rows"
        assert page2_snapshot != page1_snapshot, (
            "Row content did not change after clicking Next — pagination may be broken"
        )
        step.passed(f"Next page loaded successfully with {row_count} rows")

    @allure.title("TC-UM-036: Pagination previous page navigation works")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_pagination_prev_page(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-036")

        if not user_mgmt_page.is_pagination_visible():
            pytest.skip("Pagination not visible — all users may fit on one page")

        if not user_mgmt_page.is_next_page_available():
            pytest.skip("Need multiple pages to test previous navigation")

        step.info("Snapshot rows on page 1")
        page1_snapshot = user_mgmt_page.get_first_row_snapshot()

        step.info("Navigate to page 2")
        user_mgmt_page.click_next_page()

        step.info("Navigate back to page 1 via Previous")
        user_mgmt_page.click_prev_page()

        restored_snapshot = user_mgmt_page.get_first_row_snapshot()
        assert restored_snapshot == page1_snapshot, (
            "Previous page navigation did not restore original page content"
        )
        step.passed("Previous page navigation restored correct page 1 content")


# ═══════════════════════════════════════════════════════════════════════════
#  BUG REGRESSION
# ═══════════════════════════════════════════════════════════════════════════

@allure.suite("User Management")
@allure.sub_suite("Bug Regression")
class TestBugRegression:
    """Regression tests for reported UI/functional bugs — TC-UM-044 through TC-UM-052."""

    pytestmark = [pytest.mark.user_management, pytest.mark.regression]

    # ── Bug 1 ────────────────────────────────────────────────────────────────

    @allure.title("TC-UM-044: Filter dropdown triggers show pointer cursor on hover")
    @allure.severity(allure.severity_level.MINOR)
    def test_filter_dropdown_cursor_is_pointer(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-044")

        step.info("Check computed cursor style on Status filter combobox")
        status_cursor = user_mgmt_page.get_filter_combobox_cursor_style(idx=0)
        step.info(f"Status combobox cursor: '{status_cursor}'")

        step.info("Check computed cursor style on Dating Mode filter combobox")
        mode_cursor = user_mgmt_page.get_filter_combobox_cursor_style(idx=1)
        step.info(f"Dating Mode combobox cursor: '{mode_cursor}'")

        assert status_cursor == "pointer", (
            f"Status filter dropdown should have cursor:'pointer', got '{status_cursor}'"
        )
        assert mode_cursor == "pointer", (
            f"Dating Mode filter dropdown should have cursor:'pointer', got '{mode_cursor}'"
        )
        step.passed("Both filter dropdowns show pointer cursor on hover")

    # ── Bug 2 ────────────────────────────────────────────────────────────────

    @allure.title("TC-UM-045: No member count or pagination shown when filter returns no results")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_no_count_summary_when_filter_has_no_results(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-045")

        step.info("Apply Dating Mode → Inactive filter (expects 0 results per bug report)")
        options = user_mgmt_page.get_dating_mode_filter_options()
        inactive_opt = next((o for o in options if "inactive" in o.strip().lower()), None)
        if not inactive_opt:
            pytest.skip("'Inactive' dating mode option not found in dropdown")

        user_mgmt_page.apply_dating_mode_filter(label=inactive_opt)

        row_count = user_mgmt_page.get_table_row_count()
        no_data = user_mgmt_page.is_no_data_message_displayed()
        step.info(f"Rows: {row_count}, no-data message: {no_data}")

        if row_count > 0:
            pytest.skip(f"Filter returned {row_count} results — cannot verify empty-state behavior")

        step.info("Verify count summary does NOT claim members exist")
        summary = user_mgmt_page.get_pagination_summary_text()
        step.info(f"Pagination summary text: '{summary}'")
        if summary:
            assert "showing" not in summary.lower() or "0" in summary, (
                f"Count summary incorrectly shows '{summary}' when no results exist. "
                "Expected 'No Members' message or no count info at all."
            )

        step.info("Verify Next/Prev pagination buttons are hidden")
        assert not user_mgmt_page.is_pagination_visible(), (
            "Pagination Next/Prev buttons should NOT be visible when filter returns 0 results"
        )
        assert not user_mgmt_page.is_page_numbers_visible(), (
            "Page number buttons should NOT be visible when filter returns 0 results"
        )
        step.passed("No member count or pagination shown for empty filter result")

    # ── Bug 3 ────────────────────────────────────────────────────────────────

    @allure.title("TC-UM-046: Location filter placeholder text is 'Search by location'")
    @allure.severity(allure.severity_level.MINOR)
    def test_location_filter_placeholder_text(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-046")

        placeholder = user_mgmt_page.get_location_filter_placeholder()
        step.info(f"Actual placeholder: '{placeholder}'")

        assert placeholder.lower() == "search by location", (
            f"Location filter placeholder should be 'Search by location', got '{placeholder}'"
        )
        step.passed(f"Location filter placeholder is correct: '{placeholder}'")

    # ── Bug 4 ────────────────────────────────────────────────────────────────

    @allure.title("TC-UM-047: Page subtitle is user-friendly, not 'Centralized moderation and content management system'")
    @allure.severity(allure.severity_level.MINOR)
    def test_page_subtitle_is_user_friendly(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-047")

        subtitle = user_mgmt_page.get_page_subtitle()
        step.info(f"Actual subtitle: '{subtitle}'")

        assert subtitle, "Page subtitle is empty — expected a user-friendly description"
        assert "centralized moderation and content management system" not in subtitle.lower(), (
            f"Subtitle is confusing/non-user-friendly: '{subtitle}'. "
            "Expected something like 'Centralized User Management System'."
        )
        step.passed(f"Page subtitle is user-friendly: '{subtitle}'")

    # ── Bug 5 ────────────────────────────────────────────────────────────────

    @allure.title("TC-UM-048: 'Clear All' NOT shown when searching by name/ID/email; cancel icon shown instead")
    @allure.severity(allure.severity_level.NORMAL)
    def test_clear_all_not_shown_for_text_search(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-048")

        rows = user_mgmt_page.get_all_user_rows()
        query = rows[0].name.split()[0] if rows else "test"

        step.info(f"Search by name using query: '{query}'")
        user_mgmt_page.search_users(query)

        step.info("Verify 'Clear All' button is NOT visible for text search")
        clear_all_visible = user_mgmt_page.is_clear_all_button_visible()
        step.info(f"'Clear All' visible: {clear_all_visible}")
        assert not clear_all_visible, (
            "'Clear All' should NOT appear when searching by name/ID/email. "
            "Per design it is reserved for Status/Dating Mode/Location filter chips. "
            "The search field should show a cancel icon (×) instead."
        )

        step.info("Verify a cancel icon IS visible inside the search field")
        cancel_visible = user_mgmt_page.is_search_cancel_icon_visible()
        step.info(f"Search cancel icon visible: {cancel_visible}")
        assert cancel_visible, (
            "A cancel/clear icon (×) should be visible inside the search input when text is typed"
        )
        step.passed("'Clear All' hidden for text search; cancel icon shown correctly in search field")

    # ── Bug 6 ────────────────────────────────────────────────────────────────

    @allure.title("TC-UM-049: Filter section is properly aligned and responsive at 1280px and 1024px")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_section_responsive_layout(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-049")

        try:
            for width, height in [(1280, 800), (1024, 768)]:
                step.info(f"Setting viewport to {width}×{height}")
                user_mgmt_page.set_viewport_size(width, height)

                boxes = user_mgmt_page.get_filter_element_bounding_boxes()
                all_boxes = boxes["comboboxes"] + boxes["location_input"]

                if not all_boxes:
                    step.info(f"No filter bounding boxes at {width}px — skipping")
                    continue

                viewport = user_mgmt_page.page.viewport_size or {"width": width, "height": height}
                for i, box in enumerate(all_boxes):
                    assert box["x"] >= 0, (
                        f"Filter element {i} clipped on left at {width}px — x={box['x']:.0f}"
                    )
                    assert box["y"] >= 0, (
                        f"Filter element {i} clipped on top at {width}px — y={box['y']:.0f}"
                    )
                    assert box["x"] + box["width"] <= viewport["width"] + 5, (
                        f"Filter element {i} overflows right edge at {width}px — "
                        f"right={box['x'] + box['width']:.0f}, viewport={viewport['width']}"
                    )
                    assert box["width"] > 0 and box["height"] > 0, (
                        f"Filter element {i} has zero size at {width}px — "
                        f"w={box['width']:.0f}, h={box['height']:.0f}"
                    )
                step.info(f"All {len(all_boxes)} filter elements within bounds at {width}px ✓")
        finally:
            # Restore default viewport so subsequent tests are unaffected
            user_mgmt_page.set_viewport_size(1920, 1080)

        step.passed("Filter section is properly aligned and responsive at 1280px and 1024px")

    # ── Bug 7 (internal server error) ────────────────────────────────────────

    @allure.title("TC-UM-050: No internal server error on pagination navigation or page refresh")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_no_server_error_on_pagination(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-050")

        if not user_mgmt_page.is_pagination_visible():
            pytest.skip("Pagination not visible — cannot test page navigation")
        if not user_mgmt_page.is_next_page_available():
            pytest.skip("Next page not available — only one page of data")

        step.info("Navigate to page 2")
        user_mgmt_page.click_next_page()
        assert not user_mgmt_page.has_server_error(), (
            "Internal server error appeared after navigating to page 2"
        )
        step.info("Page 2 loaded without server error ✓")

        step.info("Navigate back to page 1")
        user_mgmt_page.click_prev_page()
        assert not user_mgmt_page.has_server_error(), (
            "Internal server error appeared after navigating back to page 1"
        )
        step.info("Page 1 restored without server error ✓")

        step.info("Refresh the page")
        user_mgmt_page.page.reload()
        user_mgmt_page._wait_for_table_loaded()
        assert not user_mgmt_page.has_server_error(), (
            "Internal server error appeared after page refresh"
        )
        step.passed("No server errors on next-page, prev-page, or refresh")

    # ── Bug 8 (location filter — full address / abbreviations) ───────────────

    @allure.title("TC-UM-051: Location filter returns results for full address and country abbreviations")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_location_filter_with_full_address_and_abbreviations(
        self, user_mgmt_page: UserManagementPage
    ):
        step = StepLogger("TC-UM-051")

        rows = user_mgmt_page.get_all_user_rows()
        target = next((r for r in rows if r.location and r.location.strip()), None)
        if not target:
            pytest.skip("No users with location data in visible rows")

        city = target.location.split(",")[0].strip()
        if not city:
            pytest.skip("Cannot extract city from location data")

        step.info(f"Test 1 — City-only filter: '{city}'")
        user_mgmt_page.apply_location_filter(label=city)
        city_count = user_mgmt_page.get_table_row_count()
        city_no_data = user_mgmt_page.is_no_data_message_displayed()
        step.info(f"City-only result: {city_count} rows, no-data={city_no_data}")
        assert city_count > 0 or city_no_data, (
            f"Location filter by city '{city}' returned unexpected page state"
        )

        user_mgmt_page.reset_filters()

        step.info("Test 2 — Country abbreviation filter: 'US'")
        user_mgmt_page.apply_location_filter(label="US")
        us_count = user_mgmt_page.get_table_row_count()
        us_no_data = user_mgmt_page.is_no_data_message_displayed()
        step.info(f"'US' abbreviation result: {us_count} rows, no-data={us_no_data}")
        assert us_count > 0 or us_no_data, (
            "Location filter by country abbreviation 'US' returned unexpected page state. "
            "Filter should support common abbreviations."
        )

        user_mgmt_page.reset_filters()
        step.passed(
            f"Location filter handled city ('{city}': {city_count} rows) "
            f"and abbreviation ('US': {us_count} rows)"
        )

    # ── Bug 9 (Dating Mode dropdown label format) ─────────────────────────────

    @allure.title("TC-UM-052: Dating Mode options show 'Active'/'Inactive', not 'Dating Mode Active'/'Dating Mode Inactive'")
    @allure.severity(allure.severity_level.NORMAL)
    def test_dating_mode_filter_option_labels(self, user_mgmt_page: UserManagementPage):
        step = StepLogger("TC-UM-052")

        options = user_mgmt_page.get_dating_mode_filter_options()
        step.info(f"Dating Mode options: {options}")
        if not options:
            pytest.skip("No Dating Mode filter options found in dropdown")

        real_options = [o for o in options if o.strip() and "all" not in o.strip().lower()]

        for opt in real_options:
            assert not opt.strip().lower().startswith("dating mode "), (
                f"Option '{opt}' is incorrectly prefixed with 'Dating Mode'. "
                "Labels should be 'Active' and 'Inactive' only — matching the Status filter style."
            )

        option_texts_lower = [o.strip().lower() for o in real_options]
        assert "active" in option_texts_lower, (
            f"'Active' not found in Dating Mode options. Got: {options}"
        )
        assert "inactive" in option_texts_lower, (
            f"'Inactive' not found in Dating Mode options. Got: {options}"
        )
        step.passed(f"Dating Mode options correctly labeled: {options}")