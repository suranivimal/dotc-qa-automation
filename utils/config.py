"""
=============================================================================
DOTC Admin Panel — QA Automation Configuration
=============================================================================
Centralised config for URLs, credentials, timeouts, and environment flags.
All test files import from here so nothing is hard-coded elsewhere.
"""

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# ─── Base URLs ──────────────────────────────────────────────────────────────
BASE_URL = os.getenv("DOTC_BASE_URL", "https://admin-dotc.alianhub.com")
LOGIN_URL = f"{BASE_URL}/"
USER_MANAGEMENT_URL = f"{BASE_URL}/user-management"

# ─── Credentials ────────────────────────────────────────────────────────────
# Override via env vars in CI (GitHub Actions secrets, etc.)
VALID_EMAIL = os.getenv("DOTC_EMAIL", "admin@dotc.com")
VALID_PASSWORD = os.getenv("DOTC_PASSWORD", "Abc@223133")

INVALID_EMAIL = "wrong@example.com"
INVALID_PASSWORD = "WrongPass!999"

# ─── Timeouts (milliseconds — Playwright convention) ────────────────────────
DEFAULT_TIMEOUT = 15_000          # General element wait
NAVIGATION_TIMEOUT = 30_000       # Full page navigation
SHORT_TIMEOUT = 5_000             # Quick checks (toasts, inline errors)
LONG_TIMEOUT = 45_000             # Slow-loading tables / API-heavy pages

# ─── Browser Settings ──────────────────────────────────────────────────────
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
SLOW_MO = int(os.getenv("SLOW_MO", "0"))            # ms delay between actions
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080

# ─── Retry / Stability ─────────────────────────────────────────────────────
SCREENSHOT_ON_FAILURE = True

# ─── Expected UI Constants ──────────────────────────────────────────────────
EXPECTED_TABLE_COLUMNS = [
    "Name",
    "Email",
    "Location",
    "Status",
    "Dating Mode",
    "Actions",
]

# ─── Email Notification Settings ────────────────────────────────────────────
# SMTP configuration for sending automated bug reports
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Email addresses for notifications
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_CC = os.getenv("EMAIL_CC", "").split(",") if os.getenv("EMAIL_CC") else []

# Email notification settings
EMAIL_NOTIFICATIONS_ENABLED = os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "false").lower() == "true"
