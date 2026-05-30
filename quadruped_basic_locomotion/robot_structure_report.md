# Robot Structure Report

- model_path: `/home/dell/aperfect/carbot_ws/src/dog2_description/urdf/dog2.urdf.xacro`
- base_link: `base_link`
- root_links / floating base candidates: `base_link`
- total_links: 49
- total_joints: 48
- mapping_valid: `True`

## Joint Table

| joint_index | motion_index | joint_name | joint_type | parent_link | child_link | joint_axis | lower | upper | effort | velocity | initial_q | initial_dq |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 |  | lf_leg_mount_fixed | fixed | base_link | lf_leg_mount | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 1 |  | lh_leg_mount_fixed | fixed | base_link | lh_leg_mount | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 2 |  | rh_leg_mount_fixed | fixed | base_link | rh_leg_mount | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 3 |  | rf_leg_mount_fixed | fixed | base_link | rf_leg_mount | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 4 | 0 | lf_rail_joint | prismatic | lf_leg_mount | lf_rail_link | [1, 0, 0] | 0 | 0.111 | 100 | 5 | 0 | 0 |
| 5 |  | lf_coxa_axis_fixed | fixed | lf_rail_link | lf_coxa_axis_frame | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 6 | 1 | lf_coxa_joint | revolute | lf_coxa_axis_frame | lf_coxa_drive_frame | [0, 0, -1] | -2.618 | 2.618 | 50 | 20 | -0.3 | 0 |
| 7 |  | lf_coxa_pose_fixed | fixed | lf_coxa_drive_frame | lf_coxa_link | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 8 |  | lf_femur_axis_fixed | fixed | lf_coxa_link | lf_femur_axis_frame | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 9 | 2 | lf_femur_joint | revolute | lf_femur_axis_frame | lf_femur_drive_frame | [0, -1, 0] | -2.8 | 2.8 | 50 | 20 | 0.65 | 0 |
| 10 |  | lf_femur_pose_fixed | fixed | lf_femur_drive_frame | lf_femur_link | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 11 |  | lf_tibia_axis_fixed | fixed | lf_femur_link | lf_tibia_axis_frame | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 12 | 3 | lf_tibia_joint | revolute | lf_tibia_axis_frame | lf_tibia_drive_frame | [0, -1, 0] | -2.8 | 2.8 | 50 | 20 | -1.25 | 0 |
| 13 |  | lf_tibia_pose_fixed | fixed | lf_tibia_drive_frame | lf_tibia_link | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 14 |  | lf_foot_fixed | fixed | lf_tibia_link | lf_foot_link | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 15 | 4 | lh_rail_joint | prismatic | lh_leg_mount | lh_rail_link | [1, 0, 0] | -0.111 | 0 | 100 | 5 | 0 | 0 |
| 16 |  | lh_coxa_axis_fixed | fixed | lh_rail_link | lh_coxa_axis_frame | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 17 | 5 | lh_coxa_joint | revolute | lh_coxa_axis_frame | lh_coxa_drive_frame | [0, 0, -1] | -2.618 | 2.618 | 50 | 20 | -0.3 | 0 |
| 18 |  | lh_coxa_pose_fixed | fixed | lh_coxa_drive_frame | lh_coxa_link | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 19 |  | lh_femur_axis_fixed | fixed | lh_coxa_link | lh_femur_axis_frame | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 20 | 6 | lh_femur_joint | revolute | lh_femur_axis_frame | lh_femur_drive_frame | [0, -1, 0] | -2.8 | 2.8 | 50 | 20 | 0.65 | 0 |
| 21 |  | lh_femur_pose_fixed | fixed | lh_femur_drive_frame | lh_femur_link | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 22 |  | lh_tibia_axis_fixed | fixed | lh_femur_link | lh_tibia_axis_frame | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 23 | 7 | lh_tibia_joint | revolute | lh_tibia_axis_frame | lh_tibia_drive_frame | [0, -1, 0] | -2.8 | 2.8 | 50 | 20 | -1.25 | 0 |
| 24 |  | lh_tibia_pose_fixed | fixed | lh_tibia_drive_frame | lh_tibia_link | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 25 |  | lh_foot_fixed | fixed | lh_tibia_link | lh_foot_link | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 26 | 8 | rh_rail_joint | prismatic | rh_leg_mount | rh_rail_link | [-1, 0, 0] | -0.111 | 0 | 100 | 5 | 0 | 0 |
| 27 |  | rh_coxa_axis_fixed | fixed | rh_rail_link | rh_coxa_axis_frame | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 28 | 9 | rh_coxa_joint | revolute | rh_coxa_axis_frame | rh_coxa_drive_frame | [0, 0, -1] | -2.618 | 2.618 | 50 | 20 | 0.3 | 0 |
| 29 |  | rh_coxa_pose_fixed | fixed | rh_coxa_drive_frame | rh_coxa_link | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 30 |  | rh_femur_axis_fixed | fixed | rh_coxa_link | rh_femur_axis_frame | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 31 | 10 | rh_femur_joint | revolute | rh_femur_axis_frame | rh_femur_drive_frame | [0, -1, 0] | -2.8 | 2.8 | 50 | 20 | 0.65 | 0 |
| 32 |  | rh_femur_pose_fixed | fixed | rh_femur_drive_frame | rh_femur_link | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 33 |  | rh_tibia_axis_fixed | fixed | rh_femur_link | rh_tibia_axis_frame | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 34 | 11 | rh_tibia_joint | revolute | rh_tibia_axis_frame | rh_tibia_drive_frame | [0, -1, 0] | -2.8 | 2.8 | 50 | 20 | -1.25 | 0 |
| 35 |  | rh_tibia_pose_fixed | fixed | rh_tibia_drive_frame | rh_tibia_link | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 36 |  | rh_foot_fixed | fixed | rh_tibia_link | rh_foot_link | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 37 | 12 | rf_rail_joint | prismatic | rf_leg_mount | rf_rail_link | [-1, 0, 0] | 0 | 0.111 | 100 | 5 | 0 | 0 |
| 38 |  | rf_coxa_axis_fixed | fixed | rf_rail_link | rf_coxa_axis_frame | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 39 | 13 | rf_coxa_joint | revolute | rf_coxa_axis_frame | rf_coxa_drive_frame | [0, 0, -1] | -2.618 | 2.618 | 50 | 20 | 0.3 | 0 |
| 40 |  | rf_coxa_pose_fixed | fixed | rf_coxa_drive_frame | rf_coxa_link | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 41 |  | rf_femur_axis_fixed | fixed | rf_coxa_link | rf_femur_axis_frame | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 42 | 14 | rf_femur_joint | revolute | rf_femur_axis_frame | rf_femur_drive_frame | [0, -1, 0] | -2.8 | 2.8 | 50 | 20 | 0.65 | 0 |
| 43 |  | rf_femur_pose_fixed | fixed | rf_femur_drive_frame | rf_femur_link | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 44 |  | rf_tibia_axis_fixed | fixed | rf_femur_link | rf_tibia_axis_frame | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 45 | 15 | rf_tibia_joint | revolute | rf_tibia_axis_frame | rf_tibia_drive_frame | [0, -1, 0] | -2.8 | 2.8 | 50 | 20 | -1.25 | 0 |
| 46 |  | rf_tibia_pose_fixed | fixed | rf_tibia_drive_frame | rf_tibia_link | [0, 0, 0] |  |  |  |  | 0 | 0 |
| 47 |  | rf_foot_fixed | fixed | rf_tibia_link | rf_foot_link | [0, 0, 0] |  |  |  |  | 0 | 0 |

## Classification

- leg_revolute_joints: lf_coxa_joint, lf_femur_joint, lf_tibia_joint, lh_coxa_joint, lh_femur_joint, lh_tibia_joint, rh_coxa_joint, rh_femur_joint, rh_tibia_joint, rf_coxa_joint, rf_femur_joint, rf_tibia_joint
- rail_prismatic_joints: lf_rail_joint, lh_rail_joint, rh_rail_joint, rf_rail_joint
- passive_joints: (none)
- fixed_joints: lf_leg_mount_fixed, lh_leg_mount_fixed, rh_leg_mount_fixed, rf_leg_mount_fixed, lf_coxa_axis_fixed, lf_coxa_pose_fixed, lf_femur_axis_fixed, lf_femur_pose_fixed, lf_tibia_axis_fixed, lf_tibia_pose_fixed, lf_foot_fixed, lh_coxa_axis_fixed, lh_coxa_pose_fixed, lh_femur_axis_fixed, lh_femur_pose_fixed, lh_tibia_axis_fixed, lh_tibia_pose_fixed, lh_foot_fixed, rh_coxa_axis_fixed, rh_coxa_pose_fixed, rh_femur_axis_fixed, rh_femur_pose_fixed, rh_tibia_axis_fixed, rh_tibia_pose_fixed, rh_foot_fixed, rf_coxa_axis_fixed, rf_coxa_pose_fixed, rf_femur_axis_fixed, rf_femur_pose_fixed, rf_tibia_axis_fixed, rf_tibia_pose_fixed, rf_foot_fixed

## Rail Lock Inputs

- lf_rail_joint: initial_q=0, initial_dq=0
- lh_rail_joint: initial_q=0, initial_dq=0
- rh_rail_joint: initial_q=0, initial_dq=0
- rf_rail_joint: initial_q=0, initial_dq=0

## Leg Joint Mapping

### FL

- joint_0: `lf_coxa_joint`
- joint_1: `lf_femur_joint`
- joint_2: `lf_tibia_joint`
- foot_link: `lf_foot_link`

### FR

- joint_0: `rf_coxa_joint`
- joint_1: `rf_femur_joint`
- joint_2: `rf_tibia_joint`
- foot_link: `rf_foot_link`

### RL

- joint_0: `lh_coxa_joint`
- joint_1: `lh_femur_joint`
- joint_2: `lh_tibia_joint`
- foot_link: `lh_foot_link`

### RR

- joint_0: `rh_coxa_joint`
- joint_1: `rh_femur_joint`
- joint_2: `rh_tibia_joint`
- foot_link: `rh_foot_link`

## Validation

- No validation errors.
