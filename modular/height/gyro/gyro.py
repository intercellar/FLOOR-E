
#!/usr/bin/python
import smbus
import math

#Register
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

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

bus = smbus.SMBus(1)
address = 0x68

#german comment
bus.write_byte_data(address, power_mgmt_1,0)

print("Gyroscop")

gyro_xout = read_word_2c(0x43)
gyro_yout = read_word_2c(0x45)
gyro_zout = read_word_2c(0x47)

print "xout: ", ("%5d" % gyro_xout), " scaled: ", (gyro_xout / 131)
print "yout: ", ("%5d" % gyro_yout), " scaled: ", (gyro_yout / 131)
print "zout: ", ("%5d" % gyro_zout), " scaled: ", (gyro_zout / 131)

print "accel"

acx = read_word_2c(0x3b)
acy = read_word_2c(0x3d)
acz = read_word_2c(0x3f)

acx_scaled = acx/16384.0
acy_scaled = acy/16384.0
acz_scaled = acz/16384.0
	
print "acx: ", ("%6d" % acx), " scaled: ", (acx_scaled)
print "acy: ", ("%6d" % acy), " scaled: ", (acy_scaled)
print "acz: ", ("%6d" % acz), " scaled: ", (acz_scaled)

xrot = get_x_rotation(acx_scaled, acy_scaled, acz_scaled)
yrot = get_y_rotation(acx_scaled, acy_scaled, acz_scaled) 

xrot *=  (90/85)
yrot *=  (90/45)
xrot -= -.935
yrot -= -1.885
print "X Rotation: ", xrot
print "Y Rotation: ", yrot



