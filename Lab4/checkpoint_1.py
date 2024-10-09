#from machine import Pin, PWM, ADC
from machine import PWM, Pin, RTC, I2C, ADC, SPI
import time
import utime
import ssd1306
from debouncer import Debouncer
from clock_module import ClockModule, EditMode
from adxl345_module import ADXL345

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

def display_text(display, text1, text2, start_x, start_y, z=1):
    # current_x = start_x
    # current_y = start_y
    display.fill(0)  # Clear the display before updating
    line_height = 15  # Adjust based on your font size

    max_width = 128  # OLED width
    max_height = 32   # OLED height
    display.text(text1, start_x % max_width, int(start_y/4) % max_height,1)
    display.text(text2, start_x % max_width,(int(start_y/4) + 15) % max_height,1)
    # display.scroll(120, 0)
    # # Split the text into words
    # words = text.split(' ')
    
    # for word in words:
    #     # Check if adding this word will exceed the width of the display
    #     if current_x + len(word) * 6 > max_width:  # Assuming each character is approximately 6 pixels wide
    #         # Move to the next line
    #         current_x = start_x  # Reset x position
    #         current_y += line_height  # Move down for the next line
            
    #         # Check if we need to wrap further
    #         if current_y + line_height > max_height:  # Assuming your display height is 32 pixels
    #             current_y = 0  # Reset y position to top if it exceeds the display height

    #     # Wrap around x position
    #     if current_x >= max_width:
    #         current_x = 0
    #     elif current_x < 0:
    #         current_x = max_width - len(word) * 6  # Move to the end of the line

    #     # Wrap around y position
    #     if current_y >= max_height:
    #         current_y = 0
    #     elif current_y < 0:
    #         current_y = max_height - line_height  # Move to the bottom of the display

    #     # Display the current word
        # display.text(word, current_x, current_y, z)
    #     current_x += len(word) * 6 + 2  # Move x position to the right (2 for a space)

    #     # After displaying the word, check if current_x is now beyond the max width
    #     if current_x >= max_width:
    #         current_x = 0  # Reset x position for the next word on the next line
    #         current_y += line_height  # Move down for the next line

    #         # Wrap the y position if it exceeds the max height
    #         if current_y >= max_height:
    #             current_y = 0  # Reset y position to top if it exceeds the display height


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

    #Initializing pins
    print("Initializing Buttons")
    oled_a = Pin(OLED_BUTTON_A, Pin.IN, Pin.PULL_UP)
    oled_a.irq(handler=None)
    oled_b = Pin(OLED_BUTTON_B, Pin.IN, Pin.PULL_UP)
    oled_b.irq(handler=None)
    oled_c = Pin(OLED_BUTTON_C, Pin.IN, Pin.PULL_UP)
    oled_c.irq(handler=None)
    alarm = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
    alarm.irq(handler=None)
    print("Done initializing pins")

    # Initializing registers
    adxl345 = ADXL345(spi_bus=1, cs_pin=15)  # Initialize your ADXL345 instance
    adxl345.initialize_device()
    time.sleep(0.1)

    #Ensuring ADXL345 Connection
    print("attempting ADXL345 connection")
    device_id = adxl345.read_device_id()  # Read the device ID # Print the device ID to confirm
    if device_id in ["00e5", "e5e5"]:
        print("Successfully connected to ADXL345")
    else:
        print("Failed to connect to ADXL345. Check the connections or device ID.")
   
    # Initialize Irqs
    print("Initializing IRQs for Buttons")
    oled_a.irq(handler=oled_a_handler, trigger=Pin.IRQ_FALLING)
    oled_b.irq(handler=oled_b_handler, trigger=Pin.IRQ_FALLING)
    oled_c.irq(handler=oled_c_handler, trigger=Pin.IRQ_FALLING)
    alarm.irq(handler=alarm_handler, trigger=Pin.IRQ_FALLING)
    print("Alarm loaded loaded")

    # # Initialize ADC
    # adc = ADC(0)

    # Local variables to loop
    display_on = True

    while True:
        brightness = 255

        #Contious xyz readings:
        ############################3
        x, y, z = adxl345.adxl345_read_xyz()
        print(f'Raw coordinates: X: {x}, Y: {y}, Z: {z}')

        # #Keeping the collected data within the display constarints
        # if (x >= 128):
        #     x = 0
        # elif (x < 0):
        #     x = 128

        # if (y > 32):
        #     y = 0
        # elif (y < 0):
        #     y = 32

        # print(f'Display coordinates: X: {x}, Y: {y}, Z: {z}')
        
        #####################3
        ########
        
        if(clock.check_alarm_blaring() and clock.edit_mode == EditMode.NORMAL):
            clock.edit_mode = EditMode.ALARM_BLARING

        if clock.edit_mode == EditMode.TIME_EDIT:
            piezzo_pwm.duty(0)

            # Update the RTC based on the set time
            rtc.datetime((year, month, day, weekday, clock.curr_time.hour, clock.curr_time.min, clock.curr_time.sec, subsec))
            # If we are any of the editing modes flash the screen on and off and upate clock
            display_on = not display_on

            # print(f"Setting Clock Time as {clock.curr_time.hour:02}:{clock.curr_time.min:02}:{clock.curr_time.sec:02} ")
            mode_string = 'EDITING TIME'
            time_string = f'{clock.curr_time.hour:02}:{clock.curr_time.min:02}:{clock.curr_time.sec:02}'

        elif clock.edit_mode == EditMode.ALARM_EDIT:
            piezzo_pwm.duty(0)

            # If we are any of the editing modes flash the screen on and off and upate clock
            display_on = not display_on
            # print(f"Setting Alarm Time as {clock.alarm.hour:02}:{clock.alarm.min:02}:{clock.alarm.sec:02} ")
            mode_string = 'EDITING ALARM'
            time_string = f'{clock.alarm.hour:02}:{clock.alarm.min:02}:{clock.alarm.sec:02}'
       
        elif clock.edit_mode == EditMode.ALARM_BLARING:
            display_on = True
            piezzo_pwm.duty(512)
            # print(f"ALARM BLARING")
            mode_string = 'ALARM BLARING'
            time_string = f''            

        else:
            piezzo_pwm.duty(0)
            display_on = True
            # If we are in normal display mode get RTC time and update clock module
            year, month, day, weekday, hour, min, sec, subsec = rtc.datetime()
            clock.curr_time.set_time(hour, min, sec)
            # print(f"Displaying {clock.curr_time.hour:02}:{clock.curr_time.min:02}:{clock.curr_time.sec:02} ")
            mode_string = 'DISPLAYING TIME'
            time_string = f'{clock.curr_time.hour:02}:{clock.curr_time.min:02}:{clock.curr_time.sec:02}'
        
        if display_on:
            display.poweron()
        else:
            display.poweroff()

        # Display text with updated x and y values
        display_text(display, mode_string, time_string, x, y, z=0)
        # display_text(display, time_string, x, y + line_height, line_height, z=0)

        display.contrast(brightness)
        display.show()
        utime.sleep(0.125)


        
if __name__ == '__main__':
    main()

# display.fill(0)
# display.text(mode_string,x,y,1)
# display.text(time_string,x,(y+15),1)
# display.text(mode_string,0,0,1)
# display.text(time_string,0,15,1)