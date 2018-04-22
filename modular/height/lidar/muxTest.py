#try:
import math
import RPi.GPIO as GPIO
import time

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

#OUTPUT1 = 4
#OUTPUT2 = 17
#OUTPUT3 = 27
#OUTPUT4 = 22
#OUTPUT5 = 23
#OUTPUT6 = 24
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


lights1 = [0]*15
lights2 = [0]*15
lights3 = [0]*15
lights4 = [0]*15
lights5 = [0]*15
lights6 = [0]*15

for i in range(0,8):
    if(True):#avoid broke numbers
        i4 = (i & 0x08) >> 3
        i3 = (i & 0x04) >> 2
        i2 = (i & 0x02) >> 1
        i1 = (i & 0x01) >> 0
        print(str(i4)+""+str(i3)+""+str(i2)+""+str(i1))
        if(i1):
            GPIO.output(S3, GPIO.HIGH)
        if(i2):
            GPIO.output(S2, GPIO.HIGH)
        if(i3):
            GPIO.output(S1, GPIO.HIGH)
        if(i4):
            GPIO.output(S0, GPIO.HIGH)
        time.sleep(.5)
        
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

print lights2

#fix broke
lights1[0] = 0;# 1
lights2[3] = 0;# 19
lights5[3] = 0;# 79
lights6[14] = 0;# 90

lights = [lights1,lights2,lights3,lights4,lights5,lights6]
index = -1
for k in range(0,6):
    print "k: "+str(k)
    if(1 in lights[k]):
        index = lights[k].index(1)
        print "ind: "+str(index)
        index = (15*k)+index+1
        print "final k: "+str(k)
        break

print "output: "+str(index)
dist = index*.1

GPIO.cleanup()
#except:
#    GPIO.cleanup()
