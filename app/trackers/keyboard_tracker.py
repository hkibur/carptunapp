from __future__ import division
import threading
import time

import pythoncom
import pyHook

import tracker
import movingaverage

class KeyboardTracker(tracker.Tracker):
    def __init__(self, global_cfg):
        self.char_stream = []
        self.avg_buffer = movingaverage.MovingAverageBuffer(10)
        self.avg_history = [] #(delta, average)

    def key_handler(self, event):
        self.char_stream.append(event.Ascii)

    def run(self, delta):
        words = 0
        for i in range(len(self.char_stream))[1:]:
            if i == 1 and self.char_stream[i - 1] == 32:
                words += 1
                continue
            if self.char_stream[i] == 32 and self.char_stream[i - 1] > 32:
                words += 1
        self.char_stream = []
        self.avg_buffer.add((words / delta) * 60.0)
        timestamp = delta + self.avg_history[-1][0] if len(self.avg_history) > 0 else delta
        self.avg_history.append((timestamp, self.avg_buffer.get_average()))

KeyboardTracker.pyhook_manager.KeyDown = KeyboardTracker.gen_key_handler