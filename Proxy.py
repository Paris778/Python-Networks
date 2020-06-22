#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import socket
import select
import socketserver
import sys
import signal
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from signal import signal, SIGPIPE, SIG_DFL
import logging

#Command:::     curl lancaster.ac.uk --proxy 127.0.0.1:1024
#  curl captive.apple.com --proxy 127.0.0.1:1024
#  curl neverssl.com --proxy 127.0.0.1:1024
#  curl msftconnecttest.com --proxy 127.0.0.1:1024

class cashedData():
    allData = []
    def __init__(self,url,data):
       self.url = url
       self.data = data
       self.__class__.allData.append(self)
       print("Appended : ", self.url)
    

class Proxy():

    def __init__(self, receivePort):
        # Split address on dot. Defaut operation
        msg=("\n\n=====================\n  NEW SESSION\n=====================\n")
        makeLog(msg)
        self.host = ""
        self.listeningPort = receivePort
        signal(SIGPIPE, SIG_DFL)


        #self.sendPort = sendPort
        #self.contentDirectory = '/'
        #httpd = server_class(serverAddress, handler_class)

    def startServer(self):
    
        self.ListenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SendSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        #Binding to ports
        try:
            msg = "Proxy listening on port: %5d  " %  (self.listeningPort)
            makeLog(msg)
            print("Proxy listening on ", ":", self.listeningPort)
            self.ListenSocket.bind((self.host, self.listeningPort))
            print("Proxy succesfully started on port  ", self.listeningPort)

        except Exception as e:
            msg = "Error: Failed to bind to listening port %5d  " % (self.listeningPort)
            makeLog(msg)
            print("Error: Failed to bind to listening port   ", self.listeningPort)
            sys.exit(1)

        # Listening for proxy requests
        self.ListenSocket.listen(5)
        
        while True:
            #Get client info
            msg = ("Awaiting client request ... ")
            makeLog(msg)
            print("Awaiting client request ... ")
            try:
                (client, address) = self.ListenSocket.accept()
                #client.settimeout(60)

                msg = ("Recieved connection from %40s" % (str(address)))
                makeLog(msg)
                print("Recieved connection from ", address)
                # 4. When a connection is accepted, call handleRequest function, passing new connection socket (see https://docs.python.org/3/library/socket.html#socket.socket.accept)
                self.handleRequest(client,address)
                # 5. Close server socket
            except KeyboardInterrupt:
                self.ListenSocket.close()

    def handleRequest(self, client,address):

        CONSTANT_PACKET_SIZE = 2048

        print("CLIENT: ", client)
        print("ADDRESS: ", address)
        data = None
        dataDecoded = None
        #get connection from browser
        data = client.recv(CONSTANT_PACKET_SIZE)
        dataDecoded = data.decode()
        
        if data == None:
            msg = ("ERROR: Recieved NULL data")
            makeLog(msg)
            print("ERROR: Recieved NULL data")
            sys.exit(1)
        
        print("Successfuly received data ... ")
        msg = ("Successfuly received data from client" )
        makeLog(msg)
        firstLine = dataDecoded.split('\n')[0]
        print("FIRST LINE: ", firstLine)
        # get url
        url = firstLine.split(' ')[1]
        msg = ("URL FOUND: %45s " % (url))
        makeLog(msg)
        print("URL FOUND: ", url)
        http_pos = url.find("://")  # find pos of ://
        print("HTTP Position : ", http_pos)


        if (http_pos == -1):
            temp = url
        else:
            temp = url[(http_pos+3):]  # get the rest of url

        port_pos = temp.find(":")  # find the port pos (if any)

        # find end of web server
        webserver_pos = temp.find("/")
        if webserver_pos == -1:
            webserver_pos = len(temp)
        
        webserver = ""
        port = -1
        if (port_pos == -1 or webserver_pos < port_pos):
            # default port
            port = 80
            webserver = temp[:webserver_pos]
            msg = ("WEB-SERVER : %45s " % (webserver))
            makeLog(msg)
            print("WEB-SERVER : ", webserver)


        else:  # specific port
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos]
        
       
        #Check whether data is available from cached
        if(isInCashed(webserver,client)):
            print("Data found in cache...\nSending cached data to client...")
            msg = ("Data found in cache...")
            makeLog(msg)
            msg = ("Sending cached data to client...")
            makeLog(msg)
        else:
    
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(60)
            msg = ("Connecting to host %s, port %s" % (webserver, port))
            makeLog(msg)
            print("Connecting to host %s, port %s" % (webserver, port))
            s.connect((webserver, port))
            s.sendall(data)
            
            s.setblocking(0)

            keepGoing = True
            while True:
                # receive data from web server

                msg = ("Waiting to receive...")
                makeLog(msg)
                print("Waiting to receive...")

                ready = select.select([s], [], [], 3)
                if ready[0]:
                    data = s.recvfrom(CONSTANT_PACKET_SIZE)[0]
                else:
                    keepGoing = False 
                if (len(data) > 0):
                    # send to browser/client
                    client.send(data)
                    msg = ("Successfuly sent proxy data to %30s" % client)
                    makeLog(msg)
                    print("Successfuly sent proxy data to client.. ")    
                    newEntry = cashedData(webserver,data)
                    msg = ("Successfuly cashed website... ")
                    makeLog(msg)
                    print("Successfuly cashed website... ")
                    if(not keepGoing):
                        break
                else:
                    msg = ("ERROR: Failed to send proxy data ")
                    makeLog(msg)
                    print("ERROR: Failed to send proxy data ")
                    break
            

def isInCashed(webserver, client):
    for entry in cashedData.allData:
        print("Comparing : ", entry.url , " with ", webserver)
        if(entry.url == webserver):
            client.send(entry.data)
            return True
    print("Not found in cache")
    return False
                


def takeUserInput():

    PORT = 8000
    userInput = 2

    while True:
        print("=====================================================================================================")
        print("    CHOOSE ONE OF THE FOLLOWING NUMBERED OPTIONS")
        print("=====================================================================================================")
        print("(1) Start Proxy Server")
        print("(2) Change Port Number")
        print("(3) EXIT ")
        print("=====================================================================================================")
        print(" - Current Port Number: ", PORT)
        print("=====================================================================================================")

        userInput = input("Please make a choice ...\n")

        if userInput == '1':
            proxyServer = Proxy(PORT)
            proxyServer.startServer()
        elif userInput == '2':
            PORT = int(input("Enter new Port Number\n"))
        elif userInput == '3':
            print("Terminating program ...")
            break

def makeLog(message):
    
    text_file = open("log.txt", "a")

    timeNow = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    date = 'Date: {now}'.format(now=timeNow)
    #string = "%25s :: %30s \n" % (date,message)
    string = '{0:25s} :: {1:30s}\n'.format(date,message)
    text_file.write(string)
    #text_file.close()
    
# main
def main():
    takeUserInput()


main()
