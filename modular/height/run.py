#!/usr/bin/python

from functions import *

try:
    t1 = threading.Thread(target=lidar_fun)
    t1.daemon = True
    t1.start()

    t2 = threading.Thread(target=pcb_fun)
    t2.daemon = True
    t2.start()
    #print("start")

    t3 = threading.Thread(target=acc_fun)
    t3.daemon = True
    t3.start()

    while True:
        #lid = round(random(),2)
        #pcb = round(random(),2)
        #acc = round(random(),2)

        (lid, pcb, acc) = get_vals()
        print(lid, pcb, acc)
        lid = round(lid, 4)
        pcb = round(pcb, 4)
        acc = round(acc, 4)

        try:
            write_height(lid, pcb, acc)
        except:
            pass

        sleep(1.5)

except KeyboardInterrupt:
    print('control c')

except:
    print('unknown')
finally:
    GPIO.cleanup()
