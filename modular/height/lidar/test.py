#!/usr/bin/python

print('hello')

import serial, time

lidar = serial.Serial('/dev/serial0', baudrate=115200)

lidar.write(bytearray([0x42]))
lidar.write(bytearray([0x57]))
lidar.write(bytearray([0x02]))
lidar.write(bytearray([0x00]))
lidar.write(bytearray([0x00]))
lidar.write(bytearray([0x00]))
lidar.write(bytearray([0x01]))
lidar.write(bytearray([0x06]))

def get_byte():
    return list(bytearray(lidar.read()))[0]

while True:
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


        print('{} in'.format(val*.4))
