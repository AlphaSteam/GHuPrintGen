from PIL import Image, ImageDraw, ImageFont


def color_rules(line):
    if 'Installing' in line:
        return 'purple'
    elif 'Fetching' in line:
        return "orange"
    else:
        return 'black'


def generate_microprint_from_text(text, scale=3, output_filename="microprint.png"):

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


