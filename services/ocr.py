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

    # Получаем весь текст
    text = pytesseract.image_to_string(img)
    print("DEBUG RAW OCR TEXT:\n", repr(text))

    # Находим все цифровые блоки длиной от 3 и более
    blocks = re.findall(r'\d{3,}', text)
    print("DEBUG DIGIT BLOCKS:", blocks)

    # Склеиваем подряд и ищем в получившейся строке 998 + 9 цифр
    all_digits = ''.join(blocks)
    print("DEBUG ALL DIGITS:", all_digits)

    match = re.search(r'(998\d{9})', all_digits)
    if match:
        final = '+' + match.group(1)
        print("DEBUG FINAL NUMBER:", final)
        return final

    print("DEBUG: номер не найден")
    return None
