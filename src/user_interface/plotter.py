import matplotlib
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

FIGWIDTH = 10
FIGHEIGHT = 3.75
TITLE_SIZE = 10
LABEL_SIZE = 9

def graph_curve_pair(curve_pair, root_num, fig_width=FIGWIDTH, fig_height=FIGHEIGHT):
    fig = Figure(figsize=(fig_width, fig_height))

    root_graph_axis = fig.add_subplot(121)
    root_graph_axis.plot(curve_pair.full_curve.x_vec, curve_pair.full_curve.y_vec)
    root_graph_axis.set_title("Horizontal Displacement vs. Time for Root " + str(root_num), fontsize=TITLE_SIZE)
    root_graph_axis.set_ylabel("Horizontal Displacement (mm)", fontsize=LABEL_SIZE)
    root_graph_axis.set_xlabel("Time Since Root Emergence (Hours)", fontsize=LABEL_SIZE)

    amp_graph_axis = fig.add_subplot(122)
    amp_graph_axis.plot(curve_pair.amplitude_curve.x_vec, curve_pair.amplitude_curve.y_vec)
    amp_graph_axis.set_title("Root Tip Rotational Amplitude vs. Time for Root " + str(root_num), fontsize=TITLE_SIZE)
    amp_graph_axis.set_ylabel("Rotational Amplitude (mm)", fontsize=LABEL_SIZE)
    amp_graph_axis.set_xlabel("Time Since Root Emergence (Hours)", fontsize=LABEL_SIZE)

    return fig

def graph_curves(all_curves):
    curve_num = len(all_curves)
    fig, axes = plt.subplots(curve_num, 2)
    row = 0
    for key in all_curves.keys():
        curve_pair = all_curves[key]
        axes[row, 0].plot(curve_pair.full_curve.x_vec, curve_pair.full_curve.y_vec)
        #axes[row, 0].title.set_text("Horizontal Displacement vs. Time for Root " + str(key))
        #axes[row, 0].set_ylabel("Horizontal Displacement (mm)")
        #axes[row, 0].set_xlabel("Time Since Root Emergence (Hours)")
        axes[row, 1].plot(curve_pair.amplitude_curve.x_vec, curve_pair.amplitude_curve.y_vec)
        #axes[row, 1].title.set_text("Root Tip Rotational Amplitude vs. Time for Root " + str(key))
        #axes[row, 1].set_ylabel("Rotational Amplitude (mm)")
        #axes[row, 1].set_xlabel("Time Since Root Emergence (Hours)")
        row+=1
    plt.show()

def graph(curve):
        plt.plot(curve.x_vec, curve.y_vec)
        plt.figure()