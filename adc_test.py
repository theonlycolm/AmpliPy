#! /usr/bin/python

# Python script to validate functionality of the MPC3008/ADS1015 Raspberry Pi hat 
#
#
import RPi.GPIO as GPIO
import spidev
import time
import os


CLK = 18
MISO = 23
MOSI = 24
CS = 25

channel = 3

def configSpiPins(clkPin, misoPin, mosiPin, csPin):
    GPIO.setup(clkPin, GPIO.OUT)
    GPIO.setup(misoPin, GPIO.IN)
    GPIO.setup(mosiPin, GPIO.OUT)
    GPIO.setup(csPin, GPIO.OUT)


def readAdc(channel, clkPin, misoPin, mosiPin, csPin):
    #validate inputs MPC3008 has 8 channels
    if (channel <0) or (channel >7):
        print "readAdc(): Invalid channel. CHannel must be between 0 and 7"
        return -1

    #Chip select must be pulled high per datasheet
    GPIO.output(csPin, GPIO.HIGH)

    # read command is:
    # start bit = 1
    # single-ended comparison = 1 (vs. pseudo-differential)
    # channel num bit 2
    # channel num bit 1
    # channel num bit 0 (LSB)
    read_command = 0x18
    read_command |= channel
    
    sendBits(read_command, 5, clkPin, mosiPin)
    
    adcValue = recvBits(12, clkPin, misoPin)
    
    # Set chip select high to end the read
    GPIO.output(csPin, GPIO.HIGH)
  
    return adcValue


def sendBits (data, numBits, clkPin, mosiPin):
    '''sends 1 byte or less'''
    data <<= (8-numBits)

    #set the Pi's output bit to high or low depending on the highest bit of the data field
    for bit in range(numBits):
        if data & 0x80:
            GPIO.output(mosiPin, GPIO.HIGH)
        else:
            GPIO.output(mosiPin, GPIO.LOW)

    #Move to the next bit
    data <<= 1
    #pulse clock pin
    GPIO.output(clkPin, GPIO.HIGH)
    GPIO.output(clkPin, GPIO.LOW)


def recvBits(numBits, clkPin, misoPin):
    '''receive bits from the ADC'''
    retVal = 0

    for bit in range(numBits):
        #pulse clock pin
        GPIO.output(clkPin, GPIO.HIGH)
        GPIO.output(clkPin, GPIO.LOW)

        #read inbound value
        if GPIO.input(misoPin): 
            retVal |= 0x1
    
        #next bit
        retVal <<=1
    
    return (retVal/2)
    

if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)
        configSpiPins(CLK, MISO, MOSI, CS)

        while True:
            val = readAdc(channel, CLK, MISO, MOSI, CS)
            print "For Ch ", channel, "CLK ", CLK, "MISO ", MISO, "MOSI ", MOSI, "CS ", CS
            print "--> ADC Value is ", str(val)
            time.sleep(1)

    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit(0)









