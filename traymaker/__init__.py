from traymaker.tray import Tray

APP_NAME = "tray designer (based on box designer)"
APP_VERSION = "2.1.0"
WEBSITE_URL = "@vincentadam87"

def render(file_path,width,height,depth,thickness,
           cut_width,notch_length,draw_bounding_box=False,tray=True):
    the_tray = Tray(file_path,width,height,depth,thickness,
           			   cut_width,notch_length,draw_bounding_box,tray)
    the_tray.render()
