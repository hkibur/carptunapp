from __future__ import division
import time

import mouse

import bufferutil
import mathutil

class Tracker(object):
    def __init__(self):
        self.delta_acc = 0

    def pre_run(self, delta):
        self.delta_acc += delta
        if self.delta_acc >= self.rate:
            self.run(self.delta_acc)
            self.delta_acc = 0

class KeyboardWpmTracker(Tracker):
    def __init__(self, app_inst, time_frame, smoothing, rate):
        Tracker.__init__(self)
        self.time_frame = time_frame
        self.smoothing = smoothing
        self.rate = rate
        self.thresh = 70

        self.char_buffer = []
        self.smoothing_buffer = bufferutil.MovingAverageBuffer(smoothing / rate)
        self.wpm_buffer = bufferutil.RingBuffer(time_frame / rate)

        app_inst.register_keypress_callback(self.keypress)
        app_inst.register_run_callback(self.pre_run, rate)

    def keypress(self, event):
        if len(event.name) == 1:
            self.char_buffer.append(ord(event.name))
        elif event.name == "space":
            self.char_buffer.append(ord(" "))
        elif event.name == "backspace" and len(self.char_buffer) > 0:
            self.char_buffer.pop()

    def run(self, delta):
        words = 0
        for i in range(len(self.char_buffer))[1:]:
            if i == 1 and self.char_buffer[i - 1] == 32:
                words += 1
                continue
            if self.char_buffer[i] == 32 and self.char_buffer[i - 1] > 32:
                words += 1

        self.char_buffer = []
        self.smoothing_buffer.add((words / delta) * 60.0)
        timestamp = delta + self.wpm_buffer[-1][0] if len(self.wpm_buffer) > 0 else delta
        self.wpm_buffer.append((timestamp, self.smoothing_buffer.get_average()))

class MouseDistanceActivityTracker(Tracker):
    def __init__(self, app_inst, time_frame, smoothing, rate):
        Tracker.__init__(self)
        self.time_frame = time_frame
        self.smoothing = smoothing
        self.rate = rate
        self.thresh = 70

        self.smoothing_buffer = bufferutil.MovingAverageBuffer(smoothing / rate)
        self.movement_buffer = bufferutil.RingBuffer(time_frame / rate)
        self.last_xy = None
        self.inter_dist = 0

        app_inst.register_mouse_callback(self.mousemove)
        app_inst.register_run_callback(self.pre_run, rate)

    def mousemove(self, event):
        if not isinstance(event, mouse.MoveEvent): return
        if self.last_xy is None:
            self.last_xy = (event.x, event.y)
            return
        last_x, last_y = self.last_xy
        distance = mathutil.pythag(event.x - last_x, event.y - last_y)
        self.last_xy = (event.x, event.y)
        self.inter_dist += distance

    def run(self, delta):
        self.smoothing_buffer.add(self.inter_dist)
        self.inter_dist = 0
        timestamp = delta + self.movement_buffer[-1][0] if len(self.movement_buffer) > 0 else delta
        self.movement_buffer.shift((timestamp, self.smoothing_buffer.get_average()))