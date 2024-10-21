''''
PCB and UART by Tri Do
Connect RX-TX, TX-RX, GND-GND
'''

from machine import UART, Pin, PWM, ADC
from utime import sleep_ms
import utime

MOTOR_FREQ = 1000
SERVO_FREQ = 50
#this is deadzone in 32-bits for ADC Joystick errors
DEADZONE = 4000
#the following is in millisecond, OFFSET = FULL LEFT, OFFSET+RANGE = FULL RIGHT
SERVO_OFFSET_US = 750
SERVO_RANGE_US = 1100
SERVO_MID_US = SERVO_OFFSET_US + SERVO_RANGE_US//2
SERVO_LEFT_MULTIPLIER = 1.00
SERVO_RIGHT_MULTIPLIER = 1.00
SERVO_INVERTED = True

Throttling = False
#Class Brushed Motor (forward,backward,brake,coast)
class IBT2:
    #Pin number for IBT_2, import PWM, Pin
    def __init__(self, LPWM_Pin, RPWM_Pin, L_EN_Pin, R_EN_Pin):
        self.LPWM = PWM(Pin(LPWM_Pin), freq = MOTOR_FREQ)
        self.RPWM = PWM(Pin(RPWM_Pin), freq = MOTOR_FREQ)
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
class Servo:
    def __init__(self, SERVO_PIN):
        self.servoPWM = PWM(SERVO_PIN, freq = SERVO_FREQ)
    def steering(self, percent):
        active_us = SERVO_OFFSET_US + percent*SERVO_RANGE_US//100
        self.servoPWM.duty_u16(active_us*65535//20000)
    def center(self):
        self.servoPWM.duty_u16((SERVO_OFFSET_US+SERVO_RANGE_US//2)*65535//20000)

led = Pin("LED", Pin.OUT)
t = utime.ticks_ms()
DELAY, ON_TIME = 3000, 300

adc0 = ADC(0)
adc1 = ADC(1)
adc2 = ADC(2)
uart=UART(0,baudrate=9600, bits=8, parity=None,stop=1, rx=Pin(1), tx=Pin(0), timeout=1)

LPWM, RPWM, L_EN, R_EN = 16, 17, 18, 19
ibt2 = IBT2(LPWM, RPWM, L_EN, R_EN)
SERVO_PIN = 15
servo = Servo(SERVO_PIN)

while True:
    #LED to see if powered on
    if (utime.ticks_ms()-t > DELAY):
        if (utime.ticks_ms()-t < DELAY+ON_TIME):
            led.on()
        else:
            t = utime.ticks_ms()
    else:
        led.off()

    RecData = ""
    #code block
    try:                                            #too lazy too debug(c)
        ibt2.forward(0)
        led.toggle()
        #string decode
        RecData = uart.read()       #format: a#####s#####e
        print(RecData)
        
        StrRecData = str(RecData)                    #convert to Str
        #print(StrRecData)
        accelIndex = StrRecData.find('a')            #'a' followed by acceleration pot
        steerIndex = StrRecData.find('s')            #'s' followed by steering pot
        endIndex = StrRecData.find('e')              #'e' end string
        accel = int(StrRecData[accelIndex+1:steerIndex])     #extract accel
        steer = int(StrRecData[steerIndex+1:endIndex])     #extract accel

        
        
        print('Accel: ',accel, ', Steer: ',steer)

        #keep in mind that controller is inverted both steering and acceleration
        if (accel > 32767+DEADZONE):
           forwardPercent = (accel-32767)//327//4
           ibt2.forward(forwardPercent)
           print('forward: ', forwardPercent)
           Throttling = True
        elif (accel < 32767-DEADZONE):
           backwardPercent = (32767-accel)//327
           ibt2.backward(backwardPercent)
           print('backward: ', backwardPercent)
           Throttling = True
        else:
            ibt2.coast()
            print("coasting")
            Throttling = False

        if (SERVO_INVERTED):
            steer = 65535 - steer
        if (abs(steer-32767) > DEADZONE):
            if (steer > 32767):
                steerMod = steer-DEADZONE
            else:
                steerMod = steer+DEADZONE
            steerPercent = steerMod*100//65535
            servo.steering(steerPercent)
            print("steering: ", steerPercent)
        else:
            servo.center()
            print("steering centered")


    except:
        pass
    utime.sleep_ms(35)
    
    
