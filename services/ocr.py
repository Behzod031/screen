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

    text = pytesseract.image_to_string(img)
    print("DEBUG FULL RAW TEXT:\n", text)

    matches = re.findall(r'\+998[\d\s\-]{7,20}', text)
    candidates = []

    for match in matches:
        digits = re.sub(r'[^\d]', '', match)
        if digits.startswith('998') and len(digits) >= 12:
            number = '+' + digits[:12]
            candidates.append(number)

    if candidates:
        print("DEBUG candidates:", candidates)
        return candidates[0]  # или можно выбрать по длине, уникальности и т.д.

    print("DEBUG: номер не найден")
    return None
