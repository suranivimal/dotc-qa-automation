# DOTC Admin Panel — QA Automation Suite

End-to-end test automation for the DOTC Admin Panel (`https://admin-dotc.alianhub.com/`) using **Python + Playwright + pytest + Allure**.

---

## Project Structure

```
dotc-qa-automation/
├── conftest.py                  # Shared fixtures (browser, page, auth)
├── pytest.ini                   # pytest config + Allure + markers
├── requirements.txt             # Python dependencies
│
├── pages/                       # Page Object Model
│   ├── base_page.py             # Shared helpers (wait, click, screenshot)
│   ├── login_page.py            # Login page locators + actions
│   └── user_management_page.py  # User table, filters, search, detail
│
├── tests/                       # Test suites
│   ├── test_login.py            # 9 test cases (valid, invalid, security)
│   └── test_user_management.py  # 22 test cases (table, filters, search, detail, edge)
│
├── utils/
│   ├── config.py                # URLs, credentials, timeouts, constants
│   └── logger.py                # Coloured console + rotating file logger
│
└── reports/
    ├── allure-results/          # Raw Allure data (auto-generated)
    ├── screenshots/             # Failure screenshots (auto-captured)
    └── logs/                    # Daily rotating log files
```

---

## Quick Start

```bash
# 1. Clone & enter the project
cd dotc-qa-automation

# 2. Create a virtual environment
python -m venv .venv
scls     # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 4. Run all tests
pytest

# 5. Generate Allure report
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
pytest -m "login and not security"
pytest -m edge_case
```

---

## Environment Variables

| Variable         | Default              | Description                |
| ---------------- | -------------------- | -------------------------- |
| `DOTC_BASE_URL`  | `https://admin-dotc.alianhub.com` | Application base URL |
| `DOTC_EMAIL`     | `admin@dotc.com`     | Valid login email          |
| `DOTC_PASSWORD`  | *(set via .env)*     | Valid login password       |
| `HEADLESS`       | `true`               | Run browser headless       |
| `SLOW_MO`        | `0`                  | Slow-motion delay (ms)     |

---

## Test Coverage Summary

| Module            | Test Cases | Categories                                    |
| ----------------- | ---------- | --------------------------------------------- |
| Login             | 9          | Valid, Invalid, Empty, UI Elements, Security   |
| User Management   | 22         | Navigation, Table, Filters, Search, Detail, Edge |
| **Total**         | **31**     |                                                |

---

## CI/CD (GitHub Actions)

Create `.github/workflows/qa.yml`:

```yaml
name: DOTC QA Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: playwright install chromium --with-deps
      - run: pytest --alluredir=reports/allure-results
        env:
          DOTC_EMAIL: ${{ secrets.DOTC_EMAIL }}
          DOTC_PASSWORD: ${{ secrets.DOTC_PASSWORD }}
          HEADLESS: "true"
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: allure-results
          path: reports/allure-results
```

---

## Key Design Decisions

- **POM Architecture** — Every page has its own class with locators, actions, and validations separated.
- **CSS-first Locators** — Multiple fallback selectors per element for resilience across theme changes.
- **No `time.sleep`** — All waits use Playwright's explicit `wait_for` methods.
- **Allure Integration** — Every test class and method has `@allure.step`, `@allure.title`, and severity tags.
- **Screenshot on Failure** — Automatic via `pytest_runtest_makereport` hook — attached to Allure report.
- **StepLogger** — Human-readable step-by-step console logs with pass/fail indicators.