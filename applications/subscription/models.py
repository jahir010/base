from tortoise import models, fields

class Plan(models.Model):
    id = fields.IntField(pk=True)

    name = fields.CharField(max_length=100)
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    duration_days = fields.IntField()  # 30, 90, 365

    is_active = fields.BooleanField(default=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "plans"



from enum import Enum

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Subscription(models.Model):
    id = fields.IntField(pk=True)

    organization = fields.ForeignKeyField(
        "models.Organization",
        related_name="subscriptions"
    )

    plan = fields.ForeignKeyField(
        "models.Plan",
        related_name="subscriptions"
    )

    start_date = fields.DateField()
    end_date = fields.DateField()

    status = fields.CharEnumField(SubscriptionStatus)

    auto_renew = fields.BooleanField(default=False)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "subscriptions"
