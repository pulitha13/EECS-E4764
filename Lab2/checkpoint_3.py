from machine import Pin, PWM, ADC
import machine
import utime

# Global variables
sampling_active = False  # Flag to track if sampling is active
debounce_time = 50       # Debounce delay in milliseconds
interrupt_time = 0       # Tracks the last interrupt time

# Debouncing function
def debouncer():
    global interrupt_time
    current_time = utime.ticks_ms()

    # Check if enough time has passed for debounce
    if utime.ticks_diff(current_time, interrupt_time) > debounce_time:
        interrupt_time = current_time
        return True
    return False

# Interrupt handler for the button
def button_interrupt_handler(pin):
    # state = machine.disable_irq()
    global sampling_active
    if debouncer():
        sampling_active = False
        if pin.value() == 0:
            print("Button pressed - Starting system")
            sampling_active = True  # Activate sampling when button is pressed
        else:
            print("Button released - Stopping system")
            sampling_active = False  # Deactivate sampling when button is released
    # machine.enable_irq(state)

def main():
    # PWM setup for LED and piezo
    led_pwm = PWM(Pin(4), freq=500, duty=512)     # LED on pin 4
    piezo_pwm = PWM(Pin(5), freq=500, duty=512)   # Piezo buzzer on pin 5

    # ADC setup for light sensor
    adc = ADC(0)  # Assuming light sensor is connected to ADC channel 0

    # Button setup with interrupt
    button = Pin(13, Pin.IN, Pin.PULL_UP)
    button.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=button_interrupt_handler)

    while True:
        if sampling_active:
            # Sample the light sensor when system is active
            light_value = adc.read()  # Read ADC value (0-1023)
            print(f"Light sensor value: {light_value}")

            # Adjust LED brightness based on light sensor value
            led_pwm.duty(light_value)

            # Adjust piezo pitch based on light sensor value
            piezo_pwm.duty(512)
            piezo_pwm.freq(light_value * 4)

            utime.sleep(0.1)  # Sampling rate of 100ms
        else:
            # If system is deactivated, turn off the LED and piezo
            led_pwm.duty(0)  # Turn off LED
            piezo_pwm.duty(0)
              # Stop piezo by setting duty cycle to 0
            utime.sleep(0.1)  # Delay to avoid busy-waiting loop

if __name__ == '__main__':
    main()
