# ✅ Fix: "Invalid Redirect: must contain a domain" Error

## Problem
Google Cloud Console doesn't accept `urn:ietf:wg:oauth:2.0:oob` for **Web application** type OAuth clients.

## Solution
Use your **Streamlit Cloud URL** as the redirect URI instead.

---

## Step 1: Add Your Streamlit Cloud URL in Google Cloud

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on your OAuth 2.0 Client ID
3. In **"Authorized redirect URIs"** section:
   - Click **"ADD URI"**
   - Add your Streamlit Cloud app URL:
     ```
     https://your-app-name.streamlit.app
     ```
   - **Replace `your-app-name` with your actual Streamlit app name**
   - Example: `https://ai-email-agent.streamlit.app`
4. Click **"SAVE"**

**Note**: Don't add `urn:ietf:wg:oauth:2.0:oob` - it won't work for web applications.

---

## Step 2: Update Streamlit Secrets (Optional)

You can optionally add your Streamlit Cloud URL to secrets for automatic detection:

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

**This is optional** - the code will try to auto-detect your Streamlit URL.

---

## Step 3: How It Works Now

Even though we use a redirect URI in Google Cloud, the authentication flow still works manually:

1. User clicks "Authenticate with Gmail"
2. App generates authorization URL
3. User clicks link and authorizes on Google
4. Google shows authorization code on the page
5. User copies the code
6. User pastes code into Streamlit app
7. Authentication completes

**The redirect URI is required by Google, but we still use manual code copy-paste flow.**

---

## Find Your Streamlit App URL

Your Streamlit Cloud app URL format is:
```
https://[your-app-name].streamlit.app
```

To find it:
1. Go to your Streamlit Cloud dashboard
2. Click on your app
3. The URL is shown at the top
4. Copy the full URL (e.g., `https://ai-email-agent.streamlit.app`)

---

## Example

If your Streamlit app URL is: `https://ai-email-agent.streamlit.app`

Then in Google Cloud Console, add:
```
https://ai-email-agent.streamlit.app
```

---

## Troubleshooting

### Still getting "Invalid Redirect" error?
- Make sure you're using **Web application** type (not Desktop app)
- The URL must start with `https://`
- No trailing slash
- Must be a valid domain

### "redirect_uri_mismatch" error?
- Make sure the URL in Google Cloud **exactly matches** your Streamlit app URL
- Check for typos
- Wait a few minutes after adding (propagation delay)

### Code not working?
- The code has been updated to handle this automatically
- Make sure you've pushed the latest code to GitHub
- Wait for Streamlit Cloud to redeploy

---

## Quick Checklist

- [ ] Found your Streamlit Cloud app URL
- [ ] Added it to Google Cloud Console as redirect URI
- [ ] Clicked SAVE in Google Cloud Console
- [ ] (Optional) Added redirect_uri to Streamlit secrets
- [ ] Waited for changes to propagate
- [ ] Tested authentication

---

**After adding your Streamlit Cloud URL, the error will be resolved! ✅**

