# Quick Start Guide - AI Email Agent CLI

## 🚀 Get Started in 3 Steps

### Step 1: Run the Agent
```bash
python email_agent_cli.py
```

### Step 2: Try a Simple Command
```
🤖 Agent> Send a mail to microsoft with subject 'Job Application' and body 'I am interested in working at Microsoft'
```

### Step 3: Confirm and Send
The agent will:
1. Find all Microsoft emails
2. Show you the details
3. Ask for confirmation
4. Send the emails

## 📝 Common Use Cases

### Send to a Company
```
Send email to google with subject 'Software Engineer' and body 'Hello, I am applying...'
```

### Add Attachments
```
Send mail to amazon with attachments resume.pdf cover_letter.pdf
```

### Multi-line Body (Interactive)
```
Send email to microsoft with subject 'Application'
[Then type your message, press Enter after each line, type END when done]
```

### List Available Companies
```
list companies
```

## 💡 Pro Tips

1. **Company names are case-insensitive**: "microsoft", "Microsoft", "MICROSOFT" all work
2. **File attachments**: Place files in the same folder as the script
3. **Multi-line text**: Type `END` on a new line to finish, `CANCEL` to abort
4. **Always review**: The agent shows you everything before sending

## ❓ Need Help?

Type `help` in the agent for detailed instructions.

---

**That's it! You're ready to send emails! 🎉**
