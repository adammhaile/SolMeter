import board
import time
import adafruit_veml6070

class UVMeter:
    def __init__(self, avg_time=1.0, unit_time=60.0):
        self.uv = adafruit_veml6070.VEML6070(board.I2C())
        self.raw_max = 6000
        self.mapped_max = 100
        self.last_avg_time = 1000000
        self.total_exposure = 0.0 
        self.samples = []
        
        self.last_mapped = 0
        self.last_unit_avg = 0
        
        self.avg_time = avg_time
        self.unit_time = unit_time
        
        self.start_time = 0.0
        self.target = 0
        self.running = False
        
    def Start(self, target):
        self.target = target
        self.last_avg_time = self.start_time = time.monotonic()
        self.total_exposure = 0.0
        self.samples = []
        self.running = True
        self.Update()
        
    def Stop(self):
        self.running = False

    def Complete(self):
        if not self.running:
            return False
            
        return self.total_exposure > self.target
        
    def TotalExposure(self):
        return round(self.total_exposure, 1)
        
    def TimeRemaining(self):
        if self.total_exposure == 0.0:
            return '--h--m'
            
        diff = time.monotonic() - self.start_time
        ratio = self.total_exposure / self.target
        sec = int(diff / ratio)
        
        if self.last_unit_avg > 0:
            remaining = self.target - self.total_exposure
            rem_time = (remaining / self.last_unit_avg) * self.avg_time

            sec = (sec + int(rem_time)) // 2
            
        h = sec // 3600
        
        if h > 99:
            return '??h??m'
        m = (sec % 3600) // 60
        s = sec % 3600 % 60
        if s > 30:
            m += 1
        return f'{h:0>2}h{m:0>2}m'
        
        
    def get_mapped(self):
        raw = self.uv.uv_raw
        mapped = int((raw / self.raw_max) * self.mapped_max)
            
        return mapped
        
    def LastMapped(self, clamp=True):
        val = int(self.last_mapped)
        if clamp:
            val = min(self.mapped_max, val)
        return val
        
    def Update(self):
        self.last_mapped = self.get_mapped()
        if self.running:
            now = time.monotonic()
            diff = now - self.last_avg_time
            if diff > self.avg_time:
                avg = sum(self.samples) / len(self.samples)
                avg = (avg / diff) # normalize to being exactly over avg_time span
                self.last_unit_avg = avg / self.unit_time # convert to being over unit_time span
                self.total_exposure = self.total_exposure + self.last_unit_avg # add it to the tally
                self.samples = []
                self.last_avg_time = now
            else: 
                print(self.last_mapped)
                self.samples.append(self.last_mapped)