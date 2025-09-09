import io

from zhenxun.utils.http_utils import AsyncHttpx


async def fetch_html_text(url: str) -> str | None:
    """异步获取网页内容"""
    r = await AsyncHttpx.get(url=url)
    return r.text if r.status_code == 200 else None


async def fetch_json(url: str, params: dict | None = None) -> dict | None:
    """异步获取网页json"""
    r = await AsyncHttpx.get(url=url, params=params)
    if r.status_code == 200:
        try:
            return r.json()
        except ValueError:  # 捕获 JSON 解码错误
            return None
    return None


async def fetch_media(url: str) -> io.BytesIO | None:
    """异步获取媒体文件字节流"""
    r = await AsyncHttpx.get(url=url)
    return io.BytesIO(r.content) if r.status_code == 200 else None
