#! /usr/bin/python
import EXbee

kk= EXbee.EXbee('/dev/ttyUSB0',9600)
kk.API=2
print "Response : " + kk.execute_at("SL")
