import time
import board
import json

import displayio
import framebufferio
import sharpdisplay

from analogio import AnalogIn

from dialpad import Keypad
from interface import UI
from uv_meter import UVMeter
from beeper import Beeper

class Battery:
    def __init__(self):
        self.vbat = AnalogIn(board.VOLTAGE_MONITOR)
        self.rolling_vals = [4.2] * 10
        self.minv = 3.2
        self.maxv = 4.2
        
    def Update(self):
        voltage = (self.vbat.value * 3.3) / 65536 * 2.14
        voltage = round(voltage, 1)
        self.rolling_vals.pop(0)
        self.rolling_vals.append(voltage)
        
    def Percent(self):
        avg = sum(self.rolling_vals) / 10
        percent = int(((avg - self.minv) / (self.maxv - self.minv)) * 100.0)
        return min(100, percent)
        
# Release the existing display, if any
displayio.release_displays()

bus = board.SPI()
chip_select_pin = board.D4
# For the 144x168 display (can be operated at up to 8MHz)
framebuffer = sharpdisplay.SharpMemoryFramebuffer(bus, chip_select_pin, width=144, height=168, baudrate=2000000)
display = framebufferio.FramebufferDisplay(framebuffer)

keypad = Keypad()

beep = Beeper(board.D1)
alarm_pattern = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 1.0]
beep.SetPattern(alarm_pattern)

def short_beep():
    beep.Beep()
    time.sleep(0.2)
    beep.Stop()

batt = Battery()

uv = UVMeter()

ui = UI(display, uv, beep)

entry_mode = False
entry_vals = []
target_val = 25
running = False
total_time = 0.0
last_remaining_update = 0.0
complete = False

ui.target_val.text = str(target_val)

while True:
    batt.Update()
    beep.Update()
    uv.Update()
    complete = uv.Complete()
    
    if complete:
        ui.remaining_time.text = 'Done!'
        beep.Start()

    ui.UpdateBattery(batt.Percent())
    ui.uv_bar.value = uv.LastMapped()
    
    if entry_mode:
        hide_target_icon = ((time.monotonic() % 1) >= 0.5)
        ui.bmp_target.hidden = hide_target_icon
    elif running:
        if not complete and time.monotonic() - last_remaining_update > 2.0:
            ui.remaining_time.text = uv.TimeRemaining()
            last_remaining_update = time.monotonic()
        hide_rem_time_icon = ((time.monotonic() % 1) >= 0.5)
        ui.bmp_rem_time.hidden = hide_rem_time_icon
    else:
        ui.bmp_rem_time.hidden = False
    
    # always show this so we see the previous hit value
    ui.uv_val.text = str(uv.TotalExposure())
        
    keypad.Update()
    pressed, held = keypad.GetStates()
    if held and not running and '#' in held:
        if entry_mode:
            entry_mode = False
            ui.bmp_target.hidden = False
            if len(entry_vals) > 0:
                result = 0
                for v in entry_vals:
                    result *= 10
                    result += v
                    
                if result == 0:
                    result = target_val
                target_val = result
                ui.target_val.text = str(target_val)
            short_beep()
        else:
            entry_mode = True
            entry_vals = []
            short_beep()
    elif held and not entry_mode and '*' in held:
        if running:
            running = False
            ui.remaining_time.text = ui.rem_default
            beep.Stop()
            uv.Stop()
            short_beep()
        elif target_val > 0:
            running = True
            total_time = 0.0
            last_remaining_update = time.monotonic()
            ui.remaining_time.text = uv.TimeRemaining()
            uv.Start(target_val)
            short_beep()
        
    if pressed and entry_mode:
        # only take first, multi input not supported
        val = pressed[0] 
        if isinstance(val, int):
            if len(entry_vals) == 4: # no bigger than 9999
                entry_vals.pop(0)
            entry_vals.append(val)
            ui.target_val.text = ''.join([str(v) for v in entry_vals])
            short_beep()
            
    time.sleep(0.05)
