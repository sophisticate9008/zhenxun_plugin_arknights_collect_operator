import json

import nonebot
from nonebot.plugin import PluginMetadata
from nonebot_plugin_apscheduler import scheduler

from zhenxun.services.log import logger
from zhenxun.utils.enum import PluginType
from zhenxun.configs.utils import RegisterConfig, PluginExtraData

from .types import CargoQuery
from .utils.network import fetch_json
from .utils.storage import read_file, save_file

__plugin_meta__ = PluginMetadata(
    name="明日方舟干员收集",
    description="金币收集三星以上全干员",
    usage="""
    抽干员(?十连)
    干员(皮肤|立绘)(1|2|...)
    (克洛斯|能天使)语音(?戳一下|信赖触摸)
    我的黄票,黄票兑换(年|令|...)
    我的干员,我的六星记录
    """,
    extra=PluginExtraData(
        author="sophisticate9008",
        version="0.2",
        menu_type="群内小游戏",
        plugin_type=PluginType.NORMAL,
        configs=[
            RegisterConfig(
                key="WITHDRAW_DRAW_DRAW_PIC",
                value=(0, 1),
                help="自动撤回，参1：延迟撤回图片时间(秒)，0 为关闭 | 参2：监控聊天类型，0(私聊) 1(群聊) 2(群聊+私聊)",  # noqa: E501
                default_value=(0, 1),
                type=tuple[int, int],
            ),
            RegisterConfig(
                key="IS_SAVE_VOICE",
                value=True,
                help="是否保存访问到的语音",
                default_value=True,
                type=bool,
            ),
            RegisterConfig(
                key="IS_SAVE_PAINTING",
                value=True,
                help="是否保存访问到的立绘",
                default_value=True,
                type=bool,
            ),
            RegisterConfig(
                key="PRICE",
                value=5,
                help="单抽价格",
                default_value=5,
                type=int,
            ),
        ],
    ).dict(),
)

driver = nonebot.get_driver()
from . import global_arg


async def get_cargo_data():
    try:
        data_json = await fetch_json(global_arg.Constant.cargoquery_url)
        if data_json:
            global_arg.cache_star_lists = {3: [], 4: [], 5: [], 6: []}
            global_arg.cargo_query = CargoQuery(**data_json)
            await save_file(
                data_json, global_arg.Constant.file_path / "cargo_query.json"
            )
            logger.info("从网络获取干员数据并保存成功")
        else:
            data_json = await read_file(
                global_arg.Constant.file_path / "cargo_query.json"
            )
            global_arg.cargo_query = CargoQuery(**data_json)  # type: ignore
            logger.info("从本地获取干员数据")
    except Exception:
        data_json = await read_file(global_arg.Constant.file_path / "cargo_query.json")
        data_json = json.loads(data_json)  # type: ignore
        global_arg.cargo_query = CargoQuery(**data_json)  # type: ignore
        logger.info("从本地获取干员数据")


async def get_voice_part():
    file_content = await read_file(global_arg.Constant.file_path / "voice_infos.json")
    if file_content:
        global_arg.voice_infos = json.loads(
            str(file_content)
        )
        logger.info("从本地获取解析过的语音数据")


driver.on_startup(get_cargo_data)
driver.on_startup(get_voice_part)

@scheduler.scheduled_job(
    "interval",
    hours=12,
)
async def _():
    await get_cargo_data()
    global_arg.cache_star_lists = {}


from . import handles  # noqa: F401
