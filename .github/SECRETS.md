# Required GitHub Actions Secrets

Go to: **GitHub repo → Settings → Secrets and variables → Actions → New repository secret**

## Required (tests will fail without these)

| Secret Name      | Description                        | Example                          |
|------------------|------------------------------------|----------------------------------|
| `DOTC_BASE_URL`  | Admin panel base URL               | `https://your-admin-panel-url.com` |
| `DOTC_EMAIL`     | Admin login email                  | `admin@dotc.com`                 |
| `DOTC_PASSWORD`  | Admin login password               | `YourStrongPassword`             |

## Optional (for email bug notifications)

| Secret Name                   | Description              | Example              |
|-------------------------------|--------------------------|----------------------|
| `SMTP_SERVER`                 | SMTP host                | `smtp.gmail.com`     |
| `SMTP_PORT`                   | SMTP port                | `587`                |
| `SMTP_USERNAME`               | SMTP login               | `qa@company.com`     |
| `SMTP_PASSWORD`               | SMTP password / app key  | `abcd efgh ijkl`     |
| `EMAIL_FROM`                  | Sender address           | `qa@company.com`     |
| `EMAIL_TO`                    | Recipient address        | `dev@company.com`    |
| `EMAIL_CC`                    | CC addresses (comma sep) | `lead@company.com`   |
| `EMAIL_NOTIFICATIONS_ENABLED` | Enable email alerts      | `true`               |

## GitHub Pages (for Allure report hosting)

Enable GitHub Pages on the `gh-pages` branch in:
**Settings → Pages → Source → Branch: gh-pages → / (root)**

After the first workflow run, the Allure report will be available at:
`https://<org>.github.io/<repo>/allure/<run_number>/`