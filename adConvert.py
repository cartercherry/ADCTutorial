################################################################################
# adConvert.py 2/21/23                                                         #
# convert pot readings (0-65536) to (100-0), given two points:                 #
#         (x1         ,y1)   (x2               ,y2)                            #
#         (minPotValue,100), (maxPotValue=65536, 0)                            #
#  m = slope = (y2-y1)/(x2-x1)                                                 #
#  y-y1 = m * (x - x1), x = raw pot value, y = scaled value, given x1,y1,x2,y2 #
#                                                                              #
#  calibrate the x1=minPotValue with the average of NUMSAMPLES                 #
#  display raw and scaled results in console and on SSD1306 oled dislay        #
#  oled display is I2C device  128X64 pixels display used                      #
#  ssd1306 lib available https://github.com/stlehmann/micropython-ssd1306      #
################################################################################

from machine import Pin, ADC, I2C
import ssd1306 #oled display device
from time import sleep
import sys  #for sys.exit()

NUMSAMPLES=500  #how many calibrationsamples for minPotValue=x1
DELAY=.3
POTPIN = 26  #ADO GPIO 26
adc= ADC(POTPIN)  # 0-65,536 raw reading, the x-axis
x1=minPotValue=528  #initial minumum pot reading (0-65536), updated by calibration 
x2=maxPotValue=65536 #max pot reading possible
y1=100 # y value desired at minPotValue, x1
y2=0 # y value desired at maxPotValue, x2
point1=(x1,y1)  #let's make a line with 2 points
point2=(x2,y2)  # it takes two tuples to slope

def calcSlope(point1, point2):   # slope m of line thru both points 
    m= (point2[1]-point1[1]) / (point2[0]-point1[0])  
    return m
    
def displayScaledReading(adc):  #y = m*(x- x1) + y1  since y-y1 = m*(x-x1)
    x= adc.read_u16()
    return (f'{x:0}',f'{(m*(x-x1) + y1):0.2f}')  # return raw and scaled readings as tuple

def initializeI2C(scl,sda):  # needed for oled display
    i2c = I2C(0, scl=scl, sda=sda, freq=400000)
    return i2c

def initializeOLED(i2c):
    oled= ssd1306.SSD1306_I2C(128,64,i2c)  # 128 by 64 pixel oled display
    return oled

def displayOled(raw, scaled):
    oled.text("Scaled (100-0):",0,0,1) # text,row, column, 1=white text
    oled.text(scaled,0,14,1)
    oled.text("Raw (0-65536):", 0, 28,1)
    oled.text(raw,0,42,1)
    oled.show()
    sleep(DELAY)
    oled.fill(0) #clear entire oled, 0=black pixel (off)
    
def calibrateMinPotValuePossible(numSamples,adc): #min value of pot when pot fully counterclockwise
    _=input("Turn pot fully counterclockwise, then press <ENTER> to calibrate pot minimum")
    print('Calibrating...')
    total=0
    for sample in range(numSamples):
        total += adc.read_u16()
        sleep(.005) #time between samples
    averageLowPotReading=total/numSamples
    x1=minPotValue=averageLowPotReading
    print(f'average low x1, minPotValue: {averageLowPotReading:0.1f}')
    #print(f'x1, minPotValue: {x1}, {minPotValue}')  #sanity check
    _ = input("Hit <ENTER> to continue")  # _ throw away variable
    return averageLowPotReading


''' Just get on with it already! '''
try:
    x1=minPotValue=calibrateMinPotValuePossible(NUMSAMPLES,adc)
    m=calcSlope(point1, point2)
    i2c=initializeI2C(scl=Pin(1), sda=Pin(0))
    #print(i2c.scan())  #confirm SSD1306 on I2C bus
    oled = initializeOLED(i2c)
    while True:
        raw,scaled = displayScaledReading(adc) #raw pot value and scaled y value
        print(f'raw: {raw}, scaled: {scaled}') # data to console
        displayOled(str(raw),str(scaled))      # data to Oled
        sleep(DELAY)
except KeyboardInterrupt:
    sys.exit()  # soft reset back to python repl >>>
