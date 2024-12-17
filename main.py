from matplotlib.widgets import TextBox
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# A 2D list to store the points where the user clicks
waypoints = []

# defaults
robot_width = 13.5
robot_length = 15
robot_speed = 61.32 # in/s

# This function runs when the user clicks on the field
def handle_click(event):
    if event.button == 1 and event.xdata and event.ydata:  # If left mouse button is clicked
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
    plt.imshow(field_image, extent=[0, 144, 0, 144])  # redisplay the field image
    # print(waypoints)

    if waypoints:  # only run if points are present
        for i in range(len(waypoints)):
            x_point, y_point = waypoints[i]
            if i == 0:
                color = 'green' # first waypoint
            elif i == len(waypoints) - 1:
                color = 'blue' # last waypoint
            else:
                color = 'red' # everything else
            # draw waypoints as translucent halos
            circle = plt.Circle((x_point, y_point), 3, color=color, alpha=0.5)
            plt.gca().add_patch(circle)
            # plot waypoint index number with a dark background
            plt.text(
                x_point + 1, y_point + 1, str(i + 1),
                fontsize=10, color="white",
                bbox=dict(facecolor='black', edgecolor='none', boxstyle='round,pad=0.15')
            )

        x, y = zip(*waypoints)  # "unzip" x and y coordinates solely for plotting lines
        plt.plot(x, y, 'r--')  # draw lines connecting the points (red, dashed line)

    plt.title("Click to Add Waypoints")
    plt.draw()  # Show the updated plot

# Load the image of the field
field_image = np.array(Image.open("HighStakes.png"))

# Set up the plot window
fig, ax = plt.subplots(figsize=(7, 7))  # Create a 7x7 inches plot
fig.canvas.mpl_connect('button_press_event', handle_click)  # Connect clicks to the handle_click function

ax.set_xlim(0, 144)
ax.set_ylim(0, 144)
ax.set_aspect('equal')

draw_field()  # Draw the initial empty field
plt.show()  # Display the plot
