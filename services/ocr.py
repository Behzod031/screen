# services/ocr.py
import re
import cv2
import numpy as np
import easyocr

# Глобальный объект для распознавания
reader = None


def init_easyocr():
    """Инициализирует EasyOCR с указанными языками (например, английский для номеров)."""
    global reader
    # Если номера пишутся латиницей, достаточно английского; можно добавить другие языки при необходимости
    reader = easyocr.Reader(['en'], gpu=False)


def extract_number_from_image(image_bytes: bytes) -> str | None:
    """
    Использует EasyOCR для извлечения номера телефона из изображения.
    Возвращает строку вида '+9989755526' или None, если номер не найден.
    """
    # Преобразуем байты в изображение OpenCV
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Преобразуем изображение в оттенки серого
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Можно добавить предобработку: увеличение контраста, шумоподавление и т.д.
    # Например, cv2.medianBlur(gray, 3) или adaptiveThreshold

    # Выполняем распознавание (detail=0 возвращает только строки текста)
    results = reader.readtext(gray, detail=0, paragraph=True)
    text = " ".join(results)
    print("DEBUG EasyOCR TEXT:", repr(text))

    # Ищем подстроку, начинающуюся с '+' и содержащую цифры, пробелы или дефисы
    match = re.search(r'\+\s*(\d[\d\s\-]{8,})', text)
    if match:
        candidate = match.group(0)  # например, "+998 97555 26"
        # Убираем всё, кроме '+' и цифр
        cleaned = re.sub(r'[^\d+]', '', candidate)
        if cleaned.startswith('+') and 9 <= len(cleaned) <= 15:
            return cleaned
    return None
