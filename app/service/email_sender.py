# ───── [2] Email Sender (Share) ──────────────────────────────────────────────────────
# send_email.py
import os
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain.tools import tool
from google.oauth2 import service_account
from googleapiclient.discovery import build

from langchain.tools import tool

@tool
def send_email_text(sender: str, password: str,
                    recipient: str, subject: str, html_body: str) -> str:
    """
    여행 계획표를 이메일로 공유합니다. 아래의 필요한 정보가 모두 포함되어야 합니다.
    - sender: 발신자 이메일.
    - password: 앱 비밀번호 또는 OAuth2 토큰.
    - recipient: 수신자 이메일
    - subject: 메일 제목
    - html_body: 본문(html 형식의 여행 계획서), 
    """
    msg = MIMEMultipart('alternative')
    msg['From']    = sender
    msg['To']      = recipient
    msg['Subject'] = subject

    # HTML 파트 추가
    part_html = MIMEText(html_body, 'html', _charset='utf-8')
    msg.attach(part_html)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

    return "여행 계획표를 이메일로 공유했습니다."

