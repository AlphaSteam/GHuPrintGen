from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt


def color_rules(line):
    if 'Installing' in line:
        return 'purple'
    elif 'Fetching' in line:
        return "orange"
    else:
        return 'black'


def convert_text(filename, scale):
    f = open(filename, "r")
    new_scale = scale * 10
    lines = f.readlines()
    size_x = 70 * new_scale
    size_y = len(lines) * (new_scale + 1)
    img = Image.new('RGBA', (int(size_x), int(size_y)), color="white")
    d = ImageDraw.Draw(img)
    d.fontmode = "L"
    font = ImageFont.truetype("NotoSans-Regular.ttf", new_scale)

    y = new_scale
    for line in lines:
        x = new_scale
        fill_color = color_rules(line)
        for char in line:
            if char != " " and char != "\n":
                d.text((x, y), text=char, font=font, fill=fill_color)
            x += font.getlength(char)
        y += new_scale

    plt.figure(constrained_layout=True, figsize=(10, 30))
    plt.xticks([])
    plt.yticks([])
    img_resized = img.resize((int(size_x / 2), int(size_y / 2)), Image.Resampling.LANCZOS)

    plt.imshow(img_resized)
    plt.show()
    img_resized.save("test-text.png")


