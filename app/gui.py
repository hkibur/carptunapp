from __future__ import division
import Tkinter as tk
import ttk
import sys

import appmain

import keyboard_tracker

class KeyboardTrackerGui(tk.LabelFrame, keyboard_tracker.KeyboardTracker):
    def __init__(self, parent, cfg):
        tk.LabelFrame.__init__(self, parent, text = "Keyboard Tracker")
        keyboard_tracker.KeyboardTracker.__init__(self, cfg)
        self.graph_x_axis_offset = 20
        self.graph_y_axis_offset = 40
        self.graph_x_steps = 10
        self.graph_y_steps = 10
        self.graph_step_line_len = 5

        self.status_label = tk.Label(self, text = "Status: Uninitialized")
        self.status_label.pack(side = tk.TOP)

        self.wpm_label = tk.Label(self, text = "Current WPM: %d" % (self.avg_buffer.get_average()))
        self.wpm_label.pack(side = tk.TOP)

        self.expand_graph_button = tk.Button(self, text = "Expand Graph", command = self.expand_graph)
        self.expand_graph_button.pack(side = tk.TOP)

        self.graph = tk.Canvas(self, relief = tk.GROOVE, width = "15c", height = "10c")
        self.graph.pack(side = tk.TOP)

    def update_graph(self):
        if len(self.avg_history) == 0:
            return
        x_pixel_range = self.graph.winfo_width() - (self.graph_y_axis_offset * 2)
        y_pixel_range = self.graph.winfo_height() - (self.graph_x_axis_offset * 2)
        x_time_max = self.avg_history[-1][0]
        avg_list = [avg for _, avg in self.avg_history]
        y_time_min = min(avg_list)
        y_time_max = max(avg_list)
        x_step = x_time_max / self.graph_x_steps
        y_step = (y_time_max - y_time_min) / self.graph_y_steps

        self.graph.delete(tk.ALL)

        prev_pos_x = self.graph_y_axis_offset
        prev_pos_y = self.graph_x_axis_offset + y_pixel_range
        for sec, avg in self.avg_history:
            pos_x = ((sec / x_time_max) * x_pixel_range) + self.graph_y_axis_offset
            pos_y = (y_pixel_range - (((avg - y_time_min) / (y_time_max - y_time_min + sys.float_info.epsilon)) * y_pixel_range)) + self.graph_x_axis_offset
            self.graph.create_line(prev_pos_x, prev_pos_y, pos_x, pos_y, fill = "blue")
            prev_pos_x = pos_x
            prev_pos_y = pos_y

        self.graph.create_line(self.graph_y_axis_offset, self.graph_x_axis_offset + y_pixel_range, self.graph_y_axis_offset + x_pixel_range, self.graph_x_axis_offset + y_pixel_range) #X axis
        self.graph.create_line(self.graph_y_axis_offset, self.graph_x_axis_offset + y_pixel_range, self.graph_y_axis_offset, self.graph_x_axis_offset) #Y axis
        
        for i in xrange(self.graph_x_steps + 1):
            start_x = ((x_pixel_range // self.graph_x_steps) * i) + self.graph_y_axis_offset
            start_y = self.graph_x_axis_offset + y_pixel_range
            self.graph.create_line(start_x, start_y, start_x, start_y + self.graph_step_line_len)
            self.graph.create_text(start_x, start_y + self.graph_step_line_len, anchor = tk.NW, text = str(x_step * i))

        for i in xrange(self.graph_y_steps + 1):
            start_x = self.graph_y_axis_offset
            start_y = (y_pixel_range - ((y_pixel_range // self.graph_y_steps) * i)) + self.graph_x_axis_offset
            self.graph.create_line(start_x, start_y, start_x - self.graph_step_line_len, start_y)
            self.graph.create_text(start_x - self.graph_step_line_len, start_y, anchor = tk.SE, text = str(y_time_min + (y_step * i)))

    def run(self, delta):
        keyboard_tracker.KeyboardTracker.run(self, delta)
        self.wpm_label.config(text = "Current WPM: %d" % (self.avg_buffer.get_average()))
        if self.expand_graph_button["text"] == "Collapse Graph":
            self.update_graph()

    def init_hook(self):
        self.status_label.config(text = "Status: Initialized")

    def uninit_hook(self):
        self.status_label.config(text = "Status: Uninitialized")

    def expand_graph(self):
        self.graph.pack(side = tk.TOP)
        self.expand_graph_button.config(text = "Collapse Graph", command = self.collapse_graph)
        self.update_graph()

    def collapse_graph(self):
        self.graph.pack_forget()
        self.expand_graph_button.config(text = "Expand Graph", command = self.expand_graph)

class TrackerGui(tk.Frame):
    def __init__(self, parent, inst):
        tk.Frame.__init__(self, parent)
        self.open_grid_index = 0
        self.width = 4

        self.tracker_cont = tk.Frame(self)
        self.tracker_cont.pack()

        add_frame = tk.Frame(self)
        add_frame.pack(side = tk.BOTTOM)
        self.tracker_type_combo = ttk.Combobox(add_frame, values = ["KeyboardTracker"])
        self.tracker_type_combo.pack(side = tk.LEFT)
        self.tracker_type_combo.current(0)
        tk.Button(add_frame, text = "Add", command = self._add_tracker).pack(side = tk.LEFT)

    def add_tracker(self, cls_name):
        new_tracker = eval(cls_name + "Gui")(self.tracker_cont, appmain.cfg)
        new_tracker.grid(row = self.open_grid_index // self.width, column = self.open_grid_index % self.width)
        self.open_grid_index += 1

    def _add_tracker(self):
        self.add_tracker(self.tracker_type_combo.get())

class CarpalTunnelGui(tk.Frame):
    def __init__(self, parent, inst):
        tk.Frame.__init__(self, parent)
        self.inst = inst

        header_cont = tk.Frame(self)
        header_cont.pack(side = tk.TOP, fill = tk.X)
        self.init_button = tk.Button(header_cont, text = "Start", command = self.init)
        self.init_button.pack(side = tk.LEFT)
        self.status_label = tk.Label(header_cont, text = "Status: Closed")
        self.status_label.pack(side = tk.LEFT)

        tracker_cont = tk.LabelFrame(self, text = "Trackers")
        tracker_cont.pack(fill = tk.X)
        self.tracker_frame = TrackerGui(tracker_cont, self.inst)
        self.tracker_frame.pack()

    def init(self):
        self.status_label.config(text = "Status: Starting")
        self.update_idletasks()
        self.inst.start()
        self.status_label.config(text = "Status: Running")
        self.init_button.config(text = "Close", command = self.uninit)

    def uninit(self):
        self.status_label.config(text = "Status: Closing")
        self.update_idletasks()
        self.inst.close()
        self.status_label.config(text = "Status: Closed")
        self.init_button.config(text = "Start", command = self.init)

app = appmain.CarpalTunnelApp()

root = tk.Tk()
CarpalTunnelGui(root, app).pack(expand = tk.YES, fill = tk.BOTH)
root.mainloop()