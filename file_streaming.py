from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QPoint
import json

def save_path(window, filename=None):
    if not filename:
        filename, _ = QFileDialog.getSaveFileName(
            window,
            "Save Path",
            "savefile.json",
            "JSON Files (*.json);;All Files (*)"
        )
    
    if not filename: # many many error traps
        return False
        
    data = {
        "robot": {
            "width": window.width_input.value(),
            "length": window.length_input.value(),
            "speed": window.speed_input.value(),
            "heading": window.rotation_input.value()
        },
        "waypoints": []
    }
    
    # Convert waypoints to percentages (adapts to different screen/window sizes)
    # Reference https://github.com/NoozAbooz/210K-Website/blob/ce3e381cbd746c68d1a7d54ea709eeb4a8109d31/static/path/js/save.js#L30
    for point in window.field_widget.waypoints:
        data["waypoints"].append({
            "x": point.x() / window.field_widget.width(),
            "y": point.y() / window.field_widget.height()
        })
        
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except:
        return False

def load_path(window, filename=None):
    if not filename:
        filename, _ = QFileDialog.getOpenFileName(
            window,
            "Load Path",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
    
    if not filename: 
        return False
        
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            
        # Load robot settings
        window.width_input.setValue(data["robot"]["width"])
        window.length_input.setValue(data["robot"]["length"])
        window.speed_input.setValue(data["robot"]["speed"])
        window.rotation_input.setValue(data["robot"]["heading"])
        
        # Convert percentage coordinates back to pixels
        window.field_widget.waypoints.clear()
        for point in data["waypoints"]:
            x = int(point["x"] * window.field_widget.width())
            y = int(point["y"] * window.field_widget.height())
            window.field_widget.waypoints.append(QPoint(x, y))
            
        window.field_widget.update()
        return True
    except:
        return False