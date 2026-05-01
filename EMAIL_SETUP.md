# Email Notifications Setup

This guide explains how to configure email notifications for automated bug reports when tests fail.

## Environment Variables

Email notifications are configured using environment variables. You can set them in several ways:

### Option 1: Using .env file (Recommended)

1. Create a `.env` file in the project root directory
2. Add your email configuration:

```env
# Email Notification Configuration
# SMTP server settings for sending email notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Email addresses
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=qa-team@yourcompany.com

# Optional: CC recipients (comma-separated)
EMAIL_CC=manager@yourcompany.com,dev-team@yourcompany.com

# Enable/disable email notifications
EMAIL_NOTIFICATIONS_ENABLED=true
```

### Option 2: System Environment Variables (Windows)

Set environment variables at the system level:

```powershell
# PowerShell commands
$env:SMTP_SERVER="smtp.gmail.com"
$env:SMTP_PORT="587"
$env:SMTP_USERNAME="your-email@gmail.com"
$env:SMTP_PASSWORD="your-app-password"
$env:EMAIL_FROM="your-email@gmail.com"
$env:EMAIL_TO="qa-team@yourcompany.com"
$env:EMAIL_CC="manager@yourcompany.com,dev-team@yourcompany.com"
$env:EMAIL_NOTIFICATIONS_ENABLED="true"
```

For permanent system variables, use System Properties > Environment Variables.

### Option 3: IDE Environment Variables

In PyCharm/VS Code, you can set environment variables in the run configuration.

## Gmail Setup (if using Gmail)

If you're using Gmail as your SMTP server:

1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password:
   - Go to Google Account settings
   - Security > 2-Step Verification > App passwords
   - Generate a password for "Mail"
   - Use this app password (not your regular password) in the `SMTP_PASSWORD` variable

## Configuration Details

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SMTP_SERVER` | SMTP server hostname | smtp.gmail.com | Yes |
| `SMTP_PORT` | SMTP server port | 587 | Yes |
| `SMTP_USERNAME` | SMTP authentication username | - | Yes |
| `SMTP_PASSWORD` | SMTP authentication password | - | Yes |
| `EMAIL_FROM` | Sender email address | - | Yes |
| `EMAIL_TO` | Primary recipient email(s) | - | Yes |
| `EMAIL_CC` | CC recipient email(s), comma-separated | - | No |
| `EMAIL_NOTIFICATIONS_ENABLED` | Enable/disable notifications | false | No |

## Testing Email Configuration

To test your email setup, you can run a simple test:

```python
from utils.email_notifier import email_notifier

# Test sending a bug report
success = email_notifier.send_bug_report(
    test_case_id="TC-TEST-001",
    test_name="test_email_configuration",
    error_message="This is a test email to verify configuration",
    additional_info="Testing email notifications setup"
)

if success:
    print("Email sent successfully!")
else:
    print("Email failed to send. Check your configuration.")
```

## What Happens When Tests Fail

When a test fails:

1. A screenshot is automatically captured
2. A bug report JSON file is created in `reports/bugs/`
3. An email notification is sent with:
   - Bug title and ID
   - Test case details
   - Failure description
   - Reproduction steps
   - Environment information
   - Screenshot attachment
4. The Excel report is updated with FAIL status

## Troubleshooting

### Email Not Sending

- Check that all required environment variables are set
- Verify SMTP credentials are correct
- For Gmail, ensure you're using an App Password
- Check firewall/antivirus blocking SMTP connections
- Review logs in `reports/logs/` for error messages

### Common Issues

1. **"Email configuration incomplete"**: Missing required SMTP variables
2. **Authentication failed**: Wrong username/password or not using App Password for Gmail
3. **Connection timeout**: Firewall blocking SMTP port or wrong server/port
4. **Invalid email addresses**: Check EMAIL_TO format (comma-separated for multiple)

## Security Notes

- Never commit `.env` files to version control
- Use App Passwords instead of regular passwords for Gmail
- Consider using dedicated email service accounts for notifications
- Store sensitive credentials securely (environment variables, secret managers)
