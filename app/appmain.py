import os
import sys
import time
import threading
import math

import win10toast
import keyboard
import mouse

cur_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(cur_path + "/trackers")
sys.path.append(cur_path + "/util")

import bufferutil
import mathutil
import trackers

cfg = {}

class CarpalTunnelApp(object):
    def __init__(self):
        self.toaster = win10toast.ToastNotifier()

        self.closing = False
        self.run_delta = None

        self.run_thread = None
        self.run_callbacks = []
        self.keypress_callbacks = []
        self.mouse_callbacks = []

    def run_worker(self):
        while not self.closing:
            for callback in self.run_callbacks:
                callback(self.run_delta)
            time.sleep(self.run_delta)

    def register_run_callback(self, callback, delta):
        self.run_delta = delta if self.run_delta is None else mathutil.gcd(self.run_delta, delta)
        self.run_callbacks.append(callback)

    def on_keypress(self, event):
        for callback in self.keypress_callbacks:
            callback(event)

    def register_keypress_callback(self, callback):
        self.keypress_callbacks.append(callback)

    def on_mouse(self, event):
        for callback in self.mouse_callbacks:
            callback(event)

    def register_mouse_callback(self, callback):
        self.mouse_callbacks.append(callback)

    def start(self):
        self.closing = False
        keyboard.on_press(self.on_keypress)
        mouse.hook(self.on_mouse)
        self.run_thread = threading.Thread(target = self.run_worker)
        self.run_thread.start()

    def close(self):
        self.closing = True
        keyboard.unhook_all()
        mouse.unhook_all()
        self.run_thread.join()
        self.run_thread = None