from strenum import StrEnum
from nonebot_plugin_alconna import Match
from nonebot.exception import MatcherException
from nonebot_plugin_session import EventSession

from zhenxun.services.log import logger
from zhenxun.utils.message import MessageUtils

from ..matchers import pic_matcher
from ..models.db_model import OperatorCollect
from ..utils.operator import get_info_by_name
from ..utils.storage import get_skin_img, get_basic_painting_img


class ResultType(StrEnum):
    NoOperator = "该干员不存在"
    NoHaveOperator = "未获得该干员"
    NoPic = "查看的图片不存在"


@pic_matcher.handle()
async def _(
    session: EventSession, operator: Match[str], pic_type: Match[str], index: Match[int]
):
    _index = index.result if index.available else 1
    _type = pic_type.result if pic_type.available else "立绘"
    operator_name = operator.result if operator.available else ""
    user_id = str(session.id1)
    try:
        get_info_by_name(operator_name)
        is_have = await OperatorCollect.get_operator_num(user_id, operator_name) > 0
        if not is_have:
            await MessageUtils.build_message(ResultType.NoHaveOperator).finish(
                reply_to=True
            )
        img = await get_img(operator_name, _type, _index)
        if not img:
            await MessageUtils.build_message(
                f"{ResultType.NoPic},{operator_name}{_type}{_index}",
            ).finish(reply_to=True)
        msg_list = [img, f"{operator_name}{_type}{_index}"]
        uniMessage = MessageUtils.build_message(msg_list)
        await uniMessage.finish(reply_to=True)
    except MatcherException:
        raise
    except Exception as e:
        logger.error(f"{e}")
        logger.warning(ResultType.NoOperator)


async def get_img(operator_name: str, pic_type: str, index: int):
    if pic_type == "立绘":
        return await get_basic_painting_img(operator_name, index)
    if pic_type == "皮肤":
        return await get_skin_img(operator_name, index)
