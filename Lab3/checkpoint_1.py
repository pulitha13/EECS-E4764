#from machine import Pin, PWM, ADC
from machine import PWM, Pin, RTC, I2C
import utime
import ssd1306
from debouncer import Debouncer
from clock_module import Clock

# Pin connections
SDA_PIN = 4
SCL_PIN = 5
PIEZZO_PIN = 2
BUTTON_PIN = 0
OLED_BUTTON_A = 15
OLED_BUTTON_B = 13
OLED_BUTTON_C = 14

debouncer = Debouncer()
clock = Clock()


def oled_a_handler(pin):
    global debouncer
    global clock

    # If button was pressed toggle change time mode
    if(debouncer.get_debounced(pin) > 0):
        clock.inc_clock_mode()


def oled_b_handler(pin):
    global debouncer
    global clock

    # If button was pressed increase time dep on mode
    if(debouncer.get_debounced(pin) > 0):
        match clock.edit_clock_mode:
            case 1:
                clock.inc_hours()
            case 2:
                clock.inc_min()
            case 3:
                clock.inc_sec()
            case _:
                return

def oled_c_handler(pin):
    global debouncer
    global clock

    # If button was pressed toggle change time mode
    if(debouncer.get_debounced(pin) > 0):
        match clock.edit_clock_mode:
            case 1:
                clock.dec_hours()
            case 2:
                clock.dec_min()
            case 3:
                clock.dec_sec()
            case _:
                return
    

def main():

    print("Initializing PWM")
    piezzo_pwm = PWM(Pin(PIEZZO_PIN), freq=500, duty=0)
    
    print("Initializing I2C and Display")
    i2c = I2C(sda=Pin(SDA_PIN), scl=Pin(SCL_PIN))
    display = ssd1306.SSD1306_I2C(128, 64, i2c)

    print("Initializing RTC")
    rtc = RTC(clock.get_clock())

    # Initialize pins
    print("Initializing Buttons")
    oled_a = Pin(OLED_BUTTON_A)
    oled_a.irq(handler=oled_a_handler, trigger=IRQ_FALLING)
    oled_b = Pin(OLED_BUTTON_B)
    oled_b.irq(handler=oled_b_handler, trigger=IRQ_FALLING)
    oled_c = Pin(OLED_BUTTON_C)
    oled_c.irq(handler=oled_c_handler, trigger=IRQ_FALLING)

    # Local variables to loop
    display_on = True

    while True:
        if clock.edit_clock_mode > 0:

            # Update the RTC based on the set time
            rtc.datetime(clock.get_clock())
            # If we are any of the editing modes flash the screen on and off and upate clock
            if display_on:
                display.poweroff()
            else:
                display.poweron()
            display_on = not display_on

        else:
            # If we are in normal display mode get RTC time and update clock module
            (year, week, day, weekday, hours, min, sec, subsec) = rtc.datetime()
            clock.set_clock(hours, min, sec)
            print(f"Got Time as {clock.hours}:{clock.min}:{clock.sec} ")
            display.text(f'{clock.hours}:{clock.min}:{clock.sec}')

        # Update clock every 1/4 sec
        display.show()
        utime.sleep(0.25)
        


        
if __name__ == '__main__':
    main()