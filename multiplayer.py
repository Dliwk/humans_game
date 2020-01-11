from game_object import Player, Condition, GameObject
import pygame
import socket
import threading
from time import sleep

EVENT_KEY = 0
EVENT_SYNC = 1


class RemotePlayer(Player):
    def __init__(self, groups, pos, name, velocity, connection: socket.socket):
        super().__init__(groups, pos, name, velocity)
        self.conn = connection
        self.keys = [0, 0, 0, 0]  # Left, right, up, punch
        self.data_listener_thread = threading.Thread(target=self.data_listener, daemon=True)
        self.data_sender_thread = threading.Thread(target=self.data_sync_sender, daemon=True)
        self.data_listener_thread.start()
        self.data_sender_thread.start()

    def disconnected(self):
        pass

    def data_sync_sender(self):
        while True:
            try:
                data = bytes()
                data += EVENT_SYNC.to_bytes(1, 'little')  # Event type
                data += str(GameObject.center.rect.x - self.rect.x).encode()
                data += b';'
                data += str(GameObject.center.rect.y - self.rect.y).encode()
                data += b';'
                data += str(self.velocity[0]).encode()
                data += b';'
                data += str(self.velocity[1]).encode()
                data += b';'
                data += str(self.health_line.val).encode()
                self.conn.send(data)
                sleep(0.1)
            except:
                pass

    def data_listener(self):
        while True:
            try:
                game_packet = self.conn.recv(5)
                if game_packet == '':
                    self.disconnected()
                event_type = game_packet[0]
                if event_type == EVENT_KEY:
                    self.keys[0] = game_packet[1]
                    self.keys[1] = game_packet[2]
                    self.keys[2] = game_packet[3]
                    self.keys[3] = game_packet[4]
            except:
                pass

    def parse_input(self):
        if self.condition in (Condition.Died, Condition.Knockout):
            return
        if self.keys[3] and self.condition != Condition.Punching:
            self.punch_all()
        if self.keys[0] and self.velocity[0] > -10:
            self.velocity[0] -= 2
        if self.keys[1] and self.velocity[0] < 10:
            self.velocity[0] += 2
        if self.keys[2]:
            if self.onground:
                self.velocity[1] -= 15


class LocalRemotePlayer(Player):
    def __init__(self, groups, pos, name, velocity, keymap, connection: socket.socket):
        super().__init__(groups, pos, name, velocity)
        self.conn = connection
        self.keys = [0, 0, 0, 0]  # Left, right, up, punch
        self.data_listener_thread = threading.Thread(target=self.data_listener, daemon=True)
        self.data_sender_thread = threading.Thread(target=self.data_sender, daemon=True)
        # self.data_flush_thread = threading.Thread(target=lambda: self.conn.)
        self.data_listener_thread.start()
        self.data_sender_thread.start()
        self.keymap = keymap

    def disconnected(self):
        pass

    def data_sender(self):
        while True:
            try:
                data = bytes()
                data += EVENT_KEY.to_bytes(1, 'little')
                data += bytes(self.keys)
                self.conn.send(data)
                sleep(0.1)
            except:
                pass

    def data_listener(self):
        while True:
            try:
                game_packet = self.conn.recv(1024)
                event_type = game_packet[0]
                if event_type == EVENT_SYNC:
                    decoded = game_packet[1:].decode()
                    x, y, v1, v2, hv = decoded.split(';')
                    self.rect.x = GameObject.center.rect.x - float(x)
                    self.rect.y = GameObject.center.rect.y - float(y)
                    self.velocity[0] = float(v1)
                    self.velocity[1] = float(v2)
                    self.health_line.set(float(hv))
            except:
                pass

    def parse_input(self):
        self.keys[0] = pygame.key.get_pressed()[self.keymap[0]]
        self.keys[1] = pygame.key.get_pressed()[self.keymap[1]]
        self.keys[2] = pygame.key.get_pressed()[self.keymap[2]]
        self.keys[3] = pygame.key.get_pressed()[self.keymap[3]]
        # if self.condition in (Condition.Died, Condition.Knockout):
        #     return
        if self.keys[0] and self.velocity[0] > -10:
            self.velocity[0] -= 2
        if self.keys[1] and self.velocity[0] < 10:
            self.velocity[0] += 2
        if self.keys[2]:
            if self.onground:
                self.velocity[1] -= 15
        if self.keys[3] and self.condition != Condition.Punching:
            self.punch_all()
