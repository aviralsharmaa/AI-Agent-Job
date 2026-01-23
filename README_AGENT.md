# AI Email Agent CLI

An intelligent command-line interface for sending emails via natural language prompts. The agent automatically finds company email addresses from your email database and sends personalized emails on your behalf.

## Features

- 🤖 **Natural Language Processing**: Write prompts in plain English
- 🎯 **Smart Company Detection**: Automatically finds emails associated with companies
- 📎 **Multiple Attachments**: Support for resume, CV, cover letters, and more
- 📝 **Multi-line Input**: Enter email body interactively with multi-line support
- ✅ **Confirmation Before Sending**: Review details before emails are sent
- 📊 **Logging**: All sent emails are tracked and logged

## Installation

### Prerequisites

1. Python 3.7 or higher
2. Gmail API credentials (`credentials.json`)
3. Email database file (`emails_from_excel.txt`)

### Setup

1. **Install dependencies** (if not already installed):
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

2. **Gmail API Setup**:
   - Follow the Gmail API setup instructions from `send_mails_gmail_api.py`
   - Ensure you have `credentials.json` in the project directory
   - On first run, you'll be asked to authenticate

3. **Email Database**:
   - Ensure `emails_from_excel.txt` exists with one email per line
   - Format: `email@company.com` or `name@domain.com`

## Usage

### Starting the Agent

```bash
python email_agent_cli.py
```

### Basic Commands

#### 1. Simple Email
```
🤖 Agent> Send a mail to microsoft with subject 'Job Application' and body 'I am interested in working at Microsoft'
```

#### 2. Email with Attachments
```
🤖 Agent> Send email to google with subject 'Software Engineer Application' and attachments resume.pdf cover_letter.pdf
```

#### 3. Interactive Multi-line Body
```
🤖 Agent> Send a mail to amazon with subject 'Backend Engineer Role'

💬 No email body found in prompt.
Would you like to enter the email body?
(Enter your text. Type 'END' on a new line when finished, or 'CANCEL' to cancel)

Dear Hiring Manager,

I am writing to express my interest in the Backend Engineer position...

Thank you for your consideration.

END
```

#### 4. Full Example with All Components
```
🤖 Agent> Send a mail to microsoft with subject 'MLOps Engineer Application' and body 'Hello, I am applying for the MLOps role' and attachments Aviral_cv3.pdf
```

### Command Reference

| Command | Description |
|---------|-------------|
| `help` or `h` | Show help message |
| `exit`, `quit`, or `q` | Exit the program |

## Prompt Format

The agent understands natural language prompts. Here's what it looks for:

### Company Name
- **Pattern**: "to [company]", "send mail to [company]", "[company] employees"
- **Example**: "microsoft", "google", "amazon"
- **Note**: Company name is matched against email domains (e.g., `@microsoft.com`)

### Subject
- **Pattern**: `subject: 'Your Subject'` or `with subject 'Your Subject'`
- **Example**: `subject: 'Job Application'`
- **Default**: If not provided, you'll be prompted to enter it

### Body
- **Pattern**: `body: 'Your message'` or text after subject
- **Example**: `body: 'I am interested in...'`
- **Interactive**: If not in prompt, you can enter multi-line text (type `END` when done)

### Attachments
- **Pattern**: `attachments: file1.pdf file2.pdf` or `attach resume.pdf`
- **Example**: `attachments: Aviral_cv3.pdf cover_letter.pdf`
- **Location**: Files should be in the current working directory
- **Supported**: PDF, DOC, DOCX, TXT, images (JPG, PNG)

## How It Works

1. **Prompt Parsing**: The agent extracts:
   - Company name from your prompt
   - Email subject
   - Email body (or prompts for it)
   - Attachment file names

2. **Email Discovery**: 
   - Searches `emails_from_excel.txt` for emails matching the company
   - Matches company name with email domains (e.g., "microsoft" → `@microsoft.com`)
   - Excludes personal email domains (gmail.com, outlook.com, etc.)

3. **Email Sending**:
   - Shows you the details and asks for confirmation
   - Sends emails using Gmail API
   - Tracks sent/failed emails in log files

## File Structure

```
job-mailer/
├── email_agent_cli.py          # Main agent CLI
├── send_mails_gmail_api.py     # Gmail API integration
├── emails_from_excel.txt       # Email database
├── credentials.json            # Gmail API credentials (not in repo)
├── token.json                  # Gmail auth token (auto-generated)
├── sent_mail.txt               # Successfully sent emails
├── not_sent.txt                # Failed emails
└── mail_log.csv                # Detailed log file
```

## Examples

### Example 1: Quick Job Application
```
🤖 Agent> Send a mail to microsoft with subject 'Software Engineer Application' and body 'Hi, I am interested in the Software Engineer role at Microsoft. Please find my resume attached.' and attachments Aviral_cv3.pdf

🔍 Parsing your request...
🔎 Searching for emails associated with 'microsoft'...
✅ Found 6 email(s) for microsoft:
   - anand.subramanian@microsoft.com
   - asingh@microsoft.com
   - idccvs@microsoft.com
   - idcjobs@microsoft.com
   - rghoshal@microsoft.com
   - v-swarnak@microsoft.com

📋 Email Details:
   Company: microsoft
   Subject: Software Engineer Application
   Body: Hi, I am interested in the Software Engineer role at Microsoft. Please find my resume attached.
   Attachments: Aviral_cv3.pdf
   Recipients: 6

❓ Send these emails? (yes/no): yes

📧 Preparing to send emails to 6 recipients...
   Subject: Software Engineer Application
   Attachments: Aviral_cv3.pdf
  ✅ Attached: Aviral_cv3.pdf
[1/6] ✅ Sent to anand.subramanian@microsoft.com
[2/6] ✅ Sent to asingh@microsoft.com
...
✅ Done! Sent: 6, Failed: 0
```

### Example 2: Multi-line Body
```
🤖 Agent> Send email to google with subject 'ML Engineer Position'

💬 No email body found in prompt.
Would you like to enter the email body?
(Enter your text. Type 'END' on a new line when finished, or 'CANCEL' to cancel)

Dear Google Hiring Team,

I am writing to express my strong interest in the ML Engineer position
at Google. With my background in machine learning and MLOps, I believe
I would be a great fit for your team.

Key highlights:
- 3+ years of experience in ML systems
- Expertise in TensorFlow and PyTorch
- Production MLOps experience with MLflow

I have attached my resume and cover letter for your review.

Thank you for your consideration.

Best regards,
[Your Name]

END
```

## Tips & Best Practices

1. **Company Names**: Use the exact company name as it appears in email domains
   - ✅ "microsoft" (matches `@microsoft.com`)
   - ✅ "google" (matches `@google.com`)
   - ❌ "Microsoft Corporation" (might not match)

2. **File Attachments**:
   - Place files in the same directory as the script
   - Use exact file names (case-sensitive on some systems)
   - Supported formats: PDF, DOC, DOCX, TXT, images

3. **Multi-line Text**:
   - Type your message line by line
   - Press Enter after each line
   - Type `END` on a new line when finished
   - Type `CANCEL` to abort

4. **Confirmation**:
   - Always review the email details before confirming
   - Check the recipient count
   - Verify attachments are correct

5. **Error Handling**:
   - Failed emails are logged to `not_sent.txt`
   - Sent emails are tracked in `sent_mail.txt`
   - Detailed logs in `mail_log.csv`

## Troubleshooting

### "No emails found for company"
- Check if the company name matches email domains in `emails_from_excel.txt`
- Company emails should have the format `@company.com`
- Personal emails (gmail.com, outlook.com) are excluded

### "File not found" for attachments
- Ensure files are in the current working directory
- Check file names are spelled correctly
- Use relative paths (e.g., `resume.pdf` not `C:\path\to\resume.pdf`)

### Authentication errors
- Delete `token.json` and re-authenticate
- Ensure `credentials.json` is present
- Check Gmail API is enabled in Google Cloud Console

### Rate limiting
- Gmail has daily sending limits
- The agent handles rate limits automatically
- Wait and try again if you hit limits

## Security Notes

- Never commit `credentials.json` or `token.json` to version control
- Keep your email database file secure
- Review emails before sending
- The agent asks for confirmation before sending

## License

This project is for personal use. Ensure compliance with:
- Gmail API Terms of Service
- Email marketing regulations (CAN-SPAM, GDPR, etc.)
- Your organization's email policies

## Support

For issues or questions:
1. Check the help command: `help`
2. Review the examples above
3. Check log files for error details

---

**Happy emailing! 🚀**
