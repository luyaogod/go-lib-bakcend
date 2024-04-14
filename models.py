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
    balance = fields.IntField(description="次数余额")
    seats: fields.ManyToManyRelation[Seat]

class Task(Model):
    add_time = fields.DatetimeField(description="创建时间")
    wx_cookie = fields.TextField(description='微信cookie')
    user: fields.OneToOneRelation[User] = fields.OneToOneField(
        "models.User", on_delete=fields.OnDelete.CASCADE, related_name="book_task"
    )
    status = fields.IntField(description='任务状态：0关闭 1待执行(有效) 2执行成功 3执行失败 4失效',default=1)




