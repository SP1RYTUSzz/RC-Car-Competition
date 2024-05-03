'''
Remember to connect GND and the CORRECT PINS!!!
'''

from machine import UART, Pin, ADC
from utime import sleep_ms
import utime

pin = Pin("LED", Pin.OUT)
adc0 = ADC(0)
adc1 = ADC(1)
adc2 = ADC(2)
uart =  UART(1, baudrate=9600, bits=8, parity=None, stop=1, rx=Pin(5), tx=Pin(4), timeout=10)  #7 bits, 1 stop

#var declare
accel = int(0)
SendData = bytes()

while True:
    accel = adc0.read_u16()                     #ADC0 pot to accel
    steer = adc1.read_u16()                     #ADC1 to steer, 16 bits
    SendData = bytearray('a'+str(accel)+'s'+str(steer)+'e', 'utf-8')            #combine & convert all data to bytes 
    uart.write(SendData)                                                        #send to HC-12 through UART 7 bits
    print('Accel: ',accel,', Steer: ',steer)
    print(SendData)
    pin.toggle()
    utime.sleep_ms(10)
