from strenum import StrEnum
from nonebot_plugin_alconna import Match
from nonebot_plugin_session import EventSession

from zhenxun.services.log import logger
from zhenxun.utils.message import MessageUtils

from ..matchers import ticket_matcher
from ..models.db_model import OperatorCollect
from ..utils.operator import get_info_by_name


class ResultType(StrEnum):
    """兑换结果"""

    NoOperator = "未找到该干员"
    NoEnoughTicket = "黄票不足"
    NoPremission = "只能兑换五星以上"
    Success = "兑换成功"


@ticket_matcher.handle()
async def _(session: EventSession, operator: Match[str]):
    if not operator.available:
        if session.id1:
            ticket_num = await OperatorCollect.get_ticket(session.id1)
            await MessageUtils.build_message(f"当前有{ticket_num}张黄票").finish(
                reply_to=True
            )
        await ticket_matcher.finish()
    operator_name = operator.result if operator.available else None
    if operator_name:
        result = await exchange_operator(str(session.id1), operator_name)
        await MessageUtils.build_message(result).finish(reply_to=True)


async def exchange_operator(user_id: str, operator_name: str) -> ResultType:
    ticket_num = await OperatorCollect.get_ticket(user_id)
    price_dict: dict[int, int] = {5: 45, 6: 180}
    try:
        info = get_info_by_name(operator_name)
        if info.star < 5:
            return ResultType.NoPremission
        if price_dict[info.star] > ticket_num:
            return ResultType.NoEnoughTicket
        await OperatorCollect.subtract_ticket(user_id, price_dict[info.star])
        await OperatorCollect.operator_record(user_id, operator_name)
        return ResultType.Success
    except Exception as e:
        logger.error(f"{e}")
        return ResultType.NoOperator
