from typing import Any, TypeVar

from nonebot_plugin_session import EventSession
from pydantic import Field, BaseModel, root_validator

T = TypeVar("T", bound=BaseModel)


# 定义一个表示 "干员" 信息的模型


class OperatorInfo(BaseModel):
    charid: str
    name: str = Field(alias="干员")
    # sequence: str = Field(alias="干员序号")
    rarity: str = Field(alias="稀有度")
    # country: str = Field(alias="国家")
    # organization: str = Field(alias="组织")
    # team: str = Field(alias="团队")
    profession: str = Field(alias="职业")

    # sub_profession: str = Field(alias="子职业")
    # race: str = Field(alias="种族")
    # artist: str = Field(alias="画师")
    @property
    def star(self) -> int:
        return int(self.rarity) + 1


# 定义一个表示 "cargoquery" 的模型
class CargoQuery(BaseModel):
    cargoquery: list[OperatorInfo]

    @root_validator(pre=True)
    def remove_title_and_convert(cls, values):
        if "cargoquery" in values:
            values["cargoquery"] = [
                OperatorInfo(**item["title"]) if "title" in item else None
                for item in values["cargoquery"]
            ]
        return values


class DrawHandleCtx(BaseModel):
    """处理函数的上下文"""

    session: EventSession
    transaction: Any

    def get_user_id(self) -> str | None:
        return self.session.id1


DrawResultType = tuple[str, int]
"""干员名字,抽到的次数"""

VoicePartType = tuple[str, str, str]
"""语音title、语音文本、语音标识号"""

VoiceHtmlPraseType = dict[str, list[VoicePartType]]
"""key:干员名字 value:语音部分列表"""

VoiceUrlResultType = tuple[str, str, str, str]
"""语音列表解析结果:中文url、日文url、语音文本,语音标题"""
