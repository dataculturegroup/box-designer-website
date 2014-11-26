from boxmaker.box import Box

APP_NAME = "BoxMaker"
APP_VERSION = "2.0.0"
WEBSITE_URL = "http://boxmaker.connectionlab.org"

def render(file_path,width,height,depth,thickness,
           cut_width,notch_length,draw_bounding_box=False):
    the_box = Box(file_path,width,height,depth,thickness,
           			   cut_width,notch_length,draw_bounding_box)
    the_box.render()
