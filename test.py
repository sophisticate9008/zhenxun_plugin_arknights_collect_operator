import aiohttp
import asyncio
import sys
from lxml import etree  # type: ignore


async def fetch_prts_html(session: aiohttp.ClientSession) -> str:
    """异步请求PRTS首页，获取完整HTML"""
    target_url = "https://prts.wiki/w/%E9%A6%96%E9%A1%B5"  # 确保是首页，而非其他页面
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://prts.wiki/",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    try:
        async with session.get(url=target_url, headers=headers, timeout=20) as response:
            print(f"请求状态码：{response.status}")
            if response.status != 200:
                raise Exception(f"请求失败，状态码：{response.status}")
            return await response.text(encoding="utf-8")
    except Exception as e:
        print(f"异步请求HTML失败：{e}")
        return ""


async def extract_new_operators() -> list[str]:
    """
    单独异步函数：精准提取侧边栏“新增干员”模块的干员列表
    返回：仅包含5个目标干员的列表
    """
    async with aiohttp.ClientSession() as session:
        html_text = await fetch_prts_html(session)
        if not html_text:
            return []

        # 1. 解析HTML为DOM对象
        html = etree.HTML(html_text)

        # 2. 【关键】定位侧边栏（id="MenuSidebar"）中的“新增干员”模块
        # XPath逻辑：
        # - //div[@id="MenuSidebar"]：锁定侧边栏容器
        # - .//li[contains(b/text(), "新增干员")]：在侧边栏内找包含“新增干员”文本的<li>（模块标题所在li）
        # - ./ul/li/a：提取该<li>下的<ul>→<li>→<a>（干员链接）
        operator_a_tags = html.xpath(
            '//div[@id="MenuSidebar"]//li[contains(b/text(), "新增干员")]/ul/li/a'
        )

        if not operator_a_tags:
            print("未找到侧边栏中的“新增干员”模块，可能模块结构变化")
            return []

        # 3. 提取每个<a>标签的title属性（即干员名）
        new_operators = [
            a_tag.get("title", "").strip()
            for a_tag in operator_a_tags
            if a_tag.get("title", "").strip()  # 过滤空title
        ]

        # 4. 验证结果（确保是5个干员，符合预期）
        if len(new_operators) != 5:
            print(f"提取到{len(new_operators)}个干员（预期5个），可能包含无关数据")
            # 额外过滤：干员名是2-5个中文字符，排除非干员
            new_operators = [
                op
                for op in new_operators
                if 2 <= len(op) <= 5
                and op.isalnum() is False  # 排除纯字母/数字（非干员）
            ]

        return new_operators


async def main():
    """主函数：执行提取并输出结果"""
    new_ops_list = await extract_new_operators()
    print("\n" + "=" * 30)
    if new_ops_list:
        print(f"PRTS侧边栏新增干员列表（共{len(new_ops_list)}个）：")
        print("=" * 30)
        for idx, op_name in enumerate(new_ops_list, 1):
            print(f"{idx}. {op_name}")
    else:
        print("未提取到新增干员数据")
    print("=" * 30)


# 运行入口（适配Windows/Linux）
if __name__ == "__main__":
    if sys.platform == "win32" and sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
