#!/bin/bash
# Test script to verify leg orientation fix in RViz

echo "=========================================="
echo "Testing Fixed Leg Orientation"
echo "=========================================="
echo ""
echo "Fix applied:"
echo "- Changed hip_axis from '-1 0 0' to '1 0 0' for rear legs (Leg 3 & 4)"
echo ""
echo "Expected result:"
echo "- All four legs should point DOWNWARD at zero angles"
echo "- Configuration should look like a dog, not a spider"
echo ""
echo "Starting RViz..."
echo "=========================================="
echo ""

# Source ROS 2
source /opt/ros/humble/setup.bash
source install/setup.bash

# Launch RViz with robot state publisher
ros2 launch dog2_description view_dog2.launch.py &
LAUNCH_PID=$!

# Wait for RViz to start
sleep 5

# Run the test script to set all joints to zero
echo ""
echo "Setting all joints to zero position..."
python3 test_leg_orientation_fix.py

echo ""
echo "=========================================="
echo "Test complete!"
echo "Check RViz to verify all legs point downward"
echo "Press Ctrl+C to exit"
echo "=========================================="

# Wait for user to examine
wait $LAUNCH_PID
