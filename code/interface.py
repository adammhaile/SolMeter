import displayio
import time
from adafruit_display_text.label import Label
from terminalio import FONT
from adafruit_progressbar.horizontalprogressbar import (
    HorizontalProgressBar,
    HorizontalFillDirection,
)
import adafruit_imageload


class UI:
    def __init__(self, display, uv, beep):
        self.display = display
        self.uv = uv
        self.beep = beep

        self.rem_default = '--h--m'
        
        self.color_on = 0xffffff
        self.color_off = 0x000000
        
        self.__text_y_offset = 12
        
        self.setup_bg()
        self.load_images()
        self.show_splash()
        self.build_ui()
        
    def load_images(self):
        bmp, palette = adafruit_imageload.load('/img/sig.bmp', bitmap=displayio.Bitmap, palette=displayio.Palette)
        palette.make_transparent(0)
        self.bmp_sig = displayio.TileGrid(bmp, pixel_shader=palette)
        
        bmp, palette = adafruit_imageload.load('/img/sun.bmp', bitmap=displayio.Bitmap, palette=displayio.Palette)
        palette.make_transparent(0)
        self.bmp_sun = displayio.TileGrid(bmp, pixel_shader=palette)
        
        bmp, palette = adafruit_imageload.load('/img/battery.bmp', bitmap=displayio.Bitmap, palette=displayio.Palette)
        palette.make_transparent(0)
        self.bmp_battery = displayio.TileGrid(bmp, pixel_shader=palette, width=1, height=1, tile_width=24, tile_height=16)
        
        bmp, palette = adafruit_imageload.load('/img/summation.bmp', bitmap=displayio.Bitmap, palette=displayio.Palette)
        palette.make_transparent(0)
        self.bmp_summation = displayio.TileGrid(bmp, pixel_shader=palette)
        
        bmp, palette = adafruit_imageload.load('/img/target.bmp', bitmap=displayio.Bitmap, palette=displayio.Palette)
        palette.make_transparent(0)
        self.bmp_target = displayio.TileGrid(bmp, pixel_shader=palette)
        
        bmp, palette = adafruit_imageload.load('/img/rem_time.bmp', bitmap=displayio.Bitmap, palette=displayio.Palette)
        palette.make_transparent(0)
        self.bmp_rem_time = displayio.TileGrid(bmp, pixel_shader=palette)
        
    def setup_bg(self):
        # Create a bitmap with two colors
        self.bg_bmp = displayio.Bitmap(self.display.width, self.display.height, 2)

        # Create a two color palette
        self.palette = displayio.Palette(2)
        self.palette[0] = self.color_on
        self.palette[1] = self.color_off

        # Create a TileGrid using the Bitmap and Palette
        self.bg = displayio.TileGrid(self.bg_bmp, pixel_shader=self.palette)
        self.bg_bmp.fill(0)
        
    def show_splash(self):
        sig_group = displayio.Group()
        sig_group.append(self.bg)
        self.bmp_sig.x = 0
        self.bmp_sig.y = 0
        sig_group.append(self.bmp_sig)
        self.display.show(sig_group)
        self.beep.PlaySong()
        sig_group.remove(self.bg)
        
    def text_y(self, val):
        return val - self.__text_y_offset
        
    def build_ui(self):
        # create root group for display
        self.root = displayio.Group()
        self.root.append(self.bg)
        
        # create mapped UV value progress bar
        self.bmp_sun.x = 0
        self.bmp_sun.y = 4
        self.root.append(self.bmp_sun)
        
        bar_x = 26
        bar_y = self.bmp_sun.y
        bar_w = self.display.width - bar_x
        bar_h = 24
        
        self.uv_bar = HorizontalProgressBar((bar_x, bar_y), (bar_w, bar_h), 
                                            direction=HorizontalFillDirection.LEFT_TO_RIGHT,
                                            min_value=0, max_value=self.uv.mapped_max, value=0,
                                            bar_color=self.color_off, outline_color=self.color_off, fill_color=self.color_on)
                                            
        self.root.append(self.uv_bar)
        
        self.uv_bar
        
        # create cumulative UV value label
        cur_y = bar_y + bar_h + 10
        self.bmp_summation.x = 0
        self.bmp_summation.y = cur_y
        self.root.append(self.bmp_summation)
        
        self.uv_val = Label(font=FONT, text="0", scale=3, line_spacing=1.2, color=1)
        self.uv_val.anchor_point = (1.0, 0.0)
        self.uv_val.anchored_position = (self.display.width, self.text_y(cur_y))
        
        self.root.append(self.uv_val)
        
        # create target value UI
        cur_y += (26 + 10)
        self.bmp_target.x = 0
        self.bmp_target.y = cur_y
        self.root.append(self.bmp_target)
        
        self.target_val = Label(font=FONT, text="", scale=3, line_spacing=1.2, color=1)
        self.target_val.anchor_point = (1.0, 0.0)
        self.target_val.anchored_position = (self.display.width, self.text_y(cur_y))
        
        self.root.append(self.target_val)
        
        # create remaining time UI
        cur_y += (26 + 10)
        self.bmp_rem_time.x = 0
        self.bmp_rem_time.y = cur_y
        self.root.append(self.bmp_rem_time)
        
        self.remaining_time = Label(font=FONT, text=self.rem_default, scale=3, line_spacing=1.2, color=1)
        self.remaining_time.anchor_point = (1.0, 0.0)
        self.remaining_time.anchored_position = (self.display.width, self.text_y(cur_y))
        
        self.root.append(self.remaining_time)
        
        # # create status message UI
        
        # cur_y += (26 + 5)
        
        # self.status = Label(font=FONT, text=self.status_default, scale=2, line_spacing=1.2, color=1)
        # self.status.anchor_point = (1.0, 0.0)
        # self.status.anchored_position = (self.display.width, self.text_y(cur_y))
        
        # self.root.append(self.status)
        
        # create battery status
        self.bmp_battery[0] = 3
        self.bmp_battery.x = self.display.width - 26
        self.bmp_battery.y = self.display.height - 16
        self.root.append(self.bmp_battery)
        
        # create battery percent label
        # self.bat_val = Label(font=FONT, text="", scale=1, line_spacing=1.2, color=1)
        # self.bat_val.anchor_point = (1.0, 0.0)
        # self.bat_val.anchored_position = (self.bmp_battery.x, self.bmp_battery.y)
        # self.root.append(self.bat_val)
        
        self.display.show(self.root)
        
    def UpdateBattery(self, percent):
        if percent < 25:
            self.bmp_battery[0] = 3
        elif percent >= 25 and percent < 50:
            self.bmp_battery[0] = 2
        elif percent >= 50 and percent < 75:
            self.bmp_battery[0] = 1
        else:
            self.bmp_battery[0] = 0
            
        # self.bat_val.text = str(percent) + '% '

    