"""
Bug Reporter Module for DOTC QA Automation.

Handles creation of bug reports on test failures and sends email notifications.
"""

import json
import re
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Optional

from utils.config import (
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    EMAIL_FROM,
    EMAIL_TO,
    EMAIL_CC,
    EMAIL_NOTIFICATIONS_ENABLED,
)
from utils.logger import get_logger

log = get_logger("bug_reporter")

BUG_REPORTS_DIR = Path("reports/bugs")
BUG_REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _readable_test_name(raw_name: str) -> str:
    """Convert a pytest function name like 'test_dating_mode_filter[chromium]' → 'Dating Mode Filter'."""
    # Strip browser suffix e.g. [chromium]
    name = re.sub(r'\[.*?\]', '', raw_name)
    # Strip 'test_' prefix
    name = re.sub(r'^test_', '', name)
    # Replace underscores with spaces and title-case
    return name.replace('_', ' ').title()


def _extract_failure_summary(raw_message: str) -> str:
    """Pull a one-line human-readable reason from a raw pytest failure message."""
    if not raw_message:
        return "An unexpected error occurred during the test."

    lines = raw_message.strip().splitlines()

    # Look for AssertionError lines with a custom message first
    for line in lines:
        stripped = line.strip()
        # pytest assertion rewriting produces lines like "AssertionError: <msg>"
        if stripped.startswith("AssertionError:"):
            msg = stripped[len("AssertionError:"):].strip()
            if msg:
                return msg

    # Look for the first meaningful non-blank, non-assert, non-traceback line
    for line in lines:
        stripped = line.strip()
        if (
            stripped
            and not stripped.startswith("assert ")
            and not stripped.startswith("+ ")
            and not stripped.startswith("where ")
            and not stripped.startswith("E ")
            and not stripped.startswith("File ")
            and not stripped.startswith("Traceback")
        ):
            return stripped[:200]

    # Fallback: return first line, capped
    return lines[0][:200] if lines else "An unexpected error occurred during the test."


def create_bug_report(
    tc_id: str,
    test_name: str,
    failure_message: str,
    screenshot_path: Optional[str] = None,
    video_path: Optional[str] = None,
) -> dict:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    readable_name = _readable_test_name(test_name)
    failure_summary = _extract_failure_summary(failure_message)

    label = tc_id if tc_id != "UNKNOWN" else readable_name

    bug_report = {
        "bug_id": f"BUG_{timestamp}_{label}",
        "tc_id": tc_id,
        "test_name": test_name,
        "readable_name": readable_name,
        "failure_summary": failure_summary,
        "raw_failure": failure_message,
        "screenshot_path": screenshot_path,
        "video_path": video_path,
        "created_at": datetime.now().isoformat(),
    }

    return bug_report


def save_bug_report(bug_report: dict) -> str:
    file_path = BUG_REPORTS_DIR / f"{bug_report['bug_id']}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(bug_report, f, indent=2, ensure_ascii=False)
    log.info(f"Bug report saved: {file_path}")
    return str(file_path)


def _build_html_email(bug_report: dict, has_screenshot: bool) -> str:
    tc_id = bug_report["tc_id"]
    readable_name = bug_report["readable_name"]
    failure_summary = bug_report["failure_summary"]
    created_at = bug_report["created_at"]

    try:
        dt = datetime.fromisoformat(created_at)
        human_time = dt.strftime("%d %B %Y at %I:%M %p")
    except Exception:
        human_time = created_at

    tc_badge = (
        f'<span style="background:#e2e8f0;color:#475569;padding:2px 8px;border-radius:4px;font-size:13px;">'
        f'{tc_id}</span>'
        if tc_id != "UNKNOWN"
        else ""
    )

    screenshot_note = (
        '<p style="margin:0;color:#64748b;font-size:13px;">📎 A screenshot of the failure is attached to this email.</p>'
        if has_screenshot
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:32px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,0.08);">

        <!-- Header -->
        <tr>
          <td style="background:#dc2626;padding:24px 32px;">
            <p style="margin:0;color:#ffffff;font-size:11px;letter-spacing:1px;text-transform:uppercase;">Automated QA Report</p>
            <h1 style="margin:8px 0 0;color:#ffffff;font-size:22px;font-weight:700;">&#x1F534; Test Failure Detected</h1>
          </td>
        </tr>

        <!-- Test name -->
        <tr>
          <td style="padding:24px 32px 0;">
            <p style="margin:0 0 6px;color:#94a3b8;font-size:12px;text-transform:uppercase;letter-spacing:0.5px;">Failed Test</p>
            <h2 style="margin:0;color:#1e293b;font-size:18px;font-weight:600;">{readable_name} {tc_badge}</h2>
          </td>
        </tr>

        <!-- Divider -->
        <tr><td style="padding:0 32px;"><hr style="border:none;border-top:1px solid #e2e8f0;margin:20px 0 0;"></td></tr>

        <!-- What went wrong -->
        <tr>
          <td style="padding:20px 32px 0;">
            <p style="margin:0 0 8px;color:#94a3b8;font-size:12px;text-transform:uppercase;letter-spacing:0.5px;">What Went Wrong</p>
            <div style="background:#fef2f2;border-left:4px solid #dc2626;padding:14px 16px;border-radius:0 4px 4px 0;">
              <p style="margin:0;color:#991b1b;font-size:14px;line-height:1.6;">{failure_summary}</p>
            </div>
          </td>
        </tr>

        <!-- When -->
        <tr>
          <td style="padding:20px 32px 0;">
            <p style="margin:0 0 8px;color:#94a3b8;font-size:12px;text-transform:uppercase;letter-spacing:0.5px;">When It Happened</p>
            <p style="margin:0;color:#334155;font-size:14px;">&#x1F4C5; {human_time}</p>
          </td>
        </tr>

        <!-- Screenshot note -->
        {"<tr><td style='padding:20px 32px 0;'>" + screenshot_note + "</td></tr>" if has_screenshot else ""}

        <!-- What to do next -->
        <tr>
          <td style="padding:20px 32px 0;">
            <p style="margin:0 0 8px;color:#94a3b8;font-size:12px;text-transform:uppercase;letter-spacing:0.5px;">Next Steps</p>
            <ul style="margin:0;padding-left:18px;color:#334155;font-size:14px;line-height:2;">
              <li>Review the attached screenshot (if available) to see what the screen looked like when it failed.</li>
              <li>Share this email with the development team so they can investigate.</li>
              <li>Check the Allure report for the full test run details.</li>
            </ul>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="padding:24px 32px;margin-top:24px;">
            <hr style="border:none;border-top:1px solid #e2e8f0;margin-bottom:16px;">
            <p style="margin:0;color:#94a3b8;font-size:12px;">This report was generated automatically by the DOTC QA Automation Suite.</p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_bug_email(bug_report: dict, screenshot_path: Optional[str] = None):
    if not EMAIL_NOTIFICATIONS_ENABLED:
        log.info("Email notifications are disabled. Skipping email send.")
        return

    if not all([SMTP_USERNAME, SMTP_PASSWORD, EMAIL_TO]):
        log.warning("Email configuration incomplete. Skipping email send.")
        return

    try:
        readable_name = bug_report["readable_name"]
        tc_id = bug_report["tc_id"]
        label = f"{readable_name} ({tc_id})" if tc_id != "UNKNOWN" else readable_name

        msg = MIMEMultipart("alternative")
        msg['From'] = EMAIL_FROM
        msg['To'] = ", ".join(EMAIL_TO) if isinstance(EMAIL_TO, list) else EMAIL_TO
        if EMAIL_CC:
            msg['Cc'] = ", ".join(EMAIL_CC)
        msg['Subject'] = f"Test Failed: {label}"

        has_screenshot = bool(screenshot_path and Path(screenshot_path).exists())
        html_body = _build_html_email(bug_report, has_screenshot)
        msg.attach(MIMEText(html_body, 'html'))

        # Wrap in MIMEMultipart('mixed') only if we have an attachment
        if has_screenshot:
            outer = MIMEMultipart("mixed")
            outer['From'] = msg['From']
            outer['To'] = msg['To']
            if EMAIL_CC:
                outer['Cc'] = msg['Cc']
            outer['Subject'] = msg['Subject']
            outer.attach(msg)

            with open(screenshot_path, "rb") as f:
                part = MIMEBase('image', 'png')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{Path(screenshot_path).name}"')
                outer.attach(part)
            msg = outer

        recipients = EMAIL_TO if isinstance(EMAIL_TO, list) else [EMAIL_TO]
        if EMAIL_CC:
            recipients = list(recipients) + list(EMAIL_CC)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, recipients, msg.as_string())

        log.info(f"Bug report email sent: {label}")

    except Exception as e:
        log.error(f"Failed to send bug report email: {e}")


def report_bug_on_failure(
    tc_id: str,
    test_name: str,
    failure_message: str,
    screenshot_path: Optional[str] = None,
    video_path: Optional[str] = None,
):
    log.info(f"Creating bug report for failed test: {test_name}")
    bug_report = create_bug_report(tc_id, test_name, failure_message, screenshot_path, video_path)
    save_bug_report(bug_report)
    send_bug_email(bug_report, screenshot_path)