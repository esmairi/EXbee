#! /usr/bin/python
import EXbee 

kk= EXbee.EXbee('/dev/ttyUSB0',9600)
kk.API=2
response = kk.send_tx("Salam","0013A2004071F023","02")
print response
if response['Delivery_status'][:2] == "00":
	print "Frame sent with success"
else:
	print "Failed"	
