from tortoise import fields

from zhenxun.services.db_context import Model


class OperatorCollect(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增id"""
    user_id = fields.CharField(255)
    """用户id"""
    operators = fields.JSONField(default={})
    """干员列表"""
    ticket = fields.IntField(default=0)
    """黄票数量"""
    draw_count = fields.IntField(default=0)
    """抽卡次数"""
    six_guarantee_count = fields.IntField(default=0)  # 记录保底
    """距离上次保底已抽次数"""
    draw_six_record = fields.TextField()  # 记录六星抽卡记录
    """记录六星抽卡记录"""

    class Meta: # type: ignore  # type: ignore
        table = "operator_collect"
        table_description = "群员收集干员的数据表"

    @classmethod
    async def operator_record(cls, user_id: str, operator: str):
        """干员收集"""
        if me := await cls.get_or_none(user_id=user_id):
            operators_json = dict(me.operators)
            if operator in operators_json:
                operators_json[operator] += 1
            else:
                operators_json[operator] = 1

            me.operators = operators_json
            me.draw_count += 1
            me.six_guarantee_count += 1
            await me.save()
            return True
        else:
            await cls.create(
                user_id=user_id,
                operators={operator: 1},
                ticket=0,
                draw_count=1,
                six_guarantee_count=1,
                draw_six_record="",
            )

    @classmethod
    async def get_operator_num(cls, user_id: str, operator: str) -> int:
        """获取当前干员抽到的数量"""
        if me := await cls.get_or_none(user_id=user_id):
            operators_json = dict(me.operators)
            return operators_json[operator] if operators_json.get(operator) else 0
        return 0

    @classmethod
    async def get_all_operators_num(cls, user_id: str) -> list[tuple[str, int]]:
        """获取当前全部干员的收集情况"""
        if me := await cls.get_or_none(user_id=user_id):
            operators_json = dict(me.operators)
            return list(operators_json.items())
        else:
            return []

    @classmethod
    async def get_ticket(cls, user_id: str) -> int:
        """获取当前黄票"""
        return me.ticket if (me := await cls.get_or_none(user_id=user_id)) else 0

    @classmethod
    async def get_count(cls, user_id: str) -> int:
        """获取当前抽卡次数"""
        return me.draw_count if (me := await cls.get_or_none(user_id=user_id)) else 0

    @classmethod
    async def record_clear(cls, user_id: str):
        """清空当前保底"""
        if me := await cls.get_or_none(user_id=user_id):
            me.six_guarantee_count = 0
            await me.save()

    @classmethod
    async def get_six_guarantee_count(cls, user_id: str) -> int:
        """获取当前保底情况"""
        if me := await cls.get_or_none(user_id=user_id):
            return me.six_guarantee_count
        else:
            return 0

    @classmethod
    async def add_ticket(cls, user_id: str, num: int):
        """增加指定数量黄票"""
        if me := await cls.get_or_none(user_id=user_id):
            me.ticket += num
            await me.save()

    @classmethod
    async def subtract_ticket(cls, user_id: str, num: int):
        """减少指定数量黄票"""
        if me := await cls.get_or_none(user_id=user_id):
            me.ticket -= num
            await me.save()

    @classmethod
    async def record_six_draw(cls, user_id: str, operator: str):
        """记录六星抽卡情况"""
        if me := await cls.get_or_none(user_id=user_id):
            new_str = f"{operator}_{me.six_guarantee_count} "
            me.draw_six_record += new_str
            await me.save()

    @classmethod
    async def get_six_record(cls, user_id) -> list[tuple[str, int]]:
        """获取六星抽卡记录"""
        if me := await cls.get_or_none(user_id=user_id):
            record = me.draw_six_record
            records = record.split()
            return [(i.split("_")[0], int(i.split("_")[1])) for i in records]
        else:
            return []
