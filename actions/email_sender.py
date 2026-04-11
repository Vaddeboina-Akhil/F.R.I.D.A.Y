import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


# Gmail credentials
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"

# Email contacts directory
CONTACTS = {
    "mom": "mom@gmail.com",
    "dad": "dad@gmail.com",
    "friend": "friend@gmail.com"
}


def send_email(to_email, subject, body):
    """
    Send an email via Gmail SMTP.
    
    Args:
        to_email (str): Recipient's email address
        subject (str): Email subject
        body (str): Email body text
    
    Returns:
        tuple: (success: bool, response: str)
    """
    try:
        # Create SSL context
        context = ssl.create_default_context()
        
        # Create message
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = to_email
        message["Subject"] = subject
        
        # Attach body as plain text
        message.attach(MIMEText(body, "plain"))
        
        # Send email via Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, message.as_string())
        
        return True, "Email sent boss."
    
    except smtplib.SMTPAuthenticationError:
        error_msg = "Failed to send email: Authentication error. Check your credentials boss."
        return False, error_msg
    except smtplib.SMTPException as e:
        error_msg = f"Failed to send email: {str(e)}"
        return False, error_msg
    except Exception as e:
        error_msg = f"Failed to send email: {str(e)}"
        return False, error_msg


def get_contact_email(name):
    """
    Get a contact's email address by name.
    
    Args:
        name (str): Contact name
    
    Returns:
        str: Email address if found, None otherwise
    """
    return CONTACTS.get(name.lower().strip(), None)


def send_email_to_contact(contact_name, subject, body):
    """
    Send an email to a named contact.
    
    Args:
        contact_name (str): Name of the contact
        subject (str): Email subject
        body (str): Email body
    
    Returns:
        tuple: (success: bool, response: str)
    """
    contact_name = contact_name.lower().strip()
    
    if contact_name in CONTACTS:
        return send_email(CONTACTS[contact_name], subject, body)
    
    return False, f"I don't have {contact_name}'s email boss."
