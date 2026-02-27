import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

from api.external.ticket_generator import generate_ticket_pdf

load_dotenv()
EMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('GMAIL_CODE')

async def send_ticket(email_or_tg, event_title, event_date, event_desc, ticket_id):
    current_dir = os.path.dirname(os.path.abspath(__file__))

    html_file_path = os.path.join(current_dir, 'ticket.html')

    pdf_filename = f"ticket_{ticket_id}.pdf"
    pdf_path = os.path.join(current_dir, pdf_filename)
    
    generate_ticket_pdf(
        ticket_id=ticket_id,
        user_info=email_or_tg,
        event_title=event_title,
        event_date_str=str(event_date),
        event_desc=event_desc,
        output_path=pdf_path
    )

    msg = EmailMessage()
    msg['Subject'] = f"Ваш билет на {event_title}"
    msg['From'] = f"API Booking <{EMAIL_ADDRESS}>"
    msg['To'] = email_or_tg

    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    html_content = html_content.replace('{{event_title}}', event_title)
    html_content = html_content.replace('{{event_date}}', event_date)
    html_content = html_content.replace('{{event_title_upper}}', event_title.upper())     

    msg.set_content(
        f"Здравствуйте!\n\n"
        f"Ваш билет на событие «{event_title}» успешно оформлен.\n"
        f"Дата проведения: {event_date}\n\n"
        f"Билет прикреплен к этому письму в формате PDF. "
        f"Пожалуйста, сохраните его и покажите на входе."
    )

    msg.add_alternative(html_content, subtype='html')

    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
            
        msg.add_attachment(
            pdf_data, 
            maintype='application', 
            subtype='pdf', 
            filename=pdf_filename
        )

    try:
        print(f"Отправка билета для {email_or_tg}...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Письмо с билетом успешно отправлено!")
    except Exception as e:
        print(f"Ошибка при отправке: {e}")
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)