class TimeEntity:

    """
    TimeEntity class defines a current time set by the variables

    self.hour, self.min, self.sec


    and a self.TimeEntity mode with the following for modes

    0 - regular display time w/ no edit
    1 - edit hour hand
    2 - edit minutes hand
    3 - edit seconds hand

    each call to inc_** will increase the ** value with a overflow to 0 depending 
    on the value maximum
    """

    def __init__(self, hour=0, min=0, sec=0):
        self.hour = hour
        self.min = min
        self.sec = sec
        return

    def get_time(self):
        return ((0,0,0,0,self.hour,self.min,self.sec,0))

    def set_time(self, hour, min, sec):
        self.sec = sec
        self.min = min
        self.hour = hour

class ClockModule:
    def __init__(self):
        self.curr_time = TimeEntity()
        self.alarm = TimeEntity(23, 59, 59)
        self.alarm_blaring = False
        return

    def check_alarm_blaring(self):
        if self.curr_time.hour > self.alarm.hour:
            self.alarm_blaring = True
            return True
        elif self.curr_time.hour < self.alarm.hour:
            self.alarm_blaring = False
            return False
        else:
            if self.curr_time.min > self.alarm.min:
                self.alarm_blaring = True
                return True
            elif self.curr_time.min < self.alarm.min:
                self.alarm_blaring = False
                return False
            else:
                if self.curr_time.sec >= self.alarm.sec:
                    self.alarm_blaring = True
                    return True
                elif self.curr_time.sec < self.alarm.sec:
                    self.alarm_blaring = False
                    return False
        
