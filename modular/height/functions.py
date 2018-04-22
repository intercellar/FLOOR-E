#!/usr/bin/python

import serial, time, math, threading
import RPi.GPIO as GPIO

import math
import smbus

from urllib import urlopen
from random import random
from time import sleep

lid_val = 0
pcb_val = 0
acc_val = 0

 #Register
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
 
bus     = smbus.SMBus(1)
address = 0x68
 
lidar = serial.Serial('/dev/serial0', baudrate=115200)

lidar.write(bytearray([0x42]))
lidar.write(bytearray([0x57]))
lidar.write(bytearray([0x02]))
lidar.write(bytearray([0x00]))
lidar.write(bytearray([0x00]))
lidar.write(bytearray([0x00]))
lidar.write(bytearray([0x01]))
lidar.write(bytearray([0x06]))

mapping = {
            0:3,
            1:2,
            2:1,
            3:0,
            4:14,
            5:13,
            6:12,
            7:11,
            8:10,
            9:9,
            10:8,
            11:7,
            12:6,
            13:5,
            14:4
          }

mapping = {
            12:0,
            4:1,
            8:2,
            0:3,
            3:4,
            7:5,
            9:6,
            13:7,
            5:8,
            6:9,
            1:10,
            14:11,
            11:12,
            10:13,
            2:14
          }


### NOTE in use GPIOs NOTE
OUTPUT  = [4,17,27,22,23,24]
S3      = 5
S2      = 6
S1      = 16
S0      = 20

GPIO.setmode(GPIO.BCM)

init = GPIO.LOW

GPIO.setup(OUTPUT[0], GPIO.IN)#, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(OUTPUT[1], GPIO.IN)
GPIO.setup(OUTPUT[2], GPIO.IN)
GPIO.setup(OUTPUT[3], GPIO.IN)
GPIO.setup(OUTPUT[4], GPIO.IN)
GPIO.setup(OUTPUT[5], GPIO.IN)

GPIO.setup(S0, GPIO.OUT, initial=init)
GPIO.setup(S1, GPIO.OUT, initial=init)
GPIO.setup(S2, GPIO.OUT, initial=init)
GPIO.setup(S3, GPIO.OUT, initial=init)

def get_byte():
    temp = list(bytearray(lidar.read()))[0]
    return temp

def lidar_fun():    
    global lid_val
    if (get_byte() == 0x59) and (get_byte() == 0x59):
        t1 = get_byte()
        t2 = get_byte()

        t2 = t2<<8
        t2 += t1
        val = t2

        t1 = get_byte()
        t2 = get_byte()

        t2 = t2<<8
        t2 += t1

        get_byte()
        get_byte()
        get_byte()

        #lid_val = val
        #lid_val = (.39654*val)-10.2886
        #lid_val = (.4985*val)-22.8265
        #lid_val = val*.383

        ##NOTE cm to in
        #lid_val = val*0.393701
        lid_val = val

        #a = 1.8233*math.pow(10,-6)
        #b = -7.4406*math.pow(10,-4)
        #c = .11067
        #d = -6.60237
        #e = 142.7884
        #lid_val = (a*math.pow(val,4))+(b*math.pow(val,3))+(c*math.pow(val,2))+(d*val)+e

        a = 1.9134*(10**-6)
        b = -6.0594*(10**-4)
        c = .06702
        d = -2.5856
        e = 42.7227
        lid_val = (a*(val**4))+(b*(val**3))+(c*(val**2))+(d*val)+e


        time.sleep(.001)

    t1 = threading.Thread(target=lidar_fun)
    t1.daemon = True
    t1.start()

def write_height(lid, pcb, acc):

    to_write = 'http://core.local/store?lid={}&pcb={}&acc={}'
    to_write = to_write.format(lid, pcb, acc)

    urlopen(to_write)

def read_byte(reg):
    return bus.read_byte_data(address, reg)

def read_word(reg):
    h = bus.read_byte_data(address, reg)
    l = bus.read_byte_data(address, reg)
    value = (h << 8) + 1
    return value

def read_word_2c(reg):
    val = read_word(reg)
    if(val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(x,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

def acc_fun():
    global acc_val

    #print("hey I'm here")
    bus.write_byte_data(address, power_mgmt_1,0)

    #print("Gyroscop")
    gyro_xout = read_word_2c(0x43)
    gyro_yout = read_word_2c(0x45)
    gyro_zout = read_word_2c(0x47)
    #print "xout: ", ("%5d" % gyro_xout), " scaled: ", (gyro_xout / 131)
    #print "yout: ", ("%5d" % gyro_yout), " scaled: ", (gyro_yout / 131)
    #print "zout: ", ("%5d" % gyro_zout), " scaled: ", (gyro_zout / 131)

    #print "accel"
    acx = read_word_2c(0x3b)
    acy = read_word_2c(0x3d)
    acz = read_word_2c(0x3f)

    acx_scaled = acx/16384.0
    acy_scaled = acy/16384.0
    acz_scaled = acz/16384.0       
    #print "acx: ", ("%6d" % acx), " scaled: ", (acx_scaled)
    #print "acy: ", ("%6d" % acy), " scaled: ", (acy_scaled)
    #print "acz: ", ("%6d" % acz), " scaled: ", (acz_scaled)

    xrot = get_x_rotation(acx_scaled, acy_scaled, acz_scaled)
    yrot = get_y_rotation(acx_scaled, acy_scaled, acz_scaled) 

    xrot *=  (90/85)
    yrot *=  (90/45)
    xrot -= -.935
    yrot -= -1.885
    #print "X Rotation: ", xrot
    #print "Y Rotation: ", yrot
    acc_val = math.cos(math.radians(xrot)) * math.cos(math.radians(yrot))
    #print("acc_val ", acc_val)

    time.sleep(.4)
    t3 = threading.Thread(target=acc_fun)
    t3.daemon = True
    t3.start()

    #print('3', acc_val)

def get_vals():
    global lid_val
    global pcb_val
    global acc_val

    return lid_val, pcb_val, acc_val

def pcb_fun():
    global pcb_val

    lights1 = [0]*15
    lights2 = [0]*15
    lights3 = [0]*15
    lights4 = [0]*15
    lights5 = [0]*15
    lights6 = [0]*15

    for i in range(0,15):
        if(True):
            i4 = (i & 0x08) >> 3
            i3 = (i & 0x04) >> 2
            i2 = (i & 0x02) >> 1
            i1 = (i & 0x01) >> 0

            if(i1):
                GPIO.output(S3, GPIO.HIGH)
            else:
                GPIO.output(S3, GPIO.LOW)
            if(i2):
                GPIO.output(S2, GPIO.HIGH)
            else:
                GPIO.output(S2, GPIO.LOW)
            if(i3):
                GPIO.output(S1, GPIO.HIGH)
            else:
                GPIO.output(S1, GPIO.LOW)
            if(i4):
                GPIO.output(S0, GPIO.HIGH)
            else:
                GPIO.output(S0, GPIO.LOW)

            time.sleep(.05)
            
            lights1[mapping[i]] = GPIO.input(OUTPUT[0])
            lights2[mapping[i]] = GPIO.input(OUTPUT[1])
            lights3[mapping[i]] = GPIO.input(OUTPUT[2])
            lights4[mapping[i]] = GPIO.input(OUTPUT[3])
            lights5[mapping[i]] = GPIO.input(OUTPUT[4])
            lights6[mapping[i]] = GPIO.input(OUTPUT[5])

            time.sleep(.05)

    # broken resistors
    lights1[12] = 0
    lights2[14] = 0
    lights5[14] = 0

    lights  = [lights1,lights2,lights3,lights4,lights5,lights6]
    #print(lights)
    indexes = []
    for k in range(0,6):
        for i in range(0,15):
            if(lights[k][i] == 1):
                indexes.append((15*k)+i+1)

    if(len(indexes) == 0):
        pcb_val = -1
        #print('Resistor: None')
    else:
        index  = sum(indexes)/len(indexes)
        #print(sum(indexes))
        #print(len(indexes))
        #print('Resistor: {}'.format(index))
        pcb_val = index*.0984

    time.sleep(.25)
    t2 = threading.Thread(target=pcb_fun)
    t2.daemon = True
    t2.start()

    return pcb_val
