from tortoise.models import Model
from tortoise import fields

class Lib(Model):
    lib_name = fields.CharField(max_length=40,description="楼层名称")
    lib_id = fields.IntField(description="楼层id")

class Seat(Model):
    seat_id = fields.IntField(description='楼层id')
    seat_key = fields.CharField(max_length=20,description="楼层Key")

    user: fields.ManyToManyRelation["User"] = \
        fields.ManyToManyField("models.User", related_name="seats", on_delete=fields.CASCADE)

    lib: fields.ForeignKeyRelation[Lib] = fields.ForeignKeyField(
        "models.Lib", related_name="seats"
    )

class User(Model):
    username = fields.CharField(max_length=40, description="用户名", unique=True)
    uuid = fields.UUIDField()
    seats: fields.ManyToManyRelation[Seat]


