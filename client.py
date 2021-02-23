#!/bin/python3
import pygame
import time
from pygame.locals import *
import math

import os
import socket
import pickle
import threading
import ctypes
import sys

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
            while len(self.msg_sys) < 10:
                self.msg_sys += self.s.recv(10-len(self.msg_sys))
            size = int(self.msg_sys)

            self.msg_sys = self.s.recv(size)
            while len(self.msg_sys) < size: 
                self.msg_sys = self.s.recv(size - len(self.msg_sys))

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
Polygon [[[x, y]...], color, with]
"""
class Instruction():
    def __init__(self, Type, data):
        self.Type = Type
        self.data = data

class pictoChat():
    def __init__(self, window, ip, port = 3630):
        self.window = window
        s = socket.socket()
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        s.connect((ip, port))
        self.client = Server.Client(s)
        self.client.start()
        self.instructions = {
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
       
    def drawLigne(self, p1, p2, color, width = 1):
        pygame.draw.line(self.window, color, p1, p2, width)

    def drawRect(self, p1, p2, color):
        rect = Rect(p1, p2)
        pygame.draw.rect(self.window, color, rect)

    def drawCircle(self, p, color, r):
        pygame.draw.circle(self.window, color, p, r)

    def drawPolygon(self, points, color, width = 0):
        pygame.draw.polygon(self.window, color, points, width)

    def sendPoint(self, p, color):
        self.sendRect(p, [1, 1], color)

    def sendLigne(self, p1, p2, color, width = 1):
        self.client.send(Instruction("Ligne", [p1, p2, color, width]))

    def sendRect(self, p1, p2, color):
        rect = Rect(p1, p2)
        self.client.send(Instruction("Rect", [p1, p2, color]))

    def sendCircle(self, p, color, r):
        self.client.send(Instruction("Circle",[p, color, r]))

    def sendPolygon(self, points, color, width = 0):
        self.client.send(Instruction("Polygon", [points, color, width]))

pygame.init()
window_x = 800
window_y = 800
window = pygame.display.set_mode((window_x, window_y))

chat = 0
ip = "127.0.0.1"
if len(sys.argv) > 1:
    ip = sys.argv[1]

print(ip)
chat = pictoChat(window, ip, 3630)

if (chat == 0):
    print("connexion failed")
    exit(0)


for x in range(0, 1):
    chat.sendRect([100, 100], [100, 100], (255, 0, 0))
    chat.sendCircle([150, 100], (255, 0, 0), 30)
    chat.sendLigne([0, 0], [300, 300], (255, 255, 255), 5)
    chat.sendPoint([500, 500], (0, 0, 255))
    chat.sendPolygon([[400, 400], [500, 500], [350, 500], [350, 200]], (100, 100, 100), 0)

go = 1 #Main loop variable
T = time.time() #Define time varaible
mouse_prev_pos = (0, 0) #Previous coordinates of mouse
mouse_pos = (0, 0) #Original mouse position
current_tool = 0 # Define the current tool
while go:
    chat.display()
    for event in pygame.event.get(): #Loop on all pygame events
        if (event.type == QUIT): #User close his window
            os._exit(0)
        elif event.type == pygame.MOUSEBUTTONDOWN: #Print debug if mouse btn is pressed
            print(event)
            #chat.sendRect(event.pos, [10, 10], (0, 255, 0))
        elif event.type == pygame.KEYDOWN: #If any key is pressed
            if (event.key == pygame.K_a): # if Key 'a' is pressed
                current_tool = (current_tool + 1) % 2 #Change tool always inferior to 2
    
    buttons = pygame.mouse.get_pressed()
    mouse_prev_pos = mouse_pos
    mouse_pos = pygame.mouse.get_pos()
    if (buttons[0] == True):
        if (current_tool == 0): #If it's tool 1
            chat.sendCircle(mouse_pos, (255, 255, 255), 4) #Draw circle to pos
            chat.sendCircle(mouse_prev_pos, (255, 255, 255), 4) # Draw circle to old_pos
            chat.sendLigne(mouse_prev_pos, mouse_pos, (255, 255, 255), 9) #Draw a line between theses pos
        else: # Or tool 2
            chat.sendCircle(mouse_pos, (0, 0, 0), 20)
            chat.sendCircle(mouse_prev_pos, (0, 0, 0), 20)
            chat.sendLigne(mouse_prev_pos, mouse_pos, (0, 0, 0), 30)

    #Frame rate System
    T2 = time.time()-T
    if T2 < 1/60:
        time.sleep(1/60-T2)
    T = time.time()
    pygame.display.flip()

#End of program
print("exiting")
os._exit(0)
