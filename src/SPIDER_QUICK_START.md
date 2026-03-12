# Spider-Style Quick Validation (Dog2)

Source of truth: `src/dog2_description/urdf/dog2.urdf.xacro`

## Stage 1: Model sanity checks

1) Kinematic-only check (no physics):

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch dog2_description spider_kinematics_check.launch.py
```

2) Free-fall drop test (collision/friction sanity):

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch dog2_description spider_drop_test.launch.py spawn_z:=1.0
```

## Stage 2: ros2_control joint bringup

1) Start position-mode controllers only:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch dog2_description spider_position_startup.launch.py
```

2) Run single-leg and rail smoke test:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run dog2_description spider_joint_smoke_test.py
```

## Stage 3: 4-DOF IK quick solve (offline)

```bash
python3 src/scripts/spider_ik_4dof.py \
  --target 0.20 0.15 -0.28 \
  --rail 0.02 \
  --links 0.20 0.20 \
  --hip 0.00 0.00 0.00
```

## Stage 4: MPC/WBC parameter adaptation

`mpc_node_complete` now exposes:
- `default_stance_length`
- `default_stance_width`
- `nominal_body_height`
- `com_offset_x`, `com_offset_y`, `com_offset_z`

Example launch:

```bash
ros2 launch dog2_visualization visualization_no_gazebo.launch.py \
  mode:=walking rviz:=false
```

Then tune the above stance/CoM parameters in your launch or YAML.
