import os
import base64
import time
import csv
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ---------------------------------------------------
# Gmail API scope: only send emails
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# --------- CONFIGURE THESE ---------
SUBJECT = "Application for Engineer / ML Engineer Role"

BODY = """Hi Team,

I hope you’re doing well. I’m reaching out to express my interest in any Engineer / Machine Learning Engineer roles at your organization. I’ve attached my resume for your reference.

I’m currently working as an ML Engineer at ONEARVO, where I build and deploy real-world ML systems — mainly around computer vision, MLOps pipelines, and production-grade deployments on AWS. A lot of my work revolves around turning ML models into reliable products that scale in real environments.

A few highlights from my recent work:
• Built and deployed Vision Transformer (ViT) based QR-code authentication models trained on 200K+ images, achieving 97.9% accuracy.
• Designed end-to-end MLOps pipelines using AWS SageMaker, Airflow, MLflow, Docker & Kubernetes.
• Created real-time inference endpoints with optimized latency (improved by 65%).
• Implemented monitoring dashboards using Grafana & CloudWatch to track drift, performance, and reliability.

I genuinely enjoy working on applied machine learning — taking a problem, building a model, wrapping it in clean pipelines, deploying it, and ensuring it runs reliably in real-world scenarios. I’m looking for a place where I can work on impactful engineering problems, learn from the team, and contribute to meaningful products.

I would really appreciate it if you could consider my profile for any suitable positions.
Thanks a lot for your time — looking forward to hearing from you.

Warm regards,
Aviral Sharma
+91 9355319465
aviralsharma5531@gmail.com

LinkedIn: https://linkedin.com/in/aviralsharma5531
GitHub: https://github.com/aviralsharmaa
"""

RESUME_PATH = "Aviral_Sharma_Resume.pdf"   # Resume file
RECIPIENTS_FILE = "emails.txt"             # One email per line
COMPLETED_FILE = "emails_completed.txt"   # Emails that have been sent
INVALID_FILE = "emails_invalid.txt"        # Invalid/bounced emails

BATCH_SIZE = 20                            # Emails per batch
SLEEP_BETWEEN_BATCHES = 60                 # Seconds between batches
RATE_LIMIT_RETRY_DELAY = 300              # 5 minutes wait when rate limited
MAX_RATE_LIMIT_RETRIES = 3                # Max retries for rate limit errors

LOG_FILE = "mail_log.csv"                  # Excel-friendly log file
# ---------------------------------------------------


def get_gmail_service():
    """Authorize and return a Gmail API service."""
    creds = None
    # token.json stores the user's access and refresh tokens
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials, let user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for next runs
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    return service


def load_recipients(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def init_log_file():
    log_path = Path(LOG_FILE)
    if not log_path.exists():
        with log_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "email", "status", "error_message", "gmail_message_id"])


def log_result(email: str, status: str, error_message: str = "", message_id: str = ""):
    timestamp = datetime.now().isoformat(timespec="seconds")
    with Path(LOG_FILE).open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, email, status, error_message, message_id])


def move_to_completed(email: str):
    """Move an email to the completed file after successful send."""
    completed_path = Path(COMPLETED_FILE)
    with completed_path.open("a", encoding="utf-8") as f:
        f.write(email + "\n")


def move_to_invalid(email: str):
    """Move an invalid/bounced email to the invalid file."""
    invalid_path = Path(INVALID_FILE)
    with invalid_path.open("a", encoding="utf-8") as f:
        f.write(email + "\n")


def is_rate_limit_error(error_message: str) -> bool:
    """
    Check if the error is a rate limit error (429).
    These are temporary errors and should NOT be treated as invalid emails.
    """
    error_lower = str(error_message).lower()
    rate_limit_patterns = [
        "429",
        "httperror 429",
        "rate limit",
        "quota exceeded",
        "too many requests",
        "user rate limit exceeded",
    ]
    return any(pattern in error_lower for pattern in rate_limit_patterns)


def is_invalid_email_error(error_message: str) -> bool:
    """
    Check if the error indicates an invalid/non-existent email address.
    Common patterns for bounced/invalid emails:
    - "couldn't be delivered"
    - "remote server is misconfigured"
    - "does not exist"
    - "invalid recipient"
    - "address not found"
    - "no such user"
    - "mailbox unavailable"
    - "550" (common bounce code)
    - "553" (common bounce code)
    - Office 365 specific: "550 5.1.10", "RecipientNotFound"
    """
    error_lower = error_message.lower()
    
    invalid_patterns = [
        # General bounce patterns
        "couldn't be delivered",
        "could not be delivered",
        "message not delivered",
        "remote server is misconfigured",
        "does not exist",
        "invalid recipient",
        "address not found",
        "no such user",
        "mailbox unavailable",
        "user unknown",
        "recipient address rejected",
        "permanent failure",
        "hard bounce",
        
        # SMTP error codes (550, 553 are common bounce codes)
        "550",
        "553",
        "550-5.1.1",  # Gmail bounce code
        "550 5.1.1",   # Gmail bounce code
        
        # Office 365 specific patterns
        "550 5.1.10",  # Office 365 RecipientNotFound
        "550-5.1.10",  # Office 365 RecipientNotFound (with dash)
        "5.1.10",      # Office 365 error code
        "recipientnotfound",  # Office 365 error
        "recipient not found",  # Office 365 error
        "wasn't found at",  # Office 365: "user wasn't found at domain.com"
        "not found by smtp",  # Office 365: "not found by SMTP address lookup"
        "resolver.adr.recipientnotfound",  # Office 365 internal error
        "resolver.adr.recipient not found",  # Office 365 internal error
        
        # Additional patterns
        "user not found",
        "mailbox does not exist",
        "no mailbox here",
        "invalid mailbox",
    ]
    
    return any(pattern in error_lower for pattern in invalid_patterns)


def create_message(sender: str, to: str, subject: str, body_text: str, attachment_path: str):
    """Create a MIME message with optional PDF attachment."""
    message = MIMEMultipart()
    message["To"] = to
    message["From"] = sender
    message["Subject"] = subject

    # Body
    message.attach(MIMEText(body_text, "plain"))

    # Attachment
    resume_file = Path(attachment_path)
    if resume_file.exists():
        with resume_file.open("rb") as f:
            part = MIMEBase("application", "pdf")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{resume_file.name}"',
        )
        message.attach(part)
    else:
        print(f"⚠️ Resume file not found: {attachment_path} (sending without attachment)")

    # Encode to base64 for Gmail API
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw_message}


def send_message(service, user_id: str, message_body: dict):
    """Send email using Gmail API."""
    message = service.users().messages().send(userId=user_id, body=message_body).execute()
    return message  # contains id, threadId, etc.


def main():
    init_log_file()
    recipients = load_recipients(RECIPIENTS_FILE)
    print(f"Total recipients: {len(recipients)}")

    service = get_gmail_service()
    user_id = "me"

    sent_count = 0
    failed_count = 0
    invalid_count = 0
    batch_count = 0
    sent_emails = set()  # Track successfully sent emails
    invalid_emails = set()  # Track invalid/bounced emails

    for i, email in enumerate(recipients, start=1):
        try:
            mime_message = create_message(
                sender="",   # Gmail API uses authenticated user; "me" is enough
                to=email,
                subject=SUBJECT,
                body_text=BODY,
                attachment_path=RESUME_PATH,
            )

            # ---- SEND & VERIFY ----
            result = send_message(service, user_id, mime_message)
            message_id = result.get("id", "")
            status = "SENT"
            error_message = ""

            sent_count += 1
            batch_count += 1
            sent_emails.add(email)  # Track successful send
            
            # Move to completed file immediately after successful send
            move_to_completed(email)
            
            print(f"[{i}/{len(recipients)}] ✅ Sent to {email} (message id: {message_id})")

        except Exception as e:
            error_message = str(e)
            message_id = ""
            
            # Check if this is a rate limit error (temporary, should retry)
            if is_rate_limit_error(error_message):
                status = "RATE_LIMITED"
                failed_count += 1
                print(f"[{i}/{len(recipients)}] ⚠️  Rate limited: {email}")
                print(f"    Waiting {RATE_LIMIT_RETRY_DELAY // 60} minutes before continuing...")
                time.sleep(RATE_LIMIT_RETRY_DELAY)  # Wait longer for rate limit
                batch_count = 0  # Reset batch counter after rate limit wait
                
            # Check if this is an invalid email error (permanent, don't retry)
            elif is_invalid_email_error(error_message):
                status = "INVALID"
                invalid_count += 1
                invalid_emails.add(email)  # Track invalid email
                
                # Move to invalid file immediately
                move_to_invalid(email)
                
                print(f"[{i}/{len(recipients)}] 🚫 Invalid email: {email} - {error_message[:100]}")
            else:
                # Other temporary errors (network, etc.)
                status = "FAILED"
                failed_count += 1
                print(f"[{i}/{len(recipients)}] ❌ Failed to send to {email}: {error_message[:100]}")

        # Log every attempt
        log_result(email, status, error_message, message_id)

        # Batching to be safe with quotas
        if batch_count >= BATCH_SIZE:
            print(f"⏸️ Pausing {SLEEP_BETWEEN_BATCHES} seconds to avoid limits...")
            time.sleep(SLEEP_BETWEEN_BATCHES)
            batch_count = 0

    # Update emails.txt to remove successfully sent emails and invalid emails
    remaining_emails = [
        email for email in recipients 
        if email not in sent_emails and email not in invalid_emails
    ]
    
    if remaining_emails:
        print(f"\n📝 Updating {RECIPIENTS_FILE} with remaining {len(remaining_emails)} emails...")
        with Path(RECIPIENTS_FILE).open("w", encoding="utf-8") as f:
            for email in remaining_emails:
                f.write(email + "\n")
    else:
        # All emails processed, clear the file
        print(f"\n📝 All emails processed! Clearing {RECIPIENTS_FILE}...")
        Path(RECIPIENTS_FILE).write_text("", encoding="utf-8")

    print("\n" + "="*60)
    print("✅ Finished.")
    print("="*60)
    print(f"Total recipients: {len(recipients)}")
    print(f"✅ Successfully sent: {sent_count}")
    print(f"🚫 Invalid emails (moved to {INVALID_FILE}): {invalid_count}")
    print(f"❌ Failed (temporary errors - will retry): {failed_count}")
    if failed_count > 0:
        print(f"   Note: Rate limit errors (429) are temporary and will be retried on next run")
    print(f"📋 Remaining in {RECIPIENTS_FILE}: {len(remaining_emails)}")
    print(f"✅ Completed emails saved to: {COMPLETED_FILE}")
    print(f"🚫 Invalid emails saved to: {INVALID_FILE}")
    print(f"📊 Log saved to: {LOG_FILE} (open it in Excel).")
    print("="*60)


if __name__ == "__main__":
    main()
