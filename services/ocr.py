import re
import pytesseract
import numpy as np
import cv2
from config import TESSERACT_PATH

if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def extract_number_from_image(image_bytes: bytes) -> str | None:
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Получаем текст с изображения
    text = pytesseract.image_to_string(img)
    print("DEBUG RAW OCR TEXT:\n", repr(text))

    # Убираем пробелы и дефисы, делаем всё одной строкой
    clean_text = text.replace('\n', ' ').replace('-', ' ').replace('\r', '')
    matches = re.findall(r'\+998[\d\s]{7,15}', clean_text)

    candidates = []
    for match in matches:
        digits = re.sub(r'[^\d]', '', match)
        if digits.startswith('998') and len(digits) == 12:
            number = '+' + digits
            candidates.append(number)

    if candidates:
        final = candidates[-1]  # ← берём ПОСЛЕДНИЙ найденный номер
        print("DEBUG FINAL NUMBER (last):", final)
        return final

    print("DEBUG: номер не найден")
    return None
