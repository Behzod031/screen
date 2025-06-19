import platform

API_TOKEN = "7719820520:AAGy0QDOjOBSa76AhKkIpv_HE5JHc7THxKM"
OPERATOR_ID = 7112971881  # Telegram user_id оператора
ALBUM_TIMEOUT = 5         # Секунды ожидания перед обработкой альбома

# Универсальный путь до Tesseract (для Windows и Linux)
if platform.system() == "Windows":
    TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    TESSERACT_PATH = "/usr/bin/tesseract"

# Webhook для Bitrix24
BITRIX24_WEBHOOK_URL = "https://xonsaroy.bitrix24.ru/rest/57183/nurmhsapdkh117bh/"
