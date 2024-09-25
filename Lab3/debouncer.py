import utime


class Debouncer:

    def __init__(self):
        self.last_interrupt_time = 0
        self.debounce_period = 50


    # Debouncing function
    def debounce(self):
        current_time = utime.ticks_ms()

        # ensures that the amount of time since the interrupt is greater than the debounce delay
        if utime.ticks_diff(current_time, self.last_interrupt_time) > self.debounce_period:
            self.interrupt_time = current_time
            return True
        
        return False

    def get_debounced(self, pin):

        if self.debounce():
            return pin.value()
        else:
            return -1