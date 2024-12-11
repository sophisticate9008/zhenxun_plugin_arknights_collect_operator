import io
import os
import re
import urllib.parse
from pathlib import Path
from typing import TypeVar

import aiofiles
from pydantic import BaseModel

from zhenxun.services.log import logger

from . import intact_url
from .. import global_arg
from .network import fetch_media
from ..utils.utils import read_file, save_file



async def get_basic_painting_img(name: str, index: int) -> io.BytesIO | None:
    """获取干员基础立绘图片"""
    url = intact_url.get_basic_url(name, index)

    return await get_media_by_url(url, "painting")


async def get_skin_img(name: str, index: int) -> io.BytesIO | None:
    """获取干员皮肤图片"""
    url = intact_url.get_skin_url(name, index)
    return await get_media_by_url(url, "skin")


async def get_avatar_img(name: str, index: int) -> io.BytesIO | None:
    """获取干员头像图片"""
    url = intact_url.get_avatar_url(name, index)
    return await get_media_by_url(url, "avatar")


async def get_portrait_img(name: str, char_id: str) -> io.BytesIO | None:
    """获取干员头像图片"""
    url = intact_url.get_portrait_url(name, char_id)
    return await get_media_by_url(url, "portrait")


async def get_voice(
    name: str, lang: str, title: str = "随机"
) -> tuple[str, str, io.BytesIO] | None:
    """获取指定语音的标题,文本,语音"""
    tmp = await intact_url.get_voice_url_and_text(name, title)
    if tmp:
        text = tmp[2]
        title = tmp[3]
        url = ""
        if lang == "cn":
            url = tmp[0]
        elif lang == "jp":
            url = tmp[1]
        if result := await get_media_by_url(url, "voice"):
            return title, text, result


async def get_media_by_url(url: str, media_type: str) -> io.BytesIO | None:
    """根据 URL 获取媒体文件, 优先查找本地文件,根据配置保存"""
    # 使用 sanitize_filename 清理 URL 获取合法的文件名
    url_file_name = sanitize_filename(url)
    full_path = global_arg.Constant.file_path / media_type / url_file_name

    # 检查本地是否存在文件
    if os.path.exists(full_path):
        # 如果文件存在，异步读取本地文件
        async with aiofiles.open(full_path, "rb") as f:
            return io.BytesIO(await f.read())
    else:
        # 如果文件不存在，从 URL 下载图像
        media_data = await fetch_media(url)
        if not media_data:
            return None
        if media_type not in ["painting", "voice"]:
            await save_file(media_data, full_path)
        # 下载成功后，并且配置允许保存后，异步将媒体文件保存到本地
        if media_type == "painting" and global_arg.plugin_config.get(
            "IS_SAVE_PAINTING"
        ):
            await save_file(media_data, full_path)
        if media_type == "voice" and global_arg.plugin_config.get("IS_SAVE_VOICE"):
            await save_file(media_data, full_path)
        return media_data


def sanitize_filename(url: str) -> str:
    """清除 URL 中不能作为文件名的字符，去掉协议和域名部分"""
    # 解析 URL，提取路径部分
    parsed_url = urllib.parse.urlparse(url)
    # 获取路径部分并去掉开头的 '/'（如果有的话）
    path = parsed_url.path.lstrip("/")
    # 用路径的剩余部分作为文件名
    filename = path
    # 定义一个正则，替换掉 Windows 和 Linux 上常见的非法字符
    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'  # 包含控制字符
    filename = re.sub(invalid_chars, "_", filename) or "default_file_name"
    return filename



T = TypeVar("T", bound=BaseModel)


class PydanticHandler:
    """
    用于处理 Pydantic 模型实例的类。
    """

    @staticmethod
    async def save(instance: BaseModel, file_path: str | Path):
        await save_file(instance.json(), file_path)

    @staticmethod
    async def load(model_class: type[T], file_path: str | Path) -> T | None:
        """
        从文件加载数据并解析为 Pydantic 模型实例。
        :param model_class: Pydantic 模型类
        :param file_path: 文件路径
        :return: 返回解析后的 Pydantic 模型实例
        """
        try:
            raw_data = await read_file(file_path)
            return model_class.parse_obj({"data": raw_data})
        except Exception as e:
            logger.error(f"pydantic 从文件中导入失败: {file_path}, {e}")
