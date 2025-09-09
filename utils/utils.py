import io
import json
import os
from pathlib import Path
from typing import Any
from collections.abc import Callable

import aiofiles
from tortoise.transactions import in_transaction

from zhenxun.services.log import logger


def create_transaction():
    return in_transaction()


async def exec_db_write(transaction: Any, *args):
    """执行写操作"""
    # async with transaction:
    for func in args:
        if isinstance(func, Callable):
            await func()
            # 执行每个无参匿名函数


async def save_file(data: Any, file_path: str | Path):
    """
    将数据保存到指定的文件中，支持 JSON、文本、二进制、音频等格式。
    如果目录不存在，则递归创建。

    :param data: 要保存的数据，可以是 JSON 可序列化的对象，文本，二进制数据，或音频文件数据
    :param file_path: 要保存文件的路径
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)
    # 确保目录存在，如果不存在则递归创建
    directory = Path(file_path).parent
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)

    # 判断文件类型，根据不同的格式进行保存
    file_extension = Path(file_path).suffix.lower()

    if file_extension == ".json":
        # 保存为 JSON 文件
        async with aiofiles.open(file_path, mode="w", encoding="utf-8") as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=4))
    elif file_extension in {".txt", ".md", ".log"}:
        # 保存为文本文件
        async with aiofiles.open(file_path, mode="w", encoding="utf-8") as f:
            await f.write(str(data))
    elif file_extension in {".jpg", ".jpeg", ".png", ".gif", ".bmp"}:
        # 保存为二进制文件（如图片）
        async with aiofiles.open(file_path, mode="wb") as f:
            await f.write(data.read())
    elif file_extension in {".mp3", ".wav", ".flac", ".aac", ".ogg"}:
        # 保存为音频文件（处理音频数据）
        async with aiofiles.open(file_path, mode="wb") as f:
            await f.write(data.read())
    else:
        # 处理未知格式（如 XML, CSV 等）
        async with aiofiles.open(file_path, mode="w", encoding="utf-8") as f:
            await f.write(str(data))


async def read_file(file_path: str | Path) -> str | io.BytesIO | None:
    """
    异步读取指定文件的内容。根据文件类型，返回文本或二进制数据。

    :param file_path: 文件路径，可以是 str 或 Path 类型。
    :return: 文本数据（str）或二进制数据（io.BytesIO）
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    if not os.path.exists(file_path):
        logger.error(f"文件不存在{file_path}")
        return None
    # 判断文件的扩展名，决定读取方式
    file_extension = file_path.suffix.lower()

    if file_extension in {".txt", ".md", ".log", ".json"}:
        # 如果是文本文件（包括 JSON）
        async with aiofiles.open(file_path, encoding="utf-8") as f:
            return await f.read()

    elif file_extension in {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".mp4",
        ".mp3",
        ".wav",
        ".flac",
    }:
        # 如果是二进制文件（如图片、音频、视频）
        async with aiofiles.open(file_path, "rb") as f:
            return io.BytesIO(await f.read())

    else:
        logger.error(f"不支持的文件类型: {file_extension}")
    return None
