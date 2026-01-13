import smtplib
from email.message import EmailMessage

def send_email(filename, success, config, logger):
    msg = EmailMessage()
    status = "SUCCESS" if success else "FAILURE"
    msg.set_content(f"File processing {status} for: {filename}")
    msg['Subject'] = f"[Automation] {status}: {filename}"
    msg['From'] = config['EMAIL']['sender']
    msg['To'] = config['EMAIL']['receiver']

    try:
        with smtplib.SMTP(config['EMAIL']['smtp_server'], int(config['EMAIL']['smtp_port'])) as smtp:
            smtp.starttls()
            smtp.login(config['EMAIL']['username'], config['EMAIL']['password'])
            smtp.send_message(msg)
        logger.info(f"Email sent for {filename}")
    except Exception as e:
        logger.error(f"Email error: {str(e)}")