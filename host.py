#!/bin/python3
import pygame
import time
from pygame.locals import *
import math

import os, sys
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
Polygon [points, color, width]
"""
class Instruction():
    def __init__(self, Type, data):
        self.Type = ""
        self.data = []
    
class pictoChat():
    def __init__(self):
        pygame.init()
        self.window_x = 800
        self.window_y = 800
        self.window = pygame.display.set_mode((window_x, window_y))

    def drawPoint(self, data):
        pygame.draw.rect(self.window, color, rect)

    def drawLigne(self, data):
        pass

    def drawRect(self, data):
        pass

    def drawCircle(self, data):
        pass

    def drawPolygon(self, data):
        pass



server = Server(port=3630)
server.start()

pygame.init()
window_x = 800
window_y = 800
window = pygame.display.set_mode((window_x, window_y))

go = 1
while go:
    for event in pygame.event.get():
        if (event.type == QUIT):
            go = 0

    for client in server.clients:
        while len(client.msg) > 0:
            print(client.msg.pop(0))
            
server.stop()
os._exit(1)
print("exiting")