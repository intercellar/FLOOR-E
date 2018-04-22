#!/usr/bin/python -B

from __future__ import division
import threading

import Tkinter as tk
import urllib
import json

from time import sleep, time
from os import system, listdir
import tkMessageBox

import Robot

import os

import Adafruit_PCA9685

#import RPi.GPIO as GPIO
#GPIO.setmode(GPIO.BCM)
#light_pin = 21
#GPIO.setup(light_pin, GPIO.OUT)
#GPIO.output(light_pin, GPIO.LOW)

os.system("xset r off")

display = {'lid': -1,
           'pcb': -1,
           'acc': -1
           }

FS = 2
WAIT = .1

LEFT_TRIM   = 0
RIGHT_TRIM  = 0

#ROBOT VARIABLES
robot = Robot.Robot(left_trim=LEFT_TRIM, right_trim=RIGHT_TRIM)
key = {"key":"w","first":0,"last":1}
light = 0
bright = 50
speed = 160
heights = []
h = 0

#servo stuff
pwm = Adafruit_PCA9685.PCA9685()
#150 600
servo_minh = 550
servo_maxh = 750
servo_minv = 250
servo_maxv = 500
servo_minp = 25
servo_maxp = 350
servo_midh = int((servo_minh+servo_maxh)/2)
servo_midv = int((servo_minv+servo_maxv)/2)
servo_midp = int((servo_minp+servo_maxp)/2)
pwm.set_pwm_freq(60)
shori = 4
svert = 7
spcb = 2
print("start")
#pwm.set_pwm(shori, 0, servo_midh)
#pwm.set_pwm(svert, 0, servo_midv)
#pwm.set_pwm(spcb, 0, servo_maxp)
#sleep(1)
#pwm.set_pwm(svert, 0, servo_min)
servo0 = servo_midv
servo1 = servo_midh
servo2 = servo_maxp

class MainApp(tk.Tk):
    def __init__(self, display):
        tk.Tk.__init__(self)
        tk.Tk.wm_title(self, 'Intercellar')
        self.attributes('-fullscreen', True)

        self.display = display

        self.container = tk.Frame(self)
        self.container.pack(side='top', fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.menubar = tk.Menu(self)

        self.menubar.add_command(label='Quit', command=quit)
        self.menubar.add_command(label='Main', command=lambda: self.show_frame(Main))
        self.menubar.add_command(label='Testing', command=lambda: self.show_frame(Testing))

        tk.Tk.config(self, menu=self.menubar)

        self.frames = {}
        for F in [Main, Testing]:
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(Testing)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class Main(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.info_widget = Info_Widget(self)
        self.info_widget.pack(side=tk.RIGHT)

        self.info_widget.add_number('LID', '--', 0, 0, top='LIDAR', bottom='in')
        self.info_widget.add_number('PCB', '--', 1, 0, top='PCB', bottom='in')
        self.info_widget.add_number('ACC', '--', 2, 0, top='ACC', bottom='')
        self.info_widget.add_number('RES', '--', 3, 0, top='RES', bottom='in')

        self.info_widget2 = Info_Widget(self)
        self.info_widget2.pack(side=tk.LEFT)

        self.info_widget2.add_number('LIGHT', '--', 0, 0, top='LIGHT', bottom='')
        self.info_widget2.add_number('LM', '--', 1, 0, top='LM', bottom='/255')
        self.info_widget2.add_number('RM', '--', 2, 0, top='RM', bottom='/255')
        self.info_widget2.add_number('ECE', '--', 3, 0, top='ECE', bottom='')

    def refresh(self, display):
        global h
        self.info_widget.info['LID'].change_text(display['lid'])
        self.info_widget.info['PCB'].change_text(display['pcb'])
        self.info_widget.info['ACC'].change_text(display['acc'])

        try:
            lid = float(display['lid'])
            pcb = float(display['pcb'])
            acc = float(display['acc'])
        except:
            lid = 0
            pcb = 0
            acc = 1

        res = round((lid - pcb) * acc, 2)
        res = min(45, res)
        res = max(0, res)
        h = res

        self.info_widget.info['RES'].change_text(str(res))

class Testing(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.BD1 = Button_Display(self, opt=1)
        self.BD1.pack(side=tk.LEFT)


        self.info_widget = Info_Widget(self)

        self.info_widget.add_big('RES', '--', 0, 0, top='HEIGHT', bottom='in')

        """
        self.info_widget.add_number('PCB', 'PCB: -- in', 1, 0)
        self.info_widget.add_number('LID', 'LID: -- in', 2, 0)
        self.info_widget.add_number('ANG', 'ANG: -- ' + u'\u00B0', 3, 0)
        """

        self.info_widget.pack(side=tk.LEFT, padx=60, pady=10)

        self.BD2 = Button_Display(self, opt=2)
        self.BD2.pack(side=tk.RIGHT)

    def refresh(self, display):
        global h

        try:
            lid = float(display['lid'])
            pcb = float(display['pcb'])
            acc = float(display['acc'])
        except:
            lid = 0
            pcb = 0
            acc = 1

        res = round((lid - pcb) * acc, 2)
        res = min(45, res)
        res = max(0, res)
        h = res

        self.info_widget.info['RES'].change_text(str(res))


class Button_Display(tk.Frame):
    def __init__(self, parent, opt=1):
        tk.Frame.__init__(self, parent)

        pady=10
        height=3
        width=20

        if opt == 1:
            self.B1 = tk.Button(self, text='SPEED', font='Consolas 14 bold', pady=pady, height=height, width=10, disabledforeground='black', bg='#4286f4', state=tk.DISABLED)
            self.B2 = tk.Button(self, text='LOW',  pady=pady, height=height, width=width, command=set_speed_low)
            self.B3 = tk.Button(self, text='MED', pady=pady, height=height, width=width, command=set_speed_med)
            self.B4 = tk.Button(self, text='HIGH', pady=pady, height=height, width=width, command=set_speed_high)

            for self.B in [self.B1, self.B2, self.B3, self.B4]:
                self.B.pack(side=tk.TOP, pady=pady)

        if opt == 2:
            self.B1 = tk.Button(self, text='LIGHT', font='Consolas 14 bold', pady=pady, height=height, width=10, disabledforeground='black', bg='#4286f4', state=tk.DISABLED)
            self.B2 = tk.Button(self, text='LOW', pady=pady, height=height, width=width, command=set_light_low)
            self.B3 = tk.Button(self, text='MED', pady=pady, height=height, width=width, command=set_light_med)
            self.B4 = tk.Button(self, text='HIGH', pady=pady, height=height, width=width, command=set_light_high)

            for self.B in [self.B1, self.B2, self.B3, self.B4]:
                self.B.pack(side=tk.TOP, pady=pady)


class Info_Widget(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.info = {}

    def add_big(self, id_str, text, row, column, top=False, bottom=False):

        PADX = 5
        PADY = 10

        self.info[id_str] = Number_Display(self, text, top=top, bottom=bottom)
        self.info[id_str].grid(padx=PADX, pady=PADY, row=row, column=column)

    def add_number(self, id_str, text, row, column, top=False, bottom=False):

        PADX = 5
        PADY = 1

        self.info[id_str] = Number_Display2(self, text, top=top, bottom=bottom)
        self.info[id_str].grid(padx=PADX, pady=PADY, row=row, column=column)

    def change_text(self, text):
        self.itemconfig(self.text, text=text)

class Number_Display2(tk.Canvas):
    def __init__(self, parent, text, top=False, bottom=False):
        tk.Canvas.__init__(self, parent, height=100, width=100)

        #self.rect = self.create_rectangle(0, 0, 100, 30, fill='#C0C0C0', width=0)
        self.rect = self.create_rectangle(0, 0, 100, 30, fill='#C0C0C0', width=0)
        self.text = self.create_text(50, 15, text=text, fill='black', font='Consolas 9 bold')

        """
        if top:
            self.top = self.create_text(50, 15, text=top, fill='black', font='Consolas 9 bold')
        if bottom:
            self.bot = self.create_text(50, 85, text=bottom, fill='black', font='Consolas 9 bold')
        """

    def change_text(self, text):
        self.itemconfig(self.text, text=text)


class Number_Display(tk.Canvas):
    def __init__(self, parent, text, top=False, bottom=False):
        tk.Canvas.__init__(self, parent, height=152, width=152)

        #self.rect = self.create_rectangle(0, 0, 150, 150, fill='#C0C0C0', width=0)
        self.rect = self.create_rectangle(1, 1, 150, 150, outline='black', activeoutline='black', width=1)
        self.text = self.create_text(75, 75, text=text, fill='black', font='Consolas 14 bold')

        if top:
            self.top = self.create_text(75, 25, text=top, fill='black', font='Consolas 9 bold')
        if bottom:
            self.bot = self.create_text(75, 125, text=bottom, fill='black', font='Consolas 9 bold')

    def change_text(self, text):
        self.itemconfig(self.text, text=text)

last = (time(), None)

def key_input(event):
    key_press = event.char
    kp = key_press.lower()
    st = 0

    print(key_press.lower())
    global key
    global speed
    global bright

    now = time()
    #print('pressed: {}, {}'.format(key_press.lower(), now-last[0]))
    
    if(kp=='w' or kp=='a' or kp=='s' or kp=='d'):
        if(kp == key["key"]):
            key["last"] = now
        else:
            key["key"] = kp
            key["first"] = now
            key["last"] = now 
        if key_press.lower() == 's':
            #print("pressed")
            robot.forward(speed)
            sleep(st)
        if key_press.lower() == 'w':
            #print("pressed")
            robot.backward(speed)
            sleep(st)
        if key_press.lower() == 'd':
            robot.right(speed)
            sleep(st)
        if key_press.lower() == 'a':
            robot.left(speed)
            sleep(st)

    global h
    #non-movement controls
    if key_press.lower() == 'p':
        party_bot()
    if key_press.lower() == 'e': 
        heights.append(h)
    if key_press.lower() == 'q':
        print("Heights: ", heights)   
        robot.set_light1(0)
        #GPIO.output(light_pin, GPIO.LOW)
        quit()
    if key_press.lower() == 'r':
        global light
        if(light):
            light = 0
            robot.set_light1(0)
            #GPIO.output(light_pin, GPIO.LOW)
        else:
            light = 1
            print("light") #250
            robot.set_light1(bright)
            #GPIO.output(light_pin, GPIO.HIGH)

    #key = key_press.lower()

    #servo controls
    global servo0
    global servo1
    global servo2
    global s
    global up
    global svert
    global shori
    global spcb

    delta = 5
    delta2 = 1
    if kp=='t' or kp=='g' or kp=='h' or kp=='f':
        if kp == key['key']:
            key['last'] = now
        else:
            key['key'] = kp
            key['first'] = now
            key['last'] = now
        if key_press.lower() == 't':
            if(servo0 < servo_maxv):
                servo0 = min(servo_maxv, servo0+delta)
                pwm.set_pwm(svert, 0, servo0)
                s = svert
                up = True
                press_servo()
            #while(now-key['first'] <= .49 and servo0 < servo_max):
            #    servo0 = min(servo_max, servo0+delta2)
            #    pwm.set_pwm(0,0,servo0)
        if key_press.lower() == 'g':
            if(servo0 > servo_minv):
                servo0 = max(servo_minv, servo0-delta)
                pwm.set_pwm(svert, 0, servo0)
                s = svert
                up = False
                press_servo()
            #while(now-key['first'] <=.49 and servo0 > servo_min):
            #    servo0 = max(servo_min, servo0-delta2)
            #    pwm.set_pwm(0, 0, servo0)
        if key_press.lower() == 'f':
            if(servo1 < servo_maxh):
                servo1 = min(servo_maxh, servo1+delta)
                pwm.set_pwm(shori, 0, servo1)
                s = shori
                up = True
                press_servo()
            #while(now-key['first'] <= .49 and servo1 < servo_max):
            #    servo1 = min(servo_max, servo1+delta2)
            #    pwm.set_pwm(1, 0, servo1)
        if key_press.lower() == 'h':
            if(servo1 > servo_minh):
                servo1 = max(servo_minh, servo1-delta)
                pwm.set_pwm(shori, 0, servo1)
                s = shori
                up = False
                press_servo()
            #while(now-key['first'] <=.49 and servo1 > servo_min):
            #    servo1 = max(servo_min, servo1-delta2)
            #    pwm.set_pwm(1, 0, servo1)

    if key_press.lower() == 'v':
        servo2 = pwm.set_pwm(spcb, 0, servo_minp)
    if key_press.lower() == 'b':
        servo2 = pwm.set_pwm(spcb, 0, servo_maxp)
    #print(servo0)

def stop_bot(event):
    global key
    #key = None
    #print("depressed")
    key_release = event.char
    kp = key_release.lower()
    now = time()
    #print('released: {}, {}'.format(key_release.lower(), now-last[0]))

    if key_release.lower() == 'a' or key_release.lower() == 'w' or key_release.lower() == 's' or key_release.lower() == 'd':
        if(now-key["first"] <= .49):
        #if False:
            print("stopbot++++++++++++++++++++++++++++++++++++++++++++++")
            print(key["first"])
            key["key"] = "-1"
            robot.stop()

    if kp=='t' or kp=='g' or kp=='f' or kp=='h':
        if(now-key['first'] <= .49):
            print("stop serv")
            key["key"] = "-1"
            key["first"] = 0

def fformat(item):
    return str(item)

def check_for_stop():
    global key
    #print("cfs")
    now = time()
    if(now-key["first"] > .49):#.485
        if(now-key["last"] > .1):
            #print("cfs")
            #print(key["first"])
            key["key"] = "-1"
            robot.stop()
        
    sleep(.05)
    t = threading.Thread(target=check_for_stop)
    t.daemon = True
    t.start()

def press_servo():
    global key
    global servo0
    global servo1
    global s
    global up
    global shori
    #global svert
    
    #if(s == shori):
    #    servoX = servo1
    #else:
    #    servoX = servo0
    #print("press_servo")
    now = time()
    servoX = servo1 if s == shori else servo0
    servo_min = servo_minh if s==shori else servo_minv
    servo_max = servo_maxh if s==shori else servo_maxv
    if(now-key['first']<=.49 and servoX > servo_min and servoX < servo_max):
        #if(up):
        #    servoX = min(servo_max, servoX+1)
        #else:
        delta = 2
        servoX = min(servo_max,servoX+delta) if up else max(servo_min, servoX-delta)
        pwm.set_pwm(s, 0, servoX)
        if(s == shori):
            servo1 = servoX
        else:
            servo0 = servoX

        sleep(.05)
        t = threading.Thread(target=press_servo)
        t.daemon = True
        t.start()

def party_bot():
    robot.right(250)
    now = time()
    while(now - time() < 5):
        robot.set_light1(250)
        sleep(.5)
        robot.set_light1(0)
        sleep(.5)
    robot.stop()
    robot.set_light(0)

def set_speed_low():
    global speed
    global app

    app.frames[Testing].BD1.B2.config(relief=tk.SUNKEN)
    app.frames[Testing].BD1.B3.config(relief=tk.RAISED)
    app.frames[Testing].BD1.B4.config(relief=tk.RAISED)

    speed = 140

def set_speed_med():
    global speed

    app.frames[Testing].BD1.B2.config(relief=tk.RAISED)
    app.frames[Testing].BD1.B3.config(relief=tk.SUNKEN)
    app.frames[Testing].BD1.B4.config(relief=tk.RAISED)

    speed = 190

def set_speed_high():
    global speed

    app.frames[Testing].BD1.B2.config(relief=tk.RAISED)
    app.frames[Testing].BD1.B3.config(relief=tk.RAISED)
    app.frames[Testing].BD1.B4.config(relief=tk.SUNKEN)

    speed = 254

def set_light_low():
    global bright

    app.frames[Testing].BD2.B2.config(relief=tk.SUNKEN)
    app.frames[Testing].BD2.B3.config(relief=tk.RAISED)
    app.frames[Testing].BD2.B4.config(relief=tk.RAISED)

    bright = 10

def set_light_med():
    global bright

    app.frames[Testing].BD2.B2.config(relief=tk.RAISED)
    app.frames[Testing].BD2.B3.config(relief=tk.SUNKEN)
    app.frames[Testing].BD2.B4.config(relief=tk.RAISED)

    bright = 60

def set_light_high():
    global bright

    app.frames[Testing].BD2.B2.config(relief=tk.RAISED)
    app.frames[Testing].BD2.B3.config(relief=tk.RAISED)
    app.frames[Testing].BD2.B4.config(relief=tk.SUNKEN)

    bright = 250

def build_display():
    try:
        dataLink    = 'http://core.local/getinfo'
        data        = urllib.urlopen(dataLink)
        data        = data.read().decode('utf-8')
        data        = json.loads(data)

        #print(data)
    except:
        print('problem')
        exit()

    display = data

    return display

def update():
    global display

    display = build_display()
    app.frames[Testing].refresh(display)

    t           = threading.Timer(FS, update)
    t.daemon    = True
    t.start()

app = None
if __name__ == '__main__':

    check_for_stop()

    app = MainApp(display)
    app.bind('<KeyPress>', key_input)
    app.bind('<KeyRelease>', stop_bot)
    update()
    app.mainloop()
