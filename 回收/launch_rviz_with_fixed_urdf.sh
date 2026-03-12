#!/bin/bash
# Launch RViz with post-processed URDF that fixes rear legs

echo "Generating and fixing URDF..."

# Source ROS 2
source /opt/ros/humble/setup.bash
source install/setup.bash

# Generate URDF from xacro
xacro src/dog2_description/urdf/dog2.urdf.xacro > /tmp/generated.urdf

# Post-process to fix rear legs
python3 post_process_urdf.py /tmp/generated.urdf /tmp/fixed_dog2.urdf

# Copy to standard location
cp /tmp/fixed_dog2.urdf /tmp/robot_description.urdf

echo "✓ URDF fixed and ready"
echo ""
echo "Launching RViz..."

# Launch RViz with fixed URDF
ros2 launch dog2_description view_dog2.launch.py
