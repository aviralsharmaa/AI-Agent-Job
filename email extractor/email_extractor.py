# import re

# def extract_emails(text):
#     # Regex to detect valid email addresses
#     email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

#     # Find all emails
#     emails = re.findall(email_pattern, text)

#     # Remove duplicates while preserving order
#     seen = set()
#     cleaned = []
#     for email in emails:
#         if email not in seen:
#             cleaned.append(email)
#             seen.add(email)
#     return cleaned


# if __name__ == "__main__":
#     input_file = "input2.txt"    # Your raw text file
#     output_file = "emails2.txt"  # Output cleaned email file

#     # Read text file
#     with open(input_file, "r", encoding="utf-8") as f:
#         text = f.read()

#     # Extract emails
#     emails = extract_emails(text)

#     # Save to emails.txt
#     with open(output_file, "w", encoding="utf-8") as f:
#         for email in emails:
#             f.write(email + "\n")

#     # Print on screen
#     print("\n✔ Extracted & Saved Emails to emails.txt:\n")
#     for e in emails:
#         print(e)

#     print(f"\nTotal Emails Found: {len(emails)}")


import re

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


if __name__ == "__main__":
    input_file = "input2.txt"    # <- put your log/text file here
    output_file = "emails2.txt"  # <- output file

    # Read the whole input file
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    # Extract emails
    emails = extract_emails(text)

    # Write them to emails.txt, one per line
    with open(output_file, "w", encoding="utf-8") as f:
        for email in emails:
            f.write(email + "\n")

    # Optional: print summary
    print("✔ Extracted emails (also saved to emails.txt):\n")
    for e in emails:
        print(e)

    print(f"\nTotal unique emails: {len(emails)}")
