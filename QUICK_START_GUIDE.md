# AI Email Agent - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Setup Gmail API

1. Download `credentials.json` from Google Cloud Console
2. Place it in the project directory
3. Enable Gmail API in your Google Cloud project

### Step 3: Prepare Email Database

Create `emails_from_excel.txt` with one email per line:
```
email1@company.com
email2@company.com
email3@company.com
```

### Step 4: Run the Agent

**Web Interface (Recommended):**
```bash
streamlit run email_agent_streamlit.py
```

**CLI Interface:**
```bash
python email_agent_cli.py
```

### Step 5: Send Your First Email

**In Web Interface:**
1. Click "Authenticate with Gmail"
2. Enter: `Send a mail to microsoft`
3. Fill subject and body
4. Upload resume (optional)
5. Click "Send Emails"
6. Confirm and send!

**In CLI:**
```
🤖 Agent> Send a mail to microsoft with subject 'Job Application' and body 'I am interested...'
```

## 📝 Common Commands

| Command | Description |
|---------|-------------|
| `Send a mail to [company]` | Send email to company |
| `list companies` | Show all available companies |
| `help` | Show help message |
| `exit` | Exit the agent |

## 💡 Tips

1. **Company Names**: Use simple names (e.g., "microsoft" not "Microsoft Corporation")
2. **Preview First**: Always review the preview before sending
3. **Start Small**: Test with 1-2 emails first
4. **Check Logs**: Review `sent_mail.txt` and `not_sent.txt` regularly

## ❓ Need Help?

- See `AI_AGENT_DOCUMENTATION.md` for detailed documentation
- Check troubleshooting section
- Review error messages in console

---

**That's it! You're ready to send emails! 🎉**
