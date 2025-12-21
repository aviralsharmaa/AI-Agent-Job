import re
import socket
import smtplib
from typing import Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False
    print("Warning: dnspython not installed. Install it with: pip install dnspython")
    print("Email verification will be limited to format checking only.\n")


def extract_emails(text: str):
    # Regex to detect valid email addresses (case-insensitive)
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    # Find all emails in the text
    emails = re.findall(email_pattern, text)

    # Remove duplicates (case-insensitive) while preserving order
    seen = set()
    cleaned = []
    for email in emails:
        email_norm = email.strip()
        email_key = email_norm.lower()  # for dedup
        if email_key not in seen:
            seen.add(email_key)
            cleaned.append(email_norm)

    return cleaned


def check_mx_record(domain: str) -> bool:
    """Check if domain has valid MX records"""
    if not DNS_AVAILABLE:
        # Fallback: try basic socket connection to port 25
        try:
            socket.create_connection((domain, 25), timeout=5)
            return True
        except (socket.gaierror, socket.timeout, OSError):
            return False
    
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return len(mx_records) > 0
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout, Exception):
        return False


def verify_email_smtp(email: str, mx_host: str) -> bool:
    """Verify email exists on SMTP server"""
    try:
        # Connect to SMTP server
        server = smtplib.SMTP(timeout=10)
        server.set_debuglevel(0)
        server.connect(mx_host)
        server.helo(server.local_hostname)
        server.mail('test@example.com')
        code, message = server.rcpt(email)
        server.quit()
        
        # 250 means email is valid
        return code == 250
    except (smtplib.SMTPConnectError, smtplib.SMTPException, socket.timeout, Exception):
        return False


def verify_email(email: str) -> Tuple[bool, str]:
    """
    Verify if email is valid and exists
    Returns: (is_valid, reason)
    """
    # Basic format validation
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        return False, "Invalid format"
    
    # Extract domain
    try:
        domain = email.split('@')[1]
    except IndexError:
        return False, "Invalid format"
    
    # Check if domain has MX records
    if not check_mx_record(domain):
        return False, "No MX records found"
    
    # Try to get MX host for SMTP verification
    if DNS_AVAILABLE:
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            mx_host = str(mx_records[0].exchange).rstrip('.')
            
            # Attempt SMTP verification (may fail due to server restrictions)
            if verify_email_smtp(email, mx_host):
                return True, "Valid"
            else:
                # Domain exists but SMTP verification failed (may be due to server blocking)
                # Still consider it potentially valid if MX records exist
                return True, "Domain valid (SMTP check inconclusive)"
        except Exception:
            # If we can't verify via SMTP but MX exists, consider it potentially valid
            return True, "Domain valid (SMTP check failed)"
    else:
        # If DNS library not available, just check if domain can receive mail
        return True, "Domain appears valid (limited verification)"


def process_email_batch(email: str, index: int, total: int) -> Tuple[str, bool, str]:
    """Process a single email and return result"""
    is_valid, reason = verify_email(email)
    return email, is_valid, reason


if __name__ == "__main__":
    input_file = "input.txt"    # <- put your log/text file here
    valid_output_file = "emails.txt"  # <- valid emails output file
    invalid_output_file = "not_valid_email.txt"  # <- invalid emails output file
    batch_size = 500  # Process first 500 emails
    max_workers = 5   # Process 5 emails concurrently

    # Read the whole input file
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    # Extract emails
    all_emails = extract_emails(text)
    
    # Take first 500 emails
    emails_to_process = all_emails[:batch_size]
    remaining_emails = all_emails[batch_size:]
    
    print(f"Found {len(all_emails)} total unique emails.")
    print(f"Processing first {len(emails_to_process)} emails using {max_workers} threads...\n")
    
    valid_emails = []
    invalid_emails = []
    processed_count = 0
    lock = Lock()
    
    # Process emails using ThreadPoolExecutor (5 concurrent threads)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_email = {
            executor.submit(process_email_batch, email, i+1, len(emails_to_process)): email 
            for i, email in enumerate(emails_to_process)
        }
        
        # Process completed tasks as they finish
        for future in as_completed(future_to_email):
            email = future_to_email[future]
            try:
                processed_email, is_valid, reason = future.result()
                processed_count += 1
                
                with lock:
                    if is_valid:
                        valid_emails.append(processed_email)
                        print(f"[{processed_count}/{len(emails_to_process)}] ✓ {processed_email} - Valid ({reason})")
                    else:
                        invalid_emails.append((processed_email, reason))
                        print(f"[{processed_count}/{len(emails_to_process)}] ✗ {processed_email} - Invalid ({reason})")
            except Exception as e:
                processed_count += 1
                with lock:
                    invalid_emails.append((email, f"Error: {str(e)}"))
                    print(f"[{processed_count}/{len(emails_to_process)}] ✗ {email} - Error: {str(e)}")
    
    # Append valid emails to emails.txt
    with open(valid_output_file, "a", encoding="utf-8") as f:
        for email in valid_emails:
            f.write(email + "\n")
    
    # Append invalid emails to not_valid_email.txt
    with open(invalid_output_file, "a", encoding="utf-8") as f:
        for email, reason in invalid_emails:
            f.write(f"{email} - {reason}\n")
    
    # Remove processed emails from input.txt
    # Remove processed emails from the text using regex (case-insensitive)
    for email in emails_to_process:
        # Escape special regex characters in email
        escaped_email = re.escape(email)
        # Remove the email from text (with word boundaries to avoid partial matches)
        # Use lookahead/lookbehind to handle emails that might be surrounded by various characters
        pattern = r'\b' + escaped_email + r'\b'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Clean up extra whitespace (multiple newlines/spaces)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple newlines to double
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
    text = re.sub(r'\n[ \t]+', '\n', text)  # Remove leading spaces on lines
    text = re.sub(r'[ \t]+\n', '\n', text)  # Remove trailing spaces on lines
    text = text.strip()  # Remove leading/trailing whitespace
    
    # Write updated text back to input.txt
    with open(input_file, "w", encoding="utf-8") as f:
        f.write(text)
    
    # Print summary
    print("\n" + "="*60)
    print("✔ Batch Processing Complete!")
    print(f"Processed: {len(emails_to_process)} emails")
    print(f"Valid emails: {len(valid_emails)} (appended to {valid_output_file})")
    print(f"Invalid emails: {len(invalid_emails)} (appended to {invalid_output_file})")
    print(f"Remaining emails in {input_file}: {len(remaining_emails)}")
    print("="*60)
