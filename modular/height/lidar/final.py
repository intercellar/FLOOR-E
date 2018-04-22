#!/usr/bin/python

import serial, time, math, threading
import RPi.GPIO as GPIO
    
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
            3:0,
            2:1,
            1:2,
            0:3,
            14:4,
            13:5,
            12:6,
            11:7,
            10:8,
            9:9,
            8:10,
            7:11,
            6:12,
            5:13,
            4:14
          }

OUTPUT = [4,17,27,22,23,24]

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

lidar_val = 0
dist_val  = 0

def get_byte():
    return list(bytearray(lidar.read()))[0]

def lidar_fun():    
    global lidar_val
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

        lidar_val = val*.4

        time.sleep(.0001)

        t1 = threading.Thread(target=lidar_fun)
        t1.daemon = True
        t1.start()

def pcb_fun():
    global dist_val

    lights1 = [0]*15
    lights2 = [0]*15
    lights3 = [0]*15
    lights4 = [0]*15
    lights5 = [0]*15
    lights6 = [0]*15

    for i in range(0,8):
        if(True):
            i4 = (i & 0x08) >> 3
            i3 = (i & 0x04) >> 2
            i2 = (i & 0x02) >> 1
            i1 = (i & 0x01) >> 0
            if(i1):
                GPIO.output(S3, GPIO.HIGH)
            if(i2):
                GPIO.output(S2, GPIO.HIGH)
            if(i3):
                GPIO.output(S1, GPIO.HIGH)
            if(i4):
                GPIO.output(S0, GPIO.HIGH)
            time.sleep(.1)
            
            lights1[mapping[i]] = GPIO.input(OUTPUT[0])
            lights2[mapping[i]] = GPIO.input(OUTPUT[1])
            lights3[mapping[i]] = GPIO.input(OUTPUT[2])
            lights4[mapping[i]] = GPIO.input(OUTPUT[3])
            lights5[mapping[i]] = GPIO.input(OUTPUT[4])
            lights6[mapping[i]] = GPIO.input(OUTPUT[5])

            GPIO.output(S0, GPIO.LOW)
            GPIO.output(S1, GPIO.LOW)
            GPIO.output(S2, GPIO.LOW)
            GPIO.output(S3, GPIO.LOW)

    #fix broke
    lights1[0]  = 0;# 1
    lights2[3]  = 0;# 19
    lights5[3]  = 0;# 79
    lights6[14] = 0;# 90

    lights  = [lights1,lights2,lights3,lights4,lights5,lights6]
    index   = -1
    for k in range(0,6):
        if(1 in lights[k]):
            index = lights[k].index(1)
            index = (15*k)+index+1
            break

    dist        = index*.1
    dist_val    = dist

    time.sleep(.2)
    t2 = threading.Thread(target=pcb_fun)
    t2.daemon = True
    t2.start()

timer = 0

lidar_fun()
pcb_fun()

while True:
    print(lidar_val, dist_val)
    if dist_val == -.1:
        print('no pcb, lidar={}'.format(lidar_val))
    else:
        print('distance: {}'.format(lidar_val - dist_val))
    time.sleep(.5)
