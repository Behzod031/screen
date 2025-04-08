import re
import cv2
import numpy as np
import pytesseract
from config import TESSERACT_PATH

if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def extract_number_from_image(image_bytes: bytes) -> str | None:
    import re
    import numpy as np
    import cv2
    import pytesseract
    from config import TESSERACT_PATH

    if TESSERACT_PATH:
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    gray = cv2.medianBlur(gray, 3)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    custom_config = r'-c tessedit_char_whitelist=0123456789+ --psm 6'
    raw_text = pytesseract.image_to_string(thresh, config=custom_config)
    print("DEBUG OCR TEXT:", repr(raw_text))

    # Убираем пробелы и дефисы, делим на "блоки"
    cleaned = raw_text.replace('\n', ' ').replace('-', ' ')
    blocks = re.findall(r'\d{5,}', cleaned)
    print("DEBUG blocks:", blocks)

    # Ищем блок, начинающийся с 998 и длиной от 9 до 12
    for block in blocks:
        digits = re.sub(r'\D', '', block)
        if digits.startswith('998') and 11 <= len(digits) <= 12:
            result = '+' + digits
            print("DEBUG final number:", result)
            return result

    print("DEBUG: номер не найден")
    return None

