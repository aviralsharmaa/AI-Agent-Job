# 🤖 AI Email Agent - Intelligent Email Sending System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Gmail API](https://img.shields.io/badge/Gmail%20API-Enabled-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**An intelligent AI-powered email agent that uses natural language processing to automatically find and send personalized emails to companies.**

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Examples](#-examples)

</div>

---

## 🌟 Overview

The **AI Email Agent** is an intelligent system that combines **Natural Language Processing (NLP)** with **Gmail API** to automate email sending. Instead of manually searching for email addresses, you simply tell the agent what you want in plain English, and it handles everything automatically.

### What Makes This AI Agent Special?

- 🧠 **Natural Language Understanding**: Understands prompts like "Send a mail to microsoft"
- 🎯 **Intelligent Company Detection**: Automatically finds all emails associated with a company
- 🔍 **Smart Email Discovery**: Matches company names with email domains using exact matching algorithms
- 📧 **Automated Sending**: Handles the entire email composition and sending process
- 📊 **Real-time Tracking**: Monitors and logs all email activities

---

## ✨ Features

### 🤖 AI-Powered Natural Language Processing

The agent uses advanced pattern matching and regex to understand your intent:

```python
# The agent understands these prompts:
"Send a mail to microsoft"
"Send email to apple company"
"all microsoft mails"
"Send mail to google with subject 'Job Application'"
```

### 🎯 Intelligent Company Email Discovery

The AI agent automatically:
- Extracts company names from your prompts
- Searches through thousands of emails
- Matches exact domain names (e.g., "microsoft" → @microsoft.com)
- Filters out personal email domains
- Returns all matching company emails

### 🌐 Beautiful Streamlit Web Interface

A modern, user-friendly web interface built with Streamlit:

- **Interactive Prompt Input**: Type natural language commands
- **Real-time Preview**: See exactly what will be sent before confirming
- **File Upload**: Drag-and-drop attachments (resume, CV, cover letter)
- **Progress Tracking**: Visual progress bars and status updates
- **Statistics Dashboard**: View sent/failed email counts
- **Company Browser**: Explore all available companies

### 💻 Command-Line Interface (CLI)

For power users who prefer the terminal:

- Interactive prompt-based interface
- Multi-line text input support
- Real-time status updates
- Batch processing capabilities

### 📎 Multi-Attachment Support

- Upload multiple files at once
- Supports PDF, DOC, DOCX, TXT formats
- Automatic MIME type detection
- Files attached to all emails automatically

### 📊 Comprehensive Tracking

- **Sent Emails Log**: Track all successfully sent emails
- **Failed Emails Log**: Review delivery failures with error reasons
- **CSV Logs**: Detailed logs with timestamps and message IDs
- **Excel Reports**: Beautiful formatted reports for analysis

---

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Gmail account
- Google Cloud Project with Gmail API enabled

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/aviralsharmaa/job-mailer.git
   cd job-mailer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Gmail API**
   - Create a Google Cloud Project
   - Enable Gmail API
   - Download `credentials.json` and place it in the project directory
   - See [Gmail API Setup Guide](AI_AGENT_DOCUMENTATION.md#step-2-gmail-api-setup) for details

4. **Prepare email database**
   - Create `emails_from_excel.txt` with one email per line
   - Format: `email@company.com`

### Running the AI Agent

#### 🌐 Web Interface (Recommended)

```bash
streamlit run email_agent_streamlit.py
```

The web interface will open at `http://localhost:8501`

**Features:**
- Beautiful, modern UI
- Interactive prompt input
- Real-time preview
- Drag-and-drop file uploads
- Progress tracking

#### 💻 CLI Interface

```bash
python email_agent_cli.py
```

**Features:**
- Interactive terminal interface
- Multi-line text input
- Command history
- Batch processing

---

## 🎯 How the AI Agent Works

### 1. Natural Language Processing

The AI agent parses your natural language prompts using pattern matching:

```python
# Input: "Send a mail to microsoft"
# Agent extracts:
{
    "company": "microsoft",
    "subject": "Job Application",  # default or from prompt
    "body": "...",                  # from prompt or manual input
    "attachments": []               # from file upload or prompt
}
```

### 2. Company Email Discovery

The agent uses intelligent matching algorithms:

```python
# Company: "microsoft"
# Algorithm:
1. Load all emails from database
2. Extract domain: email.split("@")[1]  # "microsoft.com"
3. Extract main domain: domain.split(".")[0]  # "microsoft"
4. Match exactly: main_domain == "microsoft"
5. Filter personal emails (gmail.com, outlook.com, etc.)
6. Return matching emails
```

### 3. Email Composition & Sending

The agent automatically:
- Creates MIME messages with attachments
- Encodes messages for Gmail API
- Sends emails via authenticated Gmail account
- Tracks success/failure for each email
- Updates logs and reports

### Architecture

```
User Prompt
    ↓
[NLP Parser] → Extract: company, subject, body, attachments
    ↓
[Email Finder] → Search database, match company domains
    ↓
[Email Composer] → Create MIME message with attachments
    ↓
[Gmail API] → Send email via authenticated account
    ↓
[Logger] → Track and log all activities
```

---

## 📖 Usage Examples

### Example 1: Simple Job Application

**Web Interface:**
1. Enter prompt: `Send a mail to microsoft`
2. Subject: `Software Engineer Application`
3. Body: `I am interested in the Software Engineer position...`
4. Upload: `resume.pdf`
5. Click "Send Emails"
6. Review preview and confirm

**CLI:**
```
🤖 Agent> Send a mail to microsoft with subject 'Software Engineer Application' and body 'I am interested in...'
```

**Result:**
- Finds all @microsoft.com emails (6 emails)
- Sends personalized email to each
- Attaches resume automatically
- Logs all activities

### Example 2: Bulk Application with Attachments

**Web Interface:**
1. Prompt: `Send email to google`
2. Upload: `resume.pdf`, `cover_letter.pdf`, `portfolio.pdf`
3. Send

**Result:**
- Finds all Google emails
- Sends with all attachments
- Tracks each send

### Example 3: Finding Company Emails

**CLI:**
```
🤖 Agent> list companies
```

**Output:**
```
📋 Found 6388 companies:
  • Microsoft
  • Google
  • Amazon
  • Apple
  ... and 6384 more
```

---

## 🏗️ Project Structure

```
job-mailer/
├── email_agent_streamlit.py      # 🌐 Streamlit Web Interface (AI Agent)
├── email_agent_cli.py             # 💻 CLI Interface (AI Agent)
├── send_mails_gmail_api.py       # 📧 Gmail API Integration
├── emails_from_excel.txt         # 📊 Email Database
├── credentials.json               # 🔐 Gmail API Credentials
├── token.json                     # 🔑 Auth Token (auto-generated)
│
├── AI_AGENT_DOCUMENTATION.md      # 📚 Complete Documentation
├── QUICK_START_GUIDE.md          # ⚡ Quick Start Guide
│
├── sent_mail.txt                 # ✅ Sent Emails Log
├── not_sent.txt                  # ❌ Failed Emails Log
├── mail_log.csv                  # 📋 Detailed CSV Log
└── uploads/                      # 📎 Temporary File Storage
```

---

## 🧠 AI Agent Components

### 1. Prompt Parser (`extract_company_name`)

Uses regex patterns to extract information from natural language:

```python
def extract_company_name(prompt: str) -> Optional[str]:
    """
    AI-powered natural language parser that extracts company names
    from user prompts using pattern matching and regex.
    
    Examples:
        "Send a mail to microsoft" → "microsoft"
        "all microsoft mails" → "microsoft"
        "Send email to apple company" → "apple"
    """
    patterns = [
        r"(?:all\s+)?([a-zA-Z0-9]+)\s+(?:mails?|emails?)",
        r"to\s+(?:all\s+)?([a-zA-Z0-9]+)",
        r"send\s+(?:a\s+)?(?:mail|email)\s+to\s+([a-zA-Z0-9]+)",
        # ... more intelligent patterns
    ]
    # Match and extract company name
```

### 2. Email Finder (`find_company_emails`)

Intelligent algorithm to find company emails:

```python
def find_company_emails(company_name: str, all_emails: List[str]) -> List[str]:
    """
    AI agent's intelligent email discovery algorithm.
    Matches company names with email domains using exact matching.
    
    Algorithm:
    1. Extract main domain part from each email
    2. Match exactly with company name (case-insensitive)
    3. Filter out personal email domains
    4. Return all matching company emails
    """
    # Exact domain matching logic
    # Filters personal emails
    # Returns matched emails
```

### 3. Email Composer (`create_message_with_attachments`)

Automatically creates MIME messages:

```python
def create_message_with_attachments(to: str, subject: str, body: str, 
                                    attachment_paths: List[str]):
    """
    AI agent's email composition system.
    Automatically creates MIME messages with multiple attachments.
    """
    # Create multipart message
    # Add body
    # Add attachments with proper MIME types
    # Encode for Gmail API
```

### 4. Email Sender (`send_emails`)

Handles the entire sending process:

```python
def send_emails(service, emails: List[str], subject: str, body: str, 
                attachment_paths: List[str], progress_bar, status_text):
    """
    AI agent's email sending system.
    Sends emails via Gmail API with progress tracking and error handling.
    """
    # Iterate through emails
    # Create and send each message
    # Track progress
    # Handle errors
    # Log results
```

---

## 🎨 Streamlit Web Interface Features

### Main Interface

- **🤖 Prompt Input**: Natural language command input
- **📝 Manual Fields**: Optional subject and body inputs
- **📎 File Uploader**: Drag-and-drop multiple attachments
- **🚀 Send Button**: One-click email sending

### Sidebar Features

- **🔐 Gmail Authentication**: Secure OAuth2 authentication
- **📊 Statistics**: Real-time sent/failed email counts
- **📋 Company Browser**: Explore all available companies
- **💡 Tips**: Helpful usage tips

### Preview & Confirmation

- **📋 Email Preview**: See all details before sending
- **✅ Confirmation**: Safety checkbox to prevent accidental sends
- **📊 Progress Tracking**: Real-time progress bars
- **🎉 Success Animation**: Visual feedback on completion

---

## 🔧 Configuration

### Environment Setup

1. **Gmail API Credentials**
   - Download `credentials.json` from Google Cloud Console
   - Place in project root directory

2. **Email Database**
   - Create `emails_from_excel.txt`
   - One email per line
   - UTF-8 encoding

3. **Optional Configuration**
   - Modify `PERSONAL_EMAIL_DOMAINS` to filter different domains
   - Adjust batch sizes in `send_mails_gmail_api.py`

---

## 📚 Documentation

- **[Complete Documentation](AI_AGENT_DOCUMENTATION.md)**: Comprehensive guide covering all aspects
- **[Quick Start Guide](QUICK_START_GUIDE.md)**: Get started in 5 minutes
- **[Streamlit Guide](README_STREAMLIT.md)**: Detailed web interface documentation
- **[CLI Guide](README_AGENT.md)**: Command-line interface documentation

---

## 🛠️ Technologies Used

- **Python 3.7+**: Core programming language
- **Streamlit**: Web interface framework
- **Gmail API**: Email sending service
- **Natural Language Processing**: Pattern matching and regex
- **MIME**: Email message formatting
- **OAuth2**: Secure authentication

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## ⚠️ Disclaimer

This tool is intended for legitimate business communications. Users are responsible for:
- Complying with email marketing laws (CAN-SPAM, GDPR, etc.)
- Respecting recipient privacy
- Following Gmail Terms of Service
- Using the tool ethically

**The authors are not responsible for misuse of this tool.**

---

## 📞 Support

For issues, questions, or contributions:
- Check the [Documentation](AI_AGENT_DOCUMENTATION.md)
- Review the [Troubleshooting Guide](AI_AGENT_DOCUMENTATION.md#troubleshooting)
- Open an issue on GitHub

---

## 🌟 Star History

If you find this project useful, please consider giving it a star ⭐

---

<div align="center">

**Built with ❤️ using Python, Streamlit, and Gmail API**

[⬆ Back to Top](#-ai-email-agent---intelligent-email-sending-system)

</div>
