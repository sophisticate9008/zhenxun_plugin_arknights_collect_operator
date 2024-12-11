from pathlib import Path
from nonebot_plugin_alconna import AlconnaMatcher
from zhenxun.configs.config import Config
from zhenxun.configs.path_config import DATA_PATH, FONT_PATH

from .types import CargoQuery, OperatorInfo,VoiceHtmlPraseType


class Constant:
    cargoquery_url: str = (
        """
        https://prts.wiki/api.php?
        action=cargoquery&
        format=json&
        limit=500&
        tables=chara,chara_data,chara_extra_info,char_obtain&
        fields=chara.charId=charid, chara._pageName=干员,
        chara.rarity=稀有度, chara.profession=职业&
        where=chara.charIndex>0&
        join_on=chara._pageName=chara_data._pageName,
        chara._pageName=chara_extra_info._pageName,
        chara._pageName=char_obtain._pageName&
        utf8=1
    """.strip()
        .replace("\n", "")
        .replace(" ", "")
    )
    pic_url: str = "https://media.prts.wiki/{}/{}{}/"
    voice_cn_url: str = (
        "https://torappu.prts.wiki/assets/audio/voice_cn/{}/{}?filename={}.wav"
    )
    voice_jp_url: str = (
        "https://torappu.prts.wiki/assets/audio/voice/{}/{}?filename={}.wav"
    )
    voice_text_url: str = "https://prts.wiki/index.php?title={}/语音记录&action=edit"
    char_portrait_url: str = "https://torappu.prts.wiki/assets/char_portrait/{}_1.png"
    file_path = DATA_PATH / "arknights_collect_operator/"
    font_path = FONT_PATH / "HYWenHei-85W.ttf"
    resource_path = Path(__file__).parent / "resource"


cargo_query: CargoQuery
plugin_config = Config.get("zhenxun_plugin_arknights_collect_operator")
cache_star_lists: dict[int, list[str]] = {3: [], 4: [], 5: [], 6: []}
cache_operator_info_dict: dict[str, OperatorInfo] = {}
voice_infos: VoiceHtmlPraseType = {}
