#!/usr/bin/python

from functions import *

t2 = threading.Thread(target=pcb_fun)
t2.daemon = True
t2.start()

while True:
    #lid = round(random(),2)
    #pcb = round(random(),2)
    #acc = round(random(),2)

    pcb = get_vals()
    print(pcb)
    pcb = round(pcb, 4)

    sleep(.5)
