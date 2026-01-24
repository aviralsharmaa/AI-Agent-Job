# 🔧 Fix: Invalid Redirect URI Error

## Problem
Google Cloud Console shows error: **"Invalid Redirect: must contain a domain"** when trying to add `urn:ietf:wg:oauth:2.0:oob`

## Solution
For **Web application** type OAuth clients, Google requires actual URLs, not URNs. Use your Streamlit Cloud URL instead.

---

## Step 1: Add Your Streamlit Cloud URL

In Google Cloud Console → OAuth 2.0 Client → Authorized redirect URIs:

1. Click **"ADD URI"**
2. Add your Streamlit Cloud app URL:
   ```
   https://your-app-name.streamlit.app
   ```
   Replace `your-app-name` with your actual Streamlit app name.

3. **Don't add** `urn:ietf:wg:oauth:2.0:oob` - it won't work for web applications

4. Click **"SAVE"**

---

## Step 2: Update Streamlit Secrets

Add your Streamlit Cloud URL to secrets so the app knows where to redirect:

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
redirect_uri = "https://your-app-name.streamlit.app"
```

**Replace `your-app-name` with your actual Streamlit app name.**

---

## Step 3: How OAuth Flow Works Now

1. User clicks "Authenticate with Gmail"
2. App generates authorization URL with your Streamlit Cloud URL as redirect
3. User authorizes on Google
4. Google redirects back to your Streamlit app with authorization code
5. App extracts code from URL and completes authentication

---

## Alternative: Use Authorization Code in URL

The updated code will:
- Extract authorization code from the redirect URL automatically
- Handle the OAuth callback in Streamlit
- Complete authentication seamlessly

---

## Example Streamlit Cloud URLs

Your redirect URI should look like:
- `https://ai-email-agent.streamlit.app`
- `https://job-mailer.streamlit.app`
- `https://your-custom-name.streamlit.app`

**Format**: `https://[your-app-name].streamlit.app`

---

## Troubleshooting

### "redirect_uri_mismatch" error
- Make sure the URL in Google Cloud Console **exactly matches** your Streamlit app URL
- Check for typos (https vs http, trailing slashes, etc.)
- Wait a few minutes after adding (propagation delay)

### Authorization code not appearing
- Check browser console for errors
- Verify redirect URI is correct
- Make sure you're using the same Google account

### Code updated
The code has been updated to automatically handle redirect-based OAuth flow for web applications.

---

**After updating, your OAuth will work with the redirect-based flow! 🎉**

