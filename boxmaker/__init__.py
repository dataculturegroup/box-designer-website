import os

from boxmaker.box import Box

APP_NAME = "box designer"
APP_VERSION = "2.4.4"
WEBSITE_URL = "http://boxdesigner.connectionlab.org"

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def render(file_path, width, height, depth, thickness, cut_width, notch_length, draw_bounding_box=False,
           file_type='pdf', tray=False):
    the_box = Box(file_path, width, height, depth, thickness, cut_width, notch_length, draw_bounding_box,
                  file_type, tray)
    the_box.render()
