import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib.colors import HexColor, black
from reportlab.lib.utils import ImageReader


def generate_ticket_pdf(ticket_id, user_info, event_title, event_date_str, event_desc, output_path="ticket.pdf"):
    # ШРИФТ (Montserrat с кириллицей)
    font_path = os.path.join(os.path.dirname(__file__), "Montserrat-Regular.ttf")
    try:
        pdfmetrics.registerFont(TTFont("Montserrat", font_path))
    except Exception:
        raise RuntimeError(
            f"Шрифт не найден по пути {font_path}. Поместите Montserrat-Regular.ttf рядом со скриптом."
        )

    width, height = A4  # портрет
    c = canvas.Canvas(output_path, pagesize=portrait(A4))

    # Фон — почти белый с легким серым оттенком
    c.setFillColor(HexColor("#F9F9F9"))
    c.rect(0, 0, width, height, stroke=0, fill=1)

    # Легкая текстура точек
    c.setFillColor(HexColor("#D3D3D3"))
    c.setStrokeColor(HexColor("#D3D3D3"))
    c.setLineWidth(0.4)
    for i in range(120):
        x = (i * 37) % width
        y = (height - 40 - (i * 53) % int(height - 80))
        c.circle(x, y, 0.4, stroke=1, fill=1)

    margin = 35

    # Верхняя картинка
    image_path = os.path.join(os.path.dirname(__file__), "top_image.jpg")
    if os.path.exists(image_path):
        img = ImageReader(image_path)
        img_w, img_h = img.getSize()
        max_w, max_h = width - 2 * margin, 110
        scale = min(max_w / img_w, max_h / img_h)
        draw_w, draw_h = img_w * scale, img_h * scale
        img_x = (width - draw_w) / 2
        img_y = height - margin - draw_h
        c.drawImage(img, img_x, img_y, width=draw_w, height=draw_h, mask="auto")
        top_y = img_y - 20
    else:
        top_y = height - margin - 40

    # Тонкая пунктирная линия под верхней частью
    c.setStrokeColor(black)
    c.setLineWidth(1)
    c.setDash(6, 3)
    c.line(margin, top_y, width - margin, top_y)
    c.setDash()

    # Линия с данными заказа
    c.setFillColor(black)

    # event_title жирнее (больше кегль + caps)
    base_left = margin
    y_pos = top_y - 24

    order_part = f"order #{ticket_id:03d} for "
    title_part = f"\"{event_title.upper()}\""

    # обычный текст
    c.setFont("Montserrat", 11)
    c.setFillColor(black)
    c.drawString(base_left, y_pos, order_part)

    # «жирный» только для title_part за счёт многократного рисования
    title_x = base_left + c.stringWidth(order_part, "Montserrat", 11)
    c.setFont("Montserrat", 12)
    for dx, dy in [(0, 0), (0.3, 0), (0, 0.3), (0.3, 0.3)]:
        c.drawString(title_x + dx, y_pos + dy, title_part)

    # event_date_str визуально выделяем небольшим бэйджем
    c.setFont("Montserrat", 10)
    date_text = event_date_str
    date_w = c.stringWidth(date_text, "Montserrat", 10)
    date_x = margin
    date_y = top_y - 42
    c.setFillColor(HexColor("#000000"))
    c.rect(date_x - 4, date_y - 3, date_w + 8, 16, stroke=0, fill=1)
    c.setFillColor(HexColor("#FFFFFF"))
    c.drawString(date_x, date_y, date_text)

    # Пунктирная линия под заголовком
    line_y = top_y - 58
    c.setStrokeColor(black)
    c.setLineWidth(1.2)
    c.setDash(6, 3)
    c.line(margin, line_y, width - margin, line_y)

    # Шапка таблицы
    c.setDash()
    c.setFillColor(black)
    c.setFont("Montserrat", 11)
    c.drawString(margin, line_y - 24, "QTY")
    c.drawString(margin + 40, line_y - 24, "ITEM")

    # Пунктир под шапкой
    header_bottom_y = line_y - 32
    c.setDash(6, 3)
    c.line(margin, header_bottom_y, width - margin, header_bottom_y)
    c.setDash()

    # Список ITEM
    list_top_y = header_bottom_y - 22
    c.setFont("Montserrat", 11)
    current_y = list_top_y

    base_lines = []
    raw = event_desc.replace("\n", " ")
    separators = [".", ",", ";"]
    temp = ""
    for ch in raw:
        if ch in separators:
            if temp.strip():
                base_lines.append(temp.strip())
            temp = ""
        else:
            temp += ch
    if temp.strip():
        base_lines.append(temp.strip())
    if not base_lines and raw:
        base_lines = [raw]

    # Нормализуем длину строк
    normalized_lines = []
    max_width = width - margin - 80
    for ln in base_lines:
        words = ln.split()
        line = ""
        for w in words:
            test = (line + " " + w).strip()
            if c.stringWidth(test, "Montserrat", 11) <= max_width:
                line = test
            else:
                if line:
                    normalized_lines.append(line)
                line = w
        if line:
            normalized_lines.append(line)

    # Рисуем максимум 12 строк
    visible_lines = normalized_lines[:12]
    for idx, ln in enumerate(visible_lines, start=1):
        qty_str = f"{idx:02d}"
        c.drawString(margin, current_y, qty_str)
        c.drawString(margin + 40, current_y, ln.upper())
        current_y -= 22

    last_row_y = current_y + 10

    # Нижняя пунктирная линия
    c.setDash(6, 3)
    c.line(margin, last_row_y - 10, width - margin, last_row_y - 10)
    c.setDash()

    # ITEM COUNT
    c.setFont("Montserrat", 11)
    c.setFillColor(black)
    c.drawString(margin, last_row_y - 28, "ITEM COUNT:")
    c.drawRightString(width - margin, last_row_y - 28, str(len(visible_lines)))


    # Инструкция по использованию QR-кода
    info_y = last_row_y - 70
    c.setFont("Montserrat", 9)
    c.setFillColor(black)
    c.drawString(margin, info_y, "QR-код ниже необходимо предъявить на входе.")
    c.drawString(margin, info_y - 13, "Не передавайте и не пересылайте его третьим лицам.")
    c.drawString(margin, info_y - 26, "По этому коду может пройти только один человек один раз.")

    # QR‑код по центру внизу
    qr_value = f"TICKET:{ticket_id}"
    qr_code = createBarcodeDrawing("QR", value=qr_value, width=110, height=110)
    qr_x = (width - 110) / 2
    qr_y = margin + 40
    qr_code.drawOn(c, qr_x, qr_y)

    if user_info:
        c.setFont("Montserrat", 9)
        c.setFillColor(black)
        # центрируем под QR-кодом
        footer_text = f"ПОЛЬЗОВАТЕЛЬ: {user_info}"
        text_w = c.stringWidth(footer_text, "Montserrat", 9)
        footer_x = (width - text_w) / 2
        footer_y = qr_y - 20  # немного ниже нижнего края QR
        c.drawString(footer_x, footer_y, footer_text)

    c.showPage()
    c.save()