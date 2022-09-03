from PIL import Image, ImageDraw, ImageFont
import svgwrite
import logging

def get_rules():
    file = open('config.json')

    config = json.load(file)

    return config


def check_color_line_rule(rules, color_type, text_line):
    text_line = text_line.lower()

    line_rules = rules["line_rules"]
    for rule in line_rules:
        if text_line.find(rule) != -1:
            return line_rules[rule][color_type]

    if color_type == "text_color":
        return rules["default_colors"]["text_color"]

    return rules["default_colors"]["background_color"]


def generate_raster_microprint_from_text(text, scale=2, vertical_spacing=1, output_filename="microprint.png"):
    logging.info('Generating raster microprint')

    text_lines = text.split('\n')
    
    scale_with_spacing = scale * vertical_spacing

    rules = get_rules()

    size_x = 40 * scale
    size_y = len(text_lines) * scale_with_spacing

    default_background_color = rules["default_colors"]["background_color"]

    img = Image.new('RGBA', (int(size_x), int(size_y)), color=default_background_color)

    d = ImageDraw.Draw(img)
    d.fontmode = "L"

    font = ImageFont.truetype("fonts/NotoSans-Regular.ttf", scale)

    y = 0
    for line in text_lines:
        background_color = check_color_line_rule(rules=rules, color_type="background_color", text_line=text_line)

        ImageDraw.rectangle((0, y), fill=background_color, outline=None, width=1)

        text_color = check_color_line_rule(rules=rules, color_type="text_color", text_line=text_line)
        
        d.text((0, y), text=line, font=font, fill=text_color)
            
        y += scale

    img.save(output_filename)


def generate_svg_microprint_from_text(text, scale=2, vertical_spacing=1, output_filename="microprint.svg"):
    logging.info('Generating svg microprint')

    text_lines = text.split('\n')

    scale_with_spacing = scale * vertical_spacing

    rules = get_rules()

    svg_width = 40 * scale
    svg_height = len(text_lines) * scale_with_spacing

    dwg = svgwrite.Drawing(output_filename, (svg_width, svg_height))

    default_background_color = rules["default_colors"]["background_color"]

    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill=default_background_color))

    backgrounds = dwg.add(dwg.g())
    texts = dwg.add(dwg.g(font_size=scale))

    attribs = {'xml:space': 'preserve'}
    texts.update(attribs)

    y = 0
    for text_line in text_lines:
        background_color = check_color_line_rule(rules=rules, color_type="background_color", text_line=text_line)

        background_rect = dwg.rect(insert=(0, y), size=('100%', scale + 0.3),
                                   rx=None, ry=None, fill=background_color)

        text_color = check_color_line_rule(rules=rules, color_type="text_color", text_line=text_line)

        text = dwg.text(text_line, insert=(0, y),
                        fill=text_color, dominant_baseline="hanging")

        backgrounds.add(background_rect)
        texts.add(text)

        y += scale_with_spacing

    dwg.save()
