from PIL import Image, ImageDraw, ImageFont
import svgwrite
import logging

def color_rules(line):
    line = line.lower()
    if 'installing' in line:
        return 'purple'
    elif 'fetching' in line:
        return "orange"
    elif 'complete' in line:
        return "orange"
    else:
        return 'black'


def generate_raster_microprint_from_text(text, scale=2, output_filename="microprint.png"):
    logging.info('Generating raster microprint')

    text_lines = text.split('\n')
    new_scale = scale * 10
    
    size_x = 70 * new_scale
    size_y = len(text_lines) * (new_scale + 1)

    img = Image.new('RGBA', (int(size_x), int(size_y)), color="white")

    d = ImageDraw.Draw(img)
    d.fontmode = "L"

    font = ImageFont.truetype("fonts/NotoSans-Regular.ttf", new_scale)

    y = new_scale
    for line in text_lines:
        x = new_scale

        fill_color = color_rules(line)
        
        for char in line:
            if char != " " and char != "\n":
                d.text((x, y), text=char, font=font, fill=fill_color)

            x += font.getlength(char)
            
        y += new_scale

    img_resized = img.resize((int(size_x / 2), int(size_y / 2)), Image.Resampling.LANCZOS)
    img_resized.save(output_filename)


def generate_svg_microprint_from_text(text, scale=9, output_filename="microprint.svg"):
    logging.info('Generating svg microprint')

    text_lines = text.split('\n')

    dwg = svgwrite.Drawing(output_filename, (50 * scale, (len(text_lines) + 1) * scale))

    paragraph = dwg.add(dwg.g(font_size=scale))

    y = scale + 1

    for line in text_lines:
        fill_color = color_rules(line)

        atext = dwg.text(line, insert=(0, y), fill=fill_color)
        
        paragraph.add(atext)

        y += scale + 1

    dwg.save()
