# Launch Files Using dog2.urdf

This document records which launch files reference `dog2.urdf` before the Xacro migration.

## dog2_description Package

1. `src/dog2_description/launch/view_dog2.launch.py` - RViz visualization
2. `src/dog2_description/launch/gazebo_test.launch.py` - Gazebo testing
3. `src/dog2_description/launch/view_dog2_gazebo.launch.py` - Gazebo + RViz
4. `src/dog2_description/launch/minimal_gazebo.launch.py` - Minimal Gazebo setup
5. `src/dog2_description/launch/view_dog2_static.launch.py` - Static visualization
6. `src/dog2_description/launch/gazebo_dog2.launch.py` - Gazebo simulation
7. `src/dog2_description/launch/view_dog2_control.launch.py` - Control visualization
8. `src/dog2_description/launch/view_dog2_small_inertia.launch.py` - Small inertia visualization
9. `src/dog2_description/view_robot.launch.py` - Robot viewer

## dog2_visualization Package

10. `src/dog2_visualization/launch/visualization_no_gazebo.launch.py` - Visualization without Gazebo

## dog2_mpc Package

11. `src/dog2_mpc/launch/complete_simulation.launch.py` - Complete MPC simulation
12. `src/dog2_mpc/launch/mpc_wbc_simulation.launch.py` - MPC/WBC simulation

## dog2_champ_config Package

13. `src/dog2_champ_config/launch/dog2_champ_gazebo.launch.py` - CHAMP Gazebo integration

## Notes

- All launch files directly reference `dog2.urdf` (not `dog2.urdf.xacro`)
- After Xacro migration, `dog2.urdf` will be auto-generated from `dog2.urdf.xacro`
- No launch file changes needed - they will continue to use `dog2.urdf`
- The build system will handle Xacro → URDF conversion automatically
