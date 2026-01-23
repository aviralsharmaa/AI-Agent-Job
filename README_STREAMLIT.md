# AI Email Agent - Streamlit Web Interface

A beautiful, user-friendly web interface for the AI Email Agent built with [Streamlit](https://streamlit.io/).

## 🚀 Quick Start

### Installation

1. **Install Streamlit** (if not already installed):
   ```bash
   pip install streamlit
   ```
   
   Or install all requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Streamlit app**:
   ```bash
   streamlit run email_agent_streamlit.py
   ```

3. **Open your browser**:
   - The app will automatically open at `http://localhost:8501`
   - Or manually navigate to the URL shown in the terminal

## 📋 Features

### 🎯 Main Interface

- **🤖 Prompt Input**: Enter natural language queries like:
  - "Send a mail to microsoft"
  - "Send email to apple company"
  - "Send mail to google"

- **📝 Manual Input Fields** (Optional):
  - **Subject**: Email subject line
  - **Body**: Email body content
  - These can be filled manually or extracted from your prompt

- **📎 File Uploader**:
  - Upload multiple files (PDF, DOC, DOCX, TXT)
  - Resume, CV, Cover Letter attachments
  - Files are automatically attached to emails

### ⚙️ Sidebar Features

- **🔐 Gmail Authentication**:
  - One-click authentication with Gmail
  - Secure token management
  - Disconnect option

- **📊 Statistics**:
  - Total emails in database
  - Sent emails count
  - Failed emails count

- **📋 Available Companies**:
  - View all companies in your email database
  - Quick reference for company names

### ✨ Smart Features

- **Automatic Company Detection**: Extracts company name from your prompt
- **Email Discovery**: Finds all emails associated with the company
- **Preview Before Sending**: Review all details before confirmation
- **Progress Tracking**: Real-time progress bar during email sending
- **Error Handling**: Graceful error handling with detailed messages

## 🎨 Interface Overview

```
┌─────────────────────────────────────────────────────────┐
│              📧 AI Email Agent                          │
│     Intelligent Email Sending Assistant - Web Interface │
├──────────────────────┬──────────────────────────────────┤
│                      │  ⚙️ Settings (Sidebar)          │
│  📝 Compose Email    │  - Gmail Authentication         │
│                      │  - Statistics                   │
│  🤖 Prompt Input     │  - Available Companies          │
│  [Text Area]         │                                  │
│                      │                                  │
│  📋 Manual Fields    │  📖 Quick Guide                 │
│  - Subject           │  - Usage Instructions           │
│  - Body              │  - Examples                      │
│                      │  - Tips                          │
│  📎 Attachments       │  📊 Statistics                   │
│  [File Uploader]     │  - Sent/Failed counts           │
│                      │                                  │
│  🚀 Send Emails      │                                  │
│  [Button]            │                                  │
└──────────────────────┴──────────────────────────────────┘
```

## 📖 Usage Guide

### Step 1: Authenticate

1. Click **"🔑 Authenticate with Gmail"** in the sidebar
2. A browser window will open for Gmail authentication
3. Grant permissions to the app
4. You'll see "✅ Authenticated successfully!"

### Step 2: Enter Your Prompt

In the main text area, enter a natural language prompt:

```
Send a mail to microsoft
```

Or:

```
Send email to apple company
```

### Step 3: Fill Optional Fields

**Option A: Use Manual Fields**
- Expand "📋 Manual Input Fields"
- Enter Subject and Body manually

**Option B: Let Agent Extract**
- The agent will use your prompt as the body
- Subject defaults to "Job Application"

### Step 4: Upload Attachments (Optional)

1. Click "Upload Resume/CV/Cover Letter"
2. Select one or more files
3. Files will be attached to all emails

### Step 5: Review and Send

1. Click **"🚀 Send Emails"**
2. Review the preview:
   - Company name
   - Subject
   - Recipients list
   - Body preview
   - Attachments
3. Check the confirmation checkbox
4. Watch the progress bar as emails are sent

## 💡 Examples

### Example 1: Simple Email

**Prompt:**
```
Send a mail to microsoft
```

**Manual Fields:**
- Subject: `Software Engineer Application`
- Body: `I am interested in the Software Engineer position...`

**Result:** Sends to all Microsoft emails with your subject and body.

### Example 2: With Attachments

**Prompt:**
```
Send email to google
```

**Attachments:** `resume.pdf`, `cover_letter.pdf`

**Result:** Sends to all Google emails with attachments.

### Example 3: Full Custom

**Prompt:**
```
Send mail to apple company
```

**Subject:** `ML Engineer Position`
**Body:** `[Your custom message]`
**Attachments:** `cv.pdf`

**Result:** Fully customized email to all Apple emails.

## 🎯 Tips & Best Practices

1. **Company Names**: Use simple names (e.g., "microsoft" not "Microsoft Corporation")
2. **Case Insensitive**: "microsoft", "Microsoft", "MICROSOFT" all work
3. **File Formats**: Supported formats: PDF, DOC, DOCX, TXT
4. **Multiple Files**: You can upload multiple files at once
5. **Preview Always**: Always review the preview before sending
6. **Confirmation**: The confirmation checkbox prevents accidental sends

## 🔧 Troubleshooting

### "Please authenticate with Gmail first"

**Solution:** Click the "🔑 Authenticate with Gmail" button in the sidebar.

### "No emails found for company"

**Possible causes:**
- Company name doesn't match email domains
- Company emails not in database
- Typo in company name

**Solution:** 
- Check available companies in sidebar
- Use exact company name (e.g., "microsoft" not "ms")

### File Upload Issues

**Solution:**
- Ensure files are in supported formats (PDF, DOC, DOCX, TXT)
- Check file size (Gmail has attachment limits)
- Try uploading one file at a time

### Authentication Errors

**Solution:**
- Delete `token.json` and re-authenticate
- Ensure `credentials.json` is present
- Check Gmail API is enabled in Google Cloud Console

## 📊 Files & Logs

The app uses the same file structure as the CLI version:

- **emails_from_excel.txt**: Email database
- **sent_mail.txt**: Successfully sent emails
- **not_sent.txt**: Failed emails
- **mail_log.csv**: Detailed logs
- **uploads/**: Temporary folder for uploaded files

## 🆚 CLI vs Web Interface

| Feature | CLI | Web Interface |
|---------|-----|---------------|
| Natural Language | ✅ | ✅ |
| File Attachments | ✅ | ✅ |
| Multi-line Input | ✅ | ✅ (Manual fields) |
| Progress Tracking | ✅ | ✅ (Visual progress bar) |
| Preview | ✅ | ✅ (Better visualization) |
| Statistics | ✅ | ✅ (Real-time) |
| Company List | ✅ | ✅ (Sidebar) |
| User Experience | Terminal | Modern Web UI |

## 🚀 Deployment

### Local Development
```bash
streamlit run email_agent_streamlit.py
```

### Production Deployment

You can deploy to:
- **Streamlit Community Cloud**: Free hosting for public apps
- **Streamlit on Snowflake**: Enterprise-grade deployment
- **Your own server**: Using Streamlit's server options

See [Streamlit Deployment Guide](https://docs.streamlit.io/deploy) for details.

## 📝 Notes

- The web interface uses the same Gmail API credentials as the CLI
- All sent emails are logged the same way
- The interface is responsive and works on mobile devices
- Uploaded files are stored temporarily in the `uploads/` folder

## 🎉 Enjoy!

You now have a beautiful web interface for your AI Email Agent! 

For CLI usage, see `README_AGENT.md`.

---

**Built with ❤️ using [Streamlit](https://streamlit.io/)**
