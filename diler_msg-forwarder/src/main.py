import os
import json
from dotenv import load_dotenv
from message_scraper import MessageScraper
from email_utils import send_email_with_attachments
import smtplib

load_dotenv()

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
WEBSITE_URL = os.getenv('DILER_URL')



def main():
    accounts_path = os.path.join(os.path.dirname(__file__), '../accounts.json')
    with open(accounts_path, encoding='utf-8') as f:
        accounts = json.load(f)

    for account in accounts:
        username = account.get('DILER_USERNAME')
        password = account.get('DILER_PASSWORD')
        to_addresses = account.get('TO_EMAIL_ADDRESS')
        if isinstance(to_addresses, str):
            to_addresses = [addr.strip() for addr in to_addresses.split(',')]

        print(f"Verarbeite Account: {username}")
        with MessageScraper(WEBSITE_URL, username, password) as scraper:
            unread_messages = scraper.get_unread_messages()
            for msg in unread_messages:
                subject = f"{msg['subject']} ({msg['date']})" if msg.get('date') else msg['subject']
                try:
                    send_email_with_attachments(
                        smtp_server=SMTP_SERVER,
                        smtp_port=SMTP_PORT,
                        email_address=EMAIL_ADDRESS,
                        email_password=EMAIL_PASSWORD,
                        to_address=to_addresses,
                        subject=subject,
                        body=msg['body'],
                        attachments=msg['attachments']
                    )
                    scraper.mark_message_as_read(msg['id'])
                except smtplib.SMTPAuthenticationError:
                    print("Invalid username or password. Please check your login credentials and try again.")
                except smtplib.SMTPException as e:
                    print("An error occurred:", e)
                    try:
                        send_email_with_attachments(
                            smtp_server=SMTP_SERVER,
                            smtp_port=SMTP_PORT,
                            email_address=EMAIL_ADDRESS,
                            email_password=EMAIL_PASSWORD,
                            to_address=to_addresses,
                            subject=subject,
                            body=msg['body'],
                            attachments=[]
                        )
                        scraper.mark_message_as_read(msg['id'])
                    except Exception as e:
                        raise Exception(f"Failed to send email without attachments: {e}")
                except Exception as e:
                    print(f"Failed to forward message {msg['id']}: {e}")

if __name__ == "__main__":
    main()