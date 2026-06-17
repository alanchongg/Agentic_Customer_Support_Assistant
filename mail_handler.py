import os
from dotenv import load_dotenv
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import imaplib
import time
from email.header import decode_header

load_dotenv()

def get_unread_emails():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(os.getenv("mail_name"), os.getenv("mail_pass")) 
    mail.select("inbox")
    _, data = mail.search(None, "UNSEEN")
    email_ids = data[0].split()

    emails = []
    for e_id in email_ids:
        _, msg_data = mail.fetch(e_id, "(RFC822)")

        for content in msg_data:
            if isinstance(content, tuple):
                msg = email.message_from_bytes(content[1])
                msg_id = msg["Message-ID"]
                msg_ref = msg["References"]
                subject=decode_header(msg["Subject"])[0][0]
                sender=msg.get("From")

                if msg.is_multipart():
                    for part in msg.walk():
                        body=""
                        if part.get_content_type() == "text/plain":
                            body=part.get_payload(decode=True).decode()
                            break

                else: body=msg.get_payload(decode=True).decode()
                emails.append((msg_id, msg_ref, sender, subject, body))

    mail.logout()

    return emails

def replay_format(msg_id, msg_ref, sender, subject, body):

    reply_msg = MIMEMultipart()

    current_msg_id = msg_id
    reply_msg["In-Reply-To"] = current_msg_id
    current_references = msg_ref
    reply_msg["References"] = (
        f"{current_references} {current_msg_id}".strip()
        if current_references
        else current_msg_id
    )

    reply_msg["Subject"]=f"Re: {subject}"
    reply_msg["To"] = sender
    reply_msg["From"] = os.getenv("mail_name")
    reply_msg.attach(MIMEText(body, "plain", "utf-8"))

    return reply_msg

def draft_email(msg_id, msg_ref, sender, subject, body):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(os.getenv("mail_name"), os.getenv("mail_pass")) 

    drafted_reply = replay_format(msg_id, msg_ref, sender, subject, body)
    draft_bytes = drafted_reply.as_bytes()

    internal_date = imaplib.Time2Internaldate(time.time())

    mail.append("[Gmail]/Drafts", r"(\Draft)", internal_date, draft_bytes)
    print(f"Successfully appended draft reply to '{"[Gmail]/Drafts"}'.")