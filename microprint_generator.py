from PIL import Image, ImageDraw, ImageFont
import svgwrite
import logging
import json
from pathlib import Path
import os
from abc import ABC, abstractmethod
import math


class MicroprintGenerator(ABC):

    def _load_config_file(self):
        config_path = Path(os.environ['INPUT_MICROPRINT_CONFIG_PATH'])
        config_filename = (
            os.environ['INPUT_MICROPRINT_CONFIG_FILENAME'] + ".json")

        config_file_path = config_path / config_filename

        try:
            _file = open(config_file_path)
        except OSError as _:
            self.rules = {}
        else:
            with _file:
                rules = json.load(_file)

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
        self.scale_with_spacing = self.scale * self.vertical_spacing

        self.scaled_microprint_height = len(
            self.text_lines) * self.scale_with_spacing

        if "number_of_columns" not in self.rules:

            self.max_microprint_height = self.rules.get(
                "max_microprint_height", len(self.text_lines) * self.scale_with_spacing)

            self.number_of_columns = math.ceil(
                self.scaled_microprint_height / self.max_microprint_height)
        else:
            self.number_of_columns = self.rules["number_of_columns"]

            self.max_microprint_height = math.floor(
                self.scaled_microprint_height / self.number_of_columns)

        self.column_width = self.rules.get(
            "microprint_width", 120)

        self.column_gap_size = self.rules.get(
            "column_gap_size", 0.2) * self.scale
        self.column_gap_color = self.rules.get("column_gap_color", "white")

        self.microprint_width = (
            self.column_width + self.column_gap_size) * self.number_of_columns

        self.microprint_height = min(
            len(self.text_lines) * self.scale_with_spacing, self.max_microprint_height)

        self.text_lines_per_column = math.floor(
            self.microprint_height / self.scale_with_spacing)

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
            output_filename, (self.microprint_width, self.microprint_height), debug=False)

        self.font_family = self.rules.get("font-family", "Sans")
        self._load_svg_fonts()

    def render_microprint_column(self, first_line, last_line, x_with_gap, y, current_line):

        backgrounds = self.drawing.add(self.drawing.g())
        texts = self.drawing.add(self.drawing.g(font_size=self.scale))

        attributes = {'xml:space': 'preserve',
                      "font-family": self.font_family}

        texts.update(attributes)

        for text_line in self.text_lines[first_line:last_line]:
            background_color = self.check_color_line_rule(
                color_type="background_color", text_line=text_line)

            background_rect = self.drawing.rect(insert=(x_with_gap, y),
                                                size=(self.column_width,
                                                      self.scale + 0.3),
                                                rx=None, ry=None, fill=background_color)

            text_color = self.check_color_line_rule(
                color_type="text_color", text_line=text_line)

            text = self.drawing.text(text_line, insert=(x_with_gap, y),
                                     fill=text_color, dominant_baseline="hanging")

            text.update({"data-text-line": current_line})
            background_rect.update({"data-text-line": current_line})

            backgrounds.add(background_rect)
            texts.add(text)

            y += self.scale_with_spacing
            current_line += 1

    def render_microprint(self):
        logging.info('Generating svg microprint')

        default_background_color = self.default_colors["background_color"]

        self.drawing.add(self.drawing.rect(insert=(0, 0), size=('100%', '100%'),
                                           rx=None, ry=None, fill=default_background_color))

        current_line = 0

        for column in range(self.number_of_columns):
            x = math.ceil(column * self.column_width)
            x_with_gap = x if column == 0 else x + self.column_gap_size

            self.drawing.add(self.drawing.rect(insert=(x_with_gap, 0), size=(self.column_width, '100%'),
                                               rx=None, ry=None, fill=default_background_color))

            if column != 0:
                self.drawing.add(self.drawing.rect(insert=(x, 0), size=(self.column_gap_size, '100%'),
                                                   rx=None, ry=None, fill=self.column_gap_color))

            y = 0

            first_line = math.ceil(column * self.text_lines_per_column)

            last_line = min(
                math.ceil((column + 1) * self.text_lines_per_column), len(self.text_lines) - 1)

            if first_line >= len(self.text_lines):
                break

            self.render_microprint_column(
                first_line=first_line, last_line=last_line, x_with_gap=x_with_gap, y=y, current_line=current_line)

            current_line += self.text_lines_per_column

        self.drawing.save()


class RasterMicroprintGenerator(MicroprintGenerator):

    def __init__(self, output_filename="microprint.png", text=""):
        super().__init__(output_filename, text)
        default_background_color = self.default_colors["background_color"]

        self.img = Image.new('RGB', (int(self.microprint_width), int(self.microprint_height)),
                             color=default_background_color)

        self.drawing = ImageDraw.Draw(self.img)
        self.drawing.fontmode = "1"

    def render_microprint(self):
        logging.info('Generating raster microprint')

        font = ImageFont.truetype(
            "fonts/NotoSans-Regular.ttf", int(self.scale))

        y = 0

        for text_line in self.text_lines:
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
