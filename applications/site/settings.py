from tortoise import fields
from tortoise.models import Model
STATUS = (
    ('daily', "Daily"),
    ('weekly', "Weekly"),
    ('monthly', "Monthly"),
)

class UserSettings(Model):
    user  = fields.ForeignKeyField('models.User', on_delete=fields.CASCADE)  # Should reference users.id in your actual DB

    email_notifications = fields.BooleanField(default=False)
    whatsapp_notifications = fields.BooleanField(default=False)
    call_reminder_notifications = fields.BooleanField(default=False)
    daily_summery_alert = fields.BooleanField(default=False)
    performance_alert = fields.BooleanField(default=False)

    status = fields.CharField(choices=STATUS, default='daily', max_length=100)

    class Meta:
        table = "user_settings"

