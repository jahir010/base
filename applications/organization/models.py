from tortoise import fields, models
from applications.user.models import User
from applications.subscription.models import Subscription



class Organization(models.Model):
    id = fields.IntField(pk=True)

    name = fields.CharField(max_length=150, unique=True)

    is_active = fields.BooleanField(default=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    users: fields.ReverseRelation["User"]
    subscription: fields.ReverseRelation["Subscription"]

    class Meta:
        table = "organizations"
