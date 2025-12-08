#!/usr/bin/env python3
"""
Script to compare two email files and remove duplicates from emails.txt
that exist in emails2.txt
"""

from pathlib import Path


def load_emails(file_path: str) -> set:
    """Load emails from a file into a set (case-insensitive)."""
    emails = set()
    file = Path(file_path)
    
    if not file.exists():
        print(f"⚠️  File not found: {file_path}")
        return emails
    
    with file.open("r", encoding="utf-8") as f:
        for line in f:
            email = line.strip().lower()  # Case-insensitive comparison
            if email:  # Skip empty lines
                emails.add(email)
    
    return emails


def remove_duplicates_from_file(source_file: str, reference_file: str, output_file: str = None):
    """
    Remove emails from source_file that exist in reference_file.
    
    Args:
        source_file: File to clean (emails.txt)
        reference_file: File containing emails to remove (emails2.txt)
        output_file: Output file (defaults to source_file to overwrite)
    """
    # Load reference emails (emails2.txt)
    print(f"📖 Loading reference emails from: {reference_file}")
    reference_emails = load_emails(reference_file)
    print(f"   Found {len(reference_emails)} unique emails in reference file")
    
    # Load source emails (emails.txt)
    print(f"\n📖 Loading emails from: {source_file}")
    source_path = Path(source_file)
    
    if not source_path.exists():
        print(f"❌ Error: Source file not found: {source_file}")
        return
    
    # Read all lines from source file
    original_emails = []
    with source_path.open("r", encoding="utf-8") as f:
        for line in f:
            original_emails.append(line.rstrip("\n\r"))  # Preserve original line
    
    print(f"   Found {len(original_emails)} lines in source file")
    
    # Filter out duplicates
    filtered_emails = []
    removed_count = 0
    
    for line in original_emails:
        email = line.strip().lower()
        if email and email in reference_emails:
            removed_count += 1
            print(f"   🗑️  Removing duplicate: {line.strip()}")
        else:
            filtered_emails.append(line)
    
    # Write cleaned emails
    output_path = Path(output_file) if output_file else source_path
    print(f"\n💾 Writing cleaned emails to: {output_path}")
    
    with output_path.open("w", encoding="utf-8") as f:
        for line in filtered_emails:
            f.write(line + "\n")
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"Original emails in {source_file}: {len(original_emails)}")
    print(f"Reference emails in {reference_file}: {len(reference_emails)}")
    print(f"Duplicates removed: {removed_count}")
    print(f"Remaining emails: {len(filtered_emails)}")
    print(f"Output file: {output_path}")
    print("="*60)


def main():
    """Main function."""
    emails_file = "emails.txt"
    emails2_file = "emails2.txt"
    
    # Optional: create backup before modifying
    backup_file = "emails_backup.txt"
    emails_path = Path(emails_file)
    
    if emails_path.exists():
        print(f"💾 Creating backup: {backup_file}")
        import shutil
        shutil.copy2(emails_file, backup_file)
    
    # Remove duplicates
    remove_duplicates_from_file(
        source_file=emails_file,
        reference_file=emails2_file,
        output_file=emails_file  # Overwrite original file
    )


if __name__ == "__main__":
    main()

