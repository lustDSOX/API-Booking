from api.external.email_code import send_code

def test_email_sending():
    send_code("uraxara.sox@yandex.ru")