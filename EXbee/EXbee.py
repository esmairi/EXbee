from serial import Serial
import binascii
import time
class EXbee:
	#port = '/dev/ttyUSB0'
	#baud = 9600
	#ser  
	START_BYTE="7E"
	ESCAPED_CHARACTER=["7E","7D","11","13"]
	delivery_status={   "00" :  "Success",
						"01" :  "MAC ACK Failure",
						"02" :  "CCA Failure",
						"15" :  "Invalid destination endpoint",
						"21" :  "Network ACK Failure",
						"22" :  "Not Joined to Network",
						"23" :  "Self-addressed",
						"24" :  "Address Not Found",
						"25" :  "Route Not Found",
						"26" :  "Broadcast source failed to hear a neighbor relay the message",
						"2B" :  "Invalid binding table index",
						"2C" :  "Resource error lack of free buffers, timers, etc",
						"2D" :  "Attempted broadcast with APS transmission",
						"2E" :  "Attempted unicast with APS transmission, but EE=0",
						"32" :  "Resource error lack of free buffers, timers, etc.",
						"74" :  "Data payload too large",
						"75" :  "Indirect message unrequested",
					}
	discovery_status={  "00" :  "No Discovery Overhead",
						"01" :  "Address Discovery",
						"02" :  "Route Discovery" ,
						"03" :  "Address and Route",
						"04" :  "Extended Timeout Discovery"
	
					 }				

	def __init__(self,port,baud):
		self.baud=baud
		self.port=port
		self.ser=Serial(self.port, self.baud)

	def add_hex2(self,hex1, hex2):
	    	return hex(int(hex1, 16) + int(hex2, 16))
    	
	def sub_hex2(self,hex1, hex2):
    		return hex(int(hex1, 16) - int(hex2, 16)) 
	# convert byte to hex
	def xor_hex(self,a,b):
		return '%x' % (int(a,16)^int(b,16))
	def toHex(self,s):
	        lst = []
	    	for ch in s:
        		hv = hex(ord(ch)).replace('0x', '')
        		if len(hv) == 1:
               			hv = '0'+hv
        		lst.append(hv)
		return reduce(lambda x,y:x+y, lst)
  	
	def add_bytes(self,byte):
		self.bytes.append(byte)

	def get_bytes(self):
		return self.bytes
##########################################################################
#########################################################################

##	READ DATA OVER RX

########################################################################
########################################################################
	# read the type and the length of incomming frame
	def read_frame_infos(self):
		wait=True
		self.bytes=[]
		length=0
		type_hex="00"
		if self.ser.isOpen:
			pass
		else:
			self.ser.open()
		while True:
			start_byte=self.ser.read()
			if self.toHex(start_byte).upper() == EXbee.START_BYTE:
				self.bytes.append(start_byte)
				i=1
				detect=False
				while i < 3 :
					cc=self.ser.read()
					self.bytes.append(cc)
					length_hex=""
					if self.toHex(cc).upper() in EXbee.ESCAPED_CHARACTER:
						detect=True
						continue
					else:
						if detect:
							length_hex+=self.xor_hex(self.toHex(cc),"20")
							detect=False
						else:	
							length_hex+=self.toHex(cc)
						i+=1

				length=int(length_hex,16)
				# read the type of frame
				type_byte=self.ser.read()
				self.bytes.append(type_byte)
				type_hex=self.toHex(type_byte)
				return {"length" : length , "frame_type" : type_hex}	
			else:
				time.sleep(0.01)
	# read incomming  RX Frame
	def read_rx_api(self,type):
		while True:
			infos = self.read_frame_infos()
			length=infos["length"]
			if infos["frame_type"] == type:
				while length > 0:
					byte=self.ser.read()
					self.bytes.append(byte)
					if not (self.toHex(byte).upper() in EXbee.ESCAPED_CHARACTER):
						length-=1	
				return self.bytes
			else:
				return "ERROR : received a Wrong frame !!! "

	def filter_frame(self):
		if self.toHex(self.bytes[0]).upper() !="7E" :
			return "ERROR invalid Frame"
		self.fields=["7E"]	 
		detect=False
		for j in range(1,len(self.bytes)) :
			byte = self.toHex(self.bytes[j]).upper()
			if byte in EXbee.ESCAPED_CHARACTER :
				detect=True
			else:
				if detect :
					self.fields.append(self.sub_hex2(byte,"20")[2:4])
					detect=False
				else:
					self.fields.append(byte)
		return self.fields		
	def export_rx(self):
		self.frame={}
		ss=""
		for c in self.fields :
			ss+=c
		self.frame['DELIMITER'] = ss[0:2]
		self.frame['LENGTH'] = int(ss[2:6],16)
		self.frame['FRAME_TYPE']= ss[6:8]
		self.frame['SOURCE_ADDRESS_64']= ss[8:24]
		self.frame['SOURCE_ADDRESS_16']=ss[24:28]
		self.frame['RECEIVE_OPTIONS']=ss[28:30]
		self.frame['DATA_HEX']=ss[30:len(ss) - 2]
		self.frame['DATA']= binascii.unhexlify(ss[30:len(ss) - 2])
		self.frame['CHECKSUM']=self.fields[len(ss)-2 : len(ss) ]

	def read_rx(self):
		while True:
			response = self.read_rx_api("90")
			if "ERROR" in response :
				print "Not RX Frame Received !!!! "	
			else :
				self.filter_frame()
				self.export_rx()
				return self.frame	


##########################################################################
#########################################################################

##	SEND DATA OVER TX
#
########################################################################
########################################################################
	
	def send_tx(self,data, long_addr , frame_id="01",short_addr="FFFE",broadcat_radius="00",options="00" , frame_type="10"):
		length=14+len(data)
		data_hex=self.toHex(data)
		frame=[]
		frame.append("7E")
		frame.append(format(length,'04x'))
		frame.append(frame_type)
		frame.append(frame_id)
		frame.append(long_addr)
		frame.append(short_addr)
		frame.append(broadcat_radius)
		frame.append(options)
		frame.append(data_hex.upper())
		# clacul checksum
		total=frame_type;
		total=self.add_hex2(frame_id,total)[2:4]
		for i in xrange(0,len(long_addr),2):
		    total=self.add_hex2(long_addr[i:i+2],total)[2:]    
		total=self.add_hex2(short_addr[0:2],total)[2:]
		total=self.add_hex2(short_addr[2:4],total)[2:]
		total=self.add_hex2(broadcat_radius,total)[2:]
		total=self.add_hex2(options,total)[2:]
		for i in xrange(0,len(data_hex),2):
			total=self.add_hex2(data_hex[i:i+2],total)[2:]
		ss=total[len(total)-2:len(total)]
		checksum=self.sub_hex2("FF",ss).upper()

		frame.append(checksum[2:4])
		frame2=[]
		frame2.append("7E")
 		for i in xrange(1,len(frame)-1):
 			fr_i=frame[i]
 			for j in xrange(0,len(fr_i),2):
 				if (fr_i[j:j+2] == "7D" or fr_i[j:j+2] == "7E" or fr_i[j:j+2] == "11" or fr_i[j:j+2] == "13") and self.API == 2:
					frame2.append("7D")
					frame2.append(self.xor_hex("20",fr_i[j:j+2]))
				else:
					frame2.append(fr_i[j:j+2])
		
		frame2.append(checksum[2:4])
		
		ss=""
		for c in frame2:
			ss=ss+c
		self.ser.write(binascii.unhexlify(ss))

		time.sleep(0.01)	
		cc=self.ser.read(11)
		ds=""
		discov_s=""
		try:
			ds=str(self.toHex(cc[8])) + "( "+ self.delivery_status[str(self.toHex(cc[8])).upper()] +" )";
		except :
			ds=	str(self.toHex(cc[8]))
		try:
			discov_s=str(self.toHex(cc[9])) + "( "+ self.discovery_status[str(self.toHex(cc[9])).upper()] +" )";
		except:
			discov_s=str(self.toHex(cc[9]))		
		#ds=self.toHex(cc[8]) 
		return {"Start_delimiter" : self.toHex(cc[0]),
				"Length" : self.toHex(cc[1:3]),
				"Frame_type" : self.toHex(cc[3]),
				"Frame_id" : self.toHex(cc[4]),
				"des.address_16-bit" : self.toHex(cc[5:7]),
				"Retry_count" : self.toHex(cc[7]),
				"Delivery_status" : ds,
				"Discovery_status" : discov_s,
				 "Checksum" : self.toHex(cc[10])
				}
		self.ser.close()	

##########################################################################
#########################################################################

##	AT COMMAND
#
########################################################################
########################################################################


	def execute_at(self,command,param="",frame_id="01"):
		if len(command) != 2:
			return  "Error : verify the Command AT !!!!"
		else:
		
			frame_at=["7E"]
			length=str(format(4+len(param),"04x"))
			frame_at.append(length[0:2])
			frame_at.append(length[2:4])
			frame_at.append("08")
			frame_at.append(frame_id)
			frame_at.append(self.toHex(command)[0:2])
			frame_at.append(self.toHex(command)[2:4])
			if len(param) > 0:
				for i in range(0,len(self.toHex(param)),2):
					pp=self.toHex(param)[i:i+2]
					frame_at.append(pp)
			checksum="00"
 			frame=[]
			for i in range(1,len(frame_at) ):
				fr_i=frame_at[i]
				for j in range(0,len(fr_i),2):
					if (fr_i[j:j+2] == "7D" or fr_i[j:j+2] == "7E" or fr_i[j:j+2] == "11" or fr_i[j:j+2] == "13") and self.API == 2:
						frame.append("7D")
						frame.append(self.xor_hex("20",fr_i[j:j+2]))
					else:
						frame.append(fr_i[j:j+2])

					if i > 2:
						checksum=self.add_hex2(fr_i[j:j+2],checksum)

			checksum=self.sub_hex2("FF",checksum[len(checksum)-2 : len(checksum)])[2:4]
			frame.append(checksum)
			
			ss="7E"
			for c in frame:
				ss=ss+c
			self.ser.write(binascii.unhexlify(ss))
			time.sleep(0.01)
			return self.response_at()

	def response_at(self):
		while True:
			self.read_rx_api("88")
			status=self.toHex(self.bytes[7])
			if status == "00" :
				response=""
				for i in range(8,len(self.bytes)-1) :
					response+=self.toHex(self.bytes[i])
				return response	
			else:
				return "Invalid AT command !!!!!"	
			


	def send_remote_at(self,command,adress ,param="",dest_16="FFFE",frame_id="01"):
		if not self.ser.isOpen():
			self.ser.open()
		if len(command) != 2:
			return  "Error : verify the Command AT !!!!"
		else:
		
			frame_at=[]
			ll=5+len(param)+len(adress)/2+len(dest_16)/2
			length=str(format(ll,"04x"))
			frame_at.append(length[0:2])
			frame_at.append(length[2:4])
			frame_at.append("17")
			frame_at.append(frame_id)
			for i in xrange(0,len(adress),2) :
				frame_at.append(adress[i:i+2])
			frame_at.append(dest_16[0:2])
			frame_at.append(dest_16[2:4])
			frame_at.append("02")
			
			frame_at.append(self.toHex(command)[0:2])
			frame_at.append(self.toHex(command)[2:4])
			if len(param) > 0:
				for i in range(0,len(self.toHex(param)),2):
					pp=self.toHex(param)[i:i+2]
					frame_at.append(pp)
			checksum="00"
 			frame=[]
			for i in range(0,len(frame_at) ):
				fr_i=str(frame_at[i])
				for j in range(0,len(fr_i),2):
					if fr_i[j:j+2] in EXbee.ESCAPED_CHARACTER and self.API == 2:
						frame.append("7D")
						frame.append(self.xor_hex("20",fr_i[j:j+2]))
					else:
						frame.append(fr_i[j:j+2])

					if i > 1:
						checksum=self.add_hex2(fr_i[j:j+2],checksum)

			checksum=self.sub_hex2("FF",checksum[len(checksum)-2 : len(checksum)])[2:4]
			frame.append(checksum)
			ss="7E"
			for c in frame:
				ss=ss+c
			self.ser.write(binascii.unhexlify(ss))
			time.sleep(0.01)
			return self.response_remote_at()
			
	def response_remote_at(self):
		while True:
			self.read_rx_api("97")
			status=self.toHex(self.bytes[19])
			if status == "00" :
				response=""
				for i in range(20,len(self.bytes)-1) :
					response+=self.toHex(self.bytes[i])
				return response	
			else:
				return "ERROR !!!!!"					


 
