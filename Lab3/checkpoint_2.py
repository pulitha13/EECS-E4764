#from machine import Pin, PWM, ADC
from machine import PWM, Pin, RTC, I2C, ADC
import utime
import ssd1306
from debouncer import Debouncer
from clock_module import ClockModule, EditMode

# Pin connections
SDA_PIN = 4
SCL_PIN = 5
PIEZZO_PIN = 2
BUTTON_PIN = 0
OLED_BUTTON_A = 14
OLED_BUTTON_B = 13
OLED_BUTTON_C = 12

debouncer = Debouncer()
clock = ClockModule()


def oled_a_handler(pin):
    global debouncer
    global clock
    # If button was pressed toggle change time mode
    if(debouncer.get_debounced(pin) == 0):
        print("We in the oled_A_handler")
        clock.change_edit_mode(EditMode.TIME_EDIT)

def alarm_handler(pin):
    global debouncer
    global clock
    # If button was pressed toggle change time mode
    if(debouncer.get_debounced(pin) == 0):
        print("We in the alarm handler")
        clock.change_edit_mode(EditMode.ALARM_EDIT)

def oled_b_handler(pin):
    global debouncer
    global clock
    print("We in the oled_B_handler")

    # If button was pressed increase time dep on mode
    if(debouncer.get_debounced(pin) == 0):
        if (clock.get_edit_mode() == EditMode.TIME_EDIT):
            if(clock.curr_time.edit_time_mode == 1):
                clock.curr_time.inc_hour()
            elif(clock.curr_time.edit_time_mode == 2):
                clock.curr_time.inc_min()
            elif(clock.curr_time.edit_time_mode == 3):
                clock.curr_time.inc_sec()
            else:
                return
        if (clock.get_edit_mode() == EditMode.ALARM_EDIT):
            if(clock.alarm.edit_time_mode == 1):
                clock.alarm.inc_hour()
            elif(clock.alarm.edit_time_mode == 2):
                clock.alarm.inc_min()
            elif(clock.alarm.edit_time_mode == 3):
                clock.alarm.inc_sec()
            else:
                return
    


def oled_c_handler(pin):
    global debouncer
    global clock
    print("We in the oled_C_handler")

    if(debouncer.get_debounced(pin) == 0):
        if (clock.get_edit_mode() == EditMode.TIME_EDIT):
            if(clock.curr_time.edit_time_mode == 1):
                clock.curr_time.dec_hour()
            elif(clock.curr_time.edit_time_mode == 2):
                clock.curr_time.dec_min()
            elif(clock.curr_time.edit_time_mode == 3):
                clock.curr_time.dec_sec()
            else:
                return
        if (clock.get_edit_mode() == EditMode.ALARM_EDIT):
            if(clock.alarm.edit_time_mode == 1):
                clock.alarm.dec_hour()
            elif(clock.alarm.edit_time_mode == 2):
                clock.alarm.dec_min()
            elif(clock.alarm.edit_time_mode == 3):
                clock.alarm.dec_sec()
            else:
                return
    

def main():

    print("Initializing PWM")
    piezzo_pwm = PWM(Pin(PIEZZO_PIN), freq=500, duty=0)
    
    print("Initializing I2C and Display")
    i2c = I2C(sda=Pin(SDA_PIN), scl=Pin(SCL_PIN))
    display = ssd1306.SSD1306_I2C(128, 32, i2c)

    print("Initializing RTC")
    rtc = RTC()
    year, month, day, weekday, hour, min, sec, subsec = (2024,9,27,5,12,12,12,0)
    rtc.datetime()

    # Initialize pins
    print("Initializing Buttons")
    oled_a = Pin(OLED_BUTTON_A, Pin.IN, Pin.PULL_UP)
    oled_a.irq(handler=oled_a_handler, trigger=Pin.IRQ_FALLING)
    oled_b = Pin(OLED_BUTTON_B, Pin.IN, Pin.PULL_UP)
    oled_b.irq(handler=oled_b_handler, trigger=Pin.IRQ_FALLING)
    oled_c = Pin(OLED_BUTTON_C, Pin.IN, Pin.PULL_UP)
    oled_c.irq(handler=oled_c_handler, trigger=Pin.IRQ_FALLING)
    alarm = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
    alarm.irq(handler=alarm_handler, trigger=Pin.IRQ_FALLING)

    # Initialize ADC
    adc = ADC(0)

    # Local variables to loop
    display_on = True

    while True:
        brightness = adc.read_u16() >> 8
        if clock.edit_mode > 0:

            # Update the RTC based on the set time
            rtc.datetime((year, month, day, weekday, clock.curr_time.hour, clock.curr_time.min, clock.curr_time.sec, subsec))
            # If we are any of the editing modes flash the screen on and off and upate clock
            display_on = not display_on

            print(f"Setting Time as {clock.curr_time.hour:02}:{clock.curr_time.min:02}:{clock.curr_time.sec:02} ")

        else:
            display_on = True
            # If we are in normal display mode get RTC time and update clock module
            year, month, day, weekday, hour, min, sec, subsec = rtc.datetime()
            clock.curr_time.set_time(hour, min, sec)
            print(f"Displaying {clock.curr_time.hour:02}:{clock.curr_time.min:02}:{clock.curr_time.sec:02} ")
        
        if display_on:
            display.poweron()
        else:
            display.poweroff()

        # Update clock every 1/4 sec
        display_string = f'{clock.curr_time.hour:02}:{clock.curr_time.min:02}:{clock.curr_time.sec:02}'
        display.fill(0)
        display.text(display_string,0,15,1)

        if(clock.edit_mode == EditMode.ALARM_EDIT):
            display.text("ALARM", 0, 0, 1)

        display.contrast(brightness)
        display.show()
        utime.sleep(0.25)
        


        
if __name__ == '__main__':
    main()