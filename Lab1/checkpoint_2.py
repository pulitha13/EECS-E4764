from machine import Pin
import utime

BLINK_PERIOD = .25
LED_1_PERIOD = 1
LED_2_PERIOD = 5

LED_1 = 0
LED_2 = 2

def led_blink(pins, usec):

    for pin in pins:
        Pin(pin, Pin.OUT).value(0)
    
    utime.sleep(usec)
  
    for pin in pins:
        Pin(pin, Pin.OUT).value(1)

    return



def main():

    while True:

        led_blink([LED_1, LED_2], BLINK_PERIOD)
        utime.sleep(LED_1_PERIOD - BLINK_PERIOD)

        #100ms
        led_blink([LED_1], BLINK_PERIOD)

        utime.sleep(LED_1_PERIOD - BLINK_PERIOD)

        #200ms
        led_blink([LED_1], BLINK_PERIOD)

        utime.sleep(LED_1_PERIOD - BLINK_PERIOD)

        #300ms
        led_blink([LED_1], BLINK_PERIOD)

        utime.sleep(LED_1_PERIOD - BLINK_PERIOD)

        #400ms
        led_blink([LED_1], BLINK_PERIOD)

        utime.sleep(LED_1_PERIOD - BLINK_PERIOD)

if __name__ == '__main__':
    main()

