import aiohttp
import logging
from config import BITRIX24_WEBHOOK_URL

logger = logging.getLogger(__name__)


async def create_lead_in_bitrix(phone_number: str, name: str = "From Telegram Bot") -> dict:
    """
    Теперь вместо лида создаём сделку в воронке "Контакт центр" (CATEGORY_ID=67).
    Номер телефона сохраняем в пользовательское поле UF_CRM_PHONE.

    ВНИМАНИЕ: Если ваше поле называется иначе, замените "UF_CRM_PHONE" на реальный код.
    Также убедитесь, что STAGE_ID ("C67:NEW") соответствует начальному этапу в этой воронке.
    """

    url = f"{BITRIX24_WEBHOOK_URL}crm.deal.add.json"
    data = {
        "fields": {
            "TITLE": f"Сделка из Instagram ({phone_number})",
            "CATEGORY_ID": 67,  # ID вашей воронки "Контакт центр"
            "STAGE_ID": "C67:NEW",  # Код начальной стадии в этой воронке (проверьте в настройках)
            "UF_CRM_PHONE": phone_number
        },
        "params": {
            "REGISTER_SONET_EVENT": "Y"
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            try:
                result = await response.json()
                return result
            except Exception as e:
                logger.error("Ошибка при разборе JSON: %s", e)
                return {"error": str(e)}
