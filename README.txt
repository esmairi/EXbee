=========
XBee
=========

XBee provides an implementation of the Zigbee for XBee serial communication API , this 
is the first version v1.0 , it support the frame type: 
  1- 0x10  Transmit Request
  2- 0x8b  Transmit Status
  2- 0x90  Receive Packet
  2- 0x08  AT Command
  3- 0x88  AA Command Response
  3- 0x17  Remote AT
  4- 0x97  Remote AT Command Response

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




you will find examples in the examples dir :)


Dependencies
============
PySerial
