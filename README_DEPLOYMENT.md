# 🚀 AI Email Agent - Streamlit Cloud Deployment

An intelligent AI-powered email agent that uses natural language processing to automatically find and send personalized emails to companies.

## 🌟 Features

- 🤖 **Natural Language Processing**: Understands prompts like "Send a mail to microsoft"
- 🎯 **Smart Company Detection**: Automatically finds all emails associated with a company
- 📧 **Automated Email Sending**: Sends personalized emails via Gmail API
- 📎 **File Attachments**: Supports multiple attachments (resume, CV, cover letter)
- 🌐 **Web Interface**: Beautiful Streamlit-based web UI

## 🚀 Quick Deploy to Streamlit Cloud

### Step 1: Deploy on Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Sign in with GitHub
3. Click "New app"
4. Select this repository: `AI-Agent-Job`
5. Main file: `email_agent_streamlit_cloud.py`
6. Click "Deploy"

### Step 2: Configure Secrets

1. In Streamlit Cloud, go to "Advanced settings" → "Secrets"
2. Add your Gmail OAuth credentials:

```toml
[gmail]
credentials_json = '''
{
  "installed": {
    "client_id": "YOUR-CLIENT-ID.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR-CLIENT-SECRET",
    "redirect_uris": ["http://localhost"]
  }
}
'''
```

### Step 3: Update Google Cloud OAuth Settings

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. APIs & Services → Credentials
3. Edit your OAuth 2.0 Client
4. Add authorized redirect URI: `https://your-app-name.streamlit.app`
5. Save

### Step 4: First Use

1. Open your deployed app
2. Upload email database via sidebar (or use included `emails_from_excel.txt`)
3. Click "Authenticate with Gmail"
4. Complete OAuth flow
5. Start sending emails!

## 📖 Documentation

- **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** - Fast 5-minute deployment guide
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete deployment instructions
- **[DEPLOYMENT_SUMMARY.txt](DEPLOYMENT_SUMMARY.txt)** - Deployment summary

## 📁 Project Structure

```
AI-Agent-Job/
├── email_agent_streamlit_cloud.py  # Main Streamlit app (cloud version)
├── send_mails_gmail_api_cloud.py    # Gmail API module (cloud version)
├── emails_from_excel.txt            # Email database
├── requirements.txt                 # Python dependencies
├── .streamlit/
│   └── config.toml                  # Streamlit configuration
├── QUICK_DEPLOY.md                  # Quick deployment guide
├── DEPLOYMENT_GUIDE.md              # Complete deployment guide
└── README_DEPLOYMENT.md             # This file
```

## 🔧 Setup Gmail API

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project

2. **Enable Gmail API**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

3. **Create OAuth Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download credentials as `credentials.json`
   - Copy the JSON content to Streamlit secrets

4. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" > "OAuth consent screen"
   - Choose "External" (for personal use)
   - Fill required fields
   - Add your email as test user

## 💡 Usage

1. **Upload Email Database** (sidebar)
   - Upload `emails_from_excel.txt` or use the included file
   - Format: One email per line

2. **Authenticate with Gmail** (sidebar)
   - Click "Authenticate with Gmail"
   - Complete OAuth flow

3. **Send Emails**
   - Enter prompt: "Send a mail to microsoft"
   - Fill subject and body (optional)
   - Upload attachments (optional)
   - Review preview
   - Confirm and send

## ⚠️ Important Notes

- **Never commit** `credentials.json` or `token.json` to GitHub
- Email database (`emails_from_excel.txt`) is included in this repo
- Tokens are stored in session state (temporary)
- Re-authenticate if app restarts

## 🆓 Cost

- **Streamlit Cloud**: Free forever
- **Gmail API**: Free tier (500-2000 emails/day)
- **Total**: $0/month

## 📚 More Information

For detailed documentation, see:
- [QUICK_DEPLOY.md](QUICK_DEPLOY.md) - Quick start guide
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Complete guide

## 🔗 Links

- **Streamlit Cloud**: https://streamlit.io/cloud
- **Google Cloud Console**: https://console.cloud.google.com
- **Repository**: https://github.com/aviralsharmaa/AI-Agent-Job

---

**Built with ❤️ using Python, Streamlit, and Gmail API**

