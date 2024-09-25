from machine import Pin, PWM, ADC
import utime

def main():

    # piezzo_pwm = PWM(Pin(), freq=500, duty=512)
    led_pwm = PWM(Pin(4), freq=500, duty=512)
    piezzo_pwm = PWM(Pin(5), freq=500, duty=512)

    adc = ADC(0)            # create ADC object on ADC pin

    while True:
        input = adc.read()
        print(input)
        led_pwm.duty(input)
        piezzo_pwm.freq(input * 4)
        utime.sleep(.1)
        #led_pwm.duty(1023)



        
if __name__ == '__main__':
    main()