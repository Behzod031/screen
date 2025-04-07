import re
import cv2
import numpy as np
import pytesseract
from config import TESSERACT_PATH

# Для Windows — вручную путь, для Linux — пропускаем
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

    matches = re.findall(r'\+\s*(\d[\d\s\-]*)', text)
    extras = re.findall(r'\b\d{2,4}\b', text)

    if matches:
        base_number = '+' + re.sub(r'[^\d]', '', matches[0])

        # ❗️ Отбрасываем всё, что не +998
        if not base_number.startswith('+998'):
            print("DEBUG: найден номер НЕ из Узбекистана, пропускаем:", base_number)
            return None

        print("DEBUG base_number:", base_number)

        extension = ''
        for extra in extras:
            cleaned_extra = re.sub(r'\D', '', extra)
            if cleaned_extra not in base_number and len(cleaned_extra) <= 4:
                extension = cleaned_extra
                break

        full_number = base_number + extension

        digits_only = re.sub(r'[^\d]', '', full_number)
        trimmed = '+' + digits_only[:12]
        print("DEBUG trimmed number:", trimmed)

        if 10 <= len(trimmed) <= 14:
            return trimmed
        else:
            print("DEBUG: trimmed номер всё ещё слишком длинный или короткий:", trimmed)

    return None
