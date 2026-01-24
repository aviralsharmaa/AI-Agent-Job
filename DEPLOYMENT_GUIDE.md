# 🚀 Deployment Guide - AI Email Agent (Streamlit)

## Free Cloud Deployment Options

This guide covers deploying the Streamlit AI Email Agent to free cloud platforms.

### Recommended Platforms:
1. **Streamlit Cloud** (Best for Streamlit apps) - FREE
2. **Render** - FREE tier available
3. **Railway** - FREE tier available
4. **Fly.io** - FREE tier available

---

## Option 1: Streamlit Cloud (Recommended) ⭐

### Why Streamlit Cloud?
- Specifically designed for Streamlit apps
- Free tier with unlimited apps
- Easy deployment from GitHub
- Built-in secrets management
- Automatic HTTPS
- No credit card required

### Prerequisites:
1. GitHub account
2. Google Cloud Project with Gmail API enabled
2. OAuth credentials (credentials.json)

### Step-by-Step Deployment:

#### Step 1: Prepare Your Repository

1. **Create a GitHub repository** (if not already created)
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/job-mailer.git
   git push -u origin main
   ```

2. **Create `.streamlit/config.toml`** (optional, for app configuration)
   ```toml
   [theme]
   primaryColor = "#1f77b4"
   backgroundColor = "#ffffff"
   secondaryBackgroundColor = "#f0f2f6"
   textColor = "#262730"
   font = "sans serif"
   ```

#### Step 2: Update requirements.txt

Make sure your `requirements.txt` includes all dependencies:

```txt
streamlit>=1.28.0
google-auth>=2.0.0
google-auth-oauthlib>=0.5.0
google-api-python-client>=2.0.0
dnspython>=2.4.0
```

#### Step 3: Prepare Gmail Credentials

1. **Convert credentials.json to Streamlit Secrets:**
   - Open your `credentials.json` file
   - Copy the entire JSON content
   - You'll add this to Streamlit Cloud secrets

2. **Prepare for OAuth:**
   - In Google Cloud Console, update OAuth redirect URIs:
     - Add: `https://your-app-name.streamlit.app`
     - For local testing: `http://localhost:8501`

#### Step 4: Deploy to Streamlit Cloud

1. **Go to [Streamlit Cloud](https://streamlit.io/cloud)**
   - Sign in with GitHub
   - Click "New app"

2. **Configure Deployment:**
   - **Repository**: Select your GitHub repo
   - **Branch**: `main` (or your default branch)
   - **Main file path**: `email_agent_streamlit.py`
   - **App URL**: Choose your app name (e.g., `ai-email-agent`)

3. **Add Secrets:**
   - Click "Advanced settings"
   - Go to "Secrets" tab
   - Add the following secrets:

   ```toml
   [gmail]
   credentials_json = '''
   {
     "installed": {
       "client_id": "your-client-id",
       "project_id": "your-project-id",
       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
       "token_uri": "https://oauth2.googleapis.com/token",
       "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
       "client_secret": "your-client-secret",
       "redirect_uris": ["http://localhost"]
     }
   }
   '''
   ```

   **OR** if you have the full credentials.json content:
   ```toml
   [gmail]
   credentials_json = '''
   [PASTE YOUR ENTIRE credentials.json CONTENT HERE]
   '''
   ```

4. **Deploy:**
   - Click "Deploy"
   - Wait for deployment (2-5 minutes)
   - Your app will be live at: `https://your-app-name.streamlit.app`

#### Step 5: Upload Email Database

Since `emails_from_excel.txt` won't be in the repo, you have two options:

**Option A: Add to Repository (Recommended for small files)**
```bash
git add emails_from_excel.txt
git commit -m "Add email database"
git push
```

**Option B: Upload via Streamlit Interface**
- Add file uploader in the app to upload email database
- Store in session state or temporary file

#### Step 6: First-Time Authentication

1. Open your deployed app
2. Click "Authenticate with Gmail"
3. Complete OAuth flow
4. Token will be stored in session state (temporary) or you can use Streamlit secrets

---

## Option 2: Render

### Step 1: Create render.yaml

Create `render.yaml` in your project root:

```yaml
services:
  - type: web
    name: ai-email-agent
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run email_agent_streamlit.py --server.port=$PORT --server.address=0.0.0.0
    envVars:
      - key: GMAIL_CREDENTIALS_JSON
        sync: false
    plan: free
```

### Step 2: Deploy

1. Go to [Render](https://render.com)
2. Sign up with GitHub
3. Connect your repository
4. Create new Web Service
5. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run email_agent_streamlit.py --server.port=$PORT --server.address=0.0.0.0`
6. Add environment variable:
   - Key: `GMAIL_CREDENTIALS_JSON`
   - Value: Your credentials.json content (as JSON string)

---

## Option 3: Railway

### Step 1: Create railway.json

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run email_agent_streamlit.py --server.port=$PORT --server.address=0.0.0.0",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Step 2: Deploy

1. Go to [Railway](https://railway.app)
2. Sign up with GitHub
3. New Project → Deploy from GitHub
4. Select your repository
5. Add environment variable:
   - `GMAIL_CREDENTIALS_JSON`: Your credentials.json content

---

## Important Notes for Cloud Deployment

### 1. OAuth Redirect URI

Update your Google Cloud OAuth settings:
- Add your cloud app URL to authorized redirect URIs
- Format: `https://your-app-name.streamlit.app` or `https://your-app.onrender.com`

### 2. Token Storage

On cloud platforms, `token.json` won't persist between sessions. Options:
- Store token in Streamlit secrets (for Streamlit Cloud)
- Use session state (temporary, requires re-auth each session)
- Use database (for persistent storage)

### 3. File Storage

- `emails_from_excel.txt`: Add to repo or use file uploader
- `sent_mail.txt`, `not_sent.txt`: Consider using database or cloud storage
- Logs: Use cloud logging or database

### 4. Security

- Never commit `credentials.json` or `token.json` to GitHub
- Use platform secrets/environment variables
- Add to `.gitignore`:
  ```
  credentials.json
  token.json
  *.txt
  !requirements.txt
  ```

---

## Code Modifications Needed

The current code uses `run_local_server()` which won't work on cloud. You'll need to:

1. **Modify `get_gmail_service()`** to use Streamlit secrets
2. **Handle OAuth flow** in Streamlit interface
3. **Store token** in session state or secrets

See `send_mails_gmail_api_cloud.py` for cloud-compatible version.

---

## Troubleshooting

### Issue: "Credentials not found"
- **Solution**: Make sure credentials are in Streamlit secrets or environment variables

### Issue: "OAuth redirect URI mismatch"
- **Solution**: Add your cloud app URL to Google Cloud Console OAuth settings

### Issue: "Token expired"
- **Solution**: Re-authenticate. Consider implementing token refresh in session state

### Issue: "File not found: emails_from_excel.txt"
- **Solution**: Add file to repository or implement file uploader

### Issue: "Port already in use"
- **Solution**: Use `--server.port=$PORT` for cloud platforms

---

## Quick Start Checklist

- [ ] GitHub repository created
- [ ] requirements.txt updated
- [ ] credentials.json converted to secrets format
- [ ] OAuth redirect URIs updated in Google Cloud
- [ ] .gitignore updated (exclude sensitive files)
- [ ] Deployed to cloud platform
- [ ] Secrets/environment variables configured
- [ ] Email database uploaded
- [ ] Tested authentication
- [ ] Tested email sending

---

## Support

For issues:
1. Check Streamlit Cloud logs
2. Review error messages in app
3. Verify secrets are correctly formatted
4. Check Google Cloud OAuth settings

---

**Happy Deploying! 🚀**

