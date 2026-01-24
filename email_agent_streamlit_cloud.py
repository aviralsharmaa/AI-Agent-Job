#!/usr/bin/env python3
"""
Streamlit Web Interface for AI Email Agent - Cloud Deployment Version
Optimized for deployment on Streamlit Cloud, Render, Railway, etc.
"""

import streamlit as st
import re
import os
from pathlib import Path
from typing import List, Dict, Optional
import base64
from datetime import datetime
import json
from urllib.parse import parse_qs, urlparse
from googleapiclient.discovery import build

# Import cloud-compatible Gmail API module
from send_mails_gmail_api_cloud import (
    get_gmail_service,
    authenticate_gmail_flow,
    complete_gmail_auth,
    log_result,
    init_log_file,
    move_to_sent_mail,
    move_to_failed_mail,
    is_rate_limit_error,
    is_delivery_failure_error,
    SENT_MAIL_FILE,
    FAILED_MAIL_FILE,
    LOG_FILE,
)

# Configuration
RECIPIENTS_FILE = "emails_from_excel.txt"
PERSONAL_EMAIL_DOMAINS = ["gmail.com", "outlook.com", "yahoo.com", "hotmail.com", "icloud.com", "protonmail.com"]

# Page configuration
st.set_page_config(
    page_title="AI Email Agent",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_emails():
    """Load all emails from the recipients file."""
    if not Path(RECIPIENTS_FILE).exists():
        return []
    
    with open(RECIPIENTS_FILE, "r", encoding="utf-8") as f:
        emails = [line.strip() for line in f if line.strip()]
    
    return emails


def extract_company_name(prompt: str) -> Optional[str]:
    """Extract company name from prompt."""
    patterns = [
        r"(?:all\s+)?([a-zA-Z0-9]+)\s+(?:mails?|emails?|mail\s+id|email\s+id)",
        r"to\s+(?:all\s+)?([a-zA-Z0-9]+)",
        r"send\s+(?:a\s+)?(?:mail|email)\s+to\s+(?:all\s+)?([a-zA-Z0-9]+)",
        r"([a-zA-Z0-9]+)\s+(?:employees|company|team|people)",
        r"company\s+([a-zA-Z0-9]+)",
    ]
    
    prompt_lower = prompt.lower()
    for pattern in patterns:
        match = re.search(pattern, prompt_lower, re.IGNORECASE)
        if match:
            company = match.group(1).strip()
            if company not in ["a", "an", "the", "mail", "email", "send", "all"]:
                return company
    
    return None


def find_company_emails(company_name: str, all_emails: List[str]) -> List[str]:
    """Find emails associated with a company."""
    if not company_name:
        return []
    
    company_lower = company_name.lower().strip()
    matching_emails = []
    
    if company_lower == "all":
        for email in all_emails:
            if "@" not in email:
                continue
            domain = email.split("@")[1].lower()
            if domain not in PERSONAL_EMAIL_DOMAINS:
                matching_emails.append(email)
        return matching_emails
    
    for email in all_emails:
        email_lower = email.lower()
        
        if "@" not in email:
            continue
        
        domain = email.split("@")[1].lower()
        
        if domain in PERSONAL_EMAIL_DOMAINS:
            continue
        
        domain_parts = domain.split(".")
        main_domain = domain_parts[0] if domain_parts else ""
        
        if main_domain == company_lower:
            matching_emails.append(email)
    
    # Remove duplicates
    seen = set()
    unique_emails = []
    for email in matching_emails:
        if email not in seen:
            seen.add(email)
            unique_emails.append(email)
    
    return unique_emails


def create_message_with_attachments(to: str, subject: str, body: str, attachment_paths: List[str]):
    """Create email message with multiple attachments."""
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email import encoders
    
    message = MIMEMultipart()
    message["To"] = to
    message["From"] = ""
    message["Subject"] = subject
    
    message.attach(MIMEText(body, "plain"))
    
    for attachment_path in attachment_paths:
        file_path = Path(attachment_path)
        if file_path.exists():
            try:
                with file_path.open("rb") as f:
                    suffix = file_path.suffix.lower()
                    if suffix == ".pdf":
                        main_type, sub_type = "application", "pdf"
                    elif suffix in [".doc", ".docx"]:
                        main_type, sub_type = "application", "msword"
                    elif suffix == ".txt":
                        main_type, sub_type = "text", "plain"
                    elif suffix in [".jpg", ".jpeg"]:
                        main_type, sub_type = "image", "jpeg"
                    elif suffix == ".png":
                        main_type, sub_type = "image", "png"
                    else:
                        main_type, sub_type = "application", "octet-stream"
                    
                    part = MIMEBase(main_type, sub_type)
                    part.set_payload(f.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{file_path.name}"',
                )
                message.attach(part)
            except Exception as e:
                st.error(f"Error attaching {file_path.name}: {e}")
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw_message}


def send_emails(service, emails: List[str], subject: str, body: str, attachment_paths: List[str], progress_bar, status_text):
    """Send emails to the list of recipients."""
    sent_count = 0
    failed_count = 0
    user_id = "me"
    
    total = len(emails)
    
    for i, email in enumerate(emails, 1):
        try:
            if attachment_paths:
                message_body = create_message_with_attachments(email, subject, body, attachment_paths)
            else:
                from email.mime.text import MIMEText
                message = MIMEText(body, "plain")
                message["To"] = email
                message["From"] = ""
                message["Subject"] = subject
                raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
                message_body = {"raw": raw_message}
            
            result = service.users().messages().send(userId=user_id, body=message_body).execute()
            message_id = result.get("id", "")
            
            sent_count += 1
            move_to_sent_mail(email)
            log_result(email, "SENT", "", message_id)
            
            progress_bar.progress(i / total)
            status_text.text(f"✅ Sent to {email} ({i}/{total})")
            
        except Exception as e:
            error_message = str(e)
            failed_count += 1
            
            if is_delivery_failure_error(error_message):
                move_to_failed_mail(email, error_message[:100])
                log_result(email, "DELIVERY_FAILED", error_message[:200], "")
            else:
                log_result(email, "FAILED", error_message[:200], "")
            
            progress_bar.progress(i / total)
            status_text.text(f"❌ Failed: {email} - {error_message[:100]}")
    
    return sent_count, failed_count


def get_available_companies(all_emails: List[str]) -> List[str]:
    """Get list of available companies from email database."""
    companies = set()
    
    for email in all_emails:
        if "@" not in email:
            continue
        
        domain = email.split("@")[1].lower()
        
        if domain in PERSONAL_EMAIL_DOMAINS:
            continue
        
        domain_parts = domain.split(".")
        if domain_parts:
            company = domain_parts[0].capitalize()
            companies.add(company)
    
    return sorted(companies)


def main():
    # Initialize session state
    if 'gmail_service' not in st.session_state:
        st.session_state.gmail_service = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'email_preview_data' not in st.session_state:
        st.session_state.email_preview_data = None
    if 'sending_emails' not in st.session_state:
        st.session_state.sending_emails = False
    if 'auth_in_progress' not in st.session_state:
        st.session_state.auth_in_progress = False
    
    # Header
    st.markdown('<div class="main-header">📧 AI Email Agent</div>', unsafe_allow_html=True)
    st.markdown("### Intelligent Email Sending Assistant - Cloud Edition")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Authentication
        if not st.session_state.authenticated:
            # Check if we have authorization code in URL (OAuth callback)
            query_params = st.query_params
            if 'code' in query_params and 'state' in query_params:
                # We have the authorization code from OAuth callback
                auth_code = query_params['code']
                try:
                    with st.spinner("Completing authentication..."):
                        if complete_gmail_auth:
                            creds = complete_gmail_auth(auth_code)
                            st.session_state.gmail_service = build("gmail", "v1", credentials=creds)
                            st.session_state.authenticated = True
                            # Clear OAuth state
                            if 'oauth_authorization_url' in st.session_state:
                                del st.session_state.oauth_authorization_url
                            if 'oauth_flow' in st.session_state:
                                del st.session_state.oauth_flow
                            # Clear URL parameters
                            st.query_params.clear()
                            st.success("✅ Authenticated successfully!")
                            st.rerun()
                        else:
                            st.error("Authentication function not available")
                except Exception as e:
                    st.error(f"❌ Authentication failed: {e}")
                    import traceback
                    with st.expander("Error Details"):
                        st.code(traceback.format_exc())
                    # Clear URL parameters on error
                    st.query_params.clear()
            
            st.info("🔐 Please authenticate with Gmail to start sending emails.")
            
            # Check if we're in the middle of OAuth flow
            if 'oauth_authorization_url' in st.session_state:
                st.markdown("### Step 2: Enter Authorization Code")
                st.info("1. Click the link below to authorize")
                st.markdown(f"[🔗 Authorize with Google]({st.session_state.oauth_authorization_url})")
                st.info("2. After authorizing, copy the authorization code from the page")
                
                auth_code = st.text_input("Enter authorization code:", type="default", help="Paste the code you received after authorizing")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Complete Authentication", type="primary"):
                        if auth_code:
                            try:
                                with st.spinner("Completing authentication..."):
                                    if complete_gmail_auth:
                                        creds = complete_gmail_auth(auth_code)
                                        st.session_state.gmail_service = build("gmail", "v1", credentials=creds)
                                        st.session_state.authenticated = True
                                        if 'oauth_authorization_url' in st.session_state:
                                            del st.session_state.oauth_authorization_url
                                        st.success("✅ Authenticated successfully!")
                                        st.rerun()
                                    else:
                                        st.error("Authentication function not available")
                            except Exception as e:
                                st.error(f"❌ Authentication failed: {e}")
                        else:
                            st.warning("Please enter the authorization code")
                
                with col2:
                    if st.button("🔄 Cancel"):
                        if 'oauth_authorization_url' in st.session_state:
                            del st.session_state.oauth_authorization_url
                        if 'oauth_flow' in st.session_state:
                            del st.session_state.oauth_flow
                        st.rerun()
            else:
                # Initial authentication button
                if st.button("🔑 Authenticate with Gmail", type="primary"):
                    try:
                        with st.spinner("Starting authentication..."):
                            # Try to get existing service first
                            try:
                                st.session_state.gmail_service = get_gmail_service()
                                st.session_state.authenticated = True
                                st.success("✅ Authenticated successfully!")
                                st.rerun()
                            except ValueError as e:
                                # Need to start OAuth flow
                                if authenticate_gmail_flow:
                                    auth_url = authenticate_gmail_flow()
                                    if auth_url:
                                        st.session_state.oauth_authorization_url = auth_url
                                        st.rerun()
                                    else:
                                        st.error("Failed to generate authorization URL")
                                else:
                                    st.error("Authentication function not available")
                    except Exception as e:
                        st.error(f"❌ Authentication failed: {e}")
                        st.info("💡 Make sure Gmail credentials are configured in Streamlit secrets or environment variables.")
                        import traceback
                        with st.expander("Error Details"):
                            st.code(traceback.format_exc())
        else:
            st.success("✅ Authenticated with Gmail")
            if st.button("🔓 Disconnect"):
                st.session_state.authenticated = False
                st.session_state.gmail_service = None
                if 'gmail_token' in st.session_state:
                    del st.session_state.gmail_token
                st.rerun()
        
        st.divider()
        
        # Email database upload
        st.subheader("📊 Email Database")
        uploaded_email_file = st.file_uploader(
            "Upload Email Database (emails_from_excel.txt)",
            type=['txt'],
            help="Upload your email database file (one email per line)"
        )
        
        if uploaded_email_file:
            # Save uploaded file
            with open(RECIPIENTS_FILE, "wb") as f:
                f.write(uploaded_email_file.getbuffer())
            st.success("✅ Email database uploaded!")
            st.cache_data.clear()  # Clear cache to reload emails
        
        # Load emails
        with st.spinner("Loading email database..."):
            all_emails = load_emails()
        
        st.metric("📊 Total Emails", len(all_emails))
        
        if len(all_emails) == 0:
            st.warning("⚠️ No emails loaded. Please upload email database file.")
        
        # Show available companies
        if st.button("📋 Show Available Companies"):
            companies = get_available_companies(all_emails)
            st.write(f"**Found {len(companies)} companies:**")
            
            with st.expander("View All Companies", expanded=True):
                cols = st.columns(4)
                for i, company in enumerate(companies):
                    cols[i % 4].write(f"• {company}")
        
        st.divider()
        st.caption("💡 Tip: Use natural language prompts like 'Send a mail to microsoft'")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Compose Email")
        
        # Prompt input
        prompt = st.text_area(
            "🤖 Enter your prompt:",
            placeholder="Example: Send a mail to microsoft\nOr: Send email to apple company",
            height=100,
            help="Enter a natural language prompt to find and send emails to a company"
        )
        
        # Manual input fields
        with st.expander("📋 Manual Input Fields (Optional)", expanded=False):
            st.write("Fill these fields manually or let the agent extract from your prompt")
            
            col_subject, col_body = st.columns(2)
            
            with col_subject:
                manual_subject = st.text_input(
                    "📌 Subject:",
                    placeholder="Job Application",
                    help="Email subject line"
                )
            
            with col_body:
                manual_body = st.text_area(
                    "💬 Body:",
                    placeholder="Enter your email body here...",
                    height=200,
                    help="Email body content"
                )
        
        # File uploader
        st.subheader("📎 Attachments")
        uploaded_files = st.file_uploader(
            "Upload Resume/CV/Cover Letter:",
            type=['pdf', 'doc', 'docx', 'txt'],
            accept_multiple_files=True,
            help="Upload your resume, CV, or cover letter"
        )
        
        # Process button
        if st.session_state.email_preview_data is None:
            if st.button("🚀 Send Emails", type="primary", use_container_width=True):
                if not st.session_state.authenticated:
                    st.error("❌ Please authenticate with Gmail first (check sidebar)")
                    return
                
                if not prompt.strip():
                    st.error("❌ Please enter a prompt (e.g., 'Send a mail to microsoft')")
                    return
                
                if len(all_emails) == 0:
                    st.error("❌ Please upload email database file first (check sidebar)")
                    return
                
                # Extract company name
                company_name = extract_company_name(prompt)
                
                if not company_name:
                    st.error("❌ Could not extract company name from prompt. Please include company name (e.g., 'microsoft', 'apple')")
                    return
                
                # Find company emails
                with st.spinner(f"🔎 Searching for emails associated with '{company_name}'..."):
                    company_emails = find_company_emails(company_name, all_emails)
                
                if not company_emails:
                    st.warning(f"❌ No emails found for company '{company_name}'. Try a different company name.")
                    return
                
                # Determine subject and body
                subject = manual_subject.strip() if manual_subject.strip() else "Job Application"
                body = manual_body.strip() if manual_body.strip() else prompt
                
                # Save uploaded files
                attachment_paths = []
                if uploaded_files:
                    upload_dir = Path("uploads")
                    upload_dir.mkdir(exist_ok=True)
                    
                    for uploaded_file in uploaded_files:
                        file_path = upload_dir / uploaded_file.name
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        attachment_paths.append(str(file_path))
                
                # Store preview data
                st.session_state.email_preview_data = {
                    'company_name': company_name,
                    'company_emails': company_emails,
                    'subject': subject,
                    'body': body,
                    'attachment_paths': attachment_paths
                }
                st.rerun()
        else:
            # Show preview
            preview_data = st.session_state.email_preview_data
            company_name = preview_data['company_name']
            company_emails = preview_data['company_emails']
            subject = preview_data['subject']
            body = preview_data['body']
            attachment_paths = preview_data['attachment_paths']
            
            st.divider()
            st.subheader("📋 Email Preview")
            
            preview_col1, preview_col2 = st.columns(2)
            
            with preview_col1:
                st.write(f"**Company:** {company_name}")
                st.write(f"**Subject:** {subject}")
                st.write(f"**Recipients:** {len(company_emails)}")
                if attachment_paths:
                    st.write(f"**Attachments:** {', '.join([Path(p).name for p in attachment_paths])}")
            
            with preview_col2:
                st.write("**Recipients:**")
                with st.container():
                    recipient_text = "\n".join([f"• {email}" for email in company_emails])
                    st.text_area("", recipient_text, height=200, disabled=True, label_visibility="collapsed")
            
            st.write("**Body Preview:**")
            st.text_area("Email Body Preview", body[:500] + "..." if len(body) > 500 else body, height=150, disabled=True, label_visibility="visible")
            
            # Confirmation
            st.divider()
            col_confirm, col_clear = st.columns([3, 1])
            
            with col_confirm:
                confirm = st.checkbox("✅ I confirm I want to send these emails", value=False)
            
            with col_clear:
                if st.button("🔄 Clear Preview"):
                    st.session_state.email_preview_data = None
                    st.session_state.sending_emails = False
                    st.rerun()
            
            if confirm and not st.session_state.sending_emails:
                st.session_state.sending_emails = True
                st.rerun()
            
            if st.session_state.sending_emails:
                # Send emails
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    if st.session_state.gmail_service is None:
                        st.error("❌ Gmail service not available. Please re-authenticate.")
                        st.session_state.sending_emails = False
                        st.session_state.email_preview_data = None
                        return
                    
                    with st.spinner("📧 Sending emails..."):
                        sent, failed = send_emails(
                            st.session_state.gmail_service,
                            company_emails,
                            subject,
                            body,
                            attachment_paths,
                            progress_bar,
                            status_text
                        )
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.success(f"✅ Successfully sent: {sent} emails")
                    if failed > 0:
                        st.warning(f"⚠️ Failed: {failed} emails")
                    
                    st.balloons()
                    
                    st.session_state.email_preview_data = None
                    st.session_state.sending_emails = False
                except Exception as e:
                    import traceback
                    st.error(f"❌ Error sending emails: {e}")
                    with st.expander("Error Details"):
                        st.code(traceback.format_exc())
                    st.session_state.sending_emails = False
            elif not confirm:
                st.info("👆 Please confirm to send emails")
    
    with col2:
        st.header("📖 Quick Guide")
        
        st.markdown("""
        ### How to Use:
        
        1. **Upload Email Database** (sidebar)
        
        2. **Authenticate** with Gmail (sidebar)
        
        3. **Enter a prompt** like:
           - "Send a mail to microsoft"
           - "Send email to apple company"
        
        4. **Fill optional fields:**
           - Subject
           - Body
           - Upload attachments
        
        5. **Review preview** and confirm
        
        6. **Click Send** 🚀
        
        ### Tips:
        - Company names are case-insensitive
        - Only company emails are sent
        - You can upload multiple files
        - Always review before sending
        """)
        
        st.divider()
        
        # Statistics
        st.subheader("📊 Statistics")
        
        if Path(SENT_MAIL_FILE).exists():
            with open(SENT_MAIL_FILE, "r") as f:
                sent_count = len([line for line in f if line.strip()])
            st.metric("✅ Sent Emails", sent_count)
        
        if Path(FAILED_MAIL_FILE).exists():
            with open(FAILED_MAIL_FILE, "r") as f:
                failed_count = len([line for line in f if line.strip()])
            st.metric("❌ Failed Emails", failed_count)
        
        st.metric("📧 Total in Database", len(all_emails))
    
    # Footer
    st.divider()
    st.caption("💡 Powered by Streamlit | Gmail API | AI Email Agent | Cloud Edition")
    st.caption("📁 Logs: mail_log.csv | Sent: sent_mail.txt | Failed: not_sent.txt")


if __name__ == "__main__":
    init_log_file()
    main()

