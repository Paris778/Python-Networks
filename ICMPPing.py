#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import os
import sys
import struct
import time
import select
import binascii


ICMP_ECHO_REQUEST = 8  # ICMP type code for echo request messages
ICMP_ECHO_REPLY = 0  # ICMP type code for echo reply messages

HOST = "lancaster.ac.uk"
PORT = 123

def checksum(string):

    csum = 0

    countTo = (len(string) // 2) * 2

    count = 0

    while count < countTo:

        thisVal = string[count+1] * 256 + string[count]

        csum = thisVal + csum

        csum = csum & 0xffffffff

        count = count + 2

        if countTo < len(string):

            csum = csum + string[len(string) - 1]

            csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)

    csum = csum + (csum >> 16)

    answer = ~csum

    answer = answer & 0xffff

    answer = answer >> 8 | (answer << 8 & 0xff00)

    answer = socket.htons(answer)

    return answer


def createPacket(id):
    # """Create a new echo request packet based on the given "id"."""

    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, id, 1)
    data = 0
    # Calculate the checksum on the data and the dummy header.
    my_checksum = checksum(header+data)
    # Now that we have the right checksum, we put that in. It's just easier
    # to make up a new header than to stuff it into the dummy.
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0,
                         socket.htons(my_checksum), id, 1)
    return header + data


def receiveOnePing(icmpSocket, destinationAddress, ID, timeout,start):
	# 1. Wait for the socket to receive a reply
    # while not icmpSocket.recv(4096):
	#	sleep(0.1)

	#print("In receive one ping")
	
	data,address = icmpSocket.recvfrom(1024)
	#data = select.select([icmpSocket], [],[], timeout)

	header = data[20:28]

	#while data is None:
	#data = icmpSocket.recv(4096)
	#	print("in while loop... ")
	# 2. Once received, record time of receipt, otherwise, handle a timeout
	end = time.time()
	# 3. Compare the time of receipt to time of sending, producing the total network delay
	delay = (end - start)
	# 4. Unpack the packet header for useful information, including the ID
	#print("Packet received: ")
	#print(data)
	# 5. Check that the ID matches between the request and reply
	# 6. Return total network delay

	type, code, checksum, packetID, sequence = struct.unpack("bbHHh", header)
        # Filters out the echo request itself.
        # This can be tested by pinging 127.0.0.1
        # You'll see your own request
	if type != 8 and packetID == ID:
		#print("Correct")
        # bytesInDouble = struct.calcsize("d")
        # timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
		return delay
	return 0

def sendOnePing(icmpSocket, destinationAddress, ID):
	# 1. Build ICMP header
	header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, ID, 1)
	#print("Packet about to be sent: ")
	#print(header)
	data = struct.pack('d',1234)
	#print( "Address in SoP: " + destinationAddress)
	# 2. Checksum ICMP packet using given function
	my_checksum = checksum(header + data)
	# 3. Insert checksum into packet ????
	header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0,my_checksum, ID, 1)
	# 4. Send packet using socket
	#icmpSocket.connect((HOST, PORT))
	packet = header + data 
	icmpSocket.sendto(packet,(destinationAddress,1))
	# 5. Record time of sending
	start = time.time()
	return start
	
def doOnePing(destinationAddress, timeout,id): 
	# 1. Create ICMP socket
	icmpSocket1 = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
	#my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
	# 2. Call sendOnePing function
	start = sendOnePing(icmpSocket1, destinationAddress , id)
	# 3. Call receiveOnePing function
	timeout=1
	delay = receiveOnePing(icmpSocket1, destinationAddress , id, timeout,start)
	print("Delay: ")
	print( delay)
	# 4. Close ICMP socket
	icmpSocket1.close()
	# 5. Return total network delay
	return delay
	
	
def ping(host, timeout=1):
	# 1. Look up hostname, resolving it to an IP address
	addr = socket.gethostbyname(host)
	#print( "Address: " + addr)
	# 2. Call doOnePing function, approximately every second 
	 # & 3. Print out the returned delay
	print("=======================================================================")
	id = 1
	sum = 0
	average = 0
	max = 0
	min = 20

	while True:
		try:
			print("Ping ", id)
			time.sleep(1)
			delay = doOnePing(HOST, timeout,id)
			if(delay < min):
				min = delay
			if(delay > max):
				max = delay
			sum += delay
			average = sum/id

			id+=1
			
		except KeyboardInterrupt:
			print("\n=======================================================================")
			print("\nFinal Report")
			print("Minimum Ping: ",min)
			print("Maximum Ping: ", max)
			print("Average Ping: ", average)
			print("\nProgram Terminated...")
			print("\n=======================================================================")
			break
		print("=======================================================================")
	

ping(HOST)

