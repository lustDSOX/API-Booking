import os
import smtplib
import random
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()
EMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('GMAIL_CODE')

def send_code(email):
    otp_code = str(random.randint(1000, 9999))
    otp_ttl = "5"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_file_path = os.path.join(current_dir, 'code.html')
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    html_content = html_content.replace('{{otp_code}}', otp_code)
    html_content = html_content.replace('{{otp_ttl}}', otp_ttl)

    msg = EmailMessage()
    msg['Subject'] = f"Код подтверждения: {otp_code}"
    msg['From'] = f"API Booking <{EMAIL_ADDRESS}>"
    msg['To'] = email

    msg.set_content(
        f"Ваш код подтверждения API Booking: {otp_code}. "
        f"Никому его не сообщайте. Если это были не вы, проигнорируйте письмо."
    )

    msg.add_alternative(html_content, subtype='html')

    try:
        print(f"Отправка письма с кодом {otp_code}...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Письмо успешно отправлено!")
        return otp_code
    except Exception as e:
        print(f"Ошибка: {e}")