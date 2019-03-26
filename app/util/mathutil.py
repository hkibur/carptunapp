from __future__ import division
import math

def gcd(a,b):
    while b > 0:
        a, b = b, a % b
    return a

def pythag(a, b):
    return math.sqrt(a ** 2 + b ** 2)

def point_on_line_intersect_y(start_vec, end_vec, inter_y):
    start_x, start_y = start_vec
    end_x, end_y = end_vec
    inv_slope = (end_x - start_x) / (end_y - start_y)
    fin_x = start_x + (inv_slope * (inter_y - start_y))
    return (fin_x, inter_y)

def graph_integral(points, thresh, x_weight, y_weight):
    total_area = 0
    prev_x = 0
    prev_y = 0
    for point in points:
        x, y = point
        x *= x_weight
        y *= y_weight
        if prev_y <= thresh and y > thresh:
            inter_x, _ = point_on_line_intersect_y((prev_x, prev_y), (x, y), thresh)
            total_area += (x - inter_x) * (y - thresh) / 2
        elif prev_y > thresh and y <= thresh:
            inter_x, _ = point_on_line_intersect_y((prev_x, prev_y), (x, y), thresh)
            total_area += (inter_x - prev_x) * (prev_y - thresh) / 2
        elif prev_y > thresh and y > thresh:
            total_area += (x - prev_x) * (((prev_y + y) / 2) - thresh)
    return total_area