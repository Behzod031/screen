import re
import pytesseract
import numpy as np
import cv2
from config import TESSERACT_PATH

if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

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
    matches = re.findall(r'(?:\+?998|\b9\d)\s*\d{2,3}\s*\d{2,3}\s*\d{2,3}', clean_text)

    candidates = []
    for match in matches:
        digits = re.sub(r'[^\d]', '', match)
        if digits.startswith('998') and len(digits) == 12:
            number = '+' + digits
            candidates.append(number)
        elif digits.startswith('9') and len(digits) == 9:
            number = '+998' + digits
            candidates.append(number)

    if candidates:
        final = candidates[-1]
        print("DEBUG FINAL NUMBER:", final)
        return final

    print("DEBUG: номер не найден")
    return None
