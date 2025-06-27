import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def configure_email_server(smtp_server, port, username, password):
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.login(username, password)
    return server

def compose_email(subject, body, from_addr, to_addr):
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    return msg

def attach_file(msg, file_path):
    attachment = open(file_path, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={file_path}')
    msg.attach(part)
    attachment.close()

def send_email(server, msg):
    server.send_message(msg)
    del msg

def send_email_with_attachments(smtp_server, smtp_port, 
                                email_address, email_password, 
                                to_address, 
                                subject, body, attachments):
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = to_address
    msg['Subject'] = subject
    # Use HTML encoding for better email appearance
    msg.attach(MIMEText(body, 'html', 'utf-8'))

    for attachment_path in attachments:
        filename = os.path.basename(attachment_path)
        with open(attachment_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={filename}')
            msg.attach(part)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_address, email_password)
        server.send_message(msg)