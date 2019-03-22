from __future__ import division

class MovingAverageBuffer(object):
    def __init__(self, length):
        self.buffer = [0] * length
        self.length = length
        self.sum = 0
        self.cursor = 0

    def add(self, val):
        self.sum -= self.buffer[self.cursor]
        self.sum += val
        self.buffer[self.cursor] = val
        self.cursor += 1
        if self.cursor == self.length:
            self.cursor = 0

    def get_average(self):
        return self.sum / self.length