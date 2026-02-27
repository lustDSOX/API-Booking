from api.external.email_ticket import send_ticket

def test_email_sending():
    send_ticket(
        email_or_tg="anastasia.dnva@gmail.com",
        event_title="Занятие Анастасии Дунаевой",
        event_date="2026-05-20",
        event_desc="будем смотреть евангелион и играть в стендоф",
        ticket_id=12,
    )
  