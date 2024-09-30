
class Clock:

    """
    Clock class defines a current time set by the variables

    self.hour, self.min, self.sec


    and a self.clock mode with the following for modes

    0 - regular display time w/ no edit
    1 - edit hour hand
    2 - edit minutes hand
    3 - edit seconds hand

    each call to inc_** will increase the ** value with a overflow to 0 depending 
    on the value maximum
    """

    def __init__(self):
        self.hour = 0
        self.min = 0
        self.sec = 0

        self.edit_clock_mode = 0

        return

    def inc_clock_mode(self):
        self.edit_clock_mode += 1
        self.edit_clock_mode = self.edit_clock_mode % 4
        return
    
    def inc_hour(self):
        self.hour += 1
        self.hour = self.hour % 24

    def inc_min(self):
        self.min += 1
        self.min = self.min % 60

    def inc_sec(self):
        self.sec += 1
        self.sec = self.sec % 60

    def dec_hour(self):
        self.hour -= 1
        self.hour = 23 if self.hour < 0 else self.hour

    def dec_min(self):
        self.min -= 1
        self.min = 59 if self.min < 0 else self.min

    def dec_sec(self):
        self.sec -= 1
        self.sec = 59 if self.sec < 0 else self.sec

    def get_clock(self):
        return ((0,0,0,0,self.hour,self.min,self.sec,0))

    def set_clock(self, hour, min, sec):
        self.sec = sec
        self.min = min
        self.hour = hour