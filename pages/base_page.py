"""
=============================================================================
DOTC Admin Panel — Base Page Object
=============================================================================
Every page object inherits from this. Provides:
  • Wrapped navigation with timeout handling
  • Explicit-wait helpers (visible / hidden / text)
  • Screenshot-on-failure utility
  • Safe click / fill / select helpers with logging
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

import allure
from playwright.sync_api import Page, Locator, expect, TimeoutError as PwTimeout

from utils.config import (
    DEFAULT_TIMEOUT,
    NAVIGATION_TIMEOUT,
    SHORT_TIMEOUT,
    SCREENSHOT_ON_FAILURE,
)
from utils.logger import get_logger

log = get_logger("base_page")


class BasePage:
    """Abstract base for all page objects."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.page.set_default_timeout(DEFAULT_TIMEOUT)
        self.page.set_default_navigation_timeout(NAVIGATION_TIMEOUT)

    # ── Navigation ──────────────────────────────────────────────────────
    def navigate_to(self, url: str, *, wait_until: str = "domcontentloaded") -> None:
        """Navigate and wait for the network to settle."""
        log.info(f"Navigating to → {url}")
        try:
            self.page.goto(url, wait_until=wait_until, timeout=NAVIGATION_TIMEOUT)
            log.info(f"Page loaded — current URL: {self.page.url}")
        except PwTimeout:
            self._capture_screenshot("navigation_timeout")
            raise AssertionError(f"Timed out navigating to {url}")

    def get_current_url(self) -> str:
        return self.page.url

    def reload_page(self) -> None:
        self.page.reload(wait_until="domcontentloaded")

    # ── Explicit Waits ──────────────────────────────────────────────────
    def wait_for_element_visible(
        self, selector: str, *, timeout: int = DEFAULT_TIMEOUT
    ) -> Locator:
        """Return a Locator after it becomes visible."""
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        return locator

    def wait_for_element_hidden(
        self, selector: str, *, timeout: int = DEFAULT_TIMEOUT
    ) -> None:
        self.page.locator(selector).wait_for(state="hidden", timeout=timeout)

    def wait_for_url_contains(
        self, fragment: str, *, timeout: int = NAVIGATION_TIMEOUT
    ) -> None:
        """Block until the URL contains *fragment*."""
        log.debug(f"Waiting for URL to contain '{fragment}'")
        self.page.wait_for_url(f"**{fragment}**", timeout=timeout)

    def wait_for_network_idle(self, *, timeout: int = NAVIGATION_TIMEOUT) -> None:
        self.page.wait_for_load_state("networkidle", timeout=timeout)

    # ── Safe Interaction Helpers ────────────────────────────────────────
    def safe_click(self, selector: str, *, description: str = "") -> None:
        desc = description or selector
        log.info(f"Clicking → {desc}")
        self.page.locator(selector).click(timeout=DEFAULT_TIMEOUT)

    def safe_fill(self, selector: str, value: str, *, description: str = "") -> None:
        desc = description or selector
        log.info(f"Filling '{desc}' with '{value[:30]}{'…' if len(value) > 30 else ''}'")
        field = self.page.locator(selector)
        field.click()
        field.fill(value)

    def safe_clear_and_fill(self, selector: str, value: str, *, description: str = "") -> None:
        """Triple-click to select all → fill."""
        desc = description or selector
        log.info(f"Clearing & filling '{desc}'")
        field = self.page.locator(selector)
        field.click(click_count=3)
        field.fill(value)

    def safe_select_option(
        self, selector: str, *, value: str = "", label: str = "", description: str = ""
    ) -> None:
        desc = description or selector
        log.info(f"Selecting option in '{desc}' — value='{value}' label='{label}'")
        if value:
            self.page.locator(selector).select_option(value=value)
        elif label:
            self.page.locator(selector).select_option(label=label)

    # ── Text Helpers ────────────────────────────────────────────────────
    def get_text(self, selector: str, *, timeout: int = DEFAULT_TIMEOUT) -> str:
        return (
            self.page.locator(selector)
            .inner_text(timeout=timeout)
            .strip()
        )

    def get_all_texts(self, selector: str) -> list[str]:
        return [el.strip() for el in self.page.locator(selector).all_inner_texts()]

    def element_is_visible(self, selector: str, *, timeout: int = SHORT_TIMEOUT) -> bool:
        try:
            self.page.locator(selector).wait_for(state="visible", timeout=timeout)
            return True
        except PwTimeout:
            return False

    def get_element_count(self, selector: str) -> int:
        return self.page.locator(selector).count()

    # ── Screenshot Utility ──────────────────────────────────────────────
    def _capture_screenshot(self, tag: str = "error") -> Optional[str]:
        if not SCREENSHOT_ON_FAILURE:
            return None
        ss_dir = os.path.join("reports", "screenshots")
        os.makedirs(ss_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(ss_dir, f"{tag}_{ts}.png")
        self.page.screenshot(path=path, full_page=True)
        log.warning(f"Screenshot saved → {path}")
        allure.attach.file(path, name=tag, attachment_type=allure.attachment_type.PNG)
        return path

    def take_screenshot(self, name: str) -> str:
        """Public screenshot (for positive evidence too)."""
        return self._capture_screenshot(tag=name)