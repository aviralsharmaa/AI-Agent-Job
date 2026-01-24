# 📁 Project Structure - AI Email Agent (Streamlit Cloud)

## Essential Files for Streamlit Deployment

### Core Application Files
- `email_agent_streamlit_cloud.py` - Main Streamlit web application
- `send_mails_gmail_api_cloud.py` - Gmail API integration module
- `emails_from_excel.txt` - Email database (one email per line)

### Configuration Files
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit configuration
- `.gitignore` - Git ignore rules

### Data Files (Generated at Runtime)
- `done_mail.txt` - Sent emails log
- `mail_log.csv` - Detailed email log
- `sent_mail.txt` - Successfully sent emails (created at runtime)
- `not_sent.txt` - Failed emails (created at runtime)

## Documentation

All documentation files are in the `docs/` folder:
- `README.md` - Main project documentation
- `DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `QUICK_DEPLOY.md` - Quick deployment guide
- `AI_AGENT_DOCUMENTATION.md` - Complete technical documentation
- And other documentation files...

## Removed Files

The following files were removed as they're not needed for Streamlit Cloud deployment:
- `email_agent_cli.py` - CLI version (not needed for web)
- `email_agent_streamlit.py` - Old Streamlit version
- `send_mails_gmail_api.py` - Old Gmail API version
- `run_streamlit.bat` / `run_streamlit.sh` - Local run scripts (not needed for cloud)
- `email extractor/` folder - Email extraction tools (not needed for deployment)

## Project Structure

```
job-mailer/
├── email_agent_streamlit_cloud.py  # Main Streamlit app
├── send_mails_gmail_api_cloud.py   # Gmail API module
├── emails_from_excel.txt           # Email database
├── requirements.txt                 # Dependencies
├── .streamlit/
│   └── config.toml                 # Streamlit config
├── .gitignore                       # Git ignore
├── docs/                            # All documentation
│   ├── README.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── QUICK_DEPLOY.md
│   └── ... (other .md files)
└── [Runtime files - created when app runs]
    ├── sent_mail.txt
    ├── not_sent.txt
    └── mail_log.csv
```

## For Streamlit Cloud Deployment

Only these files are needed in the repository:
1. `email_agent_streamlit_cloud.py`
2. `send_mails_gmail_api_cloud.py`
3. `emails_from_excel.txt`
4. `requirements.txt`
5. `.streamlit/config.toml`
6. `.gitignore`

All documentation is in the `docs/` folder for reference.

