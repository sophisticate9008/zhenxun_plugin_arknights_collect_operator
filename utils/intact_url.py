import re
import random
import asyncio
from hashlib import md5

from lxml import etree

from zhenxun.services.log import logger

from .. import global_arg
from ..global_arg import Constant
from .network import fetch_html_text
from ..utils.utils import save_file
from ..utils.operator import get_info_by_name
from ..types import VoicePartType, VoiceUrlResultType


def get_intact_url(text: str) -> str:
    """
    根据获取图片完整url
    """
    h1 = md5()
    h1.update(text.encode("utf-8"))
    md5_ = h1.hexdigest()
    return Constant.pic_url.format(md5_[0], md5_[0], md5_[1]) + text


def get_avatar_url(name: str, index: int) -> str:
    """
    获取头像url,0代表立绘头像 index为皮肤头像
    """
    url_ = get_intact_url(f"头像_{name}_skin{index}.png")
    if index == 0:
        url_ = get_intact_url(f"头像_{name}.png")
    return url_


def get_skin_url(name: str, index: int) -> str:
    """
    获取皮肤url
    """
    return get_intact_url(f"立绘_{name}_skin{index}.png")


def get_basic_url(name: str, index: int) -> str:
    """
    获取基础立绘url
    """
    return get_intact_url(f"立绘_{name}_{index}.png")


def get_portrait_url(name: str, char_id: str) -> str:
    """
    获取肖像url
    """
    return Constant.char_portrait_url.format(char_id)


def parse_voice_data(html_text: str) -> list[VoicePartType]:
    """解析网页内容，提取语音数据"""
    parser = etree.HTMLParser()
    parse_html = etree.HTML(html_text, parser=parser)
    xpath_voice = "//textarea/text()"
    char_voice = parse_html.xpath(xpath_voice)
    texts = char_voice[0].split("\n\n")

    list_voice_parts = []
    for i in texts:
        results = re.search(r"=(.*)\n.*\|中文\|(.*)}}{{VoiceData/word\|日文\|", i)
        index = re.search(r"\|语音.*=(.*)", i)
        if results and index:
            list_tmp = [results[1], results[2], index[1]]
            list_voice_parts.append(list_tmp)

    return list_voice_parts


def select_voice(list_voice_parts: list[VoicePartType], title: str) -> VoicePartType:
    """从语音列表中选择匹配的语音记录"""
    for voice in list_voice_parts:
        if voice[0] == title:
            return voice
    return random.choice(list_voice_parts)


async def get_voice_url_and_text(name: str, title: str) -> VoiceUrlResultType | None:
    """获取语音记录文本和对应的音频文件URL"""
    url_jp = Constant.voice_jp_url
    url_cn = Constant.voice_cn_url
    url_text = Constant.voice_text_url
    char_id = get_info_by_name(name).charid
    list_voice_parts = []
    if not (list_voice_parts := global_arg.voice_infos.get(name)):
        count = 0
        while count < 3:
            try:
                html_text = await fetch_html_text(url_text.format(name))
                if html_text:
                    list_voice_parts = parse_voice_data(html_text)
                    global_arg.voice_infos[name] = list_voice_parts
                    await save_file(
                        global_arg.voice_infos,
                        global_arg.Constant.file_path / "voice_infos.json",
                    )
                    break
            except Exception as e:
                logger.warning(f"语音获取失败: {e}, 2s后重试")
                count += 1
                await asyncio.sleep(2)

    if list_voice_parts is None:
        logger.error("语音获取失败，尝试次数已达上限")
        return None
    voice_sel = select_voice(list_voice_parts, title)
    voice_title, voice_text, voice_index = voice_sel
    url_voice_jp = url_jp.format(char_id, voice_index, voice_title)
    url_voice_cn = url_cn.format(char_id, voice_index, voice_title)
    return (
        url_voice_cn.replace("CN", "cn"),
        url_voice_jp.replace("CN", "cn"),
        voice_text,
        voice_title
    )
