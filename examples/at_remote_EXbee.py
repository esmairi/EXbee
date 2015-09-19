#! /usr/bin/python
import EXbee

kk= EXbee.EXbee('/dev/ttyUSB0',9600)
kk.API=2
print "Response : "+ kk.send_remote_at("SL","0013A2004071F023")
