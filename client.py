#!/bin/python3
import pygame
import time
from pygame.locals import *
import math

import socket
import pickle
import threading
import ctypes


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
            self.s.send(bytes(f'{len(self.msg_send):<10}',"utf-8") + self.msg_send)

        def recv(self):
            self.msg_sys = self.s.recv(10)
            self.msg_sys = self.s.recv(int(self.msg_sys))
            self.msg.append(pickle.loads(self.msg_sys))
            return msg
        
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
        self.Type = ""
        self.data = []

class pictoChat():
    def __init__(self, ip, port = 3630):
        pygame.init()
        self.window_x = 800
        self.window_y = 800
        self.window = pygame.display.set_mode((self.window_x, self.window_y))
        s = socket.socket()
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        s.connect((ip, port))
        self.client = s
        self.instructions = {
            {"Point" : self.drawPoint},
            {"Ligne" : self.drawLigne}, 
            {"Rect" : self.drawRect}, 
            {"Circle" : self.drawCircle}, 
            {"Polygon" : self.drawPolygon}
        }

    def fetch(self):
        for msg in self.client.msg:
            try:
                self.instructions[msg.Type](msg.Type)
            except:
                print("failed to do instruction")
            

    def drawPoint(self, point, color):
        pass

    def drawLigne(self):
        pass

    def drawRect(self, p1, p2, color, send = 1):
        rect = Rect(p1, p2)
        pygame.draw.rect(self.window, color, rect)
        if send:
            self.client.send(Instruction("Rect", p1, p2, color))

    def drawCircle(self):
        pass

    def drawPolygon(self):
        pass




chat = pictoChat("127.0.0.1", 3630)

go = 1
while go:
    for event in pygame.event.get():
        if (event.type == QUIT):
            go = 0


print("exiting")
