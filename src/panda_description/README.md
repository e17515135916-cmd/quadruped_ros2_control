# panda_description

This directory is **not** an active ROS 2 package.

- It contains no `package.xml` or `CMakeLists.txt`.
- It is not built or installed by the colcon workspace.
- The sole active robot description source is
  `src/dog2_description/urdf/dog2.urdf.xacro`.

Do **not** place Dog2 main URDF work under `panda_description`.
If legacy CAD exports must be retained, move them into an explicitly
named archive directory (e.g. `panda_description/archive/`) that is
excluded from automated URDF scanning.
