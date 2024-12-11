from .. import global_arg
from ..types import OperatorInfo


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
