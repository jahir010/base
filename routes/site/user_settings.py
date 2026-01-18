from fastapi import APIRouter, HTTPException, Depends, Form
from applications.user.models import User
from applications.site.settings import UserSettings
from app.auth import login_required

router = APIRouter(prefix="/user-settings", tags=["User Settings"])

STATUS_CHOICES = ("daily", "weekly", "monthly")


# -----------------------------
# Get user settings for logged-in user
# -----------------------------
@router.get("/", response_model=dict)
async def get_user_settings(user: User = Depends(login_required)):
    settings = await UserSettings.get_or_none(user=user)
    if not settings:
        # Create default settings if none exist
        settings = await UserSettings.create(user=user)

    return {
        "user_id": str(settings.user_id),
        "email_notifications": settings.email_notifications,
        "whatsapp_notifications": settings.whatsapp_notifications,
        "call_reminder_notifications": settings.call_reminder_notifications,
        "daily_summery_alert": settings.daily_summery_alert,
        "performance_alert": settings.performance_alert,
        "status": settings.status,
    }


# -----------------------------
# Create or update user settings using Form
# -----------------------------
@router.post("/", response_model=dict)
async def create_or_update_user_settings(
    email_notifications: bool = Form(False),
    whatsapp_notifications: bool = Form(False),
    call_reminder_notifications: bool = Form(False),
    daily_summery_alert: bool = Form(False),
    performance_alert: bool = Form(False),
    status: str = Form("daily"),
    user: User = Depends(login_required)
):
    # Validate status
    if status not in STATUS_CHOICES:
        raise HTTPException(status_code=400, detail="Invalid status choice")

    data = {
        "email_notifications": email_notifications,
        "whatsapp_notifications": whatsapp_notifications,
        "call_reminder_notifications": call_reminder_notifications,
        "daily_summery_alert": daily_summery_alert,
        "performance_alert": performance_alert,
        "status": status,
    }

    # Fetch existing settings
    settings = await UserSettings.get_or_none(user=user)

    if settings:
        # Update existing settings
        await settings.update_from_dict(data)
        await settings.save()
        await settings.fetch_related('user')  # Refresh related user
    else:
        # Create new settings
        settings = await UserSettings.create(user=user, **data)
        await settings.fetch_related('user')

    return {
        "user_id": str(settings.user.id),
        "email_notifications": settings.email_notifications,
        "whatsapp_notifications": settings.whatsapp_notifications,
        "call_reminder_notifications": settings.call_reminder_notifications,
        "daily_summery_alert": settings.daily_summery_alert,
        "performance_alert": settings.performance_alert,
        "status": settings.status,
    }
