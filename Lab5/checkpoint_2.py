from machine import PWM, Pin, RTC, I2C, ADC, SPI
import time
import utime
import ssd1306
from clock_module import ClockModule
import network
import socket
import errno
import ujson


# Pin connections
SDA_PIN = 4
SCL_PIN = 5
PIEZZO_PIN = 2
BUTTON_PIN = 0
OLED_BUTTON_A = 14
OLED_BUTTON_B = 13
OLED_BUTTON_C = 12

# Wifi credentials
SSID = "SpectrumSetup-57F5"
Password = "silvertune468"

# Socket
CMD_PORT = 7000

clock = ClockModule()
station = network.WLAN(network.STA_IF)

def edit_clock(hour, min, sec):
    global clock
    # If button was pressed toggle change time mode
    print("Editing watch time")
    clock.curr_time.set_time(hour, min, sec)

def edit_alarm(hour, min, sec):
    global debouncer
    global clock
    # If button was pressed toggle change time mode
    print("Cycling ALARM EDIT mode")
    clock.alarm.set_time(hour, min, sec)
            
def connect_to_wifi(ssid, password):
    station.active(True)
    print('Connecting to Wi-Fi...')
    station.connect(ssid, password)

    attempts = 0
    while not station.isconnected() and attempts < 10:  # 10 attempts
        attempts += 1
        print(f'Attempt {attempts}...')
        time.sleep(1)

    if station.isconnected():
        print('Connected to Wi-Fi!')
        print('Network config:', station.ifconfig())
    else:
        # print('Failed to connect to Wi-Fi')
        raise Exception('Failed to connect to Wi-Fi.')  # Generic exception
    
    return station.ifconfig()[0]

def open_command_socket(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, port))
    s.listen(1)
    s.settimeout(.1)
    return s

def check_for_commands(s):
    try:
        client_sock, client_addr = s.accept()
        print(f"Connected to client socket: {client_addr}")

        data = client_sock.recv(1024).decode('utf-8')
        data = ujson.loads(data)
        print(f"Recieved command: {data['cmd']}")
        print(f"Recieved args: {data['args']}")
        return data

    except Exception as e:
        if isinstance(e, OSError) and (e.errno == errno.EAGAIN or e.errno == errno.ETIMEDOUT):
            pass 
        else:
            print(f"An error occurred: {e}")
    
    return None




def service_display(display, text, display_on, start_x = 0, start_y= 0, z = 1):

    display.fill(0)  # Clear the display before updating

    max_width = 128  # OLED width
    max_height = 32   # OLED height

    for i, string in enumerate(text):
        display.text(string, start_x % max_width, (int(start_y/4) + i * 15) % max_height,1)

    if display_on == True:
        display.poweron()
    else:
        display.poweroff()

    display.show()

'''
Depending on the current state of the clock module, updates the clock module based
on the on chip RTC, updates the RTC based on user edits, updates the alarm based on
user edits, or "blares" the alarm. The state of what should be displayed on the OLED
device is returned, along with any variables that were updated during servicing the clock
'''
def service_clock(rtc, display_on, piezzo_pwm):

    clock.check_alarm_blaring()
    
    if clock.alarm_blaring:
        display_on = True
        piezzo_pwm.duty(512)
        # print(f"ALARM BLARING")
        display_string = 'ALARM BLARING'     
    else:
        piezzo_pwm.duty(0)
        display_on = True
        # If we are in normal display mode get RTC time and update clock module
        year, month, day, weekday, hour, min, sec, subsec = rtc.datetime()
        clock.curr_time.set_time(hour, min, sec)
        # print(f"Displaying {clock.curr_time.hour:02}:{clock.curr_time.min:02}:{clock.curr_time.sec:02} ")
        display_string = ['DISPLAYING TIME', f'{clock.curr_time.hour:02}:{clock.curr_time.min:02}:{clock.curr_time.sec:02}']

    return display_on, display_string
    
def parse_json_cmd(json_cmd, display_on, ):
    
    cmd = ujson.loads(json_cmd)

    # return cmd_dict[cmd]

def main():
    print("Initializing PWM")
    piezzo_pwm = PWM(Pin(PIEZZO_PIN), freq=500, duty=0)
    
    print("Initializing I2C and Display")
    i2c = I2C(sda=Pin(SDA_PIN), scl=Pin(SCL_PIN))
    display = ssd1306.SSD1306_I2C(128, 32, i2c)

    print("Initializing RTC")
    rtc = RTC()
    time = (2024,9,27,5,12,12,12,0)
    rtc.datetime()

    # Local variables to loop
    display_on = True

    ip = connect_to_wifi(SSID, Password)

    s = open_command_socket(ip, CMD_PORT)

    while True:

        json_cmd = check_for_commands(s)

        display_on, display_string = service_clock(rtc, display_on, piezzo_pwm)

        service_display(display, display_string, display_on)

        utime.sleep(0.125)


if __name__ == '__main__':
    main()