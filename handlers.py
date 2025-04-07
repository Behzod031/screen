# handlers.py
import asyncio
from collections import defaultdict
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import CommandStart
from config import OPERATOR_ID, ALBUM_TIMEOUT
from services.ocr import extract_number_from_image
from services.bitrix import create_lead_in_bitrix
import pytesseract
import cv2
import numpy as np

album_buffer = defaultdict(list)
album_timer = {}


def register_handlers(dp: Dispatcher, bot: Bot):
    @dp.message(CommandStart())
    async def start(message: Message):
        await message.answer("📸 Yuboring — raqamlarni tekshiraman va operatorga yuboraman.")

    @dp.message(F.photo & F.media_group_id)
    async def handle_album_photo(message: Message):
        await message.answer("⏳ Foto(lar) qabul qilindi, qayta ishlanmoqda...")
        media_id = message.media_group_id
        album_buffer[media_id].append(message)
        if media_id in album_timer:
            album_timer[media_id].cancel()
        album_timer[media_id] = asyncio.get_event_loop().call_later(
            ALBUM_TIMEOUT, lambda: asyncio.create_task(process_album(media_id, bot))
        )

    @dp.message(F.photo)
    async def single_photo(message: Message):
        await message.answer("⏳ Foto qabul qilindi, qayta ishlanmoqda...")
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_data = await bot.download_file(file.file_path)
        image_bytes = file_data.read()

        number = extract_number_from_image(image_bytes)

        # DEBUG: Показать весь распознанный текст
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        gray = cv2.medianBlur(gray, 3)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        full_text = pytesseract.image_to_string(thresh, config='-c tessedit_char_whitelist=0123456789+ --psm 6')
        await message.answer(f"🧾 OCR natijasi:\n<code>{full_text.strip()}</code>")

        if number:
            bitrix_response = await create_lead_in_bitrix(number)
            if "error" in bitrix_response:
                await message.answer("❗️ Bitrix24 da lider yaratishda xatolik yuz berdi.")
            else:
                lead_id = bitrix_response.get("result")
                input_file = BufferedInputFile(image_bytes, filename="lead.jpg")
                await bot.send_photo(
                    chat_id=OPERATOR_ID,
                    photo=input_file,
                    caption=f"📞 <b>Yangi lid:</b> {number} (Lider #{lead_id})"
                )
                await message.answer("✅ Raqam topildi va Bitrix24 ga yuborildi.")
        else:
            input_file = BufferedInputFile(image_bytes, filename="no_number.jpg")
            await message.answer_photo(
                photo=input_file,
                caption="❗️ Raqam topilmadi yoki noto'g'ri formatda.\nIltimos, faqat <b>1 dona</b> to'g'ri formatdagi raqam yuboring.\nMasalan: <code>+998901234567</code>"
            )
