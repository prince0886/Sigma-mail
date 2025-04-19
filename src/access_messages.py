import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

def get_emails(limit=10):
    """
    Fetch recent emails and return them as a list of dictionaries.
    """
    load_dotenv()
    
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    
    if not username or not password:
        raise ValueError("Missing email credentials")
    
    emails = []
    
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(username, password)
        
        status, messages = imap.select("INBOX")
        status, message_numbers = imap.search(None, 'UNSEEN')
        message_numbers = message_numbers[0].split()[-limit:]
        
        for num in message_numbers:
            email_data = {}
            
            res, msg = imap.fetch(num, "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])
                    
                    # Get subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="ignore")
                    email_data['subject'] = subject
                    
                    # Get sender
                    from_header, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(from_header, bytes):
                        from_header = from_header.decode(encoding or "utf-8", errors="ignore")
                    email_data['from'] = from_header
                    
                    # Get content
                    email_content = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                try:
                                    body = part.get_payload(decode=True).decode()
                                    if body:
                                        email_content += body.strip() + "\n"
                                except:
                                    continue
                    else:
                        if msg.get_content_type() == "text/plain":
                            try:
                                email_content = msg.get_payload(decode=True).decode()
                            except:
                                email_content = ""
                    
                    email_data['content'] = email_content.strip()
                    
            if email_data and email_data['content']:
                emails.append(email_data)
        
        imap.close()
        imap.logout()
        
        return emails
        
    except Exception as e:
        raise Exception(f"Error accessing emails: {str(e)}")

if __name__ == "__main__":
    emails = get_emails()
    for email in emails:
        print(f"Subject: {email['subject']}")
        print(f"From: {email['from']}")
        print(f"Content: {email['content'][:100]}...")
        print("="*50)
