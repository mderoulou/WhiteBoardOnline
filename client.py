#!/bin/python3
import pygame
import time
from pygame.locals import *
import math

import socket
import pickle
import threading
import ctypes

ip_list = [3630, 3640, 3650, 4242, 5050]

class Server(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.clients = [] # array of Clients
        self.clients_sockets = [] # array of socket
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.bind(("", port))
        self.listen_socket.listen(16)
        self.go = True


    def run(self):
        while self.go:
            s = self.listen_socket.accept()
            print(s[1])
            s = s[0]
            self.clients_sockets.append(s)
            print("connection to "+ str(s))
            c = self.Client(s)
            self.clients.append(c)
            c.start()

    def stop(self):
        for client in self.clients:
            client.stop()
        self.go = False
        self.listen_socket.shutdown(socket.SHUT_WR)
        print("stop server")

    class Client(threading.Thread):
        def __init__(self, socket):
            threading.Thread.__init__(self)
            self.s = socket
            self.msg = []
            self.go = True


        def run(self):
            while self.go:
                self.recv()

        def send(self, data):
            data = pickle.dumps(data)
            self.s.send(bytes(f'{len(data):<10}',"utf-8") + data)

        def recv(self):
            self.msg_sys = self.s.recv(10)
            
            self.msg_sys = self.s.recv(int(self.msg_sys))
            print("rcvd")
            self.msg.append(pickle.loads(self.msg_sys))
        
        def stop(self):
            self.go = False
            print("stop client " + s)
            self.s.shutdown(socket.SHUT_WR)
        
"""
Point [[x, y], color]
Ligne [[x, y], [x, y], color, with]
Rect [[x, y], [x, y], color]
Circle [[x, y], color, with]
Polygon [[[x, y]...], color]
"""
class Instruction():
    def __init__(self, Type, data):
        self.Type = Type
        self.data = data

class pictoChat():
    def __init__(self, ip, port = 3630):
        pygame.init()
        self.window_x = 800
        self.window_y = 800
        self.window = pygame.display.set_mode((self.window_x, self.window_y))
        s = socket.socket()
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        s.connect((ip, port))
        self.client = Server.Client(s)
        self.client.start()
        self.T = time.time()
        self.instructions = {
            "Point" : self.drawPoint,
            "Ligne" : self.drawLigne, 
            "Rect" : self.drawRect, 
            "Circle" : self.drawCircle, 
            "Polygon" : self.drawPolygon
        }

    def display(self):
        #fetch drawing
        while len(self.client.msg):
            msg = self.client.msg.pop(0)
            try:
                self.instructions[msg.Type](*msg.data)
            except:
                print("failed to do instruction")

        #pygame events
        for event in pygame.event.get():
            if (event.type == QUIT):
                os._exit(0)

        #wait for the frame
        T2 = time.time()-self.T
        if T2 < 1/60:
            time.sleep(1/60-T2)
        self.T = time.time()
        pygame.display.flip()
       

    def drawPoint(self, data, send = 1):
        pass

    def drawLigne(self, data, send = 1):
        pass

    def drawRect(self, p1, p2, color, send = 1):
        #p1, p2, color, send = data
        rect = Rect(p1, p2)
        pygame.draw.rect(self.window, color, rect)

    def drawCircle(self, data, send = 1):
        pass

    def drawPolygon(self, data, send = 1):
        pass

    def sendPoint(self, data, send = 1):
        pass

    def sendLigne(self, data, send = 1):
        pass

    def sendRect(self, p1, p2, color, send = 1):
        rect = Rect(p1, p2)
        self.client.send(Instruction("Rect", [p1, p2, color]))

    def sendCircle(self, data, send = 1):
        pass

    def sendPolygon(self, data, send = 1):
        pass

chat = 0
chat = pictoChat("127.0.0.1", 3630)
#for port in ip_list:
#    try:
#        chat = pictoChat("127.0.0.1", port)
#        break
#    except:
#        pass

if (chat == 0):
    print("connexion failed")
    exit(0)

chat.sendRect([100, 100], [100, 100], (255, 0, 0))

go = 1
while go:
    chat.display()

print("exiting")
os._exit(0)
