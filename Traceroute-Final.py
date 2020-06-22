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

#Function to take user input
def takeUserInput():

    HOST = "lancaster.ac.uk"
    PORT = 1024
    userInput = 2
    timeout = 5
    maxHops =15
    
    while True:
        print("=====================================================================================================")
        print("    CHOOSE ONE OF THE FOLLOWING NUMBERED OPTIONS")
        print("=====================================================================================================")
        print("(1) Start Traceroute Program")
        print("(2) Change Destination Address" )
        print("(3) Change Port Number")
        print("(4) Change Timeout")
        print("(5) Change Number of max hops")
        print("(6) EXIT ")
        print("=====================================================================================================")
        print(" - Current Destination Address: ", HOST)
        print(" - Current Port Number: ", PORT)
        print(" - Current Timeout: ", timeout)
        print(" - Current Max Hops: ", maxHops)
        print("=====================================================================================================")

        userInput = input("Please make a choice ...\n")

        if userInput == '1':
            doTreceroute(PORT, HOST, 1, maxHops, 3,timeout)
            #break
        elif userInput == '2':
            HOST = input("Enter new Destination address\n")
        elif userInput == '3':
            PORT = int(input("Enter new Port Number\n"))
        elif userInput == '4':
            timeout = int(input("Enter new Timeout\n"))
        elif userInput == '5':
            maxHops = int(input("Enter new number of Maximum Hops\n"))
        elif userInput == '6':
            print("Terminating program ...")
            break
        else:
            print("Sorry, input was not recognised...\nTry a number from one to six")

# Get protocols

icmp = socket.getprotobyname("icmp")

udp = socket.getprotobyname("udp")

#Checksum function
def checksum(string):

    csum = 0

    countTo = (len(string) // 2) * 2

    count = 0

    while count < countTo:

        thisVal = string[count+1] * 256 + string[count]

        csum = csum + thisVal

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


# 1. Make treceroute function


def doTreceroute(PORT, HOST, ttl, MAX_HOPS, attemptsPossible,timeoutTime):

    print("=====================================================================================================")
    print("|  Node   |               Host Name            | Host Address  | Delay(ms)")
    print("=====================================================================================================")

    temp = ttl

    keepGoing = False


    failedPackets = 0
    noPackets = 0

    try:
        # print("2.")
        address = socket.gethostbyname(HOST)

    except Exception as hostException:
        print("ERROR !!! Host not found...")

        return

   
    timeLeft = 2

    while True:

        icmpSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        icmpSocketReceive = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        # Initialise keepGoing and attemptsPossible

        noPackets += 1

        attempt = attemptsPossible

        keepGoing = False

        timeout = struct.pack("ll", timeoutTime, 0)

        # Make sockets
        icmpSocket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        icmpSocketReceive.setsockopt(
            socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)

        icmpSocketReceive.bind(("", PORT))

        header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, 1, 1)

        data = struct.pack('d', 1234)

        my_checksum = checksum(header + data)

        header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, my_checksum, 1, 1)

        packet = header + data

        start = time.time()

        icmpSocket.sendto(packet, (address, PORT))

        while not keepGoing:
            startedSelect = time.time()

            try:

                whatReady = select.select([icmpSocketReceive], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []:  # Timeout
                    print("  *        *        *    Request timed out.")
                data, addr = icmpSocketReceive.recvfrom(1024)
                addr = addr[0]
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    print("  *        *        *    Request timed out.")

                keepGoing = True

                try:

                    currentAddr = socket.gethostbyaddr(addr)[0]

                except socket.error:

                    addr = currentAddr

            except socket.error:

                attempt -= 1

                #print("* ")

        end = time.time()

        icmpSocket.close()
        icmpSocketReceive.close()

        # print("5.5")

        header = data[20:28]

        ttl += 1

        type, code, checkSum, packetID, sequence = struct.unpack("bbHHh", header)

        delay = (end - start) * 1000

        try:
            name = socket.gethostbyaddr(addr)[0]

        except:
            name = addr

        print("%4d %40s %15s %8.4f ms " % (ttl-1, name, addr, delay))

        if(addr == address):
            print("Destination Reached Succesfully !!!")
            break

        if(ttl >= MAX_HOPS):
            break

        if code == 3:

            ttl += 1
            print("ERROR type 3 : Unreachable Port")
            failedPackets+=1
            break

        if code == 2:
            ttl += 1
            print("ERROR type 2 : Unreachable Protocol")
            failedPackets += 1
            break
    fails = ((noPackets-failedPackets)/noPackets)*100
    print("PACKET SUCCESS RATE: ", fails, "%")
    print("=====================================================================================================")

# print("1.")
takeUserInput()
