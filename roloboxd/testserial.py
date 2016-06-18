import serial

while True:
	try:
		ser = serial.Serial('/dev/ttyAMA0', 9600)
		ser.write(b'hello\n')
	except KeyboardInterrupt:
		pass

	ser.close()
