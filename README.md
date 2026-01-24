# 📧 AI Email Agent - Streamlit Cloud

An intelligent AI-powered email agent that uses natural language processing to automatically find and send personalized emails to companies via Gmail API.

## 🌟 Features

- 🤖 **Natural Language Processing**: Understand prompts like "Send a mail to microsoft"
- 🎯 **Smart Company Detection**: Automatically finds all emails associated with a company
- 📧 **Automated Email Sending**: Sends personalized emails via Gmail API
- 📎 **Multi-Attachment Support**: Upload resume, CV, cover letter, and more
- 🌐 **Beautiful Web Interface**: Modern Streamlit-based UI
- 📊 **Real-time Tracking**: Monitor sent/failed emails with detailed logs

## 🚀 Quick Start

### Deploy on Streamlit Cloud

1. **Fork this repository**
2. **Go to [Streamlit Cloud](https://streamlit.io/cloud)**
3. **Click "New app"**
4. **Select this repository**
5. **Main file**: `email_agent_streamlit_cloud.py`
6. **Add secrets** (see Configuration below)
7. **Deploy!**

## ⚙️ Configuration

### 1. Gmail API Setup

1. Create a Google Cloud Project
2. Enable Gmail API
3. Create OAuth 2.0 credentials (Web application type)
4. Add authorized redirect URI: `https://your-app-name.streamlit.app`

### 2. Streamlit Secrets

Add to Streamlit Cloud → Settings → Secrets:

```toml
[gmail]
credentials_json = '''
{
  "web": {
    "client_id": "YOUR-CLIENT-ID.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR-CLIENT-SECRET"
  }
}
'''
redirect_uri = "https://your-app-name.streamlit.app"
```

### 3. Email Database

The repository includes `emails_from_excel.txt` with email addresses. You can also upload your own via the web interface.

## 💡 Usage

1. **Authenticate** with Gmail (click button in sidebar)
2. **Upload email database** (or use included file)
3. **Enter prompt**: "Send a mail to microsoft"
4. **Fill subject and body** (optional)
5. **Upload attachments** (optional)
6. **Review preview** and confirm
7. **Send!** 🚀

## 📁 Project Structure

```
AI-Agent-Job/
├── email_agent_streamlit_cloud.py  # Main Streamlit app
├── send_mails_gmail_api_cloud.py    # Gmail API module
├── emails_from_excel.txt            # Email database
├── requirements.txt                 # Dependencies
├── .streamlit/
│   └── config.toml                  # Streamlit config
└── README.md                        # This file
```

## 🛠️ Technologies

- **Python 3.7+**
- **Streamlit** - Web framework
- **Gmail API** - Email sending
- **Natural Language Processing** - Pattern matching & regex

## 📋 Requirements

See `requirements.txt`:
- streamlit>=1.28.0
- google-auth>=2.0.0
- google-auth-oauthlib>=0.5.0
- google-api-python-client>=2.0.0

## 🔒 Security

- Never commit `credentials.json` or `token.json`
- Use Streamlit secrets for credentials
- OAuth 2.0 authentication
- Secure token storage

## ⚠️ Disclaimer

This tool is intended for legitimate business communications. Users are responsible for:
- Complying with email marketing laws (CAN-SPAM, GDPR, etc.)
- Respecting recipient privacy
- Following Gmail Terms of Service
- Using the tool ethically

## 📝 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues or questions:
- Check the code comments
- Review error messages
- Open an issue on GitHub

---

**Built with ❤️ using Python, Streamlit, and Gmail API**

⭐ If you find this project useful, please consider giving it a star!

