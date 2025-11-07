import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_reset_email(email: str, reset_link: str):
    """
    Send password reset email using Gmail SMTP
    """
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")
    
    if not sender_email or not sender_password:
        print(" SMTP credentials not configured in .env file")
        return False

    # Create message
    message = MIMEMultipart("alternative")
    message["Subject"] = "🔐 Password Reset Request - News Intelligence Platform"
    message["From"] = f"News Intelligence <{sender_email}>"
    message["To"] = email
    
    # HTML email body
    html = f"""
    <html>
      <head>
        <style>
          body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
          }}
          .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
          }}
          .header {{
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
          }}
          .content {{
            background-color: white;
            padding: 30px;
            border-radius: 0 0 5px 5px;
          }}
          .button {{
            display: inline-block;
            padding: 12px 30px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
          }}
          .footer {{
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 12px;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h2>Password Reset Request</h2>
          </div>
          <div class="content">
            <p>Hello,</p>
            <p>We received a request to reset your password for your News Intelligence Platform account.</p>
            <p>Click the button below to reset your password:</p>
            <center>
              <a href="{reset_link}" class="button">Reset Password</a>
            </center>
            <p><strong>Important:</strong> This link will expire in 15 minutes for security reasons.</p>
            <p>If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>
            <hr>
            <p style="font-size: 12px; color: #666;">
              If the button doesn't work, copy and paste this link into your browser:<br>
              <a href="{reset_link}">{reset_link}</a>
            </p>
          </div>
          <div class="footer">
            <p>This is an automated email. Please do not reply.</p>
            <p>&copy; 2025 News Intelligence Platform. All rights reserved.</p>
          </div>
        </div>
      </body>
    </html>
    """
    
    part = MIMEText(html, "html")
    message.attach(part)
    
    try:
        # Connect to Gmail SMTP server
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
        
        print(f"Password reset email sent successfully to {email}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print(" SMTP Authentication failed. Check your email/password.")
        return False
    except smtplib.SMTPException as e:
        print(f" SMTP error occurred: {e}")
        return False
    except Exception as e:
        print(f" Failed to send email: {e}")
        return False
