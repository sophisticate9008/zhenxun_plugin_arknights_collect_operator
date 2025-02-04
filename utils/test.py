# from PIL import Image, ImageDraw, ImageFont, ImageFilter

# def generate_character_cell(item, font, cell_width, cell_height, avatar_size, padding, star_color_dict, position):
#     """
#     生成单个角色单元格。

#     参数：
#         item: dict，包含单个角色的信息。
#         font: ImageFont，字体对象。
#         cell_width: int，单元格宽度。
#         cell_height: int，单元格高度。
#         avatar_size: int，头像尺寸。
#         padding: int，内边距。
#         star_color_dict: dict，稀有度对应颜色。
#         position: tuple，单元格在网格中的位置 (row, col)。

#     返回：
#         Image 对象，单个单元格图像。
#     """
#     # 创建单元格的背景图层
#     bg_color = star_color_dict.get(item["stars"], "#f0f0f0")  # 默认灰色
#     bg_img = Image.new("RGBA", (cell_width, cell_height), bg_color)

#     # 判断是否需要为偶数位置添加遮罩
#     row, col = position
#     overlay = None
#     if (row + col) % 2 == 1:
#         # 仅添加遮罩，遮罩只是影响背景颜色而不会影响透明度
#         overlay = Image.new("RGBA", (cell_width, cell_height), (255, 255, 255, 50))  # 半透明遮罩

#     # 创建内容图层
#     content_img = Image.new("RGBA", (cell_width, cell_height), (0, 0, 0, 0))  # 完全透明背景

#     # 绘制灰色边框
#     draw = ImageDraw.Draw(content_img)

#     # 如果没有头像路径，则用占位矩形代替
#     avatar_x = padding
#     avatar_y = (cell_height - avatar_size) // 2
#     if "avatar" in item and item["avatar"]:
#         avatar = Image.open(item["avatar"]).resize((avatar_size, avatar_size))
#         content_img.paste(avatar, (avatar_x, avatar_y))
#     else:
#         draw.rectangle([ (avatar_x, avatar_y), (avatar_x + avatar_size, avatar_y + avatar_size) ], fill="#cccccc")

#     # 计算名字的宽度和位置，保证名字区有足够空间
#     name_x = avatar_x + avatar_size + padding
#     name_y = (cell_height - font.size) // 2

#     # 预留一个大致宽度给名字
#     name_width = cell_width - avatar_size - 3 * padding  # 名字区域宽度

#     # 绘制名字
#     draw.text((name_x, name_y), item["name"], fill="black", font=font)

#     # 绘制数字
#     number_x = cell_width - padding - 25
#     number_y = name_y
#     draw.text((number_x, number_y), str(item["number"]), fill="black", font=font)

#     # 如果有遮罩，合并遮罩到背景图层
#     if overlay:
#         bg_img = Image.alpha_composite(bg_img, overlay)

#     # 将背景和内容图层合成
#     final_img = Image.alpha_composite(bg_img, content_img)

#     return final_img

# def add_outer_shadow_to_image(img, shadow_offset=(10, 10), shadow_opacity=0.3, blur_radius=10):
#     """
#     为图像的外围添加阴影效果，而不改变内部内容。

#     参数：
#         img: Image，待加阴影的图像。
#         shadow_offset: tuple，阴影偏移量。
#         shadow_opacity: float，阴影透明度。
#         blur_radius: int，阴影模糊半径。

#     返回：
#         Image，添加阴影后的图像。
#     """
#     # 创建一个稍大的图像，用于绘制阴影
#     shadow_width = img.width + shadow_offset[0] * 2
#     shadow_height = img.height + shadow_offset[1] * 2
#     shadow_img = Image.new("RGBA", (shadow_width, shadow_height), (0, 0, 0, 0))

#     # 在背景图上绘制阴影矩形
#     draw = ImageDraw.Draw(shadow_img)
#     shadow_color = (0, 0, 0, int(255 * shadow_opacity))
#     draw.rectangle([shadow_offset, (shadow_width - shadow_offset[0], shadow_height - shadow_offset[1])], fill=shadow_color)

#     # 使用高斯模糊处理阴影
#     shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(blur_radius))

#     # 将原图粘贴到阴影图像中心
#     shadow_img.paste(img, (shadow_offset[0], shadow_offset[1]), img.convert("RGBA").getchannel("A"))

#     return shadow_img


# def generate_character_grid_with_shadow(data, output_path, cells_per_row=4):
#     """
#     生成角色网格图片，并添加阴影、透明度和外围分割线。

#     参数：
#         data: list，包含每个角色的信息，每项是一个字典，格式如下：
#             {
#                 "avatar": "头像图片路径",
#                 "name": "角色名字",
#                 "stars": "星级数量（整数）",
#                 "number": "数字"
#             }
#         output_path: str，生成的图片保存路径。
#         cells_per_row: int，每行单元格的数量。
#     """
#     # 定义图片尺寸和样式
#     cell_width = 225
#     cell_height = 60
#     avatar_size = 40
#     padding = 10
#     font_path = "D:/05.code/01.python_code/zhenxun_bot/resources/font/HYWenHei-85W.ttf"  # 请确保本地有合适的字体文件
#     font_size = 18

#     # 稀有度对应颜色
#     star_color_dict = {
#         6: "#ce8f2f",
#         5: "#e7c891",
#         4: "#b9b1d9",
#         3: "#87bce9"
#     }

#     # 加载字体
#     try:
#         font = ImageFont.truetype(font_path, font_size)
#     except:
#         raise Exception("请确保指定的字体文件存在！")

#     # 计算图片尺寸
#     rows = (len(data) + cells_per_row - 1) // cells_per_row
#     img_width = cell_width * cells_per_row
#     img_height = cell_height * rows

#     # 创建空白图片
#     img = Image.new("RGBA", (img_width, img_height), "white")

#     for idx, item in enumerate(data):
#         row = idx // cells_per_row
#         col = idx % cells_per_row

#         # 生成单元格
#         cell_img = generate_character_cell(
#             item, font, cell_width, cell_height, avatar_size, padding, star_color_dict, (row, col)
#         )

#         # 计算粘贴位置
#         x = col * cell_width
#         y = row * cell_height

#         img.paste(cell_img, (x, y), cell_img)

#     # 绘制水平和垂直分隔线
#     draw = ImageDraw.Draw(img)
#     # for row in range(1, rows):
#     #     y = row * cell_height
#     #     # draw.line((0, y, img_width, y), fill="#e5aabe", width=2)  # 绘制水平分隔线

#     # for col in range(1, cells_per_row):
#     #     x = col * cell_width
#         # draw.line((x, 0, x, img_height), fill="#e5aabe", width=2)  # 绘制垂直分隔线

#     # 绘制外围分割线
#     draw.rectangle([0, 0, img_width-1, img_height-1], outline="#e5aabe", width=4)

#     # 转换为RGB模式保存
#     img = img.convert("RGB")

#     # 添加阴影效果：给整个网格添加阴影
#     img_with_shadow = add_outer_shadow_to_image(img, shadow_offset=(20, 20), shadow_opacity=0.3, blur_radius=10)

#     # 创建一个新的背景，确保网格居上居中对齐
#     background_width = img_with_shadow.width + 0  # 增加边距
#     background_height = img_with_shadow.height + 0  # 增加边距
#     background = Image.new("RGBA", (background_width, background_height), (255, 255, 255, 255))  # 创建白色背景

#     # 计算居中的位置，确保图像水平居中，垂直居上
#     paste_x = (background_width - img_with_shadow.width) // 2
#     paste_y = 0  # 保证图像居上

#     # 将图像粘贴到居中位置
#     background.paste(img_with_shadow, (paste_x, paste_y), img_with_shadow)

#     # 添加粉色边框
#     final_width = background.width + 20  # 增加边距
#     final_height = background.height + 20
#     final_background = Image.new("RGBA", (final_width, final_height), "#fffbfc" )  # 白色背景
#     final_draw = ImageDraw.Draw(final_background)

#     # 绘制粉色边框
#     final_draw.rectangle([0, 0, final_width-1, final_height-1], outline="#FFB6C1", width=10)

#     # 将网格图像粘贴到最终背景
#     final_background.paste(background, (10, 10))

#     # 保存最终图像
#     final_background.save(output_path)

# # 示例数据
# example_data = [
#     {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},
#         {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},    {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},    {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},
#         {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},
#         {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},    {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},    {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},    {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},
#         {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},    {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},    {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},    {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},
#         {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},    {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},    {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},    {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},
#         {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},    {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},    {"avatar": "C:/Users/catastrophe9008/Desktop/85a990b34a93a4be27df3d6e6377d310.png", "name": "芙宁娜", "stars": 6, "number": 90},
#     {"avatar": None, "name": "芙宁娜男男女女", "stars": 6, "number": 90},
#     {"avatar": None, "name": "仆人", "stars": 5, "number": 90},
# ]

# # 调用函数
# generate_character_grid_with_shadow(example_data, "output_with_pink_border.png", cells_per_row=5)


# def str_to_num(_str: str) -> int:
#     # 定义中文数字到阿拉伯数字的映射
#     chinese_num_map = {
#         "一": 1,
#         "二": 2,
#         "三": 3,
#         "四": 4,
#         "五": 5,
#         "六": 6,
#         "七": 7,
#         "八": 8,
#         "九": 9,
#         "十": 10,
#         "百": 100,
#     }
#     # 如果字符串是纯阿拉伯数字
#     if _str.isdigit():
#         num = int(_str)
#         # 检查是否是十的倍数
#         if num % 10 == 0:
#             return num
#         return 1
#     # 如果字符串是中文数字
#     # 解析中文数字
#     num = 0
#     temp = 0
#     for char in _str:
#         if char in chinese_num_map:
#             if chinese_num_map[char] == 10:  # 十
#                 temp = temp if temp != 0 else 1
#                 num += temp * 10
#                 temp = 0
#             elif chinese_num_map[char] == 100:  # 百
#                 temp = temp if temp != 0 else 1
#                 num += temp * 100
#                 temp = 0
#             else:
#                 temp += chinese_num_map[char]
#     num += temp
#     # 检查是否是十的倍数
#     if num % 10 == 0:
#         return num
#     return 1

# print(str_to_num(""))
