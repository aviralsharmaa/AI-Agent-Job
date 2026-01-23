#!/usr/bin/env python3
"""
AI Email Agent CLI - Interactive command-line interface for sending emails
via natural language prompts.

Usage:
    python email_agent_cli.py

Example prompts:
    "Send a mail to microsoft with subject 'Job Application' and body 'I am interested...'"
    "Send email to google with attachments resume.pdf and cover_letter.pdf"
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Import from existing Gmail API module
from send_mails_gmail_api import (
    get_gmail_service,
    create_message,
    send_message,
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


class EmailAgent:
    """AI Agent for parsing prompts and sending emails."""
    
    def __init__(self):
        self.service = None
        self.user_id = "me"
        self.all_emails = []
        self.load_emails()
        init_log_file()
    
    def load_emails(self):
        """Load all emails from the recipients file."""
        if not Path(RECIPIENTS_FILE).exists():
            print(f"⚠️  Warning: {RECIPIENTS_FILE} not found!")
            return
        
        with open(RECIPIENTS_FILE, "r", encoding="utf-8") as f:
            self.all_emails = [line.strip() for line in f if line.strip()]
        
        print(f"✅ Loaded {len(self.all_emails)} emails from {RECIPIENTS_FILE}")
    
    def extract_company_name(self, prompt: str) -> Optional[str]:
        """Extract company name from prompt."""
        # Common patterns: "to microsoft", "to google", "microsoft employees", etc.
        patterns = [
            r"to\s+([a-zA-Z0-9]+)",
            r"send\s+(?:a\s+)?(?:mail|email)\s+to\s+([a-zA-Z0-9]+)",
            r"([a-zA-Z0-9]+)\s+(?:employees|company|team|people)",
            r"company\s+([a-zA-Z0-9]+)",
        ]
        
        prompt_lower = prompt.lower()
        for pattern in patterns:
            match = re.search(pattern, prompt_lower, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                # Filter out common words
                if company not in ["a", "an", "the", "mail", "email", "send"]:
                    return company
        
        return None
    
    def extract_subject(self, prompt: str) -> Optional[str]:
        """Extract email subject from prompt."""
        patterns = [
            r"subject[:\s]+['\"]([^'\"]+)['\"]",
            r"subject[:\s]+([^\n]+?)(?:\s+body|\s+attachment|$)",
            r"with\s+subject[:\s]+['\"]?([^'\"]+?)['\"]?",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_body(self, prompt: str, multiline_input: Optional[str] = None) -> Optional[str]:
        """Extract email body from prompt."""
        # Check if multiline input was provided
        if multiline_input:
            return multiline_input.strip()
        
        patterns = [
            r"body[:\s]+['\"]([^'\"]+)['\"]",
            r"body[:\s]+(.+?)(?:\s+attachment|$)",
            r"message[:\s]+['\"]?([^'\"]+?)['\"]?",
            r"content[:\s]+['\"]?([^'\"]+?)['\"]?",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # If no explicit body found, try to extract text after subject
        subject_match = re.search(r"subject[:\s]+['\"]?([^'\"]+?)['\"]?", prompt, re.IGNORECASE)
        if subject_match:
            # Get text after subject
            after_subject = prompt[subject_match.end():].strip()
            # Remove attachment mentions
            after_subject = re.sub(r"attachment[:\s]+[^\n]+", "", after_subject, flags=re.IGNORECASE)
            if after_subject:
                return after_subject.strip()
        
        return None
    
    def extract_attachments(self, prompt: str) -> List[str]:
        """Extract attachment file names from prompt."""
        attachments = []
        
        # Patterns for finding attachments
        patterns = [
            r"attachment[:\s]+([^\n]+)",
            r"attach[:\s]+([^\n]+)",
            r"upload[:\s]+([^\n]+)",
            r"(?:resume|cv|cover\s+letter|coverletter)[:\s]+([^\s,]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                files_str = match.group(1).strip()
                # Split by comma or space
                files = re.split(r"[,;\s]+", files_str)
                attachments.extend([f.strip() for f in files if f.strip()])
        
        # Also look for common file patterns
        file_patterns = [
            r"([a-zA-Z0-9_\-]+\.(?:pdf|doc|docx|txt))",
            r"(resume|cv|cover_?letter)\.(?:pdf|doc|docx)",
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    attachments.append(".".join(match))
                else:
                    attachments.append(match)
        
        # Remove duplicates and normalize
        unique_attachments = []
        seen = set()
        for att in attachments:
            att_lower = att.lower()
            if att_lower not in seen:
                seen.add(att_lower)
                unique_attachments.append(att)
        
        return unique_attachments
    
    def find_company_emails(self, company_name: str) -> List[str]:
        """Find emails associated with a company."""
        if not company_name:
            return []
        
        company_lower = company_name.lower().strip()
        matching_emails = []
        
        # Common company name variations
        company_variations = [company_lower]
        if company_lower.endswith("inc"):
            company_variations.append(company_lower[:-3].strip())
        if company_lower.endswith("corp"):
            company_variations.append(company_lower[:-4].strip())
        if company_lower.endswith("llc"):
            company_variations.append(company_lower[:-3].strip())
        
        for email in self.all_emails:
            email_lower = email.lower()
            
            # Extract domain from email
            if "@" not in email:
                continue
            
            domain = email.split("@")[1].lower()
            
            # Skip personal email domains
            if domain in PERSONAL_EMAIL_DOMAINS:
                continue
            
            domain_parts = domain.split(".")
            main_domain = domain_parts[0] if domain_parts else ""
            
            # Check if company name matches domain
            # e.g., "microsoft" matches "@microsoft.com"
            for variation in company_variations:
                if variation == main_domain:
                    matching_emails.append(email)
                    break
                # Also check if company name is contained in domain
                elif variation in domain and len(variation) >= 3:
                    matching_emails.append(email)
                    break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_emails = []
        for email in matching_emails:
            if email not in seen:
                seen.add(email)
                unique_emails.append(email)
        
        return unique_emails
    
    def parse_prompt(self, prompt: str, multiline_body: Optional[str] = None) -> Dict:
        """Parse user prompt and extract email details."""
        result = {
            "company": None,
            "subject": None,
            "body": None,
            "attachments": [],
        }
        
        # Extract company name
        result["company"] = self.extract_company_name(prompt)
        
        # Extract subject
        result["subject"] = self.extract_subject(prompt)
        
        # Extract body
        result["body"] = self.extract_body(prompt, multiline_body)
        
        # Extract attachments
        result["attachments"] = self.extract_attachments(prompt)
        
        return result
    
    def get_multiline_input(self, prompt: str) -> str:
        """Get multiline input from user."""
        print(f"\n{prompt}")
        print("(Enter your text. Type 'END' on a new line when finished, or 'CANCEL' to cancel)\n")
        
        lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == "END":
                    break
                if line.strip().upper() == "CANCEL":
                    return None
                lines.append(line)
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n❌ Cancelled.")
                return None
        
        return "\n".join(lines)
    
    def get_file_paths(self, file_names: List[str]) -> List[str]:
        """Resolve file paths from file names."""
        valid_paths = []
        current_dir = Path.cwd()
        
        for file_name in file_names:
            # Try current directory first
            path = current_dir / file_name
            if path.exists():
                valid_paths.append(str(path))
            else:
                # Try to find file in current directory
                found = False
                for file_path in current_dir.glob(f"*{file_name}*"):
                    if file_path.is_file():
                        valid_paths.append(str(file_path))
                        found = True
                        break
                
                if not found:
                    print(f"⚠️  Warning: File '{file_name}' not found. Skipping...")
        
        return valid_paths
    
    def create_message_with_attachments(self, to: str, subject: str, body: str, attachment_paths: List[str]):
        """Create email message with multiple attachments."""
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email.mime.multipart import MIMEMultipart
        from email import encoders
        import base64
        
        message = MIMEMultipart()
        message["To"] = to
        message["From"] = ""  # Gmail API uses authenticated user
        message["Subject"] = subject
        
        # Body
        message.attach(MIMEText(body, "plain"))
        
        # Attachments
        for attachment_path in attachment_paths:
            file_path = Path(attachment_path)
            if file_path.exists():
                try:
                    with file_path.open("rb") as f:
                        # Determine MIME type
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
                    print(f"  ✅ Attached: {file_path.name}")
                except Exception as e:
                    print(f"  ⚠️  Error attaching {file_path.name}: {e}")
            else:
                print(f"  ⚠️  File not found: {attachment_path}")
        
        # Encode to base64 for Gmail API
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {"raw": raw_message}
    
    def send_emails(self, emails: List[str], subject: str, body: str, attachments: List[str]) -> Tuple[int, int]:
        """Send emails to the list of recipients."""
        if not self.service:
            print("🔐 Authenticating with Gmail...")
            self.service = get_gmail_service()
        
        if not emails:
            print("❌ No emails to send to!")
            return 0, 0
        
        print(f"\n📧 Preparing to send emails to {len(emails)} recipients...")
        print(f"   Subject: {subject}")
        print(f"   Attachments: {', '.join(attachments) if attachments else 'None'}")
        
        # Resolve attachment paths
        attachment_paths = self.get_file_paths(attachments) if attachments else []
        
        sent_count = 0
        failed_count = 0
        
        for i, email in enumerate(emails, 1):
            try:
                # Create message
                if attachment_paths:
                    message_body = self.create_message_with_attachments(
                        email, subject, body, attachment_paths
                    )
                else:
                    # Use existing create_message function for no attachments
                    # Create a simple message without attachment
                    from email.mime.text import MIMEText
                    import base64
                    message = MIMEText(body, "plain")
                    message["To"] = email
                    message["From"] = ""
                    message["Subject"] = subject
                    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
                    message_body = {"raw": raw_message}
                
                # Send email
                result = send_message(self.service, self.user_id, message_body)
                message_id = result.get("id", "")
                
                sent_count += 1
                move_to_sent_mail(email)
                log_result(email, "SENT", "", message_id)
                
                print(f"[{i}/{len(emails)}] ✅ Sent to {email}")
                
            except Exception as e:
                error_message = str(e)
                failed_count += 1
                
                if is_delivery_failure_error(error_message):
                    move_to_failed_mail(email, error_message[:100])
                    log_result(email, "DELIVERY_FAILED", error_message[:200], "")
                    print(f"[{i}/{len(emails)}] ❌ Delivery failed: {email}")
                else:
                    log_result(email, "FAILED", error_message[:200], "")
                    print(f"[{i}/{len(emails)}] ❌ Failed: {email} - {error_message[:100]}")
        
        return sent_count, failed_count
    
    def process_command(self, prompt: str):
        """Process a user command/prompt."""
        prompt = prompt.strip()
        
        if not prompt:
            return
        
        # Handle special commands
        if prompt.lower() in ["exit", "quit", "q"]:
            print("👋 Goodbye!")
            sys.exit(0)
        
        if prompt.lower() in ["help", "h"]:
            self.show_help()
            return
        
        if prompt.lower() in ["list", "companies", "list companies"]:
            self.list_companies()
            return
        
        # Parse the prompt
        print("\n🔍 Parsing your request...")
        parsed = self.parse_prompt(prompt)
        
        # Check if we need multiline input for body
        if not parsed["body"]:
            print("\n💬 No email body found in prompt.")
            body = self.get_multiline_input("Would you like to enter the email body?")
            if body:
                parsed["body"] = body
            else:
                print("❌ Email body is required. Cancelling...")
                return
        
        # Check if we need subject
        if not parsed["subject"]:
            print("\n📝 No subject found in prompt.")
            subject = input("Enter email subject (or press Enter for default 'Job Application'): ").strip()
            parsed["subject"] = subject if subject else "Job Application"
        
        # Validate company name
        if not parsed["company"]:
            print("❌ Could not extract company name from prompt.")
            print("   Please include the company name, e.g., 'Send a mail to microsoft...'")
            return
        
        # Find company emails
        print(f"\n🔎 Searching for emails associated with '{parsed['company']}'...")
        company_emails = self.find_company_emails(parsed["company"])
        
        if not company_emails:
            print(f"❌ No emails found for company '{parsed['company']}'")
            print("   Available companies can be found in the email file.")
            return
        
        print(f"✅ Found {len(company_emails)} email(s) for {parsed['company']}:")
        for email in company_emails[:10]:  # Show first 10
            print(f"   - {email}")
        if len(company_emails) > 10:
            print(f"   ... and {len(company_emails) - 10} more")
        
        # Confirm before sending
        print(f"\n📋 Email Details:")
        print(f"   Company: {parsed['company']}")
        print(f"   Subject: {parsed['subject']}")
        print(f"   Body: {parsed['body'][:100]}..." if len(parsed['body']) > 100 else f"   Body: {parsed['body']}")
        print(f"   Attachments: {', '.join(parsed['attachments']) if parsed['attachments'] else 'None'}")
        print(f"   Recipients: {len(company_emails)}")
        
        confirm = input("\n❓ Send these emails? (yes/no): ").strip().lower()
        if confirm not in ["yes", "y"]:
            print("❌ Cancelled.")
            return
        
        # Send emails
        sent, failed = self.send_emails(
            company_emails,
            parsed["subject"],
            parsed["body"],
            parsed["attachments"]
        )
        
        print(f"\n✅ Done! Sent: {sent}, Failed: {failed}")
    
    def list_companies(self):
        """List all available companies from the email database."""
        companies = set()
        
        for email in self.all_emails:
            if "@" not in email:
                continue
            
            domain = email.split("@")[1].lower()
            
            # Skip personal email domains
            if domain in PERSONAL_EMAIL_DOMAINS:
                continue
            
            # Extract company name from domain
            domain_parts = domain.split(".")
            if domain_parts:
                company = domain_parts[0].capitalize()
                companies.add(company)
        
        companies_sorted = sorted(companies)
        
        print(f"\n📋 Found {len(companies_sorted)} companies in email database:")
        print("=" * 60)
        
        # Display in columns
        cols = 3
        for i in range(0, len(companies_sorted), cols):
            row = companies_sorted[i:i+cols]
            print("  ".join(f"{c:20}" for c in row))
        
        print("=" * 60)
        print(f"\n💡 Use these company names in your prompts (case-insensitive)")
    
    def show_help(self):
        """Show help information."""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║              AI Email Agent CLI - Help                       ║
╚══════════════════════════════════════════════════════════════╝

📝 USAGE:
   Type natural language prompts to send emails.

📋 EXAMPLES:
   1. Basic email:
      "Send a mail to microsoft with subject 'Job Application' and body 'I am interested in...'"
   
   2. With attachments:
      "Send email to google with attachments resume.pdf and cover_letter.pdf"
   
   3. Full example:
      "Send a mail to microsoft with subject 'Software Engineer Application' 
       and body 'Hello, I am applying for...' and attachments Aviral_cv3.pdf"

💡 TIPS:
   - Company name: Just mention the company (e.g., "microsoft", "google")
   - Subject: Include "subject: 'Your Subject'" or "with subject 'Your Subject'"
   - Body: Include "body: 'Your message'" or the agent will prompt you
   - Attachments: Mention file names (e.g., "resume.pdf", "cv.pdf")
   - Multi-line body: If body is not in prompt, you'll be asked to enter it
   - File paths: Attachments should be in the current directory

🎯 COMMANDS:
   - help, h          : Show this help message
   - list, companies  : List all available companies
   - exit, quit, q    : Exit the program

📁 FILES:
   - Emails are loaded from: emails_from_excel.txt
   - Sent emails are tracked in: sent_mail.txt
   - Failed emails are tracked in: not_sent.txt
   - Logs are saved to: mail_log.csv

⚠️  NOTE:
   - The agent finds emails by matching company name with email domains
   - Only company emails are sent (personal emails like gmail.com are excluded)
   - You'll be asked to confirm before sending emails
        """
        print(help_text)


def main():
    """Main entry point."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              AI Email Agent CLI                              ║
║              Intelligent Email Sending Assistant             ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    agent = EmailAgent()
    
    print("\n💡 Type 'help' for usage instructions, or 'exit' to quit.\n")
    
    # Main loop
    while True:
        try:
            prompt = input("🤖 Agent> ").strip()
            if prompt:
                agent.process_command(prompt)
            print()  # Empty line for readability
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)
        except EOFError:
            print("\n\n👋 Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
