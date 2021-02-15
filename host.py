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

ip_list = [3630, 3640, 3650, 4242, 5050]

class Server(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.clients = [] # array of Clients
        self.clients_sockets = [] # array of socket
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            pass
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
            self.msg.append(pickle.loads(self.msg_sys))
        
        def stop(self):
            self.go = False
            print("stop client " + s)
            self.s.shutdown(socket.SHUT_WR)


"""
Point [[x, y], color]
Ligne [[x, y], [x, y], color, width]
Rect [[x, y], [x, y], color]
Circle [[x, y], color, width]
Polygon [[x, y],...] color width
"""
class Instruction():
    def __init__(self, Type, data):
        self.Type = Type
        self.data = data

class pictoChatServer():
    def __init__(self, window, port = 3630):
        self.window = window
        self.server = Server(port)
        self.server.start()
        self.instructions = {
            "Ligne" : self.drawLigne, 
            "Rect" : self.drawRect, 
            "Circle" : self.drawCircle, 
            "Polygon" : self.drawPolygon
        }

    def display(self):
        #fetch and send drawing
        for client in self.server.clients:
            while len(client.msg):
                msg = client.msg.pop(0)
                try:
                    self.instructions[msg.Type](*msg.data)
                    self.sendToAll(msg)
                except:
                    print("failed to do instruction" + str(msg))
        
    def sendToAll(self, instruction):
        for client in self.server.clients:
            try:
                client.send(instruction)
            except:
                pass
    def drawLigne(self, p1, p2, color, width = 1):
        pygame.draw.line(self.window, color, p1, p2, width)

    def drawRect(self, p1, p2, color):
        rect = Rect(p1, p2)
        pygame.draw.rect(self.window, color, rect)

    def drawCircle(self, p, color, r):
        pygame.draw.circle(self.window, color, p, r)

    def drawPolygon(self, points, color, width = 0):
        pygame.draw.polygon(self.window, color, points, width)


pygame.init()
window_x = 800
window_y = 800
window = pygame.display.set_mode((window_x, window_y))

chat = 0
chat = pictoChatServer(window, 3630)

if (chat == 0):
    print("connexion failed")
    exit(0)

go = 1
T = time.time()
while go:
    chat.display()
    for event in pygame.event.get():
        if (event.type == QUIT):
            os._exit(0)

    #wait for the frame
    T2 = time.time()-T
    if T2 < 1/60:
        time.sleep(1/60-T2)
    T = time.time()
    pygame.display.flip()

server.stop()
print("exiting")
os._exit(1)