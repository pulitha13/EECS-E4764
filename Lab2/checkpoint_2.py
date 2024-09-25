from machine import Pin
import utime

def main():
    debounce_time = 20  # Time the pushbutton output must be steady 
    interrupt_time = 0 # Tracks the last interrupt

    button = Pin(13, Pin.IN, Pin.PULL_UP)

    # Debouncing function
    def debouncer():
        nonlocal interrupt_time
        current_time = utime.ticks_ms()

        # ensures that the amount of time since the interrupt is greater than the debounce delay
        if utime.ticks_diff(current_time, interrupt_time) > debounce_time:
            interrupt_time = current_time
            return True
        return False

    # Interrupt handler
    def interrupt_handler(pin):
        # prints whether the button is pressed or released based on debounced pushbutton signal
        if debouncer():
            if pin.value() == 0:
                print("Button pressed")
            else:
                print("Button released")

    button.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=interrupt_handler)

    while True:
        utime.sleep(1)

if __name__ == '__main__':
    main()
