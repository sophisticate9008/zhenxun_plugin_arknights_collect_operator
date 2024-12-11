from nonebot_plugin_alconna import Args, Option, Alconna, on_alconna


# _matcher = on_alconna(
#     Alconna(
#         "色图",
#         Args["tags?", str],
#         Option("-n", Args["num", str, '1'], help_text="数量"),
#         Option("-id", Args["local_id", int], help_text="本地id"),
#         Option("-r", action=store_true, help_text="r18"),
#     ),
#     aliases={"涩图", "不够色", "来一发", "再来点"},
#     priority=5,
#     block=True,
# )

# _matcher.shortcut(
#      r"^(来|发|要|给).*?(?P<num>.*)[份|发|张|个|次|点](?P<tags>.*)[瑟|色|涩]图.*?",
#     command="色图",
#     arguments=["{tags}", "-n", "{num}"],
#     prefix=True,
# )
draw_matcher = on_alconna(
    Alconna(
        "抽干员",
        Option("-n", Args["num", str, "1"], help_text="数量"),
    ),
    priority=5,
    block=True,
)

draw_matcher.shortcut(
    r"^抽干员(?P<num>.*)连",
    command="抽干员",
    arguments=["-n", "{num}"],
)

draw_info_matcher = on_alconna(
    Alconna(
        "抽取情况",
        Args["info_type", str, "干员"],
    ),
    priority=5,
    block=True,
)
draw_info_matcher.shortcut(
    r"^我的(干员|六星记录)",
    command="抽取情况",
    arguments=["{0}"],
)

ticket_matcher = on_alconna(
    Alconna(
        "我的黄票",
        Args["operator?", str],
    ),
    priority=5,
    block=True,
)

ticket_matcher.shortcut(
    r"^黄票兑换(?P<tags>.*)",
    command="我的黄票",
    arguments=["{tags}"],
)

pic_matcher = on_alconna(
    Alconna(
        "干员图片",
        Args["operator", str],
        Args["pic_type", str, "立绘"],
        Option("-i", Args["index", int, 1], help_text="序列"),
    ),
    priority=5,
    block=True,
)

pic_matcher.shortcut(
    r"^(?P<operator>.*)(立绘|皮肤)(?P<index>\d*)",
    command="干员图片",
    arguments=["{operator}", "{1}", "-i", "{index}"],
)

voice_matcher = on_alconna(
    Alconna(
        "干员语音",
        Args["operator", str],
        Option("-t", Args["title", str, "随机"], help_text="标题"),
    ),
    priority=5,
    block=True,
)

voice_matcher.shortcut(
    r"^(?!方舟猜语音)(?P<operator>.*)语音(?P<title>.*)",
    command="干员语音",
    arguments=["{operator}", "-t", "{title}"],
)

voice_guess_matcher = on_alconna(
    "方舟猜语音",
    aliases={"再来一句"},
    priority=5,
    block=True,
)

