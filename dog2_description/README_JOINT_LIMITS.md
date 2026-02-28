# Dog2 Robot Joint Limits Configuration

## Overview

The Dog2 robot URDF uses Xacro for parameterized joint limit configuration. This allows easy modification of joint limits without manually editing multiple joint definitions.

## Architecture

- **Source File**: `urdf/dog2.urdf.xacro` (Xacro template with parameters)
- **Generated File**: `urdf/dog2.urdf` (Auto-generated during build)
- **Validation Script**: `../scripts/validate_urdf_limits.py`

## Current Joint Limits

### Hip Joints (j11, j21, j31, j41)
- **Range**: ±150° (±2.618 rad)
- **Purpose**: Obstacle crossing with morphing capability
- **Positions**:
  - 0°: Leg vertical (default stance)
  - +90°: Leg forward (climbing phase)
  - -90°: Leg backward (retraction phase)
  - ±150°: Extreme folding for morphing

### Knee Joints (j111, j211, j311, j411)
- **Range**: ±160° (±2.8 rad)
- **Purpose**: Bidirectional folding (elbow ↔ knee configuration)
- **Positions**:
  - 0°: Leg straight (singularity point during morphing)
  - -160°: Elbow configuration (shin behind thigh)
  - +160°: Knee configuration (shin in front of thigh)
- **⚠️ WARNING**: 0° is a singularity point - controller must handle carefully

### Prismatic Joints (j1, j2, j3, j4)
- **Type**: Vertical leg extension
- **Limits**: Vary by leg (see Xacro file)

## Modifying Joint Limits

### Step 1: Edit Xacro Properties

Open `urdf/dog2.urdf.xacro` and modify the property definitions:

```xml
<!-- Hip joint limits -->
<xacro:property name="hip_lower_limit" value="-2.618"/>
<xacro:property name="hip_upper_limit" value="2.618"/>
<xacro:property name="hip_effort" value="50"/>
<xacro:property name="hip_velocity" value="20"/>

<!-- Knee joint limits -->
<xacro:property name="knee_lower_limit" value="-2.8"/>
<xacro:property name="knee_upper_limit" value="2.8"/>
<xacro:property name="knee_effort" value="50"/>
<xacro:property name="knee_velocity" value="20"/>
```

### Step 2: Rebuild Package

```bash
colcon build --packages-select dog2_description
```

This will:
1. Generate `urdf/dog2.urdf` from `urdf/dog2.urdf.xacro`
2. Automatically validate the generated URDF
3. Report any errors or inconsistencies

### Step 3: Validate Changes

```bash
python3 scripts/validate_urdf_limits.py src/dog2_description/urdf/dog2.urdf
```

Expected output:
```
✓ ALL CHECKS PASSED

Validated joints:
  - Hip joints (4): j11, j21, j31, j41
    Limits: [-2.618, 2.618] rad (±150°)
  - Knee joints (4): j111, j211, j311, j411
    Limits: [-2.8, 2.8] rad (±160°)
```

## Testing

### Test in Gazebo

```bash
ros2 launch dog2_description gazebo_dog2.launch.py
```

Verify:
- Robot loads without errors
- Joints respect limits (cannot exceed)
- No "knee reversal" behavior

### Test with ROS 2 Control

```bash
ros2 launch dog2_description view_dog2_control.launch.py
```

Verify:
- All 12 joints are controllable
- Joint limits are enforced by controllers
- Commands stay within limits

### Test with MPC/WBC

Run your existing MPC/WBC nodes and verify:
- No crashes due to joint limit changes
- Trajectories respect new limits
- Obstacle crossing works with new limits

**⚠️ NOTE**: Controllers may need tuning after changing limits!

## Validation Scripts

### validate_urdf_limits.py
Validates that URDF has correct joint limits:
- No continuous joints
- Consistent hip/knee limits across all legs
- 0° included in knee range

### test_gazebo_joints.py
Checks Gazebo compatibility

### test_ros2_control.py
Checks ROS 2 Control compatibility

### test_mpc_wbc_compatibility.py
Checks MPC/WBC compatibility

## Obstacle Crossing Phases

The joint limits are designed to support these phases:

1. **Phase 1 (Approach)**: Hip 0° to +45°, knee -90° (elbow)
2. **Phase 2 (Climb)**: Hip +45° to +90°, knee -90° to 0° (straightening)
3. **Phase 3 (Morph)**: Hip +90°, knee 0° to +90° (elbow to knee transition)
4. **Phase 4 (Descend)**: Hip +90° to 0°, knee +90° (knee configuration)

## Troubleshooting

### "Ice Skating" Bug (Fixed)

**Problem**: Robot slides uncontrollably when standing, legs spread outward (splits).

**Cause**: Missing Gazebo friction configuration on foot links.

**Solution**: ✅ FIXED - All 4 foot links (l1111, l2111, l3111, l4111) now have proper friction:
- mu1 = 1.0 (primary friction coefficient)
- mu2 = 1.0 (secondary friction coefficient)  
- kp = 1000000.0 (contact stiffness)
- kd = 100.0 (contact damping)

**Verify**: Run `python3 scripts/verify_foot_friction.py src/dog2_description/urdf/dog2.urdf`

### Build fails with "xacro not found"
```bash
sudo apt install ros-humble-xacro
```

### Validation fails
Check that:
1. All 4 hip joints have identical limits
2. All 4 knee joints have identical limits
3. Knee range includes 0° (lower < 0 < upper)

### Gazebo shows joint limit violations
This is expected - Gazebo enforces limits. If joints try to exceed limits, they will be blocked.

### MPC/WBC crashes after limit changes
Controllers may need retuning. The new limits change the feasible workspace.

## File Structure

```
dog2_description/
├── urdf/
│   ├── dog2.urdf.xacro          # Source (edit this)
│   ├── dog2.urdf                # Generated (don't edit)
│   └── dog2.urdf.backup_xacro_migration  # Backup
├── scripts/
│   ├── validate_urdf_limits.py
│   ├── test_gazebo_joints.py
│   ├── test_ros2_control.py
│   └── test_mpc_wbc_compatibility.py
└── CMakeLists.txt               # Auto-generation config
```

## References

- Original URDF: `urdf/dog2.urdf.backup_xacro_migration`
- Spec: `.kiro/specs/urdf-xacro-joint-limits/`
- Launch files using URDF: See `.kiro/specs/urdf-xacro-joint-limits/LAUNCH_FILES_USING_URDF.md`
