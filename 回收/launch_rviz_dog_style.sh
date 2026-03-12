#!/bin/bash
# Launch RViz to view the dog-style robot configuration

echo "=========================================="
echo "Launching RViz for Dog-Style Robot"
echo "=========================================="

# Source ROS 2 environment
source /opt/ros/humble/setup.bash
source install/setup.bash

# Generate URDF from xacro
echo "Generating URDF from xacro..."
xacro src/dog2_description/urdf/dog2.urdf.xacro > /tmp/dog2_dog_style.urdf

if [ $? -ne 0 ]; then
    echo "❌ Error generating URDF"
    exit 1
fi

echo "✓ URDF generated successfully"
echo ""
echo "Starting RViz..."
echo "All joint angles will be set to ZERO to show dog-style leg orientation"
echo ""

# Launch with the generated URDF
ros2 launch dog2_description view_dog2.launch.py

echo ""
echo "RViz closed."
