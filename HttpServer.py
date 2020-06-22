#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import socket
import socketserver
import sys
import signal
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler


# Command: wget 127.0.0.1:8000/index.html

def threaded(function):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=function, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

def takeUserInput():

    userInput = 2
    host = "127.0.0.1"
    port = 8000

    while True:
        print("=====================================================================================================")
        print("    CHOOSE ONE OF THE FOLLOWING NUMBERED OPTIONS")
        print("=====================================================================================================")
        print("(1) Start Http web server")
        print("(2) Change Destination Address")
        print("(3) Change Port Number")
        print("(4) EXIT ")
        print("=====================================================================================================")
        print(" - Current Host Address: ", host)
        print(" - Current Port Number: ", port)
        print("=====================================================================================================")

        userInput = input("Please make a choice ...\n")

        if userInput == '1':
            server = HttpServer(host,port)
            server.startServer()
            pass
        elif userInput == '2':
            host = input("Enter a new Destination address\n")
        elif userInput == '3':
            port = int(input("Enter a new Port Number\n"))
        elif userInput == '4':
            print("Terminating program ...")
            break


class HttpServer( ):

    #Constructor
    def __init__(self, host, serverPort):
        # Split address on dot. Defaut operation
        self.host = host
        self.port = serverPort
        #httpd = server_class(serverAddress, handler_class)

    def startServer(self):
        # 1. Create server socket
        print("=========================================================")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 2. Bind the server socket to server address and server port
        try:
            print("Starting server on ", self.host, ":", self.port)
            
            #self.socket.connect(self.host, self.port)
            
            self.socket.bind((self.host, self.port))
            print("Server succesfully started on port  ", self.port)

        except Exception as e:
            print("Error: Failed to bind to port   ", self.port)
            #self.shutdown()
            sys.exit(1)

        # 3. Continuously listen for connections to server socket
        
        #Listening on port 8000
        self.socket.listen(5)
        
        while True:
            print("=========================================================")
            print("Awaiting client request ... ")
            (client, address) = self.socket.accept()
            client.settimeout(10)
            print("Recieved connection from ", address)
            
            #func_to_be_threaded(self):
            #thread = threading.Thread(target=self.handleRequest,args=(client))
            #thread.start()
            self.handleRequest(client)
            print("=========================================================")
            
        
        # 5. Close server socket
        self.socket.close()

    @threaded
    def handleRequest(self, client):

        PACKET_SIZE = 1024

        while True:
            print("CLIENT: ", client)
            data = None
            data = client.recv(PACKET_SIZE).decode()

            if data == None:
                break

            requestMethod = data.split(' ')[0]
            print("Method: ", requestMethod)
            print("Request data: ", data)

            # 3. Read the corresponding file from disk
            if requestMethod == "GET" or requestMethod == "HEAD":
                fileRequested = data.split(' ')[1]
                fileRequested = fileRequested.split('?')[0]
                if fileRequested == "/":
                    fileRequested = "index.html"

                filePath = fileRequested[1:]
                print("Serving request of path: ", filePath)

                try:

                    file = open(filePath, 'rb')
                    
                    if requestMethod == "GET":
                        responseData = file.read()
                    file.close()
                    respondHeader = self.makeHeader(200)
                except Exception as error:
                    print(error)
                    print("File not found. Error 404.")
                    respondHeader = self.makeHeader(404)
                    if requestMethod == "GET":
                        responseData = "<html><head>ERROR 404</head></html>"

                response = respondHeader.encode()
                #responseData = bytes(responseData, 'utf-8')
                #responseData = responseData.encode()

                if requestMethod == "GET" :
                    response = response + responseData
                    
                # 6. Send the content of the file to the socket
                client.send(response)
                # 7. Close the connection socket
                client.close()
                break
            else:
                print("ERROR: We're sorry, wrong HTTP request method")
            
            
                
    def makeHeader(self, code):
        
        header = ''
        if code == 200:
            header += 'HTTP/1.1 200 OK\n'
        elif code == 404:
            header += 'HTTP/1.1 404 Not Found\n'

        time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        header += 'Date: {now}\n'.format(now=time_now)
        header += 'Server: SCC-203 Server\n'
        # Signal that connection will be closed after completing the request
        header += 'Connection: close\n\n'
        return header
            
                
def main():

    takeUserInput()
    
main()
