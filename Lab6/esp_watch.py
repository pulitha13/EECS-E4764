from machine import PWM, Pin, RTC, I2C, ADC, SPI
import time
import utime
import ssd1306
from clock_module import ClockModule
from debouncer import Debouncer
from adxl345_module import ADXL345
import network
import socket
import errno
import ujson
import urequests
import ntptime

CLOUD_URL = "http://127.0.0.1:5000"
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
WEATHER_API_KEY = '058ef319596c10d77118e888070ca3da'

# Pin connections
SDA_PIN = 4
SCL_PIN = 5
PIEZZO_PIN = 2
BUTTON_PIN = 14
# OLED_BUTTON_A = 14
OLED_BUTTON_B = 13
OLED_BUTTON_C = 12

# Wifi credentials
SSID = "Columbia University"
Password = ""

# Socket
CMD_PORT = 7000

station = network.WLAN(network.STA_IF)

debouncer = Debouncer()
letter_update = {
    'letter': 'c',
    'new_request': 0
}

def write_button_handler(pin):
    global debouncer
    global letter_update
    # If button was pressed toggle change time mode
    # print("Alarm Handler Button Pressed outside debounce")
    if(debouncer.get_debounced(pin) == 0):
        print("Write Handler Button Pressed")
        # clock.change_edit_mode(EditMode.ALARM_EDIT)
        letter_update['new_request'] = 1


class SmartWatch():
    def __init__(self):
        self.watch_mode = 'clock'
        self.display_on = True
        self.display_string = [""]

        ntptime.settime()
        (year, month, mday, hour, min, sec, weekday, yearday) = time.localtime()
        hour = (hour - 4) % 24
        print(f"Setting time to ({hour}, {min}, {sec})")

        print("Initializing PWM")
        self.piezzo_pwm = PWM(Pin(PIEZZO_PIN), freq=500, duty=0)
        
        print("Initializing I2C and Display")
        i2c = I2C(sda=Pin(SDA_PIN), scl=Pin(SCL_PIN))
        self.display = ssd1306.SSD1306_I2C(128, 32, i2c)

        print("Initializing RTC")
        self.rtc = RTC()
        self.time = (2024,9,27,5,hour,min,sec,0)
        self.rtc.datetime((year, month, mday, weekday, hour, min, sec, 0))
        self.clock = ClockModule(hour, min, sec)

        print("Initializing the write button")
        alarm = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
        alarm.irq(handler=write_button_handler, trigger=Pin.IRQ_FALLING)

        # Initialize the ADXL345 accelerometer
        self.adxl345 = ADXL345(spi_bus=1, cs_pin=15)
        self.adxl345.initialize_device()

        return

    def record_gesture_data(self):

        start_time = utime.ticks_ms()
        readings = []
        # sampling_frequency = 10  # e.g., 50 Hz
        record_duration = 2      # e.g., 3 seconds
        
        # Collect CSV header
        # readings.append("time_ms,x,y,z,letter")
        
        # while elapsed_time < (record_duration * 1000):  # Convert to milliseconds
        while utime.ticks_ms() < record_duration*1000 + start_time:  # Convert to milliseconds
            # Read accelerometer values
            x, y, z = self.adxl345.adxl345_read_xyz()
            
            # Append data in CSV format
            readings.append(f"{utime.ticks_ms() - start_time},{x},{y},{z},{letter}")
            
            # Wait for the next sample based on sampling frequency
            utime.sleep_ms(20)
        
        # Export the collected readings to a JSON file
        # json_data = {json.dumps(readings)
        json_data = {
            'readings': readings
        }
        print(ujson.dumps(json_data))
        return ujson.dumps(json_data)


    def edit_alarm(self, hour, min, sec):
        # If button was pressed toggle change time mode
        print("Cycling ALARM EDIT mode")
        self.clock.alarm.set_time(hour, min, sec)

    def service_display(self, start_x = 0, start_y= 0, z = 1):

        self.display.fill(0)  # Clear the display before updating

        max_width = 128  # OLED width
        max_height = 32   # OLED height

        for i, string in enumerate(self.display_string):
            self.display.text(string, start_x % max_width, (int(start_y/4) + i * 15) % max_height,1)

        if self.display_on == True:
            self.display.poweron()
        else:
            self.display.poweroff()

        self.display.show()

    def service_clock(self):

        self.clock.check_alarm_blaring()
        
        if self.clock.alarm_blaring:
            self.piezzo_pwm.duty(512)
            # print(f"ALARM BLARING")
            self.watch_mode = 'alarm_blaring'
            self.display_string = ['ALARM BLARING']   
        else:
            self.piezzo_pwm.duty(0)
            # If we are in normal display mode get RTC time and update clock module
            year, month, day, weekday, hour, min, sec, subsec = self.rtc.datetime()
            self.clock.curr_time.set_time(hour, min, sec)
            # print(f"Displaying {clock.curr_time.hour:02}:{clock.curr_time.min:02}:{clock.curr_time.sec:02} ")
    
    def get_clock_string(self):
        return ['DISPLAYING TIME', f'{self.clock.curr_time.hour:02}:{self.clock.curr_time.min:02}:{self.clock.curr_time.sec:02}']
    
    def process_data_on_cloud(self, data):
        # Send data to cloud
        try:
            # Send data to the Flask server
            response = urequests.post(CLOUD_URL + '/data', json=data)
            if response.status_code == 200:
                print(f"Data sent successfully")
            else:
                print("Failed to send data, status code:", response.status_code)
            response.close()
        
        except Exception as e:
            print("An error occurred:", e)

        # Get letter from cloud
        try:
            # Send data to the Flask server
            response = urequests.get(CLOUD_URL + '/get_data')
            if response.status_code == 200:
                print(f"Got letter successfully")
            else:
                print("Failed to send data, status code:", response.status_code)
            response.close()

        except Exception as e:
            print("An error occurred:", e) 

        return response['letter'] 
        

    def update_write_string(self, string):
        update = ""
        if (letter_update['new_request'] == 1):
            # Record data from accel
            data = self.record_gesture_data()
            letter_update['letter']  = self.process_data_on_cloud(data)
            update = letter_update['letter']
        
        letter_update['new_request'] = 0
        return string + update

            
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
    s.settimeout(.25)
    return s

def get_lat_long():
    url = "http://ip-api.com/json"
    
    try:
        response = urequests.get(url)
        
        # Check if the response was successful (status code 200)
        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: Unable to retrieve location data.")
        
        data = ujson.loads(response.text)

        latitude = data.get('lat')
        longitude = data.get('lon')

        # print('Latitude:', latitude, 'Longitude:', longitude)
        
        return latitude, longitude
    except Exception as e:
        print('Error retrieving location:', e)
        return 0, 0
    
def get_weather(latitude, longitude):
    url = f"{WEATHER_URL}?lat={latitude}&lon={longitude}&appid={WEATHER_API_KEY}&units=metric"  # Metric for Celsius

    try:
        response = urequests.get(url)
        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: Unable to retrieve weather data.")
        
        data = ujson.loads(response.text)

        temperature = data['main']['temp']
        description = data['weather'][0]['description']

        return temperature, description
    
    except Exception as e:
        print(f"Exception: {e}")

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
    
def parse_json_cmd(sw, json_cmd):
    
    # If alarm blaring, we must change alarm 
    if (sw.watch_mode == 'alarm_blaring' and json_cmd['cmd'] != 'set_alarm'):
        return

    if (json_cmd['cmd'] == 'screen_on'):
        sw.display_on = True

    elif (json_cmd['cmd'] == 'screen_off'):
        sw.display_on = False
    
    elif (json_cmd['cmd'] == 'display_time'):
        sw.watch_mode = 'clock'
        print("Watch in clock mode")
    
    elif (json_cmd['cmd'] == 'display_message'):
        sw.watch_mode = 'message'
        sw.display_string = [json_cmd['args'][0]]
        print("Watch in message mode")

    elif (json_cmd['cmd'] == 'write_message'):
        sw.watch_mode = 'write'
        sw.display_string = ['Message:', '']
        print("Watch in write mode")
    
    elif (json_cmd['cmd'] == 'set_alarm'):
        args = json_cmd['args']
    
        # ADD PARAM SAFETY HERE
        sw.watch_mode = 'clock'
        sw.clock.alarm.set_time(args[0], args[1], args[2])
        print(f"Setting alarm to {sw.clock.alarm.hour}:{sw.clock.alarm.min}:{sw.clock.alarm.sec}")
   
    elif (json_cmd['cmd'] == 'display_location'):
        sw.watch_mode = 'location'
        sw.display_string = ['', '']
        print("Watch in location mode")

    elif (json_cmd['cmd'] == 'display_weather'):
        sw.watch_mode = 'weather'
        sw.display_string = ['', '']
        print("Watch in weather mode")



def main():

    ip = connect_to_wifi(SSID, Password)

    s = open_command_socket(ip, CMD_PORT)

    sw = SmartWatch()

    while True:

        sw.service_clock()

        json_cmd = check_for_commands(s)

        if(json_cmd):
            parse_json_cmd(sw, json_cmd)

        try:
            if (sw.watch_mode == 'clock'):
                sw.display_string = sw.get_clock_string()
            elif (sw.watch_mode == 'location'):
                lat, long = get_lat_long()
                sw.display_string[0] = f'Lat: {lat:3.3f}'
                sw.display_string[1] = f'Long: {long:3.3f}'
            elif (sw.watch_mode == 'weather'):
                lat, long = get_lat_long()
                temp, desc = get_weather(lat, long)
                sw.display_string[0] = f'Temp: {temp} C'
                sw.display_string[1] = f'{desc}'
            elif (sw.watch_mode == 'write'):
                sw.display_string[1] = sw.update_write_string(sw.display_string[1])
        except Exception as e:
            print(f'Exception: {e}')

        sw.service_display()

        # utime.sleep(0.125)


if __name__ == '__main__':
    main()