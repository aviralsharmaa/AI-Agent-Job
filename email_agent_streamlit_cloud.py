#!/usr/bin/env python3
"""
Streamlit Web Interface for AI Email Agent - Cloud Deployment Version
Simple edition: enter a subject + body, attach your resume, and send to the
next batch of emails from your dataset.

Rules:
- Each user (identified by their Gmail address) can send up to 200 emails
  per rolling 24-hour window.
- Every send goes to the NEXT unsent emails in the dataset, so after the
  24-hour window resets you automatically continue with new recipients.
- Per-user progress (sent / failed / remaining) is tracked and shown.
"""

import streamlit as st
import os
import json
from pathlib import Path
from typing import List, Tuple
import base64
from datetime import datetime, timedelta
from googleapiclient.discovery import build

# AI assistant (Groq)
from ai_assistant import (
    ai_available,
    extract_pdf_text,
    analyze_resume,
    body_from_description,
    improve_text,
)

# Import cloud-compatible Gmail API module
from send_mails_gmail_api_cloud import (
    get_gmail_service,
    authenticate_gmail_flow,
    complete_gmail_auth,
    log_result,
    init_log_file,
    move_to_sent_mail,
    move_to_failed_mail,
    is_delivery_failure_error,
    SENT_MAIL_FILE,
    FAILED_MAIL_FILE,
)

# Configuration
RECIPIENTS_FILE = "emails_from_excel.txt"
PROGRESS_FILE = "user_progress.json"
DAILY_LIMIT = 200          # max emails a user may send per 24h window
WINDOW_HOURS = 24

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
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# Email dataset
# --------------------------------------------------------------------------- #
@st.cache_data
def load_emails() -> List[str]:
    """Load all emails from the recipients file (one per line, de-duplicated)."""
    if not Path(RECIPIENTS_FILE).exists():
        return []

    seen = set()
    emails = []
    with open(RECIPIENTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            email = line.strip()
            if email and "@" in email and email not in seen:
                seen.add(email)
                emails.append(email)
    return emails


# --------------------------------------------------------------------------- #
# Per-user progress tracking
# --------------------------------------------------------------------------- #
def _load_progress() -> dict:
    if Path(PROGRESS_FILE).exists():
        try:
            return json.loads(Path(PROGRESS_FILE).read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_progress(data: dict) -> None:
    Path(PROGRESS_FILE).write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_user_record(email: str) -> dict:
    """Return this user's record, resetting the window if it has expired."""
    data = _load_progress()
    record = data.get(email, {
        "sent_emails": [],
        "failed_emails": [],
        "window_start": None,
        "sent_in_window": 0,
    })
    # Reset the 24h window if it has elapsed
    ws = record.get("window_start")
    if ws:
        try:
            if datetime.now() - datetime.fromisoformat(ws) >= timedelta(hours=WINDOW_HOURS):
                record["window_start"] = None
                record["sent_in_window"] = 0
        except Exception:
            record["window_start"] = None
            record["sent_in_window"] = 0
    return record


def save_user_record(email: str, record: dict) -> None:
    data = _load_progress()
    data[email] = record
    _save_progress(data)


def quota_remaining(record: dict) -> int:
    return max(0, DAILY_LIMIT - record.get("sent_in_window", 0))


def time_until_reset(record: dict):
    ws = record.get("window_start")
    if not ws:
        return None
    try:
        reset_at = datetime.fromisoformat(ws) + timedelta(hours=WINDOW_HOURS)
    except Exception:
        return None
    delta = reset_at - datetime.now()
    return delta if delta.total_seconds() > 0 else None


def format_timedelta(delta: timedelta) -> str:
    total = int(delta.total_seconds())
    hours, rem = divmod(total, 3600)
    minutes = rem // 60
    return f"{hours}h {minutes}m"


def get_next_batch(all_emails: List[str], processed: set, limit: int) -> List[str]:
    """Return up to `limit` emails from the dataset that have not been processed."""
    batch = []
    for email in all_emails:
        if email not in processed:
            batch.append(email)
            if len(batch) >= limit:
                break
    return batch


# --------------------------------------------------------------------------- #
# Email building / sending
# --------------------------------------------------------------------------- #
def create_message_with_attachments(to: str, subject: str, body: str, attachment_paths: List[str]) -> dict:
    """Create an email message with optional attachments."""
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email import encoders

    if attachment_paths:
        message = MIMEMultipart()
        message["To"] = to
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        for attachment_path in attachment_paths:
            file_path = Path(attachment_path)
            if not file_path.exists():
                continue
            suffix = file_path.suffix.lower()
            if suffix == ".pdf":
                main_type, sub_type = "application", "pdf"
            elif suffix in [".doc", ".docx"]:
                main_type, sub_type = "application", "msword"
            elif suffix == ".txt":
                main_type, sub_type = "text", "plain"
            else:
                main_type, sub_type = "application", "octet-stream"

            with file_path.open("rb") as f:
                part = MIMEBase(main_type, sub_type)
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{file_path.name}"')
            message.attach(part)
    else:
        message = MIMEText(body, "plain")
        message["To"] = to
        message["Subject"] = subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw_message}


def send_emails(service, emails: List[str], subject: str, body: str,
                attachment_paths: List[str], progress_bar, status_text) -> Tuple[List[str], List[str]]:
    """Send emails to a list of recipients. Returns (sent_list, failed_list)."""
    sent_list: List[str] = []
    failed_list: List[str] = []
    total = len(emails)

    for i, email in enumerate(emails, 1):
        try:
            message_body = create_message_with_attachments(email, subject, body, attachment_paths)
            result = service.users().messages().send(userId="me", body=message_body).execute()
            message_id = result.get("id", "")

            sent_list.append(email)
            move_to_sent_mail(email)
            log_result(email, "SENT", "", message_id)

            progress_bar.progress(i / total)
            status_text.text(f"✅ Sent to {email} ({i}/{total})")
        except Exception as e:
            error_message = str(e)
            failed_list.append(email)
            if is_delivery_failure_error(error_message):
                move_to_failed_mail(email, error_message[:100])
                log_result(email, "DELIVERY_FAILED", error_message[:200], "")
            else:
                log_result(email, "FAILED", error_message[:200], "")
            progress_bar.progress(i / total)
            status_text.text(f"❌ Failed: {email} - {error_message[:80]}")

    return sent_list, failed_list


# --------------------------------------------------------------------------- #
# AI button callbacks (run before widgets are re-instantiated, so they can
# safely set the subject/body widget state)
# --------------------------------------------------------------------------- #
def _cb_generate_body():
    desc = st.session_state.get("desc_input", "").strip()
    if not desc:
        st.session_state._ai_msg = ("warning", "✍️ Describe your message first.")
        return
    try:
        st.session_state.body_input = body_from_description(
            desc, st.session_state.get("resume_text", "")
        )
        st.session_state._ai_msg = ("success", "✨ Body generated from your description.")
    except Exception as e:
        st.session_state._ai_msg = ("error", f"AI error: {e}")


def _cb_improve_body():
    text = st.session_state.get("body_input", "").strip()
    if not text:
        st.session_state._ai_msg = ("warning", "✍️ Write or generate some body text first.")
        return
    try:
        st.session_state.body_input = improve_text(text)
        st.session_state._ai_msg = ("success", "🪄 Body improved.")
    except Exception as e:
        st.session_state._ai_msg = ("error", f"AI error: {e}")


def get_user_email(creds) -> str:
    """Get the signed-in user's email address from the OAuth userinfo endpoint."""
    try:
        oauth2 = build("oauth2", "v2", credentials=creds)
        info = oauth2.userinfo().get().execute()
        return info.get("email") or "unknown"
    except Exception:
        return "unknown"


# --------------------------------------------------------------------------- #
# Sidebar: authentication + dataset
# --------------------------------------------------------------------------- #
def render_auth_sidebar():
    if not st.session_state.authenticated:
        # OAuth callback (Google redirected back with ?code=...)
        query_params = st.query_params
        if 'code' in query_params and 'state' in query_params:
            auth_code = query_params['code']
            try:
                with st.spinner("Signing you in..."):
                    creds = complete_gmail_auth(auth_code)
                    service = build("gmail", "v1", credentials=creds)
                    st.session_state.gmail_service = service
                    st.session_state.user_email = get_user_email(creds)
                    st.session_state.authenticated = True
                    for key in ('oauth_authorization_url', 'oauth_flow'):
                        st.session_state.pop(key, None)
                    st.query_params.clear()
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Sign-in failed: {e}")
                st.query_params.clear()

        # Single button → straight to Google sign-in
        try:
            auth_url = authenticate_gmail_flow()
            st.link_button("🔐 Sign in with Google", auth_url,
                           type="primary", use_container_width=True)
        except Exception as e:
            st.error(f"❌ Could not start sign-in: {e}")
            st.info("💡 Make sure Gmail credentials are configured in Streamlit secrets.")
    else:
        st.success(f"✅ Signed in as **{st.session_state.get('user_email', 'Gmail')}**")
        if st.button("🔓 Disconnect"):
            for key in ('authenticated', 'gmail_service', 'gmail_token', 'user_email'):
                st.session_state.pop(key, None)
            st.session_state.authenticated = False
            st.rerun()


# --------------------------------------------------------------------------- #
# Main app
# --------------------------------------------------------------------------- #
def main():
    # Initialize session state
    st.session_state.setdefault('gmail_service', None)
    st.session_state.setdefault('authenticated', False)
    st.session_state.setdefault('user_email', None)

    # Header
    st.markdown('<div class="main-header">📧 AI Email Agent</div>', unsafe_allow_html=True)
    st.caption("Send your resume to the next batch of recipients — 200 emails per 24 hours.")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Account")
        render_auth_sidebar()

        st.divider()
        st.subheader("📊 Email Database")
        use_custom_list = st.toggle(
            "Upload my own email list",
            value=False,
            help="Off: use the built-in email list. On: upload your own .txt file."
        )
        if use_custom_list:
            uploaded_email_file = st.file_uploader(
                "Upload email list (.txt, one email per line)",
                type=['txt'],
                help="One email per line."
            )
            if uploaded_email_file:
                with open(RECIPIENTS_FILE, "wb") as f:
                    f.write(uploaded_email_file.getbuffer())
                st.cache_data.clear()
                st.success("✅ Email database updated!")
        else:
            st.caption("📁 Using the built-in email list.")

    all_emails = load_emails()

    # Per-user stats
    user_email = st.session_state.get('user_email')
    record = get_user_record(user_email) if user_email else None

    total_in_dataset = len(all_emails)
    sent_set = set(record["sent_emails"]) if record else set()
    failed_set = set(record["failed_emails"]) if record else set()
    processed_set = sent_set | failed_set
    sent_count = len(sent_set)
    failed_count = len(failed_set)
    remaining_count = max(0, total_in_dataset - len(processed_set))
    remaining_quota = quota_remaining(record) if record else DAILY_LIMIT

    # --- Tracking dashboard --------------------------------------------------
    st.subheader("📈 Your Progress")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📧 Total in Dataset", total_in_dataset)
    m2.metric("✅ Sent", sent_count)
    m3.metric("⏳ Remaining", remaining_count)
    m4.metric("🎯 Quota Left (24h)", remaining_quota if user_email else DAILY_LIMIT)

    if record:
        reset_in = time_until_reset(record)
        if remaining_quota <= 0 and reset_in:
            st.warning(f"🚫 Daily limit of {DAILY_LIMIT} reached. Resets in **{format_timedelta(reset_in)}**.")
        elif reset_in:
            st.caption(f"⏱️ Sent {record.get('sent_in_window', 0)}/{DAILY_LIMIT} in the current window "
                       f"(resets in {format_timedelta(reset_in)}).")
        if failed_count:
            st.caption(f"⚠️ {failed_count} address(es) failed and will be skipped.")

    st.divider()

    # --- Compose -------------------------------------------------------------
    st.session_state.setdefault("subject_input", "")
    st.session_state.setdefault("body_input", "")
    st.session_state.setdefault("attachment_paths", [])
    st.session_state.setdefault("resume_text", "")

    st.subheader("✍️ Compose Email")
    ai_on = ai_available()

    # 1. Resume / CV upload — drives auto subject + body
    uploaded_files = st.file_uploader(
        "📎 Attach Resume / CV (PDF recommended for AI analysis)",
        type=['pdf', 'doc', 'docx', 'txt'],
        accept_multiple_files=True,
        key="resume_files",
    )
    if uploaded_files:
        sig = tuple((f.name, f.size) for f in uploaded_files)
        if st.session_state.get("last_resume_sig") != sig:
            st.session_state.last_resume_sig = sig
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)
            paths = []
            for uf in uploaded_files:
                p = upload_dir / uf.name
                with open(p, "wb") as f:
                    f.write(uf.getbuffer())
                paths.append(str(p))
            st.session_state.attachment_paths = paths

            # Extract text from the first PDF/TXT for AI analysis
            resume_text = ""
            for p in paths:
                resume_text = extract_pdf_text(p)
                if resume_text:
                    break
            st.session_state.resume_text = resume_text

            # Auto-draft subject + body from the resume
            if resume_text and ai_on:
                try:
                    with st.spinner("🤖 Analyzing resume & drafting your email..."):
                        result = analyze_resume(resume_text)
                    st.session_state._pending_subject = result.get("subject", "")
                    st.session_state._pending_body = result.get("body", "")
                    st.session_state._ai_msg = (
                        "success",
                        "🤖 Subject & body auto-drafted from your resume — edit as you like.",
                    )
                except Exception as e:
                    st.session_state._ai_msg = ("error", f"Resume analysis failed: {e}")
            st.rerun()

    if not ai_on:
        st.caption("🔌 Add your Groq API key in app secrets ([groq] api_key) to enable AI writing.")

    # 2. "Describe your message" → AI writes the body
    dcol1, dcol2 = st.columns([4, 1])
    with dcol1:
        st.text_input(
            "Describe your message",
            key="desc_input",
            placeholder="✨ Describe your message (e.g. short intro applying for a backend role)",
            label_visibility="collapsed",
        )
    with dcol2:
        st.button("✨ Generate", on_click=_cb_generate_body,
                  disabled=not ai_on, use_container_width=True)

    # Apply any AI-generated content BEFORE the subject/body widgets are created
    for src, dst in (("_pending_subject", "subject_input"), ("_pending_body", "body_input")):
        if src in st.session_state:
            st.session_state[dst] = st.session_state.pop(src)

    # 3. Subject & Body
    st.text_input("📌 Subject", key="subject_input",
                  placeholder="Application for Software Engineer role")
    st.text_area("💬 Body", key="body_input", height=220,
                 placeholder="Write your email here, or use AI above...")
    st.button("🪄 Improve / Paraphrase body", on_click=_cb_improve_body, disabled=not ai_on)

    # Show any AI status message
    if "_ai_msg" in st.session_state:
        level, text = st.session_state.pop("_ai_msg")
        getattr(st, level)(text)

    subject = st.session_state.get("subject_input", "")
    body = st.session_state.get("body_input", "")
    attachment_paths = st.session_state.get("attachment_paths", [])

    next_batch_size = min(remaining_quota, remaining_count) if user_email else 0
    if user_email:
        st.info(f"▶️ Next send will go to the next **{next_batch_size}** unsent recipient(s).")

    send_clicked = st.button("📤 Send", type="primary", use_container_width=True)

    if send_clicked:
        # Validations
        if not st.session_state.authenticated:
            st.error("❌ Please authenticate with Gmail first (sidebar).")
            return
        if total_in_dataset == 0:
            st.error("❌ No emails in the dataset. Upload an email list in the sidebar.")
            return
        if not subject.strip():
            st.error("❌ Please enter a subject.")
            return
        if not body.strip():
            st.error("❌ Please enter the email body.")
            return
        if remaining_quota <= 0:
            reset_in = time_until_reset(record)
            msg = f"in {format_timedelta(reset_in)}" if reset_in else "soon"
            st.error(f"🚫 You've hit the {DAILY_LIMIT}/24h limit. Try again {msg}.")
            return
        if remaining_count == 0:
            st.success("🎉 You've already emailed everyone in the dataset!")
            return

        # Build the batch
        batch = get_next_batch(all_emails, processed_set, remaining_quota)
        if not batch:
            st.success("🎉 No new recipients left to send to.")
            return

        # Send — progress shown in the sidebar
        st.sidebar.divider()
        st.sidebar.markdown(f"### 📤 Sending {len(batch)} emails")
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        with st.spinner(f"📧 Sending {len(batch)} emails..."):
            sent_list, failed_list = send_emails(
                st.session_state.gmail_service, batch, subject.strip(),
                body.strip(), attachment_paths, progress_bar, status_text
            )
        progress_bar.empty()
        status_text.empty()

        # Update per-user record
        if record.get("window_start") is None and sent_list:
            record["window_start"] = datetime.now().isoformat(timespec="seconds")
        record["sent_in_window"] = record.get("sent_in_window", 0) + len(sent_list)
        record["sent_emails"] = list(sent_set | set(sent_list))
        record["failed_emails"] = list(failed_set | set(failed_list))
        save_user_record(user_email, record)

        st.success(f"✅ Sent {len(sent_list)} emails.")
        if failed_list:
            st.warning(f"⚠️ {len(failed_list)} failed (they'll be skipped next time).")
        st.balloons()
        st.rerun()

    # Footer
    st.divider()
    st.caption("💡 Powered by Streamlit + Gmail API · 200 emails / 24h per account")


if __name__ == "__main__":
    init_log_file()
    main()
