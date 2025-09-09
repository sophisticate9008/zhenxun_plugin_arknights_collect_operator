import io
from pathlib import Path

from PIL.Image import Image as tImage
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from .. import global_arg
from ..arknights_types import DrawResultType
from ..utils.storage import get_avatar_img, get_portrait_img
from ..utils.operator import get_info_by_name
from ..images import (
    stars,
    low_bgi,
    six_bgi,
    five_bgi,
    four_bgi,
    six_tail,
    characters,
    six_line_up,
    star_circle,
    five_line_up,
    four_line_up,
    six_line_down,
    five_line_down,
    four_line_down,
    enhance_five_line,
    enhance_four_line,
)

resource_path = Path(__file__).parent.parent / "resource"


async def simulate_image(draw_result: list[DrawResultType]) -> io.BytesIO:
    """
    依据抽卡结果生成模拟十连图片

    :param res: 抽卡结果
    :return: 图片的bytes
    """
    base = 20
    offset = 124
    l_offset = 14
    back_img = Image.open(resource_path / "gacha" / "back_image.png")
    for res in draw_result:
        info = get_info_by_name(res[0])
        portrait_img = await get_portrait_img(res[0], info.charid)
        portrait: Image.Image = (
            Image.open(portrait_img)
            if portrait_img
            else Image.open(
                global_arg.Constant.resource_path / "gacha" / "半身像_无_1.png"
            )
        )
        portrait = resize_and_crop(portrait, offset, 360)
        # portrait.resize((offset, 360), Image.Resampling.LANCZOS)
        logo: Image.Image = characters[info.profession].resize(
            (96, 96), Image.Resampling.LANCZOS
        )
        _draw = ImageDraw.Draw(portrait)
        s_size = stars[int(info.rarity)].size
        star = stars[int(info.rarity)].resize(
            (int(s_size[0] * 0.6), int(47 * 0.6)), Image.Resampling.LANCZOS
        )
        s_offset = (offset - int(star.size[0])) // 2

        if int(info.rarity) == 5:
            back_img.paste(six_line_up, (base, 0), six_line_up)
            back_img.paste(six_line_down, (base, 720 - 256), six_line_down)
            back_img.paste(six_tail, (base, 0), six_tail)
            back_img.paste(
                six_tail.transpose(Image.Transpose.ROTATE_180),
                (base, 720 - 256),
                six_tail.transpose(Image.Transpose.ROTATE_180),
            )
            basei = six_bgi.copy()
        elif int(info.rarity) == 4:
            back_img.paste(enhance_five_line, (base, 0), enhance_five_line)
            back_img.paste(five_line_up, (base, 0), five_line_up)
            back_img.paste(five_line_down, (base, 720 - 256), five_line_down)
            basei = five_bgi.copy()
        elif int(info.rarity) == 3:
            back_img.paste(enhance_four_line, (base, 0), enhance_four_line)
            back_img.paste(four_line_up, (base, 0), four_line_up)
            back_img.paste(four_line_down, (base, 720 - 256), four_line_down)
            back_img.paste(star_circle, (base - 2, 180 - 64), star_circle)
            basei = four_bgi.copy()
        else:
            basei = low_bgi.copy()
        size = portrait.size
        portrait.thumbnail(size)
        basei.paste(portrait, (0, 0), portrait)
        back_img.paste(basei, (base, 180))
        s_size = star.size
        star.thumbnail(s_size)
        back_img.paste(star, (base + s_offset, 166), star)
        l_size = logo.size
        logo.thumbnail(l_size)
        back_img.paste(logo, (base + l_offset, 492), logo)
        base += offset
    imageio = io.BytesIO()
    back_img.save(
        imageio,
        format="JPEG",
        quality=95,
        subsampling=2,
        qtables="web_high",
    )
    return imageio


async def generate_character_grid_pic(
    data: list[tuple[str, int]], cells_per_row=5
) -> io.BytesIO:
    """
    生成角色网格图片，并添加阴影、透明度和外围分割线。

    参数：
        data: tuple[str, int]，干员名字和次数
        cells_per_row: int，每行单元格的数量。
    """
    # 定义图片尺寸和样式
    cell_width = 225
    cell_height = 60
    # 计算图片尺寸
    rows = (len(data) + cells_per_row - 1) // cells_per_row
    img_width = cell_width * cells_per_row
    img_height = cell_height * rows
    # 创建空白图片
    img = Image.new("RGBA", (img_width, img_height), "white")

    for idx, item in enumerate(data):
        row = idx // cells_per_row
        col = idx % cells_per_row
        # 生成单元格
        cell_img = await generate_character_cell(
            item, (cell_width, cell_height), (row, col)
        )
        # 计算粘贴位置
        x = col * cell_width
        y = row * cell_height
        img.paste(cell_img, (x, y), cell_img)

    # 绘制水平和垂直分隔线
    draw = ImageDraw.Draw(img)
    # 绘制外围分割线
    draw.rectangle([0, 0, img_width - 1, img_height - 1], outline="#e5aabe", width=4)
    # 转换为RGB模式保存
    img = img.convert("RGB")
    # 添加阴影效果：给整个网格添加阴影
    img_with_shadow = add_outer_shadow_to_image(
        img, shadow_offset=(20, 20), shadow_opacity=0.3, blur_radius=10
    )
    # 创建一个新的背景，确保网格居上居中对齐
    background_width = img_with_shadow.width + 0  # 增加边距
    background_height = img_with_shadow.height + 0  # 增加边距
    background = Image.new(
        "RGBA", (background_width, background_height), "#fffbfc"
    )  # 创建白色背景
    # 计算居中的位置，确保图像水平居中，垂直居上
    paste_x = (background_width - img_with_shadow.width) // 2
    paste_y = 0  # 保证图像居上
    # 将图像粘贴到居中位置
    background.paste(img_with_shadow, (paste_x, paste_y), img_with_shadow)
    # 添加粉色边框
    final_width = background.width + 20  # 增加边距
    final_height = background.height + 20
    final_background = Image.new(
        "RGBA", (final_width, final_height), "#fffbfc"
    )  # 白色背景
    final_draw = ImageDraw.Draw(final_background)

    # 绘制粉色边框
    final_draw.rectangle(
        [0, 0, final_width - 1, final_height - 1], outline="#FFB6C1", width=10
    )

    # 将网格图像粘贴到最终背景
    final_background.paste(background, (10, 10))
    imageio = io.BytesIO()
    final_background.save(imageio, format="PNG")
    return imageio


async def generate_character_cell(
    item: tuple[str, int], cell_wh: tuple[int, int], position: tuple[int, int]
):
    """
    生成单个角色单元格。

    参数：
        item: dict，包含单个角色的信息。
        position: tuple，单元格在网格中的位置 (row, col)。

    返回：
        Image 对象，单个单元格图像。
    """
    # 设置内置参数
    cell_width = cell_wh[0]  # 单元格宽度
    cell_height = cell_wh[1]  # 单元格高度
    avatar_size = 50  # 头像尺寸
    padding = 10  # 内边距
    font_size = 18
    font_path = global_arg.Constant.font_path
    font_truetype = ImageFont.truetype(str(font_path), font_size)
    info = get_info_by_name(item[0])
    star = info.star
    star_color_dict = {6: "#ce8f2f", 5: "#e7c891", 4: "#b9b1d9", 3: "#87bce9"}
    # 创建单元格的背景图层
    bg_color = star_color_dict.get(star, "#f0f0f0")  # 默认灰色
    bg_img = Image.new("RGBA", (cell_width, cell_height), bg_color)
    # 判断是否需要为偶数位置添加遮罩
    row, col = position
    overlay = None
    if (row + col) % 2 == 1:
        # 仅添加遮罩，遮罩只是影响背景颜色而不会影响透明度
        overlay = Image.new(
            "RGBA", (cell_width, cell_height), (255, 255, 255, 50)
        )  # 半透明遮罩
    # 创建内容图层
    content_img = Image.new(
        "RGBA", (cell_width, cell_height), (0, 0, 0, 0)
    )  # 完全透明背景

    draw = ImageDraw.Draw(content_img)

    # 如果没有头像路径，则用占位矩形代替
    avatar_x = padding
    avatar_y = (cell_height - avatar_size) // 2
    _avatar = await get_avatar_img(item[0], 0)
    if _avatar:
        avatar = Image.open(_avatar).resize((avatar_size, avatar_size))
        content_img.paste(avatar, (avatar_x, avatar_y))
    else:
        draw.rectangle(
            [(avatar_x, avatar_y), (avatar_x + avatar_size, avatar_y + avatar_size)],
            fill="#cccccc",
        )

    # 计算名字的宽度和位置，保证名字区有足够空间
    name_x = avatar_x + avatar_size + padding
    name_y = (cell_height - font_truetype.size) // 2

    # 预留一个大致宽度给名字
    # 绘制名字
    draw.text((name_x, name_y), info.name, fill="black", font=font_truetype)
    # 绘制数字
    number_x = cell_width - padding - 25
    number_y = name_y
    draw.text((number_x, number_y), str(item[1]), fill="black", font=font_truetype)

    # 如果有遮罩，合并遮罩到背景图层
    if overlay:
        bg_img = Image.alpha_composite(bg_img, overlay)

    return Image.alpha_composite(bg_img, content_img)


def add_outer_shadow_to_image(
    img, shadow_offset=(10, 10), shadow_opacity=0.3, blur_radius=10
):
    """
    为图像的外围添加阴影效果，而不改变内部内容。

    参数：
        img: Image，待加阴影的图像。
        shadow_offset: tuple，阴影偏移量。
        shadow_opacity: float，阴影透明度。
        blur_radius: int，阴影模糊半径。

    返回：
        Image，添加阴影后的图像。
    """
    # 创建一个稍大的图像，用于绘制阴影
    shadow_width = img.width + shadow_offset[0] * 2
    shadow_height = img.height + shadow_offset[1] * 2
    shadow_img = Image.new("RGBA", (shadow_width, shadow_height), (0, 0, 0, 0))
    # 在背景图上绘制阴影矩形
    draw = ImageDraw.Draw(shadow_img)
    shadow_color = (0, 0, 0, int(255 * shadow_opacity))
    draw.rectangle(
        [
            shadow_offset,
            (shadow_width - shadow_offset[0], shadow_height - shadow_offset[1]),
        ],
        fill=shadow_color,
    )
    # 使用高斯模糊处理阴影
    shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(blur_radius))
    # 将原图粘贴到阴影图像中心
    shadow_img.paste(
        img, (shadow_offset[0], shadow_offset[1]), img.convert("RGBA").getchannel("A")
    )
    return shadow_img


def resize_and_crop(image: tImage, target_width: int, target_height: int) -> tImage:
    """
    按照目标宽度和高度调整图像大小，保持中心对齐，裁剪多余的部分。

    :param image: 原始图像对象
    :param target_width: 目标宽度
    :param target_height: 目标高度
    :return: 调整后的图像对象
    """
    # 获取原始图像的宽度和高度
    width, height = image.size

    # 计算宽度和高度的缩放比例
    width_ratio = target_width / float(width)
    height_ratio = target_height / float(height)

    # 选择最适合的比例来缩放
    ratio = max(width_ratio, height_ratio)

    # 计算缩放后的新尺寸
    new_width = int(width * ratio)
    new_height = int(height * ratio)

    # 先按比例缩放图像
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # 计算裁剪区域，确保裁剪区域居中
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = (new_width + target_width) // 2
    bottom = (new_height + target_height) // 2

    # 裁剪并返回图像
    return resized_image.crop((left, top, right, bottom))
