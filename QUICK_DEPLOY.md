# 🚀 Quick Deploy Guide - Streamlit Cloud

## Fastest Way to Deploy (5 Minutes)

### Step 1: Prepare Files

1. **Rename the cloud version:**
   ```bash
   # Use the cloud-compatible version
   cp email_agent_streamlit_cloud.py email_agent_streamlit.py
   ```

2. **Update requirements.txt:**
   ```txt
   streamlit>=1.28.0
   google-auth>=2.0.0
   google-auth-oauthlib>=0.5.0
   google-api-python-client>=2.0.0
   dnspython>=2.4.0
   ```

### Step 2: Push to GitHub

```bash
git add .
git commit -m "Prepare for cloud deployment"
git push origin main
```

### Step 3: Deploy on Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Main file: `email_agent_streamlit.py`
6. Click "Advanced settings"
7. Go to "Secrets" tab
8. Add this:

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

9. Click "Deploy"
10. Wait 2-5 minutes
11. Done! 🎉

### Step 4: Update OAuth Settings

1. Go to Google Cloud Console
2. APIs & Services > Credentials
3. Edit your OAuth 2.0 Client
4. Add authorized redirect URI:
   - `https://your-app-name.streamlit.app`
5. Save

### Step 5: First Use

1. Open your deployed app
2. Upload email database (sidebar)
3. Click "Authenticate with Gmail"
4. Complete OAuth flow
5. Start sending emails!

---

## Alternative: Use Original File with Modifications

If you want to keep using `email_agent_streamlit.py`, just ensure:

1. `send_mails_gmail_api_cloud.py` is in the repo
2. Update imports in `email_agent_streamlit.py`:
   ```python
   from send_mails_gmail_api_cloud import (
       get_gmail_service,
       ...
   )
   ```

---

## Troubleshooting

**"Credentials not found"**
- Check Streamlit secrets are correctly formatted
- Make sure JSON is valid

**"OAuth redirect URI mismatch"**
- Add your Streamlit Cloud URL to Google Cloud Console

**"File not found: emails_from_excel.txt"**
- Upload via the file uploader in sidebar

**"Token expired"**
- Re-authenticate (click "Authenticate with Gmail" again)

---

That's it! Your app is now live on the cloud! 🌐

