# DOTC Admin Panel — QA Automation Suite

End-to-end test automation for the DOTC Admin Panel (`https://your-admin-panel-url.com/`) using **Python + Playwright + pytest + Allure**.

---

## Project Structure

```
dotc-qa-automation/
├── conftest.py                  # Shared fixtures (browser, auth, video recording)
├── pytest.ini                   # pytest config + Allure + markers
├── requirements.txt             # Python dependencies
├── .env                         # Local credentials (never committed — see .gitignore)
├── .gitignore
│
├── pages/                       # Page Object Model
│   ├── base_page.py             # Shared helpers (wait, click, screenshot)
│   ├── login_page.py            # Login page locators + actions
│   └── user_management_page.py  # User table, filters, search, detail
│
├── tests/                       # Test suites
│   ├── test_login.py            # 23 test cases (valid, invalid, security, session)
│   └── test_user_management.py  # 44 test cases (table, filters, search, detail, pagination)
│
├── utils/
│   ├── config.py                # URLs, credentials, timeouts, constants
│   ├── logger.py                # Coloured console + rotating file logger
│   ├── bug_reporter.py          # Auto-generates JSON bug reports on failure
│   └── excel_reporter.py        # Generates Excel test case report (test_cases.xlsx)
│
├── .github/
│   ├── workflows/
│   │   ├── qa-ci.yml            # CI workflow — runs on push/PR, manual dispatch
│   │   └── qa-nightly.yml       # Nightly full regression at 02:00 UTC
│   └── SECRETS.md               # Guide for configuring GitHub Actions secrets
│
└── reports/                     # Auto-generated (not committed)
    ├── allure-results/          # Raw Allure data
    ├── allure-report/           # Generated HTML report
    ├── screenshots/             # Failure screenshots (auto-captured)
    ├── videos/                  # Per-test video recordings (.webm)
    ├── bugs/                    # JSON bug reports on failure
    ├── logs/                    # Daily rotating log files
    └── test_cases.xlsx          # Excel test report
```

---

## Quick Start

```bash
# 1. Clone & enter the project
git clone https://github.com/suranivimal/dotc-qa-automation.git
cd dotc-qa-automation

# 2. Create a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 4. Configure credentials
# Copy the example below into a .env file in the project root
DOTC_BASE_URL=https://your-admin-panel-url.com
DOTC_EMAIL=your-admin@email.com
DOTC_PASSWORD=your-password

# 5. Run all tests
pytest

# 6. Generate & view Allure report
allure serve reports/allure-results
```

---

## Run Specific Suites

```bash
# Login tests only
pytest tests/test_login.py -v

# User Management only
pytest tests/test_user_management.py -v

# By marker
pytest -m smoke
pytest -m regression
pytest -m login
pytest -m user_management
pytest -m filters
pytest -m search
pytest -m pagination
pytest -m security
pytest -m edge_case
```

---

## Environment Variables

| Variable         | Default                            | Description                |
| ---------------- | ---------------------------------- | -------------------------- |
| `DOTC_BASE_URL`  | `https://your-admin-panel-url.com`  | Application base URL       |
| `DOTC_EMAIL`     | `admin@dotc.com`                   | Valid login email          |
| `DOTC_PASSWORD`  | *(set via .env)*                   | Valid login password       |
| `HEADLESS`       | `true`                             | Run browser headless       |
| `SLOW_MO`        | `0`                                | Slow-motion delay (ms)     |
| `SMTP_SERVER`    | `smtp.gmail.com`                   | SMTP host for email alerts |
| `SMTP_PORT`      | `587`                              | SMTP port                  |
| `SMTP_USERNAME`  | —                                  | SMTP login email           |
| `SMTP_PASSWORD`  | *(set via .env)*                   | SMTP app password          |
| `EMAIL_FROM`     | —                                  | Sender address             |
| `EMAIL_TO`       | —                                  | Recipient address          |
| `EMAIL_NOTIFICATIONS_ENABLED` | `false`             | Enable email on failure    |

---

## Email Notifications

When a test fails, an email is automatically sent with the bug title, test details, failure description, and screenshot attachment. The Excel report is also updated with FAIL status.

### Setup (.env file)

Add the following to your `.env` file:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=qa-team@yourcompany.com
EMAIL_CC=manager@yourcompany.com
EMAIL_NOTIFICATIONS_ENABLED=true
```

### Gmail App Password

1. Enable 2-Factor Authentication on your Google account
2. Go to **Google Account → Security → 2-Step Verification → App passwords**
3. Generate a password for "Mail" and use it as `SMTP_PASSWORD`

### Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Email not sending | Missing env vars | Check all `SMTP_*` variables are set |
| Authentication failed | Wrong password | Use App Password, not your regular Gmail password |
| Connection timeout | Firewall blocking | Check port 587 is allowed |
| Invalid address | Wrong format | Use comma-separated for multiple `EMAIL_TO` |

---

## Test Coverage Summary

| Module            | Test Cases | Markers / Categories                                          |
| ----------------- | ---------- | ------------------------------------------------------------- |
| Login             | 23         | `login`, `smoke`, `regression`, `security`                    |
| User Management   | 44         | `user_management`, `smoke`, `regression`, `filters`, `search`, `pagination`, `detail`, `edge_case` |
| **Total**         | **67**     |                                                               |

---

## CI/CD (GitHub Actions)

Two workflows are configured under `.github/workflows/`:

### `qa-ci.yml` — On push / PR / manual
- Runs on every push to `main`, `master`, `develop` and on pull requests
- Supports manual dispatch with suite selection: `all`, `smoke`, `regression`, `login`, `user_management`, `filters`, `search`, `pagination`
- Uploads Allure report, screenshots, videos, Excel report, and logs as artifacts
- Posts a test summary comment on pull requests
- Deploys Allure report to GitHub Pages on `main`

### `qa-nightly.yml` — Every night at 02:00 UTC
- Runs the full regression suite nightly
- Creates a GitHub issue automatically on failure
- Uploads artifacts with 60-day retention

**Required secrets** — see `.github/SECRETS.md` for setup instructions:

| Secret           | Description              |
| ---------------- | ------------------------ |
| `DOTC_BASE_URL`  | Admin panel URL          |
| `DOTC_EMAIL`     | Admin login email        |
| `DOTC_PASSWORD`  | Admin login password     |
| `SMTP_*`         | Email notification config (optional) |

---

## Key Design Decisions

- **POM Architecture** — Every page has its own class with locators, actions, and validations separated.
- **CSS-first Locators** — Multiple fallback selectors per element for resilience across theme changes.
- **No `time.sleep`** — All waits use Playwright's explicit `wait_for` methods.
- **Allure Integration** — Every test and method has `@allure.step`, `@allure.title`, and severity tags.
- **Screenshot on Failure** — Automatic via `pytest_runtest_makereport` hook, attached to Allure report.
- **Video Recording** — Every test is recorded as a `.webm` file and attached to Allure.
- **Excel Report** — `reports/test_cases.xlsx` generated per run with pass/fail/skip per TC ID.
- **Bug Reporter** — JSON bug reports auto-created in `reports/bugs/` on test failure.
- **Structured Logging** — Human-readable step-by-step console logs with rotating daily log files.