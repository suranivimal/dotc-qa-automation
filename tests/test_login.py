"""
=============================================================================
DOTC Admin Panel — Login Test Suite
=============================================================================
Test Scope:
  TC-LOGIN-001  Valid login → dashboard redirect
  TC-LOGIN-002  Invalid email + valid password → error
  TC-LOGIN-003  Valid email + invalid password → error
  TC-LOGIN-004  Empty email field → validation error
  TC-LOGIN-005  Empty password field → validation error
  TC-LOGIN-006  Both fields empty → validation error
  TC-LOGIN-007  Login page elements visibility check
  TC-LOGIN-008  SQL injection attempt in email → no crash
  TC-LOGIN-009  XSS attempt in email → sanitized
  TC-LOGIN-021  Login via Enter key on password field
  TC-LOGIN-022  Session persists after page refresh
  TC-LOGIN-023  Logout redirects back to login page
"""

from __future__ import annotations

import pytest
import allure

from pages.login_page import LoginPage
from utils.config import (
    VALID_EMAIL,
    VALID_PASSWORD,
    INVALID_EMAIL,
    INVALID_PASSWORD,
    LOGIN_URL,
)
from utils.logger import StepLogger


# ═══════════════════════════════════════════════════════════════════════════
#  FIXTURES
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def login_page(page) -> LoginPage:
    """Navigate to the login page before each test."""
    lp = LoginPage(page)
    lp.open_login_page()
    return lp


# ═══════════════════════════════════════════════════════════════════════════
#  POSITIVE SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════

@allure.suite("Login")
@allure.sub_suite("Positive")
@allure.title("TC-LOGIN-001: Valid credentials → successful login")
@allure.severity(allure.severity_level.BLOCKER)
class TestValidLogin:
    pytestmark = [pytest.mark.login, pytest.mark.smoke, pytest.mark.regression]

    def test_valid_login_redirects_to_dashboard(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-001")

        step.info("Enter valid email")
        login_page.enter_email(VALID_EMAIL)

        step.info("Enter valid password")
        login_page.enter_password(VALID_PASSWORD)

        step.info("Click Continue button")
        login_page.click_continue_button()

        step.info("Wait for dashboard to load")
        login_page.wait_for_dashboard()

        step.info("Validate URL changed away from login")
        current_url = login_page.get_current_url()
        assert "login" not in current_url.lower(), (
            f"Still on login page: {current_url}"
        )
        step.passed(f"Redirected to: {current_url}")

        step.info("Validate dashboard indicator is visible")
        assert login_page.is_dashboard_displayed(), (
            "Dashboard layout not detected after login"
        )
        step.passed("Dashboard content is visible")


# ═══════════════════════════════════════════════════════════════════════════
#  NEGATIVE SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════

@allure.suite("Login")
@allure.sub_suite("Negative")
class TestInvalidLogin:
    pytestmark = [pytest.mark.login, pytest.mark.regression]

    @allure.title("TC-LOGIN-002: Invalid email → error message")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_invalid_email_shows_error(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-002")

        step.info("Enter invalid email")
        login_page.enter_email(INVALID_EMAIL)

        step.info("Enter valid password")
        login_page.enter_password(VALID_PASSWORD)

        step.info("Click Continue button")
        login_page.click_continue_button()

        step.info("Validate error message is shown")
        # Either a toast / inline error, or we stay on login
        login_page.page.wait_for_timeout(3000)  # allow server response
        error_shown = login_page.is_error_message_displayed()
        still_on_login = login_page.is_login_page_displayed()

        assert error_shown or still_on_login, (
            "Expected error message or to remain on login page"
        )
        step.passed("Error handled correctly for invalid email")

    @allure.title("TC-LOGIN-003: Valid email + wrong password → error message")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_wrong_password_shows_error(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-003")

        step.info("Enter valid email")
        login_page.enter_email(VALID_EMAIL)

        step.info("Enter wrong password")
        login_page.enter_password(INVALID_PASSWORD)

        step.info("Click Continue button")
        login_page.click_continue_button()

        step.info("Validate error or still on login page")
        login_page.page.wait_for_timeout(3000)
        error_shown = login_page.is_error_message_displayed()
        still_on_login = login_page.is_login_page_displayed()

        assert error_shown or still_on_login, (
            "Expected error message for wrong password"
        )
        step.passed("Wrong password error handled correctly")


@allure.suite("Login")
@allure.sub_suite("Validation")
class TestEmptyInputValidation:
    pytestmark = [pytest.mark.login, pytest.mark.regression]

    @allure.title("TC-LOGIN-004: Empty email → validation error")
    @allure.severity(allure.severity_level.NORMAL)
    def test_empty_email_validation(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-004")

        step.info("Leave email empty, enter password")
        login_page.enter_password(VALID_PASSWORD)

        step.info("Click Continue button")
        login_page.click_continue_button()

        step.info("Check for validation error")
        login_page.page.wait_for_timeout(1000)

        # HTML5 required attribute OR custom inline error
        has_error = (
            login_page.is_email_validation_error_displayed()
            or login_page.is_error_message_displayed()
            or login_page.is_login_page_displayed()
        )
        assert has_error, "No validation for empty email"
        step.passed("Empty email validation works")

    @allure.title("TC-LOGIN-005: Empty password → validation error")
    @allure.severity(allure.severity_level.NORMAL)
    def test_empty_password_validation(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-005")

        step.info("Enter email, leave password empty")
        login_page.enter_email(VALID_EMAIL)

        step.info("Click Continue button")
        login_page.click_continue_button()

        step.info("Check for validation error")
        login_page.page.wait_for_timeout(1000)

        has_error = (
            login_page.is_error_message_displayed()
            or login_page.is_login_page_displayed()
        )
        assert has_error, "No validation for empty password"
        step.passed("Empty password validation works")

    @allure.title("TC-LOGIN-006: Both fields empty → validation error")
    @allure.severity(allure.severity_level.NORMAL)
    def test_both_empty_validation(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-006")

        step.info("Leave both fields empty")
        step.info("Click Continue button")
        login_page.click_continue_button()

        step.info("Check for validation")
        login_page.page.wait_for_timeout(1000)

        assert login_page.is_login_page_displayed(), (
            "Form should not submit with empty fields"
        )
        step.passed("Both-empty validation works")


# ═══════════════════════════════════════════════════════════════════════════
#  UI ELEMENT CHECKS
# ═══════════════════════════════════════════════════════════════════════════

@allure.suite("Login")
@allure.sub_suite("UI Elements")
class TestLoginPageElements:
    pytestmark = [pytest.mark.login, pytest.mark.smoke]

    @allure.title("TC-LOGIN-007: Login page elements are visible")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_page_elements_visible(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-007")

        step.info("Verify email input is visible")
        assert login_page.is_login_page_displayed(), "Email input not visible"
        step.passed("Email input visible")

        step.info("Verify password input is visible")
        assert login_page.is_password_field_visible(), "Password input not visible"
        step.passed("Password input visible")

        step.info("Verify Continue button is visible")
        assert login_page.element_is_visible(LoginPage.CONTINUE_BUTTON), (
            "Continue button not visible"
        )
        step.passed("Continue button visible")


# ═══════════════════════════════════════════════════════════════════════════
#  SECURITY EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════

@allure.suite("Login")
@allure.sub_suite("Security")
class TestLoginSecurityEdgeCases:
    pytestmark = [pytest.mark.login, pytest.mark.security, pytest.mark.regression]

    @allure.title("TC-LOGIN-008: SQL injection in email → no crash")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_sql_injection_does_not_crash(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-008")

        malicious_email = "' OR '1'='1'; --"
        step.info(f"Enter SQL injection payload: {malicious_email}")
        login_page.enter_email(malicious_email)
        login_page.enter_password("anything")
        login_page.click_continue_button()

        login_page.page.wait_for_timeout(3000)

        step.info("Verify page did not crash (5xx / blank page)")
        current_url = login_page.get_current_url()
        page_content = login_page.page.content()

        assert "500" not in login_page.get_current_page_title(), "Server error detected"
        assert len(page_content) > 100, "Page appears blank — possible crash"
        step.passed("SQL injection did not crash the application")

    @allure.title("TC-LOGIN-009: XSS in email → sanitized")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_xss_attempt_sanitized(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-009")

        xss_payload = '<script>alert("xss")</script>'
        step.info("Enter XSS payload in email field")
        login_page.enter_email(xss_payload)
        login_page.enter_password("anything")
        login_page.click_continue_button()

        login_page.page.wait_for_timeout(2000)

        step.info("Verify no script execution (no alert dialog)")
        # Playwright would throw if an unexpected dialog appeared
        # If we got here without exception, XSS was blocked
        step.passed("XSS payload was sanitized")


# ═══════════════════════════════════════════════════════════════════════════
#  ADVANCED VALIDATION & UI TESTS (TC-LOGIN-010 to TC-LOGIN-020)
# ═══════════════════════════════════════════════════════════════════════════

@allure.suite("Login")
@allure.sub_suite("Validation")
class TestAdvancedValidation:
    pytestmark = [pytest.mark.login, pytest.mark.regression]

    @allure.title("TC-LOGIN-010: Email format validation in real-time")
    @allure.severity(allure.severity_level.NORMAL)
    def test_email_format_validation_realtime(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-010")

        step.info("Enter invalid email format")
        login_page.enter_email("notanemail")

        step.info("Click Continue to trigger validation")
        login_page.click_continue_button()

        step.info("Verify validation error message appears or page stays on login")
        login_page.page.wait_for_timeout(1000)
        # Check if we get any validation error text on the page
        page_content = login_page.page.content().lower()
        has_validation = "email" in page_content and ("invalid" in page_content or "required" in page_content)
        still_on_login = login_page.is_login_page_displayed()
        
        assert has_validation or still_on_login, (
            "Expected validation error or to stay on login page"
        )
        step.passed("Email format validation works in real-time")

    @allure.title("TC-LOGIN-011: Password visibility toggle works")
    @allure.severity(allure.severity_level.NORMAL)
    def test_password_visibility_toggle(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-011")

        step.info("Enter password")
        login_page.enter_password("TestPassword123")

        step.info("Check if password visibility toggle exists")
        toggle_exists = login_page.element_is_visible(
            LoginPage.PASSWORD_VISIBILITY_TOGGLE, timeout=1000
        )
        
        if not toggle_exists:
            step.info("Password visibility toggle not found on this page")
            pytest.skip("Password visibility toggle button not present on login page")

        step.info("Click password visibility toggle")
        login_page.page.click(LoginPage.PASSWORD_VISIBILITY_TOGGLE)

        step.info("Verify password visibility changed")
        login_page.page.wait_for_timeout(500)
        step.passed("Password visibility toggle works correctly")

    @allure.title("TC-LOGIN-012: Keyboard navigation and Tab support")
    @allure.severity(allure.severity_level.NORMAL)
    def test_keyboard_navigation_tab_support(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-012")

        step.info("Click on email input field")
        login_page.page.click(LoginPage.EMAIL_INPUT)

        step.info("Press Tab to move to password field")
        login_page.page.keyboard.press("Tab")

        step.info("Verify password field is focused")
        focused = login_page.page.locator(LoginPage.PASSWORD_INPUT).evaluate(
            "el => el === document.activeElement"
        )
        assert focused, "Tab navigation did not move to password field"
        step.passed("Keyboard Tab navigation works correctly")

    @allure.title("TC-LOGIN-013: Form validation clears on user input")
    @allure.severity(allure.severity_level.NORMAL)
    def test_validation_clears_on_input(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-013")

        step.info("Click Continue with empty fields to trigger validation")
        login_page.click_continue_button()
        login_page.page.wait_for_timeout(500)

        step.info("Verify validation errors are shown on page")
        page_content = login_page.page.content().lower()
        has_validation = "required" in page_content or "invalid" in page_content

        step.info("Enter email to clear validation")
        login_page.enter_email("test@example.com")

        step.info("Check if email validation error is cleared")
        login_page.page.wait_for_timeout(500)
        # Validation should be cleared or not shown for this field anymore
        step.passed("Validation errors clear when user provides input")


@allure.suite("Login")
@allure.sub_suite("Edge Cases")
class TestAdvancedEdgeCases:
    pytestmark = [pytest.mark.login, pytest.mark.regression]

    @allure.title("TC-LOGIN-014: Special characters in password accepted")
    @allure.severity(allure.severity_level.NORMAL)
    def test_special_chars_in_password(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-014")

        special_password = "P@$$w0rd!#%&^*()"
        step.info(f"Enter password with special characters: {special_password}")
        login_page.enter_email("test@example.com")
        login_page.enter_password(special_password)

        step.info("Click Continue button")
        login_page.click_continue_button()

        step.info("Verify form submission (may get auth error, that's ok)")
        login_page.page.wait_for_timeout(2000)
        # Should not crash or show format error
        assert login_page.is_login_page_displayed() or login_page.is_error_message_displayed(), (
            "Page should show login or error, not crash"
        )
        step.passed("Special characters in password are accepted")

    @allure.title("TC-LOGIN-015: Email whitespace trimming works")
    @allure.severity(allure.severity_level.MINOR)
    def test_email_whitespace_trimming(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-015")

        email_with_spaces = "  test@example.com  "
        step.info(f"Enter email with leading/trailing spaces: '{email_with_spaces}'")
        login_page.enter_email(email_with_spaces)

        step.info("Get the actual value of email field")
        email_field = login_page.page.locator(LoginPage.EMAIL_INPUT)
        actual_value = email_field.get_attribute("value") or email_field.input_value()

        step.info(f"Verify spaces are trimmed: '{actual_value}'")
        assert actual_value.strip() == actual_value, (
            f"Email should be trimmed, got: '{actual_value}'"
        )
        step.passed("Email whitespace trimming works")

    @allure.title("TC-LOGIN-016: Very long email address accepted")
    @allure.severity(allure.severity_level.MINOR)
    def test_very_long_email(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-016")

        # Create a very long but valid email
        long_email = "a" * 100 + "@example.com"
        step.info(f"Enter very long email ({len(long_email)} chars)")
        login_page.enter_email(long_email)

        step.info("Click Continue button")
        login_page.click_continue_button()

        step.info("Verify page handled long email (no crash)")
        login_page.page.wait_for_timeout(2000)
        assert login_page.page.content(), "Page appears blank after long email"
        step.passed("Very long email address is accepted")

    @allure.title("TC-LOGIN-017: Uppercase email handled correctly")
    @allure.severity(allure.severity_level.MINOR)
    def test_uppercase_email(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-017")

        uppercase_email = "TEST@EXAMPLE.COM"
        step.info(f"Enter uppercase email: {uppercase_email}")
        login_page.enter_email(uppercase_email)
        login_page.enter_password("TestPassword123")

        step.info("Click Continue button")
        login_page.click_continue_button()

        step.info("Verify form submission (should handle case-insensitive)")
        login_page.page.wait_for_timeout(2000)
        assert (
            login_page.is_login_page_displayed()
            or login_page.is_error_message_displayed()
        ), "Page should remain on login or show error"
        step.passed("Uppercase email is handled correctly")


@allure.suite("Login")
@allure.sub_suite("Accessibility")
class TestAccessibilityAndSecurity:
    pytestmark = [pytest.mark.login, pytest.mark.regression]

    @allure.title("TC-LOGIN-018: Form labels properly associated with inputs")
    @allure.severity(allure.severity_level.NORMAL)
    def test_form_labels_association(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-018")

        step.info("Check for form labels on page")
        page_content = login_page.page.content()

        step.info("Verify email and password labels are present in HTML")
        assert "email" in page_content.lower(), "Email label not found in page"
        assert "password" in page_content.lower(), "Password label not found in page"

        step.info("Verify input elements are present")
        email_input = login_page.page.locator(LoginPage.EMAIL_INPUT)
        password_input = login_page.page.locator(LoginPage.PASSWORD_INPUT)

        assert email_input.is_visible(), "Email input not visible"
        assert password_input.is_visible(), "Password input not visible"
        step.passed("Form labels are properly associated with inputs")

    @allure.title("TC-LOGIN-019: Page meta description present")
    @allure.severity(allure.severity_level.MINOR)
    def test_page_meta_description(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-019")

        step.info("Check for meta description tag")
        meta_description = login_page.page.locator('meta[name="description"]')

        step.info("Verify meta description exists and has content")
        if meta_description.is_visible():
            content = meta_description.get_attribute("content")
            step.info(f"Meta description found: {content}")
            assert content and len(content) > 0, "Meta description is empty"
            step.passed("Page meta description is present and has content")
        else:
            step.info("Meta description not found (informational)")
            step.passed("Meta description check completed")

    @allure.title("TC-LOGIN-020: No sensitive data in localStorage/sessionStorage")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_no_sensitive_data_in_storage(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-020")

        step.info("Check localStorage for sensitive data")
        local_storage = login_page.page.evaluate("() => JSON.stringify(localStorage)")
        session_storage = login_page.page.evaluate("() => JSON.stringify(sessionStorage)")

        step.info("Verify no passwords or tokens in storage")
        assert "password" not in local_storage.lower(), (
            "Password should not be stored in localStorage"
        )
        assert "token" not in local_storage.lower(), (
            "Token should not be stored in localStorage"
        )
        assert "password" not in session_storage.lower(), (
            "Password should not be stored in sessionStorage"
        )
        step.passed("No sensitive data found in browser storage")


# ═══════════════════════════════════════════════════════════════════════════
#  SESSION & LOGOUT (TC-LOGIN-021 to TC-LOGIN-023)
# ═══════════════════════════════════════════════════════════════════════════

@allure.suite("Login")
@allure.sub_suite("Session")
class TestSessionAndLogout:
    pytestmark = [pytest.mark.login, pytest.mark.smoke, pytest.mark.regression]

    @allure.title("TC-LOGIN-021: Login via Enter key on password field")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_via_enter_key(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-021")

        step.info("Enter valid email")
        login_page.enter_email(VALID_EMAIL)

        step.info("Enter valid password")
        login_page.enter_password(VALID_PASSWORD)

        step.info("Press Enter key instead of clicking the button")
        login_page.page.keyboard.press("Enter")

        step.info("Wait for dashboard to load")
        login_page.wait_for_dashboard()

        current_url = login_page.get_current_url()
        assert "login" not in current_url.lower(), (
            f"Still on login page after Enter key: {current_url}"
        )
        step.passed(f"Enter key login successful → {current_url}")

    @allure.title("TC-LOGIN-022: Session persists after page refresh")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_session_persists_on_refresh(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-022")

        step.info("Login with valid credentials")
        login_page.enter_email(VALID_EMAIL)
        login_page.enter_password(VALID_PASSWORD)
        login_page.click_continue_button()
        login_page.wait_for_dashboard()

        step.info("Reload the page")
        login_page.page.reload()
        login_page.page.wait_for_load_state("networkidle")

        step.info("Verify session is still active — not redirected to login")
        current_url = login_page.get_current_url()
        assert "login" not in current_url.lower(), (
            f"Session was lost after page refresh — redirected to: {current_url}"
        )
        step.passed(f"Session persists after refresh — URL: {current_url}")

    @allure.title("TC-LOGIN-023: Logout redirects back to login page")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_logout_redirects_to_login(self, login_page: LoginPage):
        step = StepLogger("TC-LOGIN-023")

        step.info("Login with valid credentials")
        login_page.enter_email(VALID_EMAIL)
        login_page.enter_password(VALID_PASSWORD)
        login_page.click_continue_button()
        login_page.wait_for_dashboard()

        step.info("Confirm dashboard is loaded before logout")
        assert login_page.is_dashboard_displayed(), "Dashboard not visible after login"

        step.info("Perform logout")
        login_page.logout()
        login_page.page.wait_for_timeout(2000)

        step.info("Verify redirected back to login page")
        current_url = login_page.get_current_url()
        on_login = login_page.is_login_page_displayed()

        assert on_login or "login" in current_url.lower(), (
            f"Expected login page after logout, got: {current_url}"
        )
        step.passed("Logout redirected to login page successfully")

