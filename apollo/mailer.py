import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
from email import encoders
import os
import markdown

class EmailSender:
    def __init__(self, provider: str = "mock", smtp_config: dict = None):
        self.provider = provider
        self.smtp_config = smtp_config or {}

    def send_email(self, to_email: str, subject: str, body: str, attachment_path: str = None) -> bool:
        """
        Send an email.
        """
        if self.provider == "mock":
            return self._send_mock(to_email, subject, body, attachment_path)
        elif self.provider == "smtp":
            return self._send_smtp(to_email, subject, body, attachment_path)
        else:
            return self._send_mock(to_email, subject, body, attachment_path)

    def _send_mock(self, to_email: str, subject: str, body: str, attachment_path: str = None) -> bool:
        print("\n" + "="*60)
        print(f"📧 [MOCK EMAIL SENDER]")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        if attachment_path:
             print(f"Attachment: {attachment_path}")
        print(f"Body:\n{body}")
        print("="*60 + "\n")
        return True

    def _send_smtp(self, to_email: str, subject: str, body: str, attachment_path: str = None) -> bool:
        try:
            # Root container (mixed) for body + attachment
            msg = MIMEMultipart('mixed')
            msg['From'] = self.smtp_config.get('email')
            msg['To'] = to_email
            msg['Subject'] = subject

            # Alternative container for Text vs HTML (client chooses best)
            msg_alternative = MIMEMultipart('alternative')
            msg.attach(msg_alternative)

            # 1. Plain Text Version (Fallback)
            part_text = MIMEText(body, 'plain', 'utf-8')
            msg_alternative.attach(part_text)

            # 2. HTML Version (Preferred)
            # Convert Markdown -> HTML
            html_body = markdown.markdown(body)
            # Wrap in minimal CSS for nice fonts
            html_content = f"""
            <html>
              <body style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #333;">
                {html_body}
              </body>
            </html>
            """
            part_html = MIMEText(html_content, 'html', 'utf-8')
            msg_alternative.attach(part_html)

            # 3. Attachment (attached to root 'mixed')
            if attachment_path and os.path.exists(attachment_path):
                try:
                    with open(attachment_path, "rb") as f:
                        part = MIMEApplication(
                            f.read(),
                            Name=os.path.basename(attachment_path)
                        )
                    # After the file is closed
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                    msg.attach(part)
                    print(f"Attached file: {attachment_path}")
                except Exception as attach_err:
                     print(f"Error attaching file: {attach_err}")
            elif attachment_path:
                print(f"Warning: Attachment not found at {attachment_path}")

            smtp_server = self.smtp_config.get('server', 'smtp.gmail.com')
            smtp_port = int(self.smtp_config.get('port', 587))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(self.smtp_config.get('email'), self.smtp_config.get('password'))
            text = msg.as_string()
            server.sendmail(self.smtp_config.get('email'), to_email, text)
            server.quit()
            return True
        except Exception as e:
            print(f"SMTP Error: {e}")
            raise e
