=========
XBee
=========

XBee provides an implementation of the Zigbee for XBee serial communication API , this 
is the first version v1.0 , it support the frame types (Zigbee) : 
  1- 0x10  Transmit Request
  2- 0x8b  Transmit Status
  3- 0x90  Receive Packet
  4- 0x08  AT Command
  5- 0x88  AA Command Response
  6- 0x17  Remote AT
  7- 0x97  Remote AT Command Response

It allows one to easily access advanced features of one or more XBee
devices from an application written in Python. 
An example use case might
look like this::

    #! /usr/bin/python
    import EXbee 
    kk= EXbee.EXbee('/dev/ttyUSB0',9600)
    kk.API=2
    response = kk.send_tx("Salam","0013A2004071E143")
    print response
    if response['Delivery_status'][:2] == "00":
      print "Frame sent with success"
    else:
      print "Failed"  
      
      
Installation
============

Extract the source code to your computer, then run the following command
in the root of the source tree::

    python setup.py install
    


Documentation
=============
To send a packet use the function send_tx
send_tx(self,data, long_addr , frame_id="01",addr_16="FFFE",broadcat_radius="00",options="00" , frame_type="10"):

Example:
#! /usr/bin/python
import EXbee 

kk= EXbee.EXbee('/dev/ttyUSB0',9600)
kk.API=2  # using API 2 if you want use API 1 replace it with kk.API=1 
response = kk.send_tx("Salam","0013A2004071F073","01")
print response
if response['Delivery_status'][:2] == "00":
	print "Frame sent with success"
else:
	print "Failed"


To wait for a packet use the function : read_rx
read_rx()
Example:

#! /usr/bin/python
import EXbee 

kk= EXbee.EXbee('/dev/ttyUSB0',9600)
kk.API=2
response = kk.read_rx()	
print "Sender:%s     " % response['SOURCE_ADDRESS_64'] 
print "Message: %s   " % response['DATA']

To execute AT command use the function: execute_at
execute_at(command)
Example:

#! /usr/bin/python
import EXbee

kk= EXbee.EXbee('/dev/ttyUSB0',9600)
print "Response : " + kk.execute_at("SL")


To execute a remote AT command use the function send_remote_at

Example:

#! /usr/bin/python
import EXbee
kk= EXbee.EXbee('/dev/ttyUSB0',9600)
print "Response : "+ kk.send_remote_at("SL","0013A2004071F073")



you will find examples in the examples dir :)


Dependencies
============
PySerial
