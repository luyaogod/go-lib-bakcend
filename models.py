from tortoise.models import Model
from tortoise import fields

class Lib(Model):
    lib_name = fields.CharField(max_length=40,description="楼层名称")
    lib_id = fields.IntField(description="楼层id")

class Seat(Model):
    seat_id = fields.IntField(description='座位id')
    seat_key = fields.CharField(max_length=20,description="楼层Key")

    user: fields.ManyToManyRelation["User"] = \
        fields.ManyToManyField("models.User", related_name="seats", on_delete=fields.CASCADE, through="seat_user")

    morning_user: fields.ManyToManyRelation["User"] = \
        fields.ManyToManyField("models.User", related_name="morning_seats", on_delete=fields.CASCADE, through="morning_seat_user")

    lib: fields.ForeignKeyRelation[Lib] = fields.ForeignKeyField(
        "models.Lib", related_name="seats"
    )

class User(Model):
    username = fields.CharField(max_length=40, description="用户名", unique=True)
    uuid = fields.UUIDField()
    balance = fields.IntField(description="次数余额")
    seats: fields.ManyToManyRelation[Seat]
    morning_seats: fields.ManyToManyRelation[Seat]

class Task(Model):
    add_time = fields.DatetimeField(description="创建时间")
    wx_cookie = fields.TextField(description='微信cookie')
    user: fields.OneToOneRelation[User] = fields.OneToOneField(
        "models.User", on_delete=fields.OnDelete.CASCADE, related_name="book_task"
    )
    status = fields.IntField(description='wx_cookie：0失效 1有效', default=1)
    open = fields.BooleanField(description='关闭、开启',default=True)

class Task_Ret(Model):
    time = fields.DateField(description="创建时间")
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="task_rets"
    )
    status = fields.IntField(description='任务执行结果：0失败 1成功')

class Task_Pool(Model):
    task: fields.OneToOneRelation[Task] = fields.OneToOneField(
        "models.Task", on_delete=fields.OnDelete.CASCADE, related_name="task_pool"
    )

class Morning_Task_Pool(Model):
    user: fields.OneToOneRelation[User] = fields.OneToOneField(
        "models.User", on_delete=fields.OnDelete.CASCADE, related_name="morning_task_pool"
    )

class Morning_Task_Ret(Model):
    time = fields.DateField(description="创建时间")
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="morning_task_rets"
    )
    status = fields.IntField(description='任务执行结果：0失败 1成功')
