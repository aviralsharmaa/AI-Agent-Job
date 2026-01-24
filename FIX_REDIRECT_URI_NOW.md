# 🚨 URGENT: Fix redirect_uri_mismatch Error

## The Problem
The code is using `http://localhost:8501` as fallback, but Google Cloud Console has `https://ai-agent-job.streamlit.app`. They MUST match exactly!

## Quick Fix - 2 Steps

### Step 1: Update Google Cloud Console

1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your OAuth 2.0 Client ID (the one you created)
3. Click on it to edit
4. Under **"Authorized redirect URIs"**:
   - **DELETE** any existing URIs (especially `http://localhost:8501` if present)
   - Click **"ADD URI"**
   - Add: `https://ai-agent-job.streamlit.app` (NO trailing slash)
5. Click **"SAVE"**
6. Wait 2-3 minutes for changes to propagate

### Step 2: Update Streamlit Secrets

1. Go to Streamlit Cloud → Your App → Settings → Secrets
2. Make sure you have `redirect_uri` in your secrets:

```toml
[gmail]
credentials_json = '''
{
  "web": {
    "client_id": "YOUR-CLIENT-ID.apps.googleusercontent.com",
    "project_id": "jobmailer-482612",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR-CLIENT-SECRET"
  }
}
'''
redirect_uri = "https://ai-agent-job.streamlit.app"
```

3. Click **"Save"**

## Verification Checklist

✅ **Google Cloud Console** has: `https://ai-agent-job.streamlit.app` (no trailing slash)
✅ **Streamlit Secrets** has: `redirect_uri = "https://ai-agent-job.streamlit.app"` (no trailing slash)
✅ Both match EXACTLY
✅ No `http://localhost:8501` anywhere
✅ Waited 2-3 minutes after saving

## After Fixing

1. Wait 2-3 minutes for Google Cloud changes to propagate
2. Wait for Streamlit Cloud to redeploy (if you updated secrets)
3. Clear your browser cache or use incognito mode
4. Try authentication again

## Code Update

I've also updated the code to use `https://ai-agent-job.streamlit.app` as the default fallback instead of `localhost`. This will be pushed to GitHub.

---

**The redirect URI must match EXACTLY in both places! ✅**

