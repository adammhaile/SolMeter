import board
import digitalio
import time
import adafruit_matrixkeypad

class Keypad:
    C2 = board.D12
    R1 = board.D11
    C1 = board.D10
    R4 = board.D9
    C3 = board.D6
    R3 = board.D5
    R2 = board.D0
    
    Cols = [digitalio.DigitalInOut(x) for x in (C1, C2, C3)]
    Rows = [digitalio.DigitalInOut(x) for x in (R1, R2, R3, R4)]
    
    Keys = ((1, 2, 3),(4, 5, 6),(7, 8, 9),('*', 0, '#'))
    
    def __init__(self, bounce_time = 0.1, hold_time = 1.0):
        self.bounce_time = bounce_time
        self.hold_time = hold_time
        self.k = adafruit_matrixkeypad.Matrix_Keypad(self.Rows, self.Cols, self.Keys)
        self.key_map = {}
        for row in self.Keys:
            for key in row:
                self.key_map[key] = 0
        self.keys = self.key_map.keys()
        self.states = {}
        for key in self.keys:
            # 0=nothing, 1=pressed, 2=held
            self.states[key] = 0
                
    def Update(self):
        state = self.k.pressed_keys
        now = time.monotonic()
        for key in self.keys:
            t = self.key_map[key]
            diff = (now - t)
            if key in state:
                if t > 0:
                    if diff >= self.hold_time and self.states[key] == 0:
                        self.states[key] = 2 # held
                else:
                    self.key_map[key] = now # start the "timer"
            else:
                self.key_map[key] = 0 # reset timer
                if self.states[key] == 0: 
                    if t > 0 and diff >= self.bounce_time:
                        self.states[key] = 1 # pressed
                elif self.states[key] >= 2: # finally released after hold
                    self.states[key] = 0 # set back to null state
                    
    def GetStates(self):
        pressed = []
        held = []
        for key, state in self.states.items():
            if state == 1: # pressed and released
                pressed.append(key)
                self.states[key] = 0
            elif state == 2: # held
                self.states[key] = 3 # held, waiting for released
                held.append(key)
                
        return (pressed, held)
        