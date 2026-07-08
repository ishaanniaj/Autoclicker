import os.path

# Source app to package (installed copy is clean + signed)
application = "/Applications/Autoclicker.app"
appname = os.path.basename(application)

format = "UDZO"                       # compressed, read-only
files = [application]
symlinks = {"Applications": "/Applications"}

background = "dmg_bg.png"
window_rect = ((240, 220), (640, 420))   # ((x, y), (width, height))
default_view = "icon-view"
icon_size = 110
text_size = 13

# icon positions match the arrow in the background image
icon_locations = {
    appname: (160, 180),
    "Applications": (480, 180),
}

include_icon_view_settings = True
include_list_view_settings = False
show_status_bar = False
show_tab_view = False
show_toolbar = False
show_pathbar = False
show_sidebar = False
