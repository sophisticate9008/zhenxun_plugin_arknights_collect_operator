import random

from strenum import StrEnum
from nonebot.adapters import Bot
from nonebot_plugin_session import EventSession
from nonebot_plugin_alconna import Match, UniMessage

from zhenxun.utils.enum import GoldHandle
from zhenxun.utils.message import MessageUtils
from zhenxun.models.user_console import UserConsole
from zhenxun.utils.withdraw_manage import WithdrawManager

from .. import global_arg
from ..models.db_model import OperatorCollect
from ..types import DrawHandleCtx, DrawResultType
from ..utils.storage import get_basic_painting_img
from ..matchers import draw_matcher, draw_info_matcher
from ..utils.utils import exec_db_write, create_transaction
from ..utils.operator import get_star_list, get_info_by_name
from ..utils.pic_make import simulate_image, generate_character_grid_pic


class PreNot(StrEnum):
    """前置不通过的理由"""

    NoEnoughGold = "NoEnoughGold"
    """没有足够金币"""
    NoData = "NoData"
    """没有数据"""


@draw_matcher.handle()
async def _(bot: Bot, session: EventSession, num: Match[str]):
    transaction = create_transaction()
    ctx = DrawHandleCtx(session=session, transaction=transaction)
    draw_count = str_to_num(num.result) if num.available else 1
    if not ctx.get_user_id():
        await MessageUtils.build_message("用户id为空...").finish()

    list_prenot = []
    if not await before_draw(ctx, draw_count, list_prenot) and list_prenot:
        await MessageUtils.build_message(",".join(list_prenot)).finish()
    draw_result = await draw(ctx, draw_count)
    msg = await draw_result_to_msg(ctx, draw_result)
    receipt = await msg.send(reply_to=True)
    if receipt:
        await after_draw(ctx, draw_count)
        if need_withdraw(draw_result):
            message_id = receipt.msg_ids[0]["message_id"]
            await WithdrawManager.withdraw_message(
                bot,
                message_id,
                global_arg.plugin_config.get("WITHDRAW_DRAW_DRAW_PIC"),
                session,
            )


async def draw_result_to_msg(
    ctx: DrawHandleCtx, draw_result: list[DrawResultType]
) -> UniMessage:
    """处理结果，转为消息，增加黄票"""
    msg_list = []
    ticket_add = 0

    # 单抽情况
    if len(draw_result) == 1:
        name = draw_result[0][0]
        drawed_count = draw_result[0][1]
        info = get_info_by_name(name)
        star_text = "★" * info.star
        img = await get_basic_painting_img(name, 1)
        ticket_add = cal_ticket(info.star, drawed_count)
        text = f"本次抽到了{name}，星级为{star_text}，第{drawed_count}次抽到，获得{ticket_add}黄票"  # noqa: E501
        msg_list.extend((img, text))

    # 十连及倍数情况
    elif len(draw_result) > 1:
        # 将结果按每10个分组
        group_size = 10
        groups = [
            draw_result[i:i+group_size]
            for i in range(0, len(draw_result), group_size)
        ]
        # 处理每个分组
        for group in groups:
            # 生成分组图片
            img = await simulate_image(group)
            msg_list.append(img)
            # 累计黄票
            for item in group:
                name, drawed_count = item[0], item[1]
                info = get_info_by_name(name)
                ticket_add += cal_ticket(info.star, drawed_count)

        # 添加总黄票信息
        msg_list.append(f"累计获得{ticket_add}黄票")

    # 写入数据库
    if ticket_add > 0:
        await exec_db_write(
            ctx.transaction,
            lambda: OperatorCollect.add_ticket(str(ctx.get_user_id()), ticket_add),
        )
    return MessageUtils.build_message(msg_list)


async def draw(ctx: DrawHandleCtx, draw_count: int) -> list[DrawResultType]:
    """抽卡函数"""
    list_result: list[DrawResultType] = []
    for _ in range(draw_count):
        result = await draw_single(ctx)
        list_result.append(result)
    return list_result


async def draw_single(
    ctx: DrawHandleCtx,
) -> DrawResultType:
    ranges = [
        (0, 0.02, 6),  # 第一组参数
        (0.92, 1, 5),  # 第二组参数
        (0.42, 0.92, 4),  # 第三组参数
        (0.02, 0.42, 3),  # 第四组参数
    ]

    result = await try_draw_assist(ctx, ranges)
    return result or ("", 0)


async def try_draw_assist(
    ctx: DrawHandleCtx, ranges: list[tuple]
) -> DrawResultType | None:
    """接受一组参数来调用抽取辅助函数"""
    rand = random.random()
    for rand_l, rand_r, star_value in ranges:
        result = await draw_assist(ctx, rand, rand_l, rand_r, star_value)
        if isinstance(result, tuple):
            return result
    return None  # 如果没有命中任何情况


async def draw_assist(
    ctx: DrawHandleCtx,
    rand_value: float,
    rand_l: float,
    rand_r: float,
    star_value: int,
) -> DrawResultType | None:
    """抽取辅助函数, 根据rand rand_l rand_r 来根据概率命中"""
    six_record = await OperatorCollect.get_six_guarantee_count(str(ctx.get_user_id()))
    if star_value == 6:
        over_fifty = six_record - 50
        if over_fifty > 0:
            # 挤占三星概率
            rand_r += over_fifty * 0.02
    if rand_value < rand_l or rand_value >= rand_r:  # 未命中
        return None

    list_star = get_star_list(star_value)
    result_name = random.choice(list_star)
    await exec_db_write(
        ctx.transaction,
        lambda: OperatorCollect.operator_record(str(ctx.get_user_id()), result_name),
    )
    info = get_info_by_name(result_name)
    if info.star == 6:
        await exec_db_write(
            ctx.transaction,
            lambda: OperatorCollect.record_six_draw(
                str(ctx.get_user_id()), result_name
            ),
            lambda: OperatorCollect.record_clear(str(ctx.get_user_id())),
        )
    drawed_count = await OperatorCollect.get_operator_num(
        str(ctx.get_user_id()),
        result_name,
    )
    # 命中
    return (result_name, drawed_count)


async def before_draw(ctx: DrawHandleCtx, draw_count: int, list_prenot: list) -> bool:
    return await judge_gold(ctx, draw_count, list_prenot)


async def after_draw(ctx: DrawHandleCtx, draw_count: int):
    await reduce_gold(ctx, draw_count * global_arg.plugin_config.get("PRICE"))


async def reduce_gold(ctx: DrawHandleCtx, gold: int):
    await exec_db_write(
        ctx.transaction,
        lambda: UserConsole.reduce_gold(
            str(ctx.get_user_id()),
            gold,
            GoldHandle.PLUGIN,
            "zhenxun_plugin_arknights_collect_operator",
        ),
    )


async def judge_gold(ctx: DrawHandleCtx, draw_count: int, list_prenot: list) -> bool:
    gold_now = (await UserConsole.get_user(str(ctx.get_user_id()))).gold
    result = gold_now >= draw_count * global_arg.plugin_config.get("PRICE")
    if not result:
        list_prenot.append(PreNot.NoEnoughGold)
    return result


def cal_ticket(star: int, drawed_count: int) -> int:
    """根据抽到的次数计算获得的黄票"""
    # 首次获得都是1
    if drawed_count == 1:
        return 1
    ticket_dict: dict[int, tuple[int, int]] = {
        6: (10, 25),
        5: (5, 13),
        4: (0, 1),
        3: (0, 0),
    }
    return ticket_dict[star][0] if drawed_count <= 5 else ticket_dict[star][1]


def need_withdraw(results: list[DrawResultType]) -> bool:
    """判断是否需要撤回,3个以上五星,或是6星"""
    five_count = 0
    for _ in results:
        info = get_info_by_name(_[0])
        if info.star == 6:
            return False
        if info.star == 5:
            five_count += 1
    return five_count < 3


@draw_info_matcher.handle()
async def _(session: EventSession, info_type: Match[str]):
    _type = info_type.result if info_type.available else "干员"
    user_id = str(session.id1)
    data_list = (
        (await OperatorCollect.get_six_record(user_id))
        if _type == "六星记录"
        else await OperatorCollect.get_all_operators_num(user_id)
    )
    if data_list:
        data_list.reverse()
        img = await generate_character_grid_pic(data_list)
        msg_list = [img, _type]
        await MessageUtils.build_message(msg_list).finish(reply_to=True)

def str_to_num(_str: str) -> int:
    # 定义中文数字到阿拉伯数字的映射
    chinese_num_map = {
        "一": 1,
        "二": 2,
        "三": 3,
        "四": 4,
        "五": 5,
        "六": 6,
        "七": 7,
        "八": 8,
        "九": 9,
        "十": 10,
        "百": 100,
    }
    # 如果字符串是纯阿拉伯数字
    if _str.isdigit():
        num = int(_str)
        # 检查是否是十的倍数
        if num % 10 == 0:
            return num
        return 1
    # 如果字符串是中文数字
    # 解析中文数字
    num = 0
    temp = 0
    for char in _str:
        if char in chinese_num_map:
            if chinese_num_map[char] == 10:  # 十
                temp = temp if temp != 0 else 1
                num += temp * 10
                temp = 0
            elif chinese_num_map[char] == 100:  # 百
                temp = temp if temp != 0 else 1
                num += temp * 100
                temp = 0
            else:
                temp += chinese_num_map[char]
    num += temp
    # 检查是否是十的倍数
    if num % 10 == 0:
        return num
    return 1
