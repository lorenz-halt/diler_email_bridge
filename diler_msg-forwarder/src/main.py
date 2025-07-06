import os
from dotenv import load_dotenv
from message_scraper import MessageScraper
from email_utils import send_email_with_attachments
import smtplib

load_dotenv()

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
TO_EMAIL_ADDRESS = os.getenv('TO_EMAIL_ADDRESS')
# Support for multiple email addresses
# If TO_EMAIL_ADDRESS is a comma-separated string, split it into a list.
TO_EMAIL_ADDRESSES = [addr.strip() for addr in TO_EMAIL_ADDRESS.split(',')] if TO_EMAIL_ADDRESS else []
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))

WEBSITE_URL = os.getenv('DILER_URL')
WEBSITE_USERNAME = os.getenv('DILER_USERNAME')
WEBSITE_PASSWORD = os.getenv('DILER_PASSWORD')


def main():
    with MessageScraper(WEBSITE_URL, WEBSITE_USERNAME, WEBSITE_PASSWORD) as scraper:
        unread_messages = scraper.get_unread_messages()
        for msg in unread_messages:
            try:
                send_email_with_attachments(
                    smtp_server=SMTP_SERVER,
                    smtp_port=SMTP_PORT,
                    email_address=EMAIL_ADDRESS,
                    email_password=EMAIL_PASSWORD,
                    to_address=TO_EMAIL_ADDRESSES,
                    subject=msg['subject'],
                    body=msg['body'],
                    attachments=msg['attachments']
                )
                scraper.mark_message_as_read(msg['id'])
            except smtplib.SMTPAuthenticationError: # Handling an authentication error if the server rejects our login credentials.
                print("Invalid username or password. Please check your login credentials and try again.")
            except smtplib.SMTPException as e: # Handling any other SMTP errors that may occur.
                print("An error occurred:", e) # Printing the error message if an error occurs.
                try:
                    send_email_with_attachments(
                        smtp_server=SMTP_SERVER,
                        smtp_port=SMTP_PORT,
                        email_address=EMAIL_ADDRESS,
                        email_password=EMAIL_PASSWORD,
                        to_address=TO_EMAIL_ADDRESSES,
                        subject=msg['subject'],
                        body=msg['body'],
                        attachments=[]  # Sending email without attachments if the first attempt fails
                    )
                    scraper.mark_message_as_read(msg['id'])
                except Exception as e:
                    raise Exception(f"Failed to send email without attachments: {e}")
            except Exception as e:
                print(f"Failed to forward message {msg['id']}: {e}")

if __name__ == "__main__":
    main()