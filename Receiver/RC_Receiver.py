''''
PCB and UART by Tri Do
Connect RX-TX, TX-RX, GND-GND
'''

from machine import UART, Pin, PWM, ADC
from utime import sleep_ms
import utime


#Class Brushed Motor (forward,backward,brake,coast)
class IBT2:
    #Pin number for IBT_2, import PWM, Pin
    def __init__(self, LPWM_Pin, RPWM_Pin, L_EN_Pin, R_EN_Pin):
        self.LPWM = PWM(Pin(LPWM_Pin), freq = 1000)
        self.RPWM = PWM(Pin(RPWM_Pin), freq = 1000)
        self.L_EN = Pin(L_EN_Pin, Pin.OUT)
        self.R_EN = Pin(R_EN_Pin, Pin.OUT)

    #forward in percentage with maximum at 98%
    def forward(self, percent):
        self.L_EN.on()
        self.R_EN.on()
        self.LPWM.duty_u16(0)
        self.RPWM.duty_u16(642*percent)

    #backward in percentage with maximum at 98%
    def backward(self, percent):
        self.L_EN.on()
        self.R_EN.on()
        self.LPWM.duty_u16(642*percent)
        self.RPWM.duty_u16(0)

    #coasting with both EN legs LOW
    def coast(self):
        self.L_EN.off()
        self.R_EN.off()

    #braking with both EN legs HIGH
    def brake(self):
        self.L_EN.on()
        self.R_EN.on()
        self.LPWM.duty_u16(0)
        self.RPWM.duty_u16(0)

    #print(motor775.test())
    def test(self):
        pass


led = Pin("LED", Pin.OUT)
t = utime.ticks_ms()
DELAY, ON_TIME = 3000, 300

adc0 = ADC(0)
adc1 = ADC(1)
adc2 = ADC(2)
uart=UART(0,baudrate=9600, bits=8, parity=None,stop=1, rx=Pin(1), tx=Pin(0), timeout=1)

LPWM, RPWM, L_EN, R_EN = 16, 17, 18, 19
ibt2 = IBT2(LPWM, RPWM, L_EN, R_EN)

while True:
    #LED to see if powered on
    if (utime.ticks_ms()-t > DELAY):
        if (utime.ticks_ms()-t < DELAY+ON_TIME):
            led.on()
        else:
            t = utime.ticks_ms()
    else:
        led.off()

    #code block
    try:                                            #too lazy too debug(c)
        #string decode
        RecData=uart.read()                         #format: a#####s#####e
        StrRecData = str(RecData)                    #convert to Str
        accelIndex = StrRecData.find('a')            #'a' followed by acceleration pot
        accel = int(StrRecData[accelIndex+1:steerIndex])     #extract accel
        steerIndex = StrRecData.find('s')            #'s' followed by steering pot
        steer = int(StrRecData[steerIndex+1:endIndex])     #extract accel
        endIndex = StrRecData.find('e')              #'e' end string
        
        
        print('Accel: ',accel, ', Steer: ',steer)

        if (accel > 32767):
           ibt2.forward((accel-32767)//327)
           print('forward: ', (accel-32767)//327)
        elif (accel < 32767):
           ibt2.backward((32767-accel)//327)
           print('backward: ', (32767-accel)//327)

    except:
        pass
    utime.sleep_ms(35)
    
    
