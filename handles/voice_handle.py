import random
import asyncio

from strenum import StrEnum
from nonebot import on_message
from nonebot.internal.adapter import Event
from nonebot.exception import MatcherException
from nonebot_plugin_session import EventSession
from nonebot_plugin_alconna import Match, Voice, UniMessage

from zhenxun.services.log import logger
from zhenxun.utils.enum import GoldHandle
from zhenxun.utils.message import MessageUtils
from zhenxun.models.user_console import UserConsole
from zhenxun.plugins.zhenxun_plugin_arknights_collect_operator import global_arg

from ..utils.storage import get_voice
from ..models.db_model import OperatorCollect
from ..matchers import voice_matcher, voice_guess_matcher
from ..utils.operator import get_star_list, get_info_by_name


class ResultType(StrEnum):
    """语音结果"""

    NoOperator = "未找到该干员"
    NoHaveOperator = "未获得该干员"
    NoVoice = "听取的语音不存在"


guess_time: int = 120


@voice_matcher.handle()
async def _(session: EventSession, operator: Match[str], title: Match[str]):
    operator_name = operator.result if operator.available else ""
    user_id = str(session.id1)
    _title = title.result if title.available else "随机"
    try:
        get_info_by_name(operator_name)
        is_have = await OperatorCollect.get_operator_num(user_id, operator_name) > 0
        if not is_have:
            await voice_matcher.finish(ResultType.NoHaveOperator, reply_to=True)
        if voice_jp := await get_voice(operator_name, "jp", _title):
            await UniMessage([Voice(raw=voice_jp[2])]).send()
            await MessageUtils.build_message(voice_jp[1]).send()
            if voice_cn := await get_voice(operator_name, "cn", voice_jp[0]):
                await UniMessage([Voice(raw=voice_cn[2])]).finish()
        await MessageUtils.build_message(ResultType.NoVoice).finish(reply_to=True)
    except MatcherException:
        raise
    except Exception as e:
        logger.error(f"{e}")
        logger.warning(ResultType.NoOperator)


class VoiceGuessHandler:
    group_id: str
    winner_user_id: str | None
    result: str
    is_open: bool
    titles: list[str]

    def __init__(self, groud_id: str, result: str):
        self.titles = [
            "任命助理",
            "交谈1",
            "交谈2",
            "交谈3",
            "信赖提升后交谈1",
            "信赖提升后交谈2",
            "信赖提升后交谈3",
            "闲置",
            "干员报到",
            "观看作战记录",
            "编入队伍",
            "任命队长",
            "行动出发",
            "行动开始",
            "选中干员1",
            "选中干员2",
            "部署1",
            "部署2",
            "作战中1",
            "作战中2",
            "完成高难行动",
            "3星结束行动",
            "非3星结束行动",
            "行动失败",
            "进驻设施",
            "戳一下",
            "信赖触摸",
            "标题",
            "新年祝福",
            "问候",
            "生日",
            "周年庆典",
        ]

        self.group_id = groud_id
        self.winner_user_id = None
        self.is_open = True
        self.result = result
        self.task = asyncio.create_task(self.auto_close())

    async def auto_close(self):
        await asyncio.sleep(guess_time)
        self.is_open = False

    async def judge_answer_with_open(self, user_id: str, answer: str) -> bool | None:
        if answer == self.result:
            self.is_open = False
            return True


voice_guess_data: dict[str, VoiceGuessHandler] = {}


@voice_guess_matcher.handle()
async def _(session: EventSession):
    global voice_guess_data
    group_id = str(session.id2)
    # 获取当前群组的猜测处理器
    handler = voice_guess_data.get(group_id)
    # 如果没有处理器或已关闭，创建新的处理器
    if not handler or not handler.is_open:
        await MessageUtils.build_message("开启新的猜语音").send()
        result = random.choice(get_all_list())
        logger.info(f"猜语音答案{result}")
        handler = VoiceGuessHandler(group_id, result)
        voice_guess_data[group_id] = handler

        async def warpper():
            await asyncio.sleep(guess_time - 1)
            if handler.is_open:
                await MessageUtils.build_message(
                    f"猜语音结束,答案是{handler.result}"
                ).finish()

        _ = asyncio.create_task(warpper())  # noqa: RUF006
    # 随机获取一个标题并从列表中移除
    if handler.titles:
        _title = random.choice(handler.titles)
        handler.titles.remove(_title)
        result = handler.result
        # 获取日语语音并发送
        voice_jp = await get_voice(result, "jp", _title)
        if voice_jp:
            await UniMessage([Voice(raw=voice_jp[2])]).send()
            await MessageUtils.build_message(voice_jp[1]).send()
            # 获取中文语音并发送
            voice_cn = await get_voice(result, "cn", voice_jp[0])
            if voice_cn:
                await UniMessage([Voice(raw=voice_cn[2])]).finish()
    await MessageUtils.build_message("所有语音已发送完毕").finish()


all_list: list[str] = []


def get_all_list() -> list[str]:
    global all_list
    if all_list:
        return all_list
    return get_star_list(3) + get_star_list(4) + get_star_list(5) + get_star_list(6)


async def is_handler_open(session: EventSession) -> bool:
    global voice_guess_data
    group_id = str(session.id2)  # 通过 event 获取群号
    handler = voice_guess_data.get(group_id)
    return bool(handler and handler.is_open)  # 只有条件满足才允许捕捉


# 添加前置过滤
guess = on_message(priority=996, block=False, rule=is_handler_open)


@guess.handle()
async def _(session: EventSession, event: Event):
    global voice_guess_data
    group_id = str(session.id2)
    user_id = str(session.id1)
    handler = voice_guess_data.get(group_id)
    if handler and handler.is_open:
        message_content = event.get_message()
        plain_text = message_content.extract_plain_text()
        if await handler.judge_answer_with_open(str(session.id1), plain_text):
            gold_add = global_arg.plugin_config.get("Price") * 3
            await UserConsole.add_gold(
                user_id,
                gold_add,
                GoldHandle.PLUGIN,
                "zhenxun_plugin_arknights_collect_operator",
            )
            await MessageUtils.build_message(
                f"恭喜你答对了，获得{gold_add}金币"
            ).finish(reply_to=True)
