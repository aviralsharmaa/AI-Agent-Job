"""
Cloud-compatible Gmail API module for Streamlit deployment.
Uses Streamlit secrets instead of local files.
"""

import os
import base64
import time
import csv
import shutil
import json

# Google may return granted scopes in a different order / add 'openid',
# which otherwise makes oauthlib raise a "Scope has changed" error.
os.environ.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", "1")
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow, Flow, Flow
from googleapiclient.discovery import build

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

try:
    import openpyxl
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

# Scopes: send email + read the signed-in user's email address (for display)
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/gmail.send",
]

# File paths
SENT_MAIL_FILE = "sent_mail.txt"
FAILED_MAIL_FILE = "not_sent.txt"
LOG_FILE = "mail_log.csv"
EXCEL_REPORT_FILE = "sent_mail_report.xlsx"


def get_credentials_from_secrets():
    """Get Gmail credentials from Streamlit secrets or environment variables."""
    credentials_json = None
    
    # Try Streamlit secrets first
    if STREAMLIT_AVAILABLE:
        try:
            if hasattr(st, 'secrets') and 'gmail' in st.secrets:
                credentials_json = st.secrets['gmail'].get('credentials_json')
        except Exception:
            pass
    
    # Fallback to environment variable
    if not credentials_json:
        credentials_json = os.environ.get('GMAIL_CREDENTIALS_JSON')
    
    if not credentials_json:
        raise ValueError(
            "Gmail credentials not found. Please set up Streamlit secrets or "
            "GMAIL_CREDENTIALS_JSON environment variable."
        )
    
    # Parse JSON string if it's a string
    if isinstance(credentials_json, str):
        try:
            credentials_dict = json.loads(credentials_json)
        except json.JSONDecodeError:
            # If it's already a dict in secrets, use it directly
            credentials_dict = credentials_json
    else:
        credentials_dict = credentials_json
    
    return credentials_dict


def get_gmail_service():
    """Authorize and return a Gmail API service (cloud-compatible)."""
    creds = None
    
    # Try to load token from session state (Streamlit) or file
    token_data = None
    
    if STREAMLIT_AVAILABLE:
        try:
            if 'gmail_token' in st.session_state:
                token_data = st.session_state.gmail_token
        except Exception:
            pass
    
    # Fallback to file (for local development)
    if not token_data and os.path.exists("token.json"):
        with open("token.json", "r") as f:
            token_data = json.load(f)
    
    # Load credentials from token if available
    if token_data:
        try:
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        except Exception:
            creds = None
    
    # If no valid credentials, need to authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save refreshed token
                if STREAMLIT_AVAILABLE:
                    st.session_state.gmail_token = json.loads(creds.to_json())
                else:
                    with open("token.json", "w") as token:
                        token.write(creds.to_json())
            except RefreshError:
                # Token expired, need to re-authenticate
                creds = None
        
        if not creds:
            # Need to start OAuth flow
            # This will be handled in the Streamlit interface
            raise ValueError(
                "Not authenticated. Please click 'Authenticate with Gmail' button."
            )
    
    service = build("gmail", "v1", credentials=creds)
    return service


def authenticate_gmail_flow():
    """
    Start OAuth flow for Gmail authentication.
    Returns credentials object.
    For cloud deployment, this should be called from Streamlit interface.
    """
    credentials_dict = get_credentials_from_secrets()
    
    # Determine if credentials are "web" or "installed" type
    if "web" in credentials_dict:
        client_config = {"web": credentials_dict["web"]}
        
        # For web applications, we need a valid URL redirect URI
        # But we'll still use manual code flow (user copies code from page)
        # Use the Streamlit Cloud URL from secrets, or construct it
        redirect_uri = None
        if STREAMLIT_AVAILABLE:
            try:
                # Try to get from secrets first
                if hasattr(st, 'secrets') and 'gmail' in st.secrets:
                    redirect_uri = st.secrets['gmail'].get('redirect_uri')
                
                # Try environment variable
                if not redirect_uri:
                    redirect_uri = os.environ.get('STREAMLIT_APP_URL')
                
                # Fallback: try to get from Streamlit's config
                if not redirect_uri:
                    try:
                        # Streamlit Cloud sets this automatically
                        redirect_uri = os.environ.get('STREAMLIT_SERVER_BASE_URL_PATH', '')
                        if redirect_uri:
                            # Construct full URL
                            redirect_uri = f"https://{os.environ.get('STREAMLIT_SERVER_HOST', '')}{redirect_uri}"
                    except:
                        pass
                
                # Final fallback: use Streamlit Cloud URL
                if not redirect_uri:
                    redirect_uri = 'https://ai-agent-job.streamlit.app'
            except:
                redirect_uri = 'https://ai-agent-job.streamlit.app'
        else:
            redirect_uri = 'https://ai-agent-job.streamlit.app'
        
        # Use Flow for web applications
        # Note: Even with redirect URI, user will copy code manually
        # autogenerate_code_verifier=False disables PKCE. PKCE's code_verifier
        # is lost when Google redirects back (Streamlit starts a fresh session),
        # which would cause "Missing code verifier" on token exchange. A web
        # client authenticates with its client_secret, so PKCE is not required.
        flow = Flow.from_client_config(
            client_config,
            SCOPES,
            redirect_uri=redirect_uri,
            autogenerate_code_verifier=False
        )
    else:
        # Fallback to installed app flow
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(credentials_dict, f)
            temp_credentials_path = f.name
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                temp_credentials_path, SCOPES
            )
        finally:
            if os.path.exists(temp_credentials_path):
                os.remove(temp_credentials_path)
    
    # Generate authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    # Store state in session for verification
    if STREAMLIT_AVAILABLE:
        st.session_state.oauth_state = state
        st.session_state.oauth_flow = flow
        return authorization_url
    else:
        # For non-Streamlit environments, print URL
        print(f"Please visit this URL to authorize the application: {authorization_url}")
        authorization_code = input("Enter the authorization code: ")
        flow.fetch_token(code=authorization_code)
        return flow.credentials


def authenticate_gmail_with_url():
    """
    Get authorization URL for OAuth flow.
    Returns (authorization_url, state) tuple.
    """
    credentials_dict = get_credentials_from_secrets()
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(credentials_dict, f)
        temp_credentials_path = f.name
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            temp_credentials_path, SCOPES
        )
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'  # For manual copy-paste
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        return authorization_url, state, temp_credentials_path
    except Exception as e:
        if os.path.exists(temp_credentials_path):
            os.remove(temp_credentials_path)
        raise e


def complete_gmail_auth(authorization_code):
    """Complete OAuth flow with authorization code."""
    if not STREAMLIT_AVAILABLE:
        raise ValueError("This function requires Streamlit")
    
    # If flow is not in session state (page reloaded), recreate it
    if 'oauth_flow' not in st.session_state:
        credentials_dict = get_credentials_from_secrets()
        
        # Determine if credentials are "web" or "installed" type
        if "web" in credentials_dict:
            client_config = {"web": credentials_dict["web"]}
            
            # Get redirect URI from secrets or use default
            redirect_uri = None
            try:
                if hasattr(st, 'secrets') and 'gmail' in st.secrets:
                    redirect_uri = st.secrets['gmail'].get('redirect_uri')
                if not redirect_uri:
                    redirect_uri = os.environ.get('STREAMLIT_APP_URL')
                if not redirect_uri:
                    redirect_uri = 'https://ai-agent-job.streamlit.app'
            except:
                redirect_uri = 'https://ai-agent-job.streamlit.app'
            
            flow = Flow.from_client_config(
                client_config,
                SCOPES,
                redirect_uri=redirect_uri,
                autogenerate_code_verifier=False
            )
        else:
            # Fallback to installed app flow
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(credentials_dict, f)
                temp_credentials_path = f.name

            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    temp_credentials_path, SCOPES
                )
            finally:
                if os.path.exists(temp_credentials_path):
                    os.remove(temp_credentials_path)
    else:
        flow = st.session_state.oauth_flow
    
    try:
        flow.fetch_token(code=authorization_code)
        creds = flow.credentials
        
        # Save token
        st.session_state.gmail_token = json.loads(creds.to_json())
        
        # Clean up
        if 'oauth_state' in st.session_state:
            del st.session_state.oauth_state
        if 'oauth_flow' in st.session_state:
            del st.session_state.oauth_flow
        
        return creds
    except Exception as e:
        # Clean up on error
        if 'oauth_state' in st.session_state:
            del st.session_state.oauth_state
        if 'oauth_flow' in st.session_state:
            del st.session_state.oauth_flow
        raise e


def init_log_file():
    """Initialize log file with headers."""
    log_path = Path(LOG_FILE)
    if not log_path.exists():
        with log_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "email", "status", "error_message", "gmail_message_id"])


def log_result(email: str, status: str, error_message: str = "", message_id: str = ""):
    """Log email sending result to CSV file."""
    timestamp = datetime.now().isoformat(timespec="seconds")
    with Path(LOG_FILE).open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, email, status, error_message, message_id])


def move_to_sent_mail(email: str):
    """Move an email to the sent_mail.txt file after successful send."""
    sent_path = Path(SENT_MAIL_FILE)
    existing_emails = set()
    if sent_path.exists():
        with sent_path.open("r", encoding="utf-8") as f:
            existing_emails = {line.strip() for line in f if line.strip()}
    
    if email not in existing_emails:
        with sent_path.open("a", encoding="utf-8") as f:
            f.write(email + "\n")


def move_to_failed_mail(email: str, error_reason: str = ""):
    """Move an email to the not_sent.txt file after delivery failure."""
    failed_path = Path(FAILED_MAIL_FILE)
    existing_emails = set()
    if failed_path.exists():
        with failed_path.open("r", encoding="utf-8") as f:
            existing_emails = {line.strip().split(" | ")[0] for line in f if line.strip()}
    
    if email not in existing_emails:
        with failed_path.open("a", encoding="utf-8") as f:
            if error_reason:
                f.write(f"{email} | {error_reason}\n")
            else:
                f.write(f"{email}\n")


def is_rate_limit_error(error_message: str) -> bool:
    """Check if the error is a rate limit error (429)."""
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


def is_delivery_failure_error(error_message: str) -> bool:
    """Check if the error indicates delivery failure."""
    error_lower = str(error_message).lower()
    delivery_failure_patterns = [
        "address not found",
        "mailbox does not exist",
        "invalid email address",
        "invalid recipient",
        "recipient address rejected",
        "user unknown",
        "no such user",
        "mailbox unavailable",
        "550",
        "551",
        "553",
        "invalid recipient address",
        "delivery has failed",
        "delivery status notification",
        "mail delivery subsystem",
        "permanent failure",
    ]
    return any(pattern in error_lower for pattern in delivery_failure_patterns)


def create_message(sender: str, to: str, subject: str, body_text: str, attachment_path: str = None):
    """Create a MIME message with optional attachment."""
    message = MIMEMultipart()
    message["To"] = to
    message["From"] = sender
    message["Subject"] = subject

    # Body
    message.attach(MIMEText(body_text, "plain"))

    # Attachment
    if attachment_path:
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

    # Encode to base64 for Gmail API
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw_message}


def send_message(service, user_id: str, message_body: dict):
    """Send email using Gmail API."""
    message = service.users().messages().send(userId=user_id, body=message_body).execute()
    return message

