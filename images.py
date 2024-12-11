from PIL import Image, ImageEnhance

from zhenxun.services.log import logger

from . import global_arg

resource_path = global_arg.Constant.resource_path
gacha_path = resource_path / "gacha"

six_bgi: Image.Image = Image.open(gacha_path / "back_six.png")
five_bgi: Image.Image = Image.open(gacha_path / "back_five.png")
four_bgi: Image.Image = Image.open(gacha_path / "back_four.png")
low_bgi: Image.Image = Image.new("RGBA", (124, 360), (49, 49, 49))
six_tail: Image.Image = Image.open(gacha_path / "six_02.png")

six_line: Image.Image = Image.open(gacha_path / "six_01.png")
five_line: Image.Image = Image.open(gacha_path / "five.png")
four_line: Image.Image = Image.open(gacha_path / "four.png")

star_circle: Image.Image = Image.open(gacha_path / "star_02.png")
enhance_five_line: Image.Image = Image.new("RGBA", (124, 720), (0x60, 0x60, 0x60, 0x50))
enhance_four_line: Image.Image = Image.new("RGBA", (124, 720), (132, 108, 210, 0x10))
brighter = ImageEnhance.Brightness(six_line)
six_line: Image.Image = brighter.enhance(1.5)
brighter = ImageEnhance.Brightness(four_line)
four_line: Image.Image = brighter.enhance(0.9)
six_line_up: Image.Image = six_line.crop((0, 0, six_line.size[0], 256))
six_line_down: Image.Image = six_line.crop((0, 256, six_line.size[0], 512))
five_line_up: Image.Image = five_line.crop((0, 0, five_line.size[0], 256))
five_line_down: Image.Image = five_line.crop((0, 256, five_line.size[0], 512))
four_line_up: Image.Image = four_line.crop((0, 0, four_line.size[0], 256))
four_line_down: Image.Image = four_line.crop((0, 256, four_line.size[0], 512))
logger.debug("basic image loaded.")
characters: dict[str, Image.Image] = {
    "先锋": Image.open(gacha_path / "图标_职业_先锋_大图_白.png"),
    "近卫": Image.open(gacha_path / "图标_职业_近卫_大图_白.png"),
    "医疗": Image.open(gacha_path / "图标_职业_医疗_大图_白.png"),
    "术师": Image.open(gacha_path / "图标_职业_术师_大图_白.png"),
    "狙击": Image.open(gacha_path / "图标_职业_狙击_大图_白.png"),
    "特种": Image.open(gacha_path / "图标_职业_特种_大图_白.png"),
    "辅助": Image.open(gacha_path / "图标_职业_辅助_大图_白.png"),
    "重装": Image.open(gacha_path / "图标_职业_重装_大图_白.png"),
}
logger.debug("careers image loaded.")
stars: dict[int, Image.Image] = {
    5: Image.open(gacha_path / "稀有度_白_5.png"),
    4: Image.open(gacha_path / "稀有度_白_4.png"),
    3: Image.open(gacha_path / "稀有度_白_3.png"),
    2: Image.open(gacha_path / "稀有度_白_2.png"),
}
logger.debug("stars image loaded.")
