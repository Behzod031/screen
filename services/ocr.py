import re
import pytesseract
from config import TESSERACT_PATH
import numpy as np
import cv2

# Устанавливаем путь только если он задан
if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def extract_number_from_image(image_bytes: bytes) -> str | None:
    # Преобразуем байты в изображение
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Получаем сырой текст без жёсткой обработки
    raw_text = pytesseract.image_to_string(img)
    print("DEBUG FULL RAW TEXT:\n", raw_text)

    # Ищем всё, что похоже на +998 и 9 цифр, с любыми пробелами/дефисами
    matches = re.findall(r'\+998[\d\s\-]{7,15}', raw_text)
    for match in matches:
        # Очищаем от мусора, оставляем только цифры
        digits = re.sub(r'[^\d]', '', match)
        if digits.startswith('998') and len(digits) == 12:
            final = '+' + digits
            print("DEBUG FINAL NUMBER:", final)
            return final

    print("DEBUG: номер не найден")
    return None
