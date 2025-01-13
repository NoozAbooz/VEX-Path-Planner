# first iteration developed in MPL, abandoned due to lack of button support

from matplotlib.widgets import TextBox, Button
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import json
from tkinter import filedialog
import tkinter as tk
import os

waypoints = []

# Constant variables for testing
robot_width = 13.5
robot_length = 15
robot_speed = 61.32 # in/s

def handle_click(event):
    if event.button == 1 and event.xdata and event.ydata:  # Check if left mouse button is clicked
        waypoints.append([event.xdata, event.ydata])  # save the click position
        draw_field()
    # if right mouse button then remove waypoint there
    elif event.button == 3 and event.xdata and event.ydata:
        for i in range(len(waypoints)):
            x, y = waypoints[i]
            if abs(x - event.xdata) < 3 and abs(y - event.ydata) < 3:
                waypoints.pop(i)
                break
        draw_field()

def draw_field():
    plt.clf()  # Clear the current plot
    plt.imshow(field_image, extent=[0, 144, 0, 144])  # redisplay the field image after clear
    print(waypoints)

    if waypoints:  # only run if points are present
        for i in range(len(waypoints)):
            x_point, y_point = waypoints[i]
            if i == 0:
                color = 'green' # first waypoint
            elif i == len(waypoints) - 1:
                color = 'blue' # last waypoint
            else:
                color = 'red' # everything else
            # translucent halos
            circle = plt.Circle((x_point, y_point), 3, color=color, alpha=0.5)
            plt.gca().add_patch(circle)
            # add dark background to labels
            plt.text(
                x_point + 1, y_point + 1, str(i + 1),
                fontsize=10, color="white",
                bbox=dict(facecolor='black', edgecolor='none', boxstyle='round,pad=0.15')
            )

        x, y = zip(*waypoints)  # "unzip" x and y coordinates solely for plotting lines
        plt.plot(x, y, 'r--')  # draw lines connecting the points (red, dashed line)

    plt.draw()  # Show the updated plot

def start_simulation(event):
    print("test")

field_image = np.array(Image.open("HighStakes.png"))

fig, ax = plt.subplots(figsize=(7, 7))  # window size
fig.canvas.mpl_connect('button_press_event', handle_click)

ax_load = plt.axes([0.7, 0.000001, 0.1, 0.075])
ax_save = plt.axes([0.81, 0.000001, 0.1, 0.075])
btn_load = Button(ax_load, 'Load')
btn_save = Button(ax_save, 'Save')

ax.set_xlim(0, 144)
ax.set_ylim(0, 144)
ax.set_aspect('equal')

draw_field()  # Draw the initial empty field
plt.show()  # Display the plot