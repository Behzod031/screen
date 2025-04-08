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

    # OCR без фильтров
    text = pytesseract.image_to_string(img)
    print("DEBUG RAW OCR TEXT:\n", repr(text))

    # Удаляем пробелы, переносы, тире и всё лишнее
    cleaned_text = re.sub(r'[\s\-]', '', text)
    digits_only = re.sub(r'[^\d]', '', cleaned_text)
    print("DEBUG CLEANED DIGITS:", digits_only)

    # Ищем 998 + 9 цифр подряд
    match = re.search(r'998\d{9}', digits_only)
    if match:
        final = '+' + match.group(0)
        print("DEBUG FINAL NUMBER:", final)
        return final

    print("DEBUG: номер не найден")
    return None
