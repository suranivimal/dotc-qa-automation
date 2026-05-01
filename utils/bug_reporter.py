"""
Bug Reporter Module for DOTC QA Automation.

Handles creation of bug reports on test failures and sends email notifications.
"""

import json
import os
import platform
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Optional

from utils.config import (
    HEADLESS,
    SLOW_MO,
    VIEWPORT_WIDTH,
    VIEWPORT_HEIGHT,
    BASE_URL,
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


def create_bug_report(
    tc_id: str,
    test_name: str,
    failure_message: str,
    screenshot_path: Optional[str] = None,
    video_path: Optional[str] = None,
) -> dict:
    """
    Create a bug report dictionary with all required fields.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    bug_title = f"Test Failure: {tc_id} - {test_name}"
    
    description = f"""
Test case {tc_id} failed during automated execution.

Test Function: {test_name}
Failure Timestamp: {datetime.now().isoformat()}
"""
    
    steps_to_reproduce = f"""
1. Set up test environment with the following configuration:
   - Browser: Chromium (Playwright)
   - Headless: {HEADLESS}
   - Viewport: {VIEWPORT_WIDTH}x{VIEWPORT_HEIGHT}
   - Slow Motion: {SLOW_MO}ms
   - Base URL: {BASE_URL}

2. Run the test suite using pytest.

3. Execute the specific test case: {test_name} (TC: {tc_id})

4. Observe the failure.
"""
    
    environment = f"""
- Operating System: {platform.system()} {platform.release()}
- Python Version: {platform.python_version()}
- Browser: Chromium
- Headless Mode: {HEADLESS}
- Viewport Size: {VIEWPORT_WIDTH}x{VIEWPORT_HEIGHT}
- Base URL: {BASE_URL}
- Test Framework: pytest + Playwright
"""
    
    actual_result = failure_message
    
    expected_result = "Test should pass without any failures or errors."
    
    bug_report = {
        "bug_id": f"BUG_{tc_id}_{timestamp}",
        "title": bug_title,
        "description": description.strip(),
        "steps_to_reproduce": steps_to_reproduce.strip(),
        "environment": environment.strip(),
        "actual_result": actual_result,
        "expected_result": expected_result,
        "screenshot_path": screenshot_path,
        "video_path": video_path,
        "created_at": datetime.now().isoformat(),
        "test_case_id": tc_id,
        "test_name": test_name,
    }
    
    return bug_report


def save_bug_report(bug_report: dict) -> str:
    """
    Save bug report to a JSON file.
    Returns the file path.
    """
    bug_id = bug_report["bug_id"]
    file_path = BUG_REPORTS_DIR / f"{bug_id}.json"
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(bug_report, f, indent=2, ensure_ascii=False)
    
    log.info(f"Bug report saved: {file_path}")
    return str(file_path)


def send_bug_email(bug_report: dict, screenshot_path: Optional[str] = None):
    """
    Send bug report via email with optional screenshot attachment.
    """
    if not EMAIL_NOTIFICATIONS_ENABLED:
        log.info("Email notifications are disabled. Skipping email send.")
        return
        
    if not all([SMTP_USERNAME, SMTP_PASSWORD, EMAIL_TO]):
        log.warning("Email configuration incomplete. Skipping email send.")
        return
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = ", ".join(EMAIL_TO) if isinstance(EMAIL_TO, list) else EMAIL_TO
        if EMAIL_CC:
            msg['Cc'] = ", ".join(EMAIL_CC)
        
        msg['Subject'] = bug_report["title"]
        
        # Email body
        body = f"""
Bug Report: {bug_report["bug_id"]}

Description:
{bug_report["description"]}

Steps to Reproduce:
{bug_report["steps_to_reproduce"]}

Environment:
{bug_report["environment"]}

Actual Result:
{bug_report["actual_result"]}

Expected Result:
{bug_report["expected_result"]}

Test Case: {bug_report["test_case_id"]}
Created: {bug_report["created_at"]}
"""
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach screenshot if available
        if screenshot_path and Path(screenshot_path).exists():
            with open(screenshot_path, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{Path(screenshot_path).name}"')
                msg.attach(part)
        
        # Prepare recipients list
        recipients = EMAIL_TO if isinstance(EMAIL_TO, list) else [EMAIL_TO]
        if EMAIL_CC:
            recipients.extend(EMAIL_CC)
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_FROM, recipients, text)
        server.quit()
        
        log.info(f"Bug report email sent to: {recipients}")
        
    except Exception as e:
        log.error(f"Failed to send bug report email: {e}")


def report_bug_on_failure(
    tc_id: str,
    test_name: str,
    failure_message: str,
    screenshot_path: Optional[str] = None,
    video_path: Optional[str] = None,
):
    """
    Main function to create bug report and send notification.
    """
    log.info(f"Creating bug report for failed test: {tc_id}")
    
    bug_report = create_bug_report(tc_id, test_name, failure_message, screenshot_path, video_path)
    save_bug_report(bug_report)
    send_bug_email(bug_report, screenshot_path)
