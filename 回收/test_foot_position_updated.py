#!/usr/bin/env python3
"""
Test the updated foot position in RViz
"""

import subprocess
import time
import os

# Source the setup
os.system("source install/setup.bash")

# Kill any existing RViz processes
os.system("pkill -f rviz2 || true")
time.sleep(1)

# Launch RViz with the updated URDF
print("Launching RViz with updated foot position...")
print("Offset changed from -0.27 to -0.31 (moving balls down)")
print("\nPlease verify:")
print("1. Balls should be lower than before")
print("2. From rear view, balls should be more centered on each leg")
print("3. Half of each ball should be exposed at shin end")
print("\nPress Ctrl+C to stop")

subprocess.run([
    "ros2", "launch", "dog2_description", "display.launch.py"
], cwd="/root/dog2_ws")
