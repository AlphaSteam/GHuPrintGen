from PIL import Image, ImageDraw, ImageFont
import svgwrite
import logging
import json
from pathlib import Path
import os
from abc import ABC


class MicroprintGenerator(ABC):

    def _load_config_file(self):
        config_path = Path(os.environ['INPUT_MICROPRINT_CONFIG_PATH'])
        config_filename = (
            os.environ['INPUT_MICROPRINT_CONFIG_FILENAME'] + ".json")

        config_file_path = config_path / config_filename

        try:
            file = open(config_file_path)
        except OSError as e:
            return {"error": e}
        else:
            with file:
                rules = json.load(file)

                self.rules = rules

    def _set_default_colors(self):
        fallback_colors = {"background_color": "white", "text_color": "black"}

        default_colors = self.rules.get("default_colors", fallback_colors)

        default_colors["background_color"] = default_colors.get(
            "background_color", fallback_colors["background_color"])

        default_colors["text_color"] = default_colors.get(
            "text_color", fallback_colors["text_color"])

        self.default_colors = default_colors

    def __init__(self, output_filename, text):

        self.output_filename = output_filename
        self.text_lines = text.split('\n')

        self._load_config_file()

        self.scale = self.rules.get("scale", 2)
        self.vertical_spacing = self.rules.get("vertical_spacing", 1)
        self.microprint_width = self.rules.get("microprint_width", 120)

        self.scale_with_spacing = self.scale * self.vertical_spacing

        self.microprint_height = len(self.text_lines) * self.scale_with_spacing

        self._set_default_colors()

    def check_color_line_rule(self, color_type, text_line):
        text_line = text_line.lower()

        line_rules = self.rules.get("line_rules", {})

        default_color = self.default_colors[color_type]

        for rule in line_rules:
            if text_line.find(rule) != -1:
                return line_rules[rule].get(color_type, default_color)

        return default_color

    @abstractmethod
    def render_microprint(self):
        pass


class SVGMicroprintGenerator(MicroprintGenerator):

    def _load_svg_fonts(self):

        additional_fonts = self.rules.get("additional_fonts",
                                          {"google_fonts": [],
                                           "truetype_fonts": []})

        google_fonts = additional_fonts.get("google_fonts", [])

        truetype_fonts = additional_fonts.get("truetype_fonts", [])

        for count, google_font in enumerate(google_fonts):
            name = google_font["name"]
            url = google_font["google_font_url"]

            self.drawing.embed_google_web_font(name, url)

        for count, truetype_font in enumerate(truetype_fonts):
            name = truetype_font["name"]
            truetype_file = truetype_font["truetype_file"]

            self.drawing.embed_font(name, truetype_file)

    def __init__(self, output_filename="microprint.svg", text=""):
        super().__init__(output_filename, text)

        self.drawing = svgwrite.Drawing(
            output_filename, (self.microprint_width, self.microprint_height))

        self.font_family = self.rules.get("font-family", "Sans")
        self._load_svg_fonts()

    def render_microprint(self):
        logging.info('Generating svg microprint')

        default_background_color = self.default_colors["background_color"]

        self.drawing.add(self.drawing.rect(insert=(0, 0), size=('100%', '100%'),
                                           rx=None, ry=None, fill=default_background_color))

        backgrounds = self.drawing.add(self.drawing.g())
        texts = self.drawing.add(self.drawing.g(font_size=self.scale))

        attributes = {'xml:space': 'preserve',
                      "font-family": self.rules["font-family"]}

        texts.update(attributes)

        y = 0

        for text_line in self.text_lines:
            background_color = self.check_color_line_rule(
                color_type="background_color", text_line=text_line)

            background_rect = self.drawing.rect(insert=(0, y), size=('100%', self.scale + 0.3),
                                                rx=None, ry=None, fill=background_color)

            text_color = self.check_color_line_rule(
                color_type="text_color", text_line=text_line)

            text = self.drawing.text(text_line, insert=(0, y),
                                     fill=text_color, dominant_baseline="hanging")

            backgrounds.add(background_rect)
            texts.add(text)

            y += self.scale_with_spacing

        self.drawing.save()


class RasterMicroprintGenerator(MicroprintGenerator):

    def __init__(self, output_filename="microprint.png", text=""):
        super().__init__(output_filename, text)
        default_background_color = self.default_colors["background_color"]

        self.img = Image.new('RGB', (int(self.microprint_width), int(self.microprint_height)),
                             color=default_background_color)

        self.drawing = ImageDraw.Draw(img)
        self.drawing.fontmode = "1"

    def render_microprint(self):
        logging.info('Generating raster microprint')

        font = ImageFont.truetype(
            "fonts/NotoSans-Regular.ttf", int(self.scale))

        y = 0

        for text_line in text_lines:
            background_color = self.check_color_line_rule(
                color_type="background_color", text_line=text_line)

            self.drawing.rectangle([(0, y - self.scale_with_spacing), (self.microprint_width, y)],
                                   fill=background_color, outline=None, width=1)

            text_color = self.check_color_line_rule(
                color_type="text_color", text_line=text_line)

            self.drawing.text((0, y), text=text_line, font=font,
                              fill=text_color, anchor="ls")

            y += self.scale_with_spacing

        self.img.save(self.output_filename)
