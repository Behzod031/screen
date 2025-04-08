@dp.message(F.photo)
async def single_photo(message: Message):
    await message.answer("⏳ Foto qabul qilindi, OCR orqali tekshirilmoqda...")

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_data = await bot.download_file(file.file_path)
    image_bytes = file_data.read()

    number = extract_number_from_image(image_bytes)

    # Покажем весь текст, который распознал OCR
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    full_text = pytesseract.image_to_string(img)

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
            caption="❗️ Raqam topilmadi yoki noto'g'ri formatda.\nIltimos, faqat <b>+998</b> bilan boshlanadigan raqam yuboring.\nMasalan: <code>+998901234567</code>"
        )
