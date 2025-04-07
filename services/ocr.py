import re
import cv2
import numpy as np
import pytesseract
from config import TESSERACT_PATH

if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def extract_number_from_image(image_bytes: bytes) -> str | None:
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    gray = cv2.medianBlur(gray, 3)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    custom_config = r'-c tessedit_char_whitelist=0123456789+ --psm 6'
    text = pytesseract.image_to_string(thresh, config=custom_config)
    print("DEBUG OCR TEXT:", repr(text))

    # Найдём первую подстроку, начинающуюся с +998
    match = re.search(r'\+998[\d\s\-]{7,}', text)
    if match:
        raw = match.group(0)
        digits = re.sub(r'[^\d]', '', raw)

        # Ищем вхождение 998 + 9 цифр
        match_digits = re.search(r'998\d{9}', digits)
        if match_digits:
            final = '+' + match_digits.group(0)
            print("DEBUG trimmed number:", final)
            return final

    print("DEBUG: корректный +998 номер не найден")
    return None
