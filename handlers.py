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
import html

album_buffer = defaultdict(list)
album_timer = {}

def register_handlers(dp: Dispatcher, bot: Bot):
    @dp.message(CommandStart())
    async def start(message: Message):
        await message.answer("📸 Foto yuboring — raqamni aniqlayman va Bitrix24'ga yuboraman.")

    @dp.message(F.photo & F.media_group_id)
    async def handle_album_photo(message: Message):
        await message.answer("⏳ Foto(lar) qabul qilindi, OCR ishlamoqda...")
        media_id = message.media_group_id
        album_buffer[media_id].append(message)
        if media_id in album_timer:
            album_timer[media_id].cancel()
        album_timer[media_id] = asyncio.get_event_loop().call_later(
            ALBUM_TIMEOUT, lambda: asyncio.create_task(process_album(media_id, bot))
        )

    @dp.message(F.photo)
    async def single_photo(message: Message):
        await message.answer("⏳ Foto qabul qilindi, OCR orqali tekshirilmoqda...")
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_data = await bot.download_file(file.file_path)
        image_bytes = file_data.read()

        number = extract_number_from_image(image_bytes)

        # Отображаем OCR текст с защитой от спецсимволов
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        raw_text = pytesseract.image_to_string(img)
        safe_text = html.escape(raw_text.strip())

        await message.answer(f"🧾 OCR natijasi:\n<code>{safe_text}</code>")

        if number:
            bitrix_response = await create_lead_in_bitrix(number)
            if "error" in bitrix_response:
                await message.answer("❗️ Bitrix24 bilan xatolik.")
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
                caption="❗️ Raqam topilmadi yoki noto‘g‘ri formatda.\nIltimos, raqamni <b>+998</b> bilan yuboring.\nMasalan: <code>+998901234567</code>"
            )
async def process_album(media_id, bot: Bot):
    messages = album_buffer.pop(media_id, [])
    album_timer.pop(media_id, None)

    results = []
    not_found = []

    for idx, msg in enumerate(messages, start=1):
        user_id = msg.from_user.id
        photo = msg.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_data = await bot.download_file(file.file_path)
        image_bytes = file_data.read()

        number = extract_number_from_image(image_bytes)
        if number:
            bitrix_response = await create_lead_in_bitrix(number)
            if "error" in bitrix_response:
                error_desc = bitrix_response.get("error_description", "Xatolik")
                results.append(f"{number} (foto {idx}, xato: {error_desc})")
            else:
                lead_id = bitrix_response.get("result")
                results.append(f"{number} (foto {idx}, Lider #{lead_id})")
        else:
            not_found.append((idx, image_bytes, user_id))

    if results:
        text_results = "\n".join(results)
        await bot.send_message(OPERATOR_ID, f"📞 <b>Yangi lidlar:</b>\n{text_results}")
    else:
        await bot.send_message(OPERATOR_ID, "❗️ Hech qanday raqam topilmadi.")

    for idx, img, user_id in not_found:
        input_file = BufferedInputFile(img, filename=f"no_number_{idx}.jpg")
        await bot.send_photo(
            chat_id=user_id,
            photo=input_file,
            caption=f"❗️ Raqam topilmadi yoki noto'g'ri formatda (foto {idx}).\nMasalan: <code>+998901234567</code>"
        )
