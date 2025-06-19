import aiohttp
import logging
from config import BITRIX24_WEBHOOK_URL

logger = logging.getLogger(__name__)


async def create_lead_in_bitrix(phone_number: str, name: str = "From Telegram Bot") -> dict:
    """
    1. Создаёт контакт с телефоном
    2. Создаёт сделку и привязывает этот контакт
    """

    base_url = BITRIX24_WEBHOOK_URL.rstrip('/')

    # 1. Создаём контакт
    contact_data = {
        "fields": {
            "NAME": name,
            "PHONE": [{"VALUE": phone_number, "VALUE_TYPE": "WORK"}]
        }
    }

    async with aiohttp.ClientSession() as session:
        # Создание контакта
        async with session.post(f"{base_url}/crm.contact.add.json", json=contact_data) as resp1:
            contact_result = await resp1.json()
            print("CONTACT RESPONSE:", contact_result)

            if "result" not in contact_result:
                return {"error": "Не удалось создать контакт", "details": contact_result}

            contact_id = contact_result["result"]

        # 2. Создаём сделку, привязывая контакт
        deal_data = {
            "fields": {
                "TITLE": f"Сделка из Telegram ({phone_number})",
                "CATEGORY_ID": 67,
                "STAGE_ID": "C67:NEW",
                "CONTACT_ID": contact_id
            },
            "params": {
                "REGISTER_SONET_EVENT": "Y"
            }
        }

        async with session.post(f"{base_url}/crm.deal.add.json", json=deal_data) as resp2:
            deal_result = await resp2.json()
            print("DEAL RESPONSE:", deal_result)
            return deal_result
