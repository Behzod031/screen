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

    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)

    custom_config = r'--oem 3 --psm 4'
    text = pytesseract.image_to_string(gray, config=custom_config)
    print("DEBUG RAW OCR TEXT:\n", repr(text))

    clean_text = text.replace('\n', ' ').replace('-', ' ').replace('–', ' ')
    parts = re.findall(r'[\d+]{7,}', clean_text)

    # Попробуем склеить подряд блоки, начинающиеся с +998 или 998
    joined = ""
    for i, part in enumerate(parts):
        joined += part

    # Вытаскиваем оттуда номер Узбекистана (12 цифр после 998)
    matches = re.findall(r'(?:\+?)998\d{9,12}', joined)
    if matches:
        digits = re.sub(r'[^\d]', '', matches[-1])
        if digits.startswith('998') and len(digits) >= 12:
            number = '+' + digits[:12]
            print("DEBUG FINAL NUMBER:", number)
            return number

    print("DEBUG: номер не найден")
    return None


