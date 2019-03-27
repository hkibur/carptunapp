from __future__ import division
import Tkinter as tk
import ttk
import sys

import appmain
import trackers
import mathutil

class LineGraph(tk.LabelFrame):
    def __init__(self, parent, coord_list, thresh, **kwargs):
        tk.LabelFrame.__init__(self, parent, **kwargs)
        self.coord_list = coord_list
        self.thresh = thresh
        self.graph_x_axis_offset = 20
        self.graph_y_axis_offset = 40
        self.graph_x_steps = 10
        self.graph_y_steps = 10
        self.graph_step_line_len = 5

        self.graph = tk.Canvas(self, relief = tk.GROOVE, width = "25c", height = "9c")
        self.graph.pack(side = tk.TOP)

    def update_graph(self, *args, **kwargs):
        if len(self.coord_list) == 0:
            return
        x_pixel_range = self.graph.winfo_width() - (self.graph_y_axis_offset * 2)
        y_pixel_range = self.graph.winfo_height() - (self.graph_x_axis_offset * 2)
        y_list = [avg for _, avg in self.coord_list]
        x_time_min = self.coord_list[0][0]
        x_time_max = self.coord_list[-1][0]
        y_time_min = min(y_list)
        y_time_max = max(y_list)
        x_step = (x_time_max - x_time_min) / self.graph_x_steps
        y_step = (y_time_max - y_time_min) / self.graph_y_steps
        thresh_y = (y_pixel_range - (((self.thresh - y_time_min) / (y_time_max - y_time_min + sys.float_info.epsilon)) * y_pixel_range)) + self.graph_x_axis_offset

        self.graph.delete(tk.ALL)

        prev_pos_x = self.graph_y_axis_offset
        prev_pos_y = self.graph_x_axis_offset + y_pixel_range
        for sec, avg in self.coord_list:
            pos_x = (((sec - x_time_min) / (x_time_max - x_time_min + sys.float_info.epsilon)) * x_pixel_range) + self.graph_y_axis_offset
            pos_y = (y_pixel_range - (((avg - y_time_min) / (y_time_max - y_time_min + sys.float_info.epsilon)) * y_pixel_range)) + self.graph_x_axis_offset
            if prev_pos_y >= thresh_y and pos_y < thresh_y:
                inter_point_x, inter_point_y = mathutil.point_on_line_intersect_y((prev_pos_x, prev_pos_y), (pos_x, pos_y), thresh_y)
                self.graph.create_polygon((inter_point_x, inter_point_y), (pos_x, pos_y), (pos_x, thresh_y), fill = "green")
            elif prev_pos_y < thresh_y and pos_y <= thresh_y:
                self.graph.create_polygon((prev_pos_x, prev_pos_y), (pos_x, pos_y), (pos_x, thresh_y), (prev_pos_x, thresh_y), fill = "green")
            elif prev_pos_y < thresh_y and pos_y > thresh_y:
                inter_point_x, inter_point_y = mathutil.point_on_line_intersect_y((prev_pos_x, prev_pos_y), (pos_x, pos_y), thresh_y)
                self.graph.create_polygon((prev_pos_x, prev_pos_y), (inter_point_x, thresh_y), (prev_pos_x, thresh_y), fill = "green")
            self.graph.create_line(prev_pos_x, prev_pos_y, pos_x, pos_y, fill = "blue")
            prev_pos_x = pos_x
            prev_pos_y = pos_y

        self.graph.create_line(self.graph_y_axis_offset, self.graph_x_axis_offset + y_pixel_range, self.graph_y_axis_offset + x_pixel_range, self.graph_x_axis_offset + y_pixel_range) #X axis
        self.graph.create_line(self.graph_y_axis_offset, self.graph_x_axis_offset + y_pixel_range, self.graph_y_axis_offset, self.graph_x_axis_offset) #Y axis
        
        for i in xrange(self.graph_x_steps + 1):
            start_x = ((x_pixel_range // self.graph_x_steps) * i) + self.graph_y_axis_offset
            start_y = self.graph_x_axis_offset + y_pixel_range
            self.graph.create_line(start_x, start_y, start_x, start_y + self.graph_step_line_len)
            self.graph.create_text(start_x, start_y + self.graph_step_line_len, anchor = tk.NW, text = str(round(x_time_min + (x_step * i), 2)))

        for i in xrange(self.graph_y_steps + 1):
            start_x = self.graph_y_axis_offset
            start_y = (y_pixel_range - ((y_pixel_range // self.graph_y_steps) * i)) + self.graph_x_axis_offset
            self.graph.create_line(start_x, start_y, start_x - self.graph_step_line_len, start_y)
            self.graph.create_text(start_x - self.graph_step_line_len, start_y, anchor = tk.SE, text = str(round(y_time_min + (y_step * i))))

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
        tk.Button(header_cont, text = "Update Graphs", command = self.update_graphs).pack(side = tk.LEFT)

        self.wpm_tracker = trackers.KeyboardWpmTracker(app_inst = inst, time_frame = 120, smoothing = 2, rate = 2)
        self.keyboard_graph = LineGraph(self, self.wpm_tracker.wpm_buffer, thresh = self.wpm_tracker.wpm_thresh, text = "Keyboard WPM")
        self.keyboard_graph.pack()

        self.mousemove_tracker = trackers.MouseDistanceActivityTracker(app_inst = inst, time_frame = 120, smoothing = 1, rate = 0.25)
        self.mousemove_graph = LineGraph(self, self.mousemove_tracker.movement_buffer, thresh = 700, text = "Mouse Distance")
        self.mousemove_graph.pack()

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

    def update_graphs(self):
        self.keyboard_graph.update_graph()
        self.mousemove_graph.update_graph()

app = appmain.CarpalTunnelApp()

root = tk.Tk()
CarpalTunnelGui(root, app).pack(expand = tk.YES, fill = tk.BOTH)
root.mainloop()