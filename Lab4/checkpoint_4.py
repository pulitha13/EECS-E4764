from machine import PWM, Pin, RTC, I2C, ADC, SPI
import network
import time
import urequests
import ujson
import utime
import ssd1306

SDA_PIN = 4
SCL_PIN = 5

#Wifi credentials
SSID = "Columbia University"
Password = ""

#Weather API key and url
API_KEY = '058ef319596c10d77118e888070ca3da'
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

station = network.WLAN(network.STA_IF)


#Push notifications
# ntfy.sh topic name
# NTFY_TOPIC = "rw3043_jm5915_weather_report"  # Replace with your unique topic

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
        raise Exception('Failed to connect to Wi-Fi.')  # Generic exception

# Function to get latitude and longitude
def get_lat_lon():
    url = "http://ip-api.com/json"
    
    try:
        response = urequests.get(url)
        
        # Check if the response was successful (status code 200)
        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: Unable to retrieve location data.")
        
        data = ujson.loads(response.text)

        latitude = data.get('lat')
        longitude = data.get('lon')

        print('Latitude:', latitude, 'Longitude:', longitude)
        
        return latitude, longitude

        # # Display latitude and longitude on the OLED
        # display.fill(0)  # Clear the display
        # display.text('Latitude: {}'.format(latitude), 0, 0)
        # display.text('Longitude: {}'.format(longitude), 0, 10)
        # display.show()

    except Exception as e:
        print('Error retrieving location:', e)

        # display.fill(0)  # Clear the display
        # display.text('Error:', 0, 0)
        # display.text(str(e), 0, 10)
        # display.show()
    
    finally:
        if 'response' in locals():
            response.close()  # Ensure response is closed if it was created

def get_weather(display, longitude, latitude):
    url = f"{WEATHER_URL}?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric"  # Metric for Celsius

    try:
        response = urequests.get(url)
        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: Unable to retrieve weather data.")
        
        data = ujson.loads(response.text)

        #Extract temp and weather description

        temperature = data['main']['temp'] #Converting from Kelvin to Celsius
        description = data['weather'][0]['description']

        #Display weather information on OLED
        display.fill(0)
        display.text('Temp: {}C'.format(temperature),0,0)
        display.text('{}'.format(description),0,15)
        display.show()

        print('Temperature:',temperature,"Description:", description)
        
        # Send weather notification to ntfy.sh
        # message = ujson.dumps(data)
        # print(message)
        # send_notification(message)

        message = f"Longitude: {longitude},Latitude:{latitude},Temp: {temperature} C, {description}"
        # message = "Hello"
        send_notification(ujson.dumps(message))  # Convert to JSON string
    
    except Exception as e:
        print('Error retrieving weather data:', e)
        display.fill(0)  # Clear the display
        display.text('Weather Error:', 0, 0)
        display.text(str(e), 0, 10)
        display.show()
    
    finally:
        if'response' in locals():
            response.close() #Making sure that if a response is created it closes

# Function to send notification to ntfy.sh
def send_notification(message):
    url = "http://ntfy.sh/rw3043-jm5915-weather-report"
    
    try:
        response = urequests.post(url, data=message, headers={"Content-Type": "application/json"})
        if response.status_code != 200:
            print(f"Failed to send notification: {response.status_code}")
        else:
            print("Notification sent successfully!")
    
    except Exception as e:
        print(f'Error sending notification: {e}')
    
    finally:
        if 'response' in locals():
            response.close()

def main():
    #main function being executed
    print("Initializing I2C and Display")
    i2c = I2C(sda=Pin(SDA_PIN), scl=Pin(SCL_PIN))
    display = ssd1306.SSD1306_I2C(128, 32, i2c)

    try:
        connect_to_wifi(SSID, Password)
        while True:
            latitude, longitude = get_lat_lon() #get coordinates
            # latitude, longitude = 40.8213, -73.9682 #get coordinates
            get_weather(display,longitude,latitude) #display weather data
            time.sleep(30) #30 seconds between updates
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()


