# save as smtp_test.py and run: python smtp_test.py
import os, smtplib
from email.mime.text import MIMEText

host, port = "smtp.office365.com", 587
user, pw = os.getenv("SMTP_USER"), os.getenv("SMTP_PASS")

msg = MIMEText("SMTP ok")
msg["Subject"] = "Test"
msg["From"] = user
msg["To"] = user

with smtplib.SMTP(host, port, timeout=20) as s:
    s.starttls()
    s.login(user, pw)
    s.send_message(msg)

print("Sent")
