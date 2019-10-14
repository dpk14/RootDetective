import statistics

from scipy.interpolate import UnivariateSpline
from scipy.signal import argrelextrema

from src.tools.back_end import models
from src.tools.back_end.line import Curve
import numpy as np
import src.tools.back_end.file_toolkit as tools

MAX = 255
START_IN_HOURS = 24
MM_PER_PIXEL = 0.3688212927756654

def find_root_curves(data, hrs_per_pixel):
    (midline_curve, full_curve) = create_curves(data=data, hrs_per_pixel=hrs_per_pixel)
    tilt_axis = find_tilt_axis(midline_curve)
    midline_curve = tilt_line(midline_curve, tilt_axis)
    full_curve = tilt_line(full_curve, tilt_axis)
    smoothed_midline = UnivariateSpline(midline_curve.x_vec, midline_curve.y_vec)
    smoothed_midline_curve = Curve(midline_curve.x_vec, smoothed_midline(midline_curve.x_vec))
    amplitude_curve = find_ampitude_curve(full_curve, smoothed_midline_curve)
    return CurvePair(full_curve=full_curve, amplitude_curve=amplitude_curve)

def create_curves(data, hrs_per_pixel):
    shape = data.shape
    row = shape[0]
    col = shape[1]
    midpoint_line_x = []
    midpoint_line_y = []
    full_line_x = []
    full_line_y = []
    for x in range(row):
        y_sum = 0
        point_count = 0
        for y in range(col):
            if data.item((x, y)) == tools.PIXEL_MAX:
                y_sum+=y
                point_count+=1
                full_line_x.append(x)
                full_line_y.append(y)
        if point_count is not 0:
            y_avg = y_sum / point_count
            midpoint_line_x.append(x)
            midpoint_line_y.append(y_avg)
    curve_midline = Curve(midpoint_line_x, midpoint_line_y)
    full_curve = Curve(full_line_x, full_line_y)
    for curve in curve_midline, full_curve:
        for index in range(curve.range):
            curve.x_vec[index] = curve.x_vec[index]*hrs_per_pixel + START_IN_HOURS
            curve.y_vec[index] = curve.y_vec[index]*MM_PER_PIXEL
        curve.initialize_map()
    return (curve_midline, full_curve)

def find_ampitude_curve(full_curve, smoothed_midline_curve):
    mins = []
    maxes = []
    for x in smoothed_midline_curve.x_vec:
        y_tuple = full_curve.get_y_at(x)
        mins.append(min(y_tuple))
        maxes.append(max(y_tuple))
    local_max_indices = argrelextrema(np.array(maxes), np.greater)[0]
    local_min_indices = argrelextrema(np.array(mins), np.less)[0]
    x_to_amp = map_x_and_amp(extrema_indices=local_min_indices, extrema=mins, smoothed_midline_curve=smoothed_midline_curve)
    x_to_amp = map_x_and_amp(extrema_indices=local_max_indices, extrema=maxes, smoothed_midline_curve=smoothed_midline_curve, x_to_amp=x_to_amp)
    x_vec = x_to_amp.keys()
    x_vec = sorted(x_vec)
    amplitudes = []
    x_vec_with_duplicates = []
    for x in x_vec:
        amp_vals = x_to_amp[x]
        for amp in amp_vals:
            x_vec_with_duplicates.append(x)
            amplitudes.append(amp)
    amplitudes = remove_noise(amplitudes)
    amplitude_curve = Curve(x_vec_with_duplicates, amplitudes)
    return amplitude_curve

def remove_noise(amplitudes):
    std = np.std(amplitudes)
    mean = np.mean(amplitudes)
    for index in range(len(amplitudes)):
        if amplitudes[index] >= mean + 2*std:
            amplitudes[index] = mean + std
        elif amplitudes[index] <= mean - 2*std:
            amplitudes[index] = mean - std
    return amplitudes

def map_x_and_amp(extrema_indices, extrema, smoothed_midline_curve, x_to_amp={}):
    for index in extrema_indices:
        x = smoothed_midline_curve.x_vec[index]
        furthest_sweep = extrema[index]
        root_center = smoothed_midline_curve.get_y_at(x)[0]
        amplitude = furthest_sweep - root_center
        if x not in x_to_amp:
            x_to_amp[x] = []
        x_to_amp[x].append(amplitude)
    return x_to_amp

def find_tilt_axis(curve):
    x_vals = []
    y_vals = []
    point_count = 0
    for index in range(curve.range):
        x = curve.x_vec[index]
        y = curve.y_vec[index]
        x_vals.append(x)
        y_vals.append(y)
        point_count += 1
    y_tilt = np.poly1d(np.polyfit(x_vals, y_vals, 1))(np.unique(x_vals))  # finds y_vals of tilted axis
    tilt_axis = Curve(x_vals, y_tilt)
    return tilt_axis

def tilt_line(midline_curve, tilt_axis):
    tilted_y_vals = []
    tilted_x_vals = []
    for index in range(len(tilt_axis.x_vec)):
        tilt_offset = tilt_axis.y_vec[index]
        x = tilt_axis.x_vec[index]
        y_vals = midline_curve.get_y_at(x)
        for y in y_vals:
            tilted_x_vals.append(x)
            tilted_y_vals.append(y - tilt_offset)
    tilted_curve = Curve(tilted_x_vals, tilted_y_vals)
    return tilted_curve

def no_root():
    no_curve = Curve([], [])
    return CurvePair(full_curve=no_curve, amplitude_curve=no_curve)

def generate_additional_stats(curve_pair):
    amp_curve = curve_pair.amplitude_curve
    if amp_curve.range == 0:
        germinated = False
        avg_amplitude = "N/A"
    else:
        germinated = True
        amplitudes = amp_curve.y_vec
        abs_amplitudes = map(abs, amplitudes)
        avg_amplitude = statistics.mean(abs_amplitudes)
    return AdditionalStats(germinated=germinated, average_amplitude=avg_amplitude)

#Classes
class CurvePair:
    def __init__(self, full_curve, amplitude_curve):
        self.full_curve = full_curve
        self.amplitude_curve = amplitude_curve

class AdditionalStats:
    def __init__(self, germinated, average_amplitude):
        self.germinated = germinated
        self.average_amplitude = average_amplitude

class DataPackage:
    def __init__(self, curve_pair, additional_stats):
        self.curve_pair = curve_pair
        self.additional_stats = additional_stats