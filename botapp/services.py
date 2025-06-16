from collections import defaultdict

from asgiref.sync import sync_to_async

from app.enums import ReceiptStatus, ReceiptType, UserType
from app.models import User, Organization, Region, OrganizationType, InviteLink, Receipt, Product

from bs4 import BeautifulSoup
import requests

import os
from datetime import datetime
from aiogram import Bot
from aiogram.types import PhotoSize
import aiofiles

MEDIA_ROOT = "media/receipts"


@sync_to_async
def get_all_regions():
    return list(Region.objects.all())

@sync_to_async
def get_region_by_name(name):
    return Region.objects.filter(name_ru=name).first()

@sync_to_async
def get_organization_by_name(name):
    return Organization.objects.filter(name=name).first()

@sync_to_async
def get_registered_user(telegram_id: int):
    return User.objects.filter(telegram_id=telegram_id).first()

@sync_to_async
def get_active_invite_link(token: str):
    return InviteLink.objects.filter(token=token, used=False).first()

@sync_to_async
def save_user(data):
    organization_id = data.get("organization_id")
    user_type = data["user_type"]

    if not organization_id:
        organization_name = data["organization"].strip()
        region_id = data["region_id"]
        organization = Organization.objects.filter(name=organization_name).first()
        if not organization:
            org_type = OrganizationType.MEDICAL_INSTITUTION if user_type == "doctor" else OrganizationType.PHARMACY
            organization = Organization.objects.create(
                name=organization_name,
                type=org_type,
                region_id=region_id
            )
        organization_id = organization.id

    user = User.objects.create(
        full_name=data["full_name"],
        user_type=user_type,
        organization_id=organization_id,
        phone=data["phone"],
        is_active=True,
        telegram_id=data["telegram_id"],
        language=data["lang"]
    )

    token = data.get("invite_token")
    if token:
        invite = InviteLink.objects.filter(token=token).first()
        if invite:
            invite.used = True
            invite.used_by = user
            invite.save()

    return user


async def save_receipt(photo_saved_path, ofd_url, user, status=None):
    if status is None:
        status = ReceiptStatus.PENDING.value

    items = []
    total_amount = None
    total_quantity = None
    if ofd_url:
        try:
            items = await parse_ofd_page(ofd_url)
            total_amount = sum(item['price_sum'] for item in items)
            total_quantity = sum(item['qty'] for item in items)
            if total_quantity > 0:
                status = ReceiptStatus.APPROVED.value
        except Exception as e:
            print(f"Ошибка при парсинге OфД: {e}")

    receipt = Receipt.objects.create(
        photo=photo_saved_path,
        ofd_url=ofd_url,
        items=items if items else None,
        amount=total_amount,
        quantity=total_quantity,
        type=ReceiptType.CHECK.value if user.user_type == UserType.PHARMACIST.value else ReceiptType.PRESCRIPTION.value,
        user_id=user.id,
        organization_id=user.organization_id,
        status=status,
    )
    return receipt

# def extract_qr_from_photo(photo_path: str):
#     qreader = QReader()
#     image = cv2.cvtColor(cv2.imread(photo_path), cv2.COLOR_BGR2RGB)
#     if image is None:
#         return None
#
#     decoded_text = qreader.detect_and_decode(image=image)
#     print(decoded_text)
#     # if bbox is not None and data:
#     #     return data
#     return None


async def parse_ofd_page(ofd_url: str):
    response = requests.get(ofd_url)
    html = response.text

    soup = BeautifulSoup(html, "lxml")

    aggregated_items = defaultdict(lambda: {"qty": 0, "price_sum": 0.0})

    product_rows = soup.select("table.products-tables tbody tr.products-row")
    for row in product_rows:
        cols = row.find_all("td")
        if len(cols) < 3:
            continue

        name = cols[0].get_text(strip=True)
        qty = int(cols[1].get_text(strip=True))
        price_sum = float(cols[2].get_text(strip=True).replace(",", "").replace(" ", ""))

        if await Product.objects.filter(name=name).aexists():
            aggregated_items[name]["qty"] += qty
            aggregated_items[name]["price_sum"] += price_sum

    items = [
        {"name": name, "qty": data["qty"], "price_sum": data["price_sum"]}
        for name, data in aggregated_items.items()
    ]

    return items


async def save_photo_to_storage(bot: Bot, photo: PhotoSize, user_id: int) -> str:
    filename = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    saved_path = os.path.join(MEDIA_ROOT, filename)

    os.makedirs(MEDIA_ROOT, exist_ok=True)

    file = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file.file_path)

    # Прочитать буфер синхронно через executor
    import asyncio
    loop = asyncio.get_running_loop()
    content = await loop.run_in_executor(None, file_bytes.read)

    async with aiofiles.open(saved_path, "wb") as out_file:
        await out_file.write(content)

    return saved_path
