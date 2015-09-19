#! /usr/bin/python
import EXbee 

kk= EXbee.EXbee('/dev/ttyUSB0',9600)
kk.API=2
response = kk.read_rx()	
print "Sender:%s     " % response['SOURCE_ADDRESS_64'] 
print "Message: %s   " % response['DATA']
