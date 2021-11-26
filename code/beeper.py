import pwmio
import time

DEFAULT_FREQ = 1568

NOTES = { 
    'f': 1397, 
    'g': 1568, 
    'a': 1760, 
    'b': 1976, 
    'c': 2093, 
    'd': 2349,
    'd#': 2489,
    'e': 2637,
    'R': 0
}

BASE_TIME = 0.5

TUNE = ('g', 'c', 'd', 'e', 'e', 'R',
        'e', 'd#', 'e', 'c', 'c', 'R')

DURATIONS = (4, 4, 4, 2, 2, 8,
             4, 4, 4, 2, 2, 8)

class Beeper:
    def __init__(self, pin, freq=DEFAULT_FREQ):
        self.buzz = pwmio.PWMOut(pin, variable_frequency=True)
        self.buzz.frequency = freq
        self.pattern = []
        self.state = False
        self.last_change = time.monotonic()
        self.running_pattern = False
        self.pattern_index = 0
        
    def __on(self):
        self.buzz.duty_cycle = 2**15
        
    def __off(self):
        self.buzz.duty_cycle = 0
        
    def RunningPattern(self):
        return self.running_pattern
        
    def Beep(self, freq=DEFAULT_FREQ):
        self.buzz.frequency = freq
        self.__on()

    def PlaySong(self):
        for i in range(len(TUNE)):
            note = NOTES[TUNE[i]]
            dur = DURATIONS[i]
            if note:
                self.Beep(note)
            time.sleep(1.0 / dur)
            self.__off()
            time.sleep(1.0 / (dur * 3))
        
    def Stop(self):
        self.__off()
        self.running_pattern = False
        
    def Start(self):
        if not self.running_pattern:
            self.state = True
            self.last_change = time.monotonic()
            self.__on()
            self.pattern_index = 0
            self.running_pattern = True
        
    def Update(self):
        if self.running_pattern:
            now = time.monotonic()
            diff = now - self.last_change
            target = self.pattern[self.pattern_index]
            if diff >= target:
                self.last_change = now
                self.state = not self.state
                if self.state:
                    self.__on()
                else:
                    self.__off()
                    
                self.pattern_index += 1
                
                if self.pattern_index > (len(self.pattern) - 1):
                    self.pattern_index = 0 # loop back around
        
    def SetPattern(self, pattern, freq=DEFAULT_FREQ):
        self.pattern = pattern
        self.buzz.frequency = freq
        self.running_pattern = False