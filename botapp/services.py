from asgiref.sync import sync_to_async
from app.models import User, Organization, Region, OrganizationType, Language, InviteLink

@sync_to_async
def get_all_regions():
    return list(Region.objects.all())

@sync_to_async
def get_region_by_name(name):
    return Region.objects.filter(name_ru=name).first()

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
        language=Language.RU,
        telegram_id=data["telegram_id"],
    )

    token = data.get("invite_token")
    if token:
        invite = InviteLink.objects.filter(token=token).first()
        if invite:
            invite.used = True
            invite.used_by = user
            invite.save()