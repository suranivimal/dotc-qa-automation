"""
=============================================================================
DOTC Admin Panel — Login Page Object
=============================================================================
Encapsulates every interaction with the login page:
  • Locators (CSS-first, XPath fallback)
  • Action methods  (enter_email, click_continue, etc.)
  • Validation methods (is_dashboard_visible, get_error_message, etc.)
"""

from __future__ import annotations

import allure
from playwright.sync_api import Page, TimeoutError as PwTimeout

from pages.base_page import BasePage
from utils.config import (
    LOGIN_URL,
    VALID_EMAIL,
    VALID_PASSWORD,
    DEFAULT_TIMEOUT,
    SHORT_TIMEOUT,
    NAVIGATION_TIMEOUT,
)
from utils.logger import get_logger

log = get_logger("login_page")


class LoginPage(BasePage):
    """Page Object for the DOTC Admin login screen."""

    # ═══════════════════════════════════════════════════════════════════
    #  LOCATORS — single source of truth
    # ═══════════════════════════════════════════════════════════════════

    # --- Input Fields ---
    EMAIL_INPUT = 'input[type="email"], input[name="email"], input[placeholder*="mail" i]'
    PASSWORD_INPUT = 'input[type="password"], input[name="password"]'
    PASSWORD_VISIBILITY_TOGGLE = 'button[aria-label*="show" i], button[aria-label*="toggle" i], button[aria-label*="password" i], .password-toggle, [class*="toggle"], [class*="visibility"]'

    # --- Buttons ---
    CONTINUE_BUTTON = 'button:has-text("Continue"), button:has-text("Login"), button:has-text("Sign in"), button[type="submit"]'
    LOGOUT_BUTTON = 'button:has-text("Logout"), button:has-text("Sign out"), a:has-text("Logout")'

    # --- Validation / Error Elements ---
    ERROR_MESSAGE = '.error-message, .alert-danger, .toast-error, [role="alert"], .Toastify__toast--error, .text-danger, .text-red-500'
    VALIDATION_ERROR = '.field-error, .input-error, .invalid-feedback, .form-error, .text-danger'
    # Sibling selectors must use concrete (non-comma-list) base selectors to stay valid CSS
    EMAIL_VALIDATION_ERROR = (
        'input[type="email"] ~ .field-error, input[name="email"] ~ .field-error, '
        'input[type="email"] ~ .invalid-feedback, input[name="email"] ~ .invalid-feedback, '
        'input[type="email"] ~ .text-danger, input[name="email"] ~ .text-danger'
    )
    PASSWORD_VALIDATION_ERROR = (
        'input[type="password"] ~ .field-error, input[name="password"] ~ .field-error, '
        'input[type="password"] ~ .invalid-feedback, input[name="password"] ~ .invalid-feedback, '
        'input[type="password"] ~ .text-danger, input[name="password"] ~ .text-danger'
    )

    # --- Dashboard Indicators (post-login) ---
    DASHBOARD_INDICATOR = '.dashboard, [class*="dashboard"], .sidebar, nav[class*="sidebar"], .main-content, [class*="layout"]'
    SIDEBAR = 'nav, aside, [class*="sidebar"], [class*="side-bar"], [role="navigation"]'
    USER_AVATAR = '.user-avatar, .avatar, [class*="profile"], [class*="user-menu"]'

    # --- Loading ---
    LOADING_SPINNER = '.spinner, .loading, [class*="loader"], [class*="spin"]'

    # ═══════════════════════════════════════════════════════════════════
    #  CONSTRUCTOR
    # ═══════════════════════════════════════════════════════════════════

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ═══════════════════════════════════════════════════════════════════
    #  ACTION METHODS
    # ═══════════════════════════════════════════════════════════════════

    @allure.step("Open login page")
    def open_login_page(self) -> "LoginPage":
        """Navigate to the login URL and wait for the form."""
        self.navigate_to(LOGIN_URL)
        self._wait_for_login_form()
        log.info("Login page loaded successfully")
        return self

    @allure.step("Enter email: {email}")
    def enter_email(self, email: str) -> "LoginPage":
        self.safe_clear_and_fill(self.EMAIL_INPUT, email, description="Email input")
        return self

    @allure.step("Enter password")
    def enter_password(self, password: str) -> "LoginPage":
        self.safe_clear_and_fill(self.PASSWORD_INPUT, password, description="Password input")
        return self

    @allure.step("Click Continue / Login button")
    def click_continue_button(self) -> "LoginPage":
        self.safe_click(self.CONTINUE_BUTTON, description="Continue button")
        return self

    @allure.step("Perform full login with email={email}")
    def login(self, email: str, password: str) -> "LoginPage":
        """High-level: fill both fields and submit."""
        log.info(f"Performing login with email: {email}")
        self.enter_email(email)
        self.enter_password(password)
        self.click_continue_button()
        return self

    @allure.step("Login with valid credentials")
    def login_with_valid_credentials(self) -> "LoginPage":
        return self.login(VALID_EMAIL, VALID_PASSWORD)

    @allure.step("Wait for dashboard to load after login")
    def wait_for_dashboard(self) -> None:
        """Block until the dashboard / main layout appears."""
        log.info("Waiting for dashboard to load…")
        try:
            # Wait for URL change away from login
            self.page.wait_for_url(
                lambda url: "login" not in url.lower() and url != LOGIN_URL,
                timeout=NAVIGATION_TIMEOUT,
            )
            # Then wait for a sidebar / main-content element
            self.page.wait_for_selector(
                self.DASHBOARD_INDICATOR, state="visible", timeout=DEFAULT_TIMEOUT
            )
            log.info(f"Dashboard loaded — URL: {self.page.url}")
        except PwTimeout:
            self._capture_screenshot("dashboard_load_timeout")
            raise AssertionError(
                f"Dashboard did not load within {NAVIGATION_TIMEOUT}ms. "
                f"Current URL: {self.page.url}"
            )

    @allure.step("Logout")
    def logout(self) -> None:
        if self.element_is_visible(self.USER_AVATAR):
            self.safe_click(self.USER_AVATAR, description="User avatar / menu")
        if self.element_is_visible(self.LOGOUT_BUTTON):
            self.safe_click(self.LOGOUT_BUTTON, description="Logout button")
            log.info("Logged out successfully")

    # ═══════════════════════════════════════════════════════════════════
    #  VALIDATION METHODS
    # ═══════════════════════════════════════════════════════════════════

    def is_login_page_displayed(self) -> bool:
        return self.element_is_visible(self.EMAIL_INPUT)

    def is_dashboard_displayed(self) -> bool:
        return self.element_is_visible(self.DASHBOARD_INDICATOR)

    def is_error_message_displayed(self) -> bool:
        return self.element_is_visible(self.ERROR_MESSAGE, timeout=SHORT_TIMEOUT)

    def get_error_message_text(self) -> str:
        """Return the first visible error message text."""
        try:
            return self.get_text(self.ERROR_MESSAGE, timeout=SHORT_TIMEOUT)
        except Exception:
            return ""

    def is_email_validation_error_displayed(self) -> bool:
        return self.element_is_visible(self.VALIDATION_ERROR, timeout=SHORT_TIMEOUT)

    def is_password_field_visible(self) -> bool:
        return self.element_is_visible(self.PASSWORD_INPUT)

    def get_current_page_title(self) -> str:
        return self.page.title()

    # ═══════════════════════════════════════════════════════════════════
    #  INTERNAL HELPERS
    # ═══════════════════════════════════════════════════════════════════

    def _wait_for_login_form(self) -> None:
        """Ensure at least the email field is rendered."""
        try:
            self.page.wait_for_selector(
                self.EMAIL_INPUT, state="visible", timeout=DEFAULT_TIMEOUT
            )
        except PwTimeout:
            self._capture_screenshot("login_form_not_loaded")
            raise AssertionError("Login form did not render — email field not visible")