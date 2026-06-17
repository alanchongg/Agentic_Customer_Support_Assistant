from func import *
from mail_handler import *
from agentic import *

def main():
    unread_emails=get_unread_emails()

    for new_mails in unread_emails:
        msg_id, msg_ref, sender, subject, new_msg = new_mails
        reply=get_response(new_msg)
        draft_email(msg_id, msg_ref, sender, subject, reply)

if __name__ == "__main__":
    main()