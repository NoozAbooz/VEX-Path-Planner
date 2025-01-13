# VEX Path Generator
# Made by Michael Zheng for CS20 at Western Canada High School
# January 10th, 2024

# All functions have return type void and have no paramaters unless specified

import sys
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QDockWidget, 
    QVBoxLayout, QWidget, QSpinBox, QDoubleSpinBox,
    QPushButton, QLabel, QFormLayout, QTextEdit)
from PyQt6.QtGui import QPainter, QPixmap, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRectF

from file_streaming import save_path, load_path

class fieldWidget(QWidget):
    def __init__(self): # logic inherited from PyQt docs: https://www.pythonguis.com/tutorials/pyqt-basic-widgets/
        super().__init__()
        # Load field image
        self.field_image = QPixmap("HighStakes.png")
        self.setMinimumSize(600, 600)
        
        # Setup waypoint coords as a array ("list" in python)
        self.waypoints = []
        
    def mousePressEvent(self, event):
        # Add mouse coordinates to waypoints list
        if event.button() == Qt.MouseButton.LeftButton:
            self.waypoints.append(event.pos())
            self.update()
            #print(event.pos())
        elif event.button() == Qt.MouseButton.RightButton and self.waypoints: # ignore blank clicks
            self.removeNearestWaypoint(event.pos())
            self.update()
        
    def removeNearestWaypoint(self, pos):
        # loop through list to find the closest point to the mouse and pop it
        nearestWayPointIndex = -1
        nearestWaypointDistance = None

        for i, waypoint in enumerate(self.waypoints): # need "enumerate" to assign a addressable index: https://www.geeksforgeeks.org/python-all-possible-pairs-in-list/
            distance = ((waypoint.x() - pos.x())**2 + (waypoint.y() - pos.y())**2)**0.5 # distance formula sqrt[(x1-2) + (y1-y2)]
            if (nearestWaypointDistance is None) or (distance < nearestWaypointDistance): # TODO revise this logic
                nearestWaypointIndex = i
                nearestWaypointDistance = distance
        if (nearestWaypointDistance < 10): # extra logic to make sure the click is on top of the waypoint itself
            self.waypoints.pop(nearestWaypointIndex)

    def paintEvent(self, event): # Think of this as the main "refresh" loop
        painter = QPainter(self)
        # Resize the field diagram to fit inside the window
        scaled_image = self.field_image.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        # Center image in widget horizontally when window scales
        x = (self.width() - scaled_image.width()) // 2
        y = (self.height() - scaled_image.height()) // 2
        painter.drawPixmap(x, y, scaled_image)

        if self.waypoints: # Make sure there are waypoints to render to prevent errors & crashes
            # Draw lines between points first so it goes on the bottom layer
            painter.setPen(QPen(QColor(205, 205, 255), 3))  # white lines
            for i in range(len(self.waypoints) - 1):
                painter.drawLine(self.waypoints[i], self.waypoints[i+1])

            painter.setPen(QPen(QColor(205, 105, 255, 128), 2))  # Set brush to make a ranslucent white points
            for i, waypoint in enumerate(self.waypoints):
                # Different colors for start/end points
                if i == 0:  # Start point (green)
                    painter.setBrush(QColor(0, 255, 0))
                elif i == len(self.waypoints) - 1:  # End point (red)
                    painter.setBrush(QColor(255, 0, 0))
                else:  # No special colours
                    painter.setBrush(QColor(205, 105, 255, 128))
                painter.drawEllipse(waypoint, 10, 10)
            
                # Number the points
                painter.setPen(Qt.GlobalColor.white)
                painter.setFont(QFont('Arial', 10))
                text_rect = QRectF(waypoint.x() + 15, waypoint.y() - 10, 20, 20)
                painter.fillRect(text_rect, QColor(0, 0, 0, 160))  # semi-transparent black background
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, str(i + 1))

            # QOL Heading indicator for the starting waypoint
            starting_waypoint = self.waypoints[0]
            heading_rad = math.radians(self.parent().rotation_input.value()) - math.pi / 2
            arrow_length = 10
            end_x = int(starting_waypoint.x() + arrow_length * math.cos(heading_rad))
            end_y = int(starting_waypoint.y() + arrow_length * math.sin(heading_rad))

            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.drawLine(int(starting_waypoint.x()), int(starting_waypoint.y()), end_x, end_y)

        # Write to code preview box when the field is updated to optimize the program instead of making another update loop
        self.parent().code_preview.setText(self.parent().copy_code())

    def mirror_path(self):
        if self.waypoints:
            field_width = self.width()
            for point in self.waypoints:
                # This logic relies on the field image being horizontally centered in the widget
                point.setX(field_width - point.x())
            self.update()

    def clear_path(self):
        self.waypoints = []
        self.update()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 800, 600)

        self.field_widget = fieldWidget()
        self.setCentralWidget(self.field_widget)

        # Create sidebar for settings using widgets
        dock = QDockWidget("Robot Settings", self)
        dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        sidebar = QWidget()
        layout = QFormLayout()

        # Input boxes for robot specs
        self.width_input = QDoubleSpinBox()
        self.width_input.setRange(1, 50)
        self.width_input.setValue(13.5)
        layout.addRow("Robot Width (in):", self.width_input)

        self.length_input = QDoubleSpinBox()
        self.length_input.setRange(1, 50)
        self.length_input.setValue(15)
        layout.addRow("Robot Length (in):", self.length_input)

        self.speed_input = QDoubleSpinBox()
        self.speed_input.setRange(1, 200)
        self.speed_input.setValue(6.38)
        layout.addRow("Speed (in/s):", self.speed_input)

        self.rotation_input = QDoubleSpinBox()
        self.rotation_input.setRange(0, 360)
        self.rotation_input.setValue(0)
        layout.addRow("Starting Rotation (deg):", self.rotation_input)

        clear_btn = QPushButton("Clear Path")
        clear_btn.clicked.connect(self.field_widget.clear_path)
        layout.addRow(clear_btn)

        mirror_btn = QPushButton("Mirror Path (X)")
        mirror_btn.clicked.connect(self.field_widget.mirror_path)
        layout.addRow(mirror_btn)

        copy_btn = QPushButton("Copy Code")
        copy_btn.clicked.connect(self.copy_code)
        layout.addRow(copy_btn)

        paths_btn = QPushButton("Save/Load Path")
        paths_btn.setToolTip("Left click to save, right click to load")
        paths_btn.clicked.connect(lambda: save_path(self))
        # The right click functionality is added to save vertical space since the code preview box is already very small ;-;
        paths_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        paths_btn.customContextMenuRequested.connect(lambda: load_path(self)) # https://stackoverflow.com/questions/71012127/making-a-custom-right-click-context-menu-in-pyqt5
        layout.addRow(paths_btn)

        self.code_preview = QTextEdit()
        self.code_preview.setReadOnly(True)
        self.code_preview.setFont(QFont("Courier New", 10))
        self.code_preview.setMinimumHeight(200)
        layout.addRow(self.code_preview)

        sidebar.setLayout(layout)
        dock.setWidget(sidebar)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    def localize_waypoint(self, point, origin, heading_deg):
        # Convert heading to radians
        heading_rad = math.radians(heading_deg)

        height = self.height() # field heigth always scales with widget size
        
        # Calculate relative position
        rel_x = (point.x() - origin.x()) * (144/height) # inches conversion
        rel_y = (point.y() - origin.y()) * (144/height)
        
        # Rotate coordinates
        # reference to my own code: https://github.com/NoozAbooz/210K-HighStakes-2025/blob/599060150f571b783ac304db27835bdb1d4cb02b/src/libKS/drivetrain/odom.cpp#L142C1-L146C1
        rot_x = round(rel_x * math.cos(heading_rad) + rel_y * math.sin(heading_rad), 1)
        rot_y = round(-rel_x * math.sin(heading_rad) + rel_y * math.cos(heading_rad), 1)
        return rot_x, -rot_y

    def copy_code(self):
        if not self.field_widget.waypoints:
            return
        
        start = self.field_widget.waypoints[0]

        code = ""
        for i, waypoint in enumerate(self.field_widget.waypoints):
            rot_x, rot_y = self.localize_waypoint(waypoint, start, self.rotation_input.value())
            code += f"chassis.moveToPoint({rot_x}, {rot_y}, 2000);\n"
        
        QApplication.clipboard().setText(code) # Overwrite clipboard
        return code

def main():
    # Initialization boilerplate
    app = QApplication(sys.argv)	
    # Create the main window
    window = MainWindow()
    window.show()
    #window.setWindowTitle("Hello, PyQt!")
    
    # Execution boilerplate
    sys.exit(app.exec())

if __name__ == "__main__":
    main()