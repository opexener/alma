import os
import smtplib
from typing import List, Optional
from config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

class EmailSender:
    def send_email(self, sender: str, recipients: List[str], subject: str, 
                  body: str, attachment_path: Optional[str] = None):
        """
        Send an email to one or more recipients
        """
        # Create an email
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        # Add attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as file:
                attachment = MIMEApplication(file.read(), Name=os.path.basename(attachment_path))
                attachment['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                msg.attach(attachment)
        
        # Send email
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                if SMTP_USERNAME and SMTP_PASSWORD:
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

# Initialize email sender
email_sender = EmailSender()

def send_prospect_confirmation(prospect_email: str, first_name: str, last_name: str):
    """
    Send the confirmation email to prospect
    """
    sender = "no-reply@company.com"
    subject = "Thank you for your application"
    body = f"""
    Dear {first_name} {last_name},
    
    Thank you for submitting your application. We have received your information and will review it shortly.
    
    Best regards,
    The Company Team
    """
    
    return email_sender.send_email(sender, [prospect_email], subject, body)


def send_attorney_notification(attorney_email: str,
                              prospect_first_name: str, prospect_last_name: str, 
                              prospect_email: str, resume_path: str):
    """
    Send notification email to attorney
    """
    sender = "leads@company.com"
    subject = f"New Lead: {prospect_first_name} {prospect_last_name}"
    body = f"""
    A new lead has been submitted:
    
    Name: {prospect_first_name} {prospect_last_name}
    Email: {prospect_email}
    
    Please review the attached resume.
    """
    
    return email_sender.send_email(sender, [attorney_email], subject, body, resume_path)