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

    def __init__(self):
        self.edit_time_mode = 0
        self.hour = 0
        self.min = 0
        self.sec = 0
        return
    
    def inc_mode(self):
        self.edit_time_mode += 1
        self.edit_time_mode = self.edit_time_mode % 4
        return self.edit_time_mode

    
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

    def get_time(self):
        return ((0,0,0,0,self.hour,self.min,self.sec,0))

    def set_time(self, hour, min, sec):
        self.sec = sec
        self.min = min
        self.hour = hour

class EditMode():
    NORMAL = 0
    ALARM_EDIT = 1
    TIME_EDIT = 2


class ClockModule:
        def __init__(self):
            self.edit_mode = EditMode.NORMAL
            self.curr_time = TimeEntity()
            self.alarm = TimeEntity()
            return
        
        def get_edit_mode(self):
            return self.edit_mode
        
        def change_edit_mode(self, edit_mode):

            if(self.edit_mode > 0 and edit_mode != self.edit_mode):
                return
            
            ret = 0
            if(self.edit_mode == EditMode.ALARM_EDIT):
                ret = self.alarm.inc_mode()
            elif(self.edit_mode == EditMode.TIME_EDIT):
                ret = self.curr_time.inc_mode()

            if ret == 0:
                self.edit_mode = EditMode.NORMAL

            return
        
