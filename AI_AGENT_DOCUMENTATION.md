# AI Email Agent - Complete Documentation

## 📚 Table of Contents

1. [Overview](#overview)
2. [How It Works](#how-it-works)
3. [Architecture](#architecture)
4. [Installation & Setup](#installation--setup)
5. [Usage Guide](#usage-guide)
6. [Features](#features)
7. [Examples](#examples)
8. [Technical Details](#technical-details)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## Overview

The **AI Email Agent** is an intelligent email sending system that uses natural language processing to automatically find and send emails to companies. Instead of manually searching for email addresses, you simply tell the agent what you want in plain English, and it handles the rest.

### Key Capabilities

- 🤖 **Natural Language Processing**: Understands prompts like "Send a mail to microsoft"
- 🎯 **Smart Company Detection**: Automatically finds all emails associated with a company
- 📧 **Automated Email Sending**: Sends personalized emails via Gmail API
- 📎 **File Attachments**: Supports multiple attachments (resume, CV, cover letter)
- 🌐 **Web Interface**: Beautiful Streamlit-based web UI
- 💻 **CLI Interface**: Command-line interface for power users

### Use Cases

- Job applications to multiple companies
- Bulk email campaigns to specific industries
- Automated outreach to company employees
- Personalized mass emailing with attachments

---

## How It Works

### 1. Natural Language Processing

The agent uses **pattern matching** and **regex** to extract information from your prompts:

```
User Input: "Send a mail to microsoft with subject 'Job Application'"
           ↓
Agent Extracts:
  - Company: "microsoft"
  - Subject: "Job Application"
  - Body: (from manual input or prompt)
```

#### Extraction Patterns

The agent recognizes these patterns:

- `"Send a mail to [company]"` → Extracts company name
- `"Send email to [company] company"` → Extracts company name
- `"subject: 'Your Subject'"` → Extracts subject
- `"attachments: file1.pdf file2.pdf"` → Extracts file names
- `"body: 'Your message'"` → Extracts body

### 2. Company Email Discovery

Once the company name is extracted, the agent searches the email database:

```
Company: "microsoft"
           ↓
Search Algorithm:
  1. Load all emails from emails_from_excel.txt
  2. Extract domain from each email (e.g., @microsoft.com)
  3. Match main domain part with company name
  4. Filter out personal emails (gmail.com, outlook.com, etc.)
  5. Return matching emails
           ↓
Result: [anand.subramanian@microsoft.com, asingh@microsoft.com, ...]
```

#### Matching Logic

- **Exact Match**: "microsoft" matches `@microsoft.com` exactly
- **Case Insensitive**: "Microsoft", "MICROSOFT", "microsoft" all work
- **Domain Extraction**: Extracts main domain part (before first dot)
- **Personal Email Filter**: Excludes gmail.com, outlook.com, yahoo.com, etc.

### 3. Email Composition

The agent creates email messages with:

- **To**: Company email addresses (found automatically)
- **From**: Your authenticated Gmail account
- **Subject**: Extracted from prompt or manual input
- **Body**: Extracted from prompt or manual input
- **Attachments**: Files uploaded or specified in prompt

### 4. Email Sending

Emails are sent via **Gmail API**:

```
1. Authenticate with Gmail (OAuth2)
2. Create MIME message with attachments
3. Encode message to base64
4. Send via Gmail API
5. Log results (sent/failed)
6. Update tracking files
```

### 5. Tracking & Logging

All email activities are tracked:

- **sent_mail.txt**: Successfully sent emails
- **not_sent.txt**: Failed emails with error reasons
- **mail_log.csv**: Detailed logs with timestamps
- **sent_mail_report.xlsx**: Excel report with all details

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                  AI Email Agent                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐         ┌──────────────┐            │
│  │   CLI Mode   │         │  Web Mode    │            │
│  │ (Terminal)   │         │ (Streamlit)  │            │
│  └──────┬───────┘         └──────┬───────┘            │
│         │                        │                     │
│         └────────┬───────────────┘                     │
│                  │                                     │
│         ┌────────▼────────┐                           │
│         │  Prompt Parser  │                           │
│         │  (NLP Engine)   │                           │
│         └────────┬────────┘                           │
│                  │                                     │
│         ┌────────▼────────┐                           │
│         │ Email Finder    │                           │
│         │ (Company Match) │                           │
│         └────────┬────────┘                           │
│                  │                                     │
│         ┌────────▼────────┐                           │
│         │ Email Composer  │                           │
│         │ (MIME Builder) │                           │
│         └────────┬────────┘                           │
│                  │                                     │
│         ┌────────▼────────┐                           │
│         │ Gmail API       │                           │
│         │ (Email Sender)  │                           │
│         └────────┬────────┘                           │
│                  │                                     │
│         ┌────────▼────────┐                           │
│         │ Logger          │                           │
│         │ (Tracking)      │                           │
│         └─────────────────┘                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### File Structure

```
job-mailer/
├── email_agent_cli.py          # CLI interface
├── email_agent_streamlit.py     # Web interface
├── send_mails_gmail_api.py     # Gmail API integration
├── emails_from_excel.txt       # Email database
├── credentials.json            # Gmail API credentials
├── token.json                  # Auth token (auto-generated)
├── sent_mail.txt              # Sent emails log
├── not_sent.txt                # Failed emails log
├── mail_log.csv                # Detailed CSV log
├── sent_mail_report.xlsx        # Excel report
└── uploads/                    # Temporary file storage
```

### Data Flow

```
User Prompt
    ↓
[Prompt Parser] → Extract: company, subject, body, attachments
    ↓
[Email Finder] → Search emails_from_excel.txt
    ↓
[Email Composer] → Create MIME message
    ↓
[Gmail API] → Send email
    ↓
[Logger] → Update logs and tracking files
```

---

## Installation & Setup

### Prerequisites

- Python 3.7 or higher
- Gmail account
- Google Cloud Project with Gmail API enabled

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `google-auth>=2.0.0`
- `google-auth-oauthlib>=0.5.0`
- `google-api-python-client>=2.0.0`
- `streamlit>=1.28.0` (for web interface)

### Step 2: Gmail API Setup

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Gmail API**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

3. **Create OAuth Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download credentials as `credentials.json`
   - Place `credentials.json` in project directory

4. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" > "OAuth consent screen"
   - Choose "External" (for personal use)
   - Fill required fields
   - Add your email as test user

### Step 3: Email Database Setup

1. **Prepare Email List**
   - Create `emails_from_excel.txt` file
   - Add one email per line:
     ```
     email1@company.com
     email2@company.com
     email3@company.com
     ```

2. **Email Format**
   - One email per line
   - No headers or extra formatting
   - UTF-8 encoding

### Step 4: First Run Authentication

When you run the agent for the first time:

1. **CLI Mode**:
   ```bash
   python email_agent_cli.py
   ```
   - Browser will open for authentication
   - Grant permissions
   - `token.json` will be created automatically

2. **Web Mode**:
   ```bash
   streamlit run email_agent_streamlit.py
   ```
   - Click "Authenticate with Gmail" in sidebar
   - Grant permissions
   - `token.json` will be created automatically

---

## Usage Guide

### CLI Mode (Command Line)

#### Starting the Agent

```bash
python email_agent_cli.py
```

#### Basic Commands

**1. Simple Email**
```
🤖 Agent> Send a mail to microsoft with subject 'Job Application' and body 'I am interested in...'
```

**2. With Attachments**
```
🤖 Agent> Send email to google with attachments resume.pdf cover_letter.pdf
```

**3. Interactive Multi-line Body**
```
🤖 Agent> Send a mail to amazon with subject 'Backend Engineer Role'
[Enter body when prompted, type END when done]
```

**4. List Available Companies**
```
🤖 Agent> list companies
```

**5. Help**
```
🤖 Agent> help
```

**6. Exit**
```
🤖 Agent> exit
```

### Web Mode (Streamlit)

#### Starting the Web Interface

```bash
streamlit run email_agent_streamlit.py
```

The app will open at `http://localhost:8501`

#### Step-by-Step Usage

1. **Authenticate**
   - Click "🔑 Authenticate with Gmail" in sidebar
   - Grant permissions in browser
   - Wait for "✅ Authenticated successfully!"

2. **Enter Prompt**
   - Type in main text area: `Send a mail to microsoft`
   - Or: `Send email to apple company`

3. **Fill Optional Fields** (if needed)
   - Expand "📋 Manual Input Fields"
   - Enter Subject and Body manually

4. **Upload Attachments** (optional)
   - Click "Upload Resume/CV/Cover Letter"
   - Select files (PDF, DOC, DOCX, TXT)

5. **Send Emails**
   - Click "🚀 Send Emails"
   - Review preview
   - Check confirmation checkbox
   - Emails send automatically

---

## Features

### 1. Natural Language Processing

**What it does:**
- Understands plain English prompts
- Extracts company names, subjects, bodies, attachments
- Handles variations in phrasing

**Examples:**
- ✅ "Send a mail to microsoft"
- ✅ "Send email to apple company"
- ✅ "Send mail to google with subject 'Job Application'"
- ✅ "all microsoft mails"

### 2. Smart Company Matching

**What it does:**
- Finds all emails associated with a company
- Matches exact domain names only
- Filters out personal email domains

**How it works:**
- Extracts main domain part (e.g., "microsoft" from "@microsoft.com")
- Matches exactly (case-insensitive)
- Returns all matching emails

**Example:**
```
Input: "microsoft"
Matches: @microsoft.com, @microsoft.co.uk
Does NOT match: @microservices.com, @microsoftstore.com
```

### 3. Multi-Attachment Support

**Supported formats:**
- PDF (.pdf)
- Word documents (.doc, .docx)
- Text files (.txt)
- Images (.jpg, .jpeg, .png)

**Usage:**
- Upload multiple files at once
- Files attached to all emails
- Automatic MIME type detection

### 4. Email Tracking

**Tracking files:**
- `sent_mail.txt`: Successfully sent emails
- `not_sent.txt`: Failed emails with reasons
- `mail_log.csv`: Detailed logs with timestamps
- `sent_mail_report.xlsx`: Excel report

**Information tracked:**
- Email address
- Send status (SENT/FAILED/DELIVERY_FAILED)
- Timestamp
- Gmail message ID
- Error messages

### 5. Error Handling

**Types of errors handled:**
- **Rate Limiting**: Automatic retry with delays
- **Delivery Failures**: Invalid addresses logged separately
- **Network Errors**: Temporary failures retried
- **Authentication Errors**: Clear error messages

### 6. Progress Tracking

**Web Interface:**
- Real-time progress bar
- Status updates per email
- Success/failure counts

**CLI Interface:**
- Per-email status messages
- Batch progress indicators
- Final summary statistics

---

## Examples

### Example 1: Simple Job Application

**CLI:**
```
🤖 Agent> Send a mail to microsoft with subject 'Software Engineer Application' and body 'I am interested in the Software Engineer position at Microsoft...'
```

**Web:**
1. Enter prompt: `Send a mail to microsoft`
2. Subject: `Software Engineer Application`
3. Body: `I am interested in...`
4. Upload: `resume.pdf`
5. Click Send

**Result:**
- Finds 6 Microsoft emails
- Sends personalized email to each
- Attaches resume
- Logs all activities

### Example 2: Bulk Application to Multiple Companies

**CLI:**
```
🤖 Agent> Send email to google
[Enter body when prompted]
END

🤖 Agent> Send email to amazon
[Enter body when prompted]
END
```

**Web:**
- Repeat process for each company
- Each company's emails found automatically
- Same body/attachments used

### Example 3: Custom Email with Multiple Attachments

**CLI:**
```
🤖 Agent> Send mail to apple with subject 'ML Engineer Position' and attachments resume.pdf cover_letter.pdf portfolio.pdf
```

**Web:**
1. Prompt: `Send mail to apple`
2. Subject: `ML Engineer Position`
3. Upload: `resume.pdf`, `cover_letter.pdf`, `portfolio.pdf`
4. Send

### Example 4: Finding Company Emails

**CLI:**
```
🤖 Agent> list companies
```

**Output:**
```
📋 Found 6388 companies in email database:
  • Microsoft
  • Google
  • Amazon
  • Apple
  ... and 6384 more
```

---

## Technical Details

### Prompt Parsing Algorithm

```python
def extract_company_name(prompt: str) -> Optional[str]:
    patterns = [
        r"(?:all\s+)?([a-zA-Z0-9]+)\s+(?:mails?|emails?)",
        r"to\s+(?:all\s+)?([a-zA-Z0-9]+)",
        r"send\s+(?:a\s+)?(?:mail|email)\s+to\s+([a-zA-Z0-9]+)",
        # ... more patterns
    ]
    # Match patterns and extract company name
```

### Company Matching Algorithm

```python
def find_company_emails(company_name: str, all_emails: List[str]) -> List[str]:
    for email in all_emails:
        domain = email.split("@")[1].lower()
        domain_parts = domain.split(".")
        main_domain = domain_parts[0]
        
        if main_domain == company_name.lower():
            matching_emails.append(email)
    return matching_emails
```

### Email Sending Process

1. **Message Creation**
   ```python
   message = MIMEMultipart()
   message["To"] = recipient_email
   message["Subject"] = subject
   message.attach(MIMEText(body, "plain"))
   # Add attachments
   ```

2. **Encoding**
   ```python
   raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
   ```

3. **Sending**
   ```python
   service.users().messages().send(
       userId="me",
       body={"raw": raw_message}
   ).execute()
   ```

### Session State Management (Web Interface)

```python
# Initialize
st.session_state.email_preview_data = None
st.session_state.sending_emails = False

# Store preview
st.session_state.email_preview_data = {
    'company_name': company_name,
    'company_emails': company_emails,
    'subject': subject,
    'body': body,
    'attachment_paths': attachment_paths
}

# Trigger sending
if confirm:
    st.session_state.sending_emails = True
    st.rerun()
```

---

## Troubleshooting

### Issue: "No emails found for company"

**Possible causes:**
- Company name doesn't match email domains
- Company emails not in database
- Typo in company name

**Solutions:**
1. Check available companies: `list companies`
2. Use exact company name (e.g., "microsoft" not "Microsoft Corporation")
3. Verify emails exist in `emails_from_excel.txt`

### Issue: "Gmail service not available"

**Possible causes:**
- Not authenticated
- Token expired
- Credentials file missing

**Solutions:**
1. Re-authenticate (click "Authenticate with Gmail")
2. Check `credentials.json` exists
3. Delete `token.json` and re-authenticate

### Issue: "Emails not sending after confirmation"

**Possible causes:**
- Gmail service not initialized
- Rate limiting
- Network issues

**Solutions:**
1. Check authentication status
2. Verify Gmail API is enabled
3. Check error messages in console
4. Review `not_sent.txt` for delivery failures

### Issue: "Wrong company emails matched"

**Possible causes:**
- Company name too generic
- Matching algorithm too broad

**Solutions:**
1. Use specific company name
2. Check preview before sending
3. Verify matched emails in preview

### Issue: "File upload not working"

**Possible causes:**
- File format not supported
- File too large
- Permission issues

**Solutions:**
1. Use supported formats: PDF, DOC, DOCX, TXT
2. Check file size (Gmail limit: 25MB)
3. Ensure file permissions are correct

### Issue: "Streamlit not found"

**Solution:**
```bash
# Use Python module instead
python -m streamlit run email_agent_streamlit.py

# Or add to PATH
$env:Path += ";V:\Aviral\job-mailer\Scripts"
```

---

## Best Practices

### 1. Company Name Usage

✅ **Good:**
- "microsoft"
- "google"
- "apple"

❌ **Avoid:**
- "Microsoft Corporation" (too long)
- "MS" (too short/ambiguous)
- "microsoft inc" (unnecessary suffix)

### 2. Email Body

✅ **Good:**
- Clear and concise
- Personalized when possible
- Professional tone
- Include relevant details

❌ **Avoid:**
- Generic templates
- Too long (keep under 500 words)
- Unprofessional language

### 3. Attachments

✅ **Good:**
- PDF format (universal)
- Named clearly (e.g., "John_Doe_Resume.pdf")
- Reasonable file size (< 5MB)
- Multiple files when needed

❌ **Avoid:**
- Very large files (> 10MB)
- Unclear file names
- Too many files (> 5)

### 4. Batch Sending

✅ **Good:**
- Send to one company at a time
- Review preview before sending
- Monitor rate limits
- Check logs regularly

❌ **Avoid:**
- Sending to too many companies at once
- Ignoring error messages
- Not reviewing previews

### 5. Security

✅ **Good:**
- Keep `credentials.json` secure
- Don't commit `token.json` to git
- Use environment variables for sensitive data
- Review sent emails regularly

❌ **Avoid:**
- Sharing credentials
- Committing secrets to version control
- Using on untrusted networks

### 6. Testing

✅ **Good:**
- Test with small batches first
- Verify email format before bulk sending
- Check preview carefully
- Monitor first few sends

❌ **Avoid:**
- Sending to hundreds without testing
- Not checking preview
- Ignoring error messages

---

## Advanced Usage

### Custom Email Templates

Create templates in your email body:

```python
body = """
Dear Hiring Manager,

I am writing to apply for the {position} role at {company}.

[Your content here]

Best regards,
{your_name}
"""
```

### Batch Processing

Process multiple companies:

```python
companies = ["microsoft", "google", "amazon"]
for company in companies:
    # Use agent for each company
    pass
```

### Integration with Other Tools

The agent can be integrated with:
- Job board APIs
- CRM systems
- Email marketing platforms
- Analytics tools

---

## API Reference

### Main Functions

#### `extract_company_name(prompt: str) -> Optional[str]`
Extracts company name from natural language prompt.

#### `find_company_emails(company_name: str, all_emails: List[str]) -> List[str]`
Finds all emails associated with a company.

#### `send_emails(service, emails: List[str], subject: str, body: str, attachment_paths: List[str]) -> Tuple[int, int]`
Sends emails to list of recipients. Returns (sent_count, failed_count).

#### `get_gmail_service() -> Service`
Authenticates and returns Gmail API service object.

---

## FAQ

**Q: Can I send to personal emails?**
A: No, the agent filters out personal email domains (gmail.com, outlook.com, etc.) to focus on company emails only.

**Q: How many emails can I send?**
A: Gmail has daily sending limits (typically 500-2000 per day). The agent respects these limits.

**Q: Can I customize the email format?**
A: Yes, you can customize subject and body. The agent uses plain text format.

**Q: What if I make a mistake?**
A: Always review the preview before sending. Once sent, emails cannot be unsent, but you can track them in logs.

**Q: Can I use this for spam?**
A: No. This tool is intended for legitimate business communications. Follow email marketing laws (CAN-SPAM, GDPR).

**Q: How do I update the email database?**
A: Simply edit `emails_from_excel.txt` and add/remove emails (one per line).

---

## Support & Contributing

### Getting Help

1. Check this documentation
2. Review error messages
3. Check log files for details
4. Review troubleshooting section

### Contributing

To improve the agent:
1. Fork the repository
2. Make changes
3. Test thoroughly
4. Submit pull request

---

## License & Disclaimer

This tool is provided as-is for personal and business use. Users are responsible for:
- Complying with email marketing laws
- Respecting recipient privacy
- Following Gmail Terms of Service
- Using the tool ethically

**Disclaimer:** The authors are not responsible for misuse of this tool or any consequences arising from its use.

---

## Version History

- **v1.0** (2026-01-23): Initial release
  - CLI interface
  - Web interface (Streamlit)
  - Natural language processing
  - Gmail API integration
  - Email tracking and logging

---

**Last Updated:** January 23, 2026

**Documentation Version:** 1.0

---

*For questions or issues, please refer to the troubleshooting section or check the log files for detailed error information.*
