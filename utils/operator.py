import json
from lxml import etree  # type: ignore
from .. import global_arg
from ..arknights_types import OperatorInfo
from ..utils.network import fetch_html_text

from ..utils.utils import save_file, read_file
from zhenxun.services.log import logger


def get_star_list(star_value: int) -> list[str]:
    """获得指定星级的全部名字列表"""
    if (
        global_arg.cache_star_lists.get(star_value)
        and len(global_arg.cache_star_lists[star_value]) > 0
    ):
        return global_arg.cache_star_lists[star_value]

    list_return = [
        i.name for i in global_arg.cargo_query.cargoquery if i.star == star_value
    ]
    global_arg.cache_star_lists[star_value] = list_return
    return list_return


def get_info_by_name(name: str) -> OperatorInfo:
    """根据名字获得元组信息(名字,char_id,职业,星级)"""
    if global_arg.cache_operator_info_dict.get(name):
        return global_arg.cache_operator_info_dict[name]
    result = next(
        (i for i in global_arg.cargo_query.cargoquery if i.name == name),
    )
    global_arg.cache_operator_info_dict[name] = result
    return result


async def update_new_operators():
    """
    从PRTS Wiki首页获取最新的干员数据，筛选出新干员，并按星级分类存储。
    """
    logger.info("开始更新新干员数据...")
    url = (
        global_arg.Constant.new_operator_page_url
    )  # MODIFIED: Changed URL to HTML page

    try:
        # MODIFIED: Use fetch_html_text instead of fetch_json
        html_text = await fetch_html_text(url)

        if html_text:
            parser = etree.HTMLParser()
            html = etree.HTML(html_text, parser=parser)

            # XPath logic from user's test.py
            operator_a_tags = html.xpath(
                '//div[@id="MenuSidebar"]//li[contains(b/text(), "新增干员")]/ul/li/a'
            )

            new_operators_list = []
            if operator_a_tags:
                for a_tag in operator_a_tags:
                    op_name = a_tag.get("title", "").strip()
                    if op_name:  # Filter empty titles
                        new_operators_list.append(op_name)
            else:
                logger.warning("未找到侧边栏中的“新增干员”模块，可能模块结构变化。")

            # Clear previous new operators
            global_arg.new_operators_by_rarity = {3: [], 4: [], 5: [], 6: []}

            for op_name in new_operators_list:
                try:
                    info = get_info_by_name(op_name)
                    if info.star in global_arg.new_operators_by_rarity:
                        global_arg.new_operators_by_rarity[info.star].append(op_name)
                except Exception as e:
                    logger.warning(f"无法获取新干员 {op_name} 的信息: {e}")

            await save_file(
                global_arg.new_operators_by_rarity,
                global_arg.Constant.file_path / "new_operators.json",
            )
            logger.info("新干员数据更新并保存成功。")
        else:
            logger.warning("从网络获取新干员数据失败或数据为空。")
    except Exception as e:
        logger.error(f"更新新干员数据时发生错误: {e}")


async def load_new_operators_from_file():
    """
    从本地文件加载新干员数据。
    """
    try:
        file_content = await read_file(
            global_arg.Constant.file_path / "new_operators.json"
        )
        if file_content:
            global_arg.new_operators_by_rarity = json.loads(str(file_content))
            logger.info("从本地加载新干员数据成功。")
        else:
            logger.info("本地没有新干员数据文件，将尝试从网络获取。")
    except Exception as e:
        logger.error(f"从本地加载新干员数据时发生错误: {e}")
        logger.info("将尝试从网络获取新干员数据。")
