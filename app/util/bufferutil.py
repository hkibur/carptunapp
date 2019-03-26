from __future__ import division

class RingBuffer(object):
    def __init__(self, length):
        self.buffer = [None] * int(length)
        self.length = length
        self.cursor = 0

    def inc(self, val):
        val += 1
        if val == self.length:
            val = 0
        return val

    def shift(self, val):
        self.buffer[self.cursor] = val
        self.cursor = self.inc(self.cursor)

    def append(self, val):
        self.shift(val)

    def __iter__(self):
        start_index = self.cursor
        if self.buffer[start_index] is not None: yield self.buffer[start_index]
        start_index = self.inc(start_index)
        while start_index != self.cursor:
            if self.buffer[start_index] is not None: yield self.buffer[start_index]
            start_index = self.inc(start_index)

    def __getitem__(self, val):
        if isinstance(val, slice):
            return list(self)[val.start : val.stop : val.step]
        else:
            return list(self)[val]

    def __len__(self):
        count = 0
        for elm in self.buffer:
            if elm is not None:
                count += 1
        return count

class MovingAverageBuffer(object):
    def __init__(self, length):
        self.buffer = [0] * int(length)
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