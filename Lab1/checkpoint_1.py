from machine import Pin
import utime

INTER_SYMBOL_TIME = .2
INTER_LETTER_TIME = .5
INTER_MESSAGE_TIME = 2
DOT_FLASH_LEN = .5
DASH_FLASH_LEN = 2 * DOT_FLASH_LEN

def led_blink(usec):

    Pin(0, Pin.OUT).value(0)
    utime.sleep(usec)
    Pin(0, Pin.OUT).value(1)

    return



def main():
    while True:


    # Pin(0, Pin.OUT).value(0)
    # utime.sleep(1)
    # Pin(0, Pin.OUT).value(1)
    # utime.sleep(1)

        #S
        led_blink(DOT_FLASH_LEN)
        utime.sleep(INTER_SYMBOL_TIME)
        led_blink(DOT_FLASH_LEN)
        utime.sleep(INTER_SYMBOL_TIME)
        led_blink(DOT_FLASH_LEN)
        utime.sleep(INTER_SYMBOL_TIME)

        #O
        led_blink(DASH_FLASH_LEN)
        utime.sleep(INTER_SYMBOL_TIME)
        led_blink(DASH_FLASH_LEN)
        utime.sleep(INTER_SYMBOL_TIME)
        led_blink(DASH_FLASH_LEN)
        utime.sleep(INTER_SYMBOL_TIME)

        #S
        led_blink(DOT_FLASH_LEN)
        utime.sleep(INTER_SYMBOL_TIME)
        led_blink(DOT_FLASH_LEN)
        utime.sleep(INTER_SYMBOL_TIME)
        led_blink(DOT_FLASH_LEN)
        utime.sleep(INTER_SYMBOL_TIME)

        utime.sleep(INTER_MESSAGE_TIME)

        
if __name__ == '__main__':
    main()