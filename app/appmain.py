import os
import sys
import time
import threading

import win10toast
import pythoncom
import pyHook

cur_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(cur_path + "/trackers")
sys.path.append(cur_path + "/util")

import keyboard_tracker

cfg = {}

class CarpalTunnelApp(object):
    def __init__(self):
        self.trackers = [keyboard_tracker.KeyboardTracker]
        self.trackers_initialized = False

        self.toaster = win10toast.ToastNotifier()

        self.closing = False
        self.pump_delta = 0.01
        self.run_delta = 1

        self.pump_thread = None
        self.run_thread = None

    def pump_worker(self):
        for tracker in self.trackers:
            tracker.initialize()
        self.trackers_initialized = True

        while not self.closing:
            pythoncom.PumpWaitingMessages()
            time.sleep(self.pump_delta)

        for tracker in self.trackers:
            tracker.uninitialize()
        self.trackers_initialized = False

    def run_worker(self):
        while not self.trackers_initialized: pass

        last_time = time.time()
        while not self.closing:
            for tracker in self.trackers:
                tracker.gen_run(self.run_delta)
            time.sleep(self.run_delta)

    def start(self):
        self.closing = False
        self.pump_thread = threading.Thread(target = self.pump_worker)
        self.pump_thread.start()
        self.run_thread = threading.Thread(target = self.run_worker)
        self.run_thread.start()

    def close(self):
        self.closing = True
        self.pump_thread.join()
        self.pump_thread = None
        self.run_thread.join()
        self.run_thread = None