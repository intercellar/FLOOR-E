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


    #fix broke
    """
    lights1[0]  = 0;# 1
    lights2[3]  = 0;# 19
    lights5[3]  = 0;# 79
    lights6[14] = 0;# 90
    """

    lights  = [lights1,lights2,lights3,lights4,lights5,lights6]
    print(lights1)
    index   = -1
    for k in range(0,6):
        if(1 in lights[k]):
            index = lights[k].index(1)
            index = (15*k)+index+1
            break

    dist       = index
    pcb_val    = dist

    time.sleep(.25)
    t2 = threading.Thread(target=pcb_fun)
    t2.daemon = True
    t2.start()

    return pcb_val
