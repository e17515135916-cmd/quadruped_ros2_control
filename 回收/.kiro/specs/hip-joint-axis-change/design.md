# Design Document: Hip Joint Axis Change

## Overview

This document describes the design for changing the Dog2 robot's hip joint rotation axes (j11, j21, j31, j41) from z-axis to x-axis rotation. This modification affects the URDF joint definitions, visual and collision meshes, kinematics solvers, and requires validation in simulation.

The change involves rotating the joint axis by 90 degrees, which fundamentally alters how the hip joints move. Currently, the joints rotate about the z-axis (vertical), and we will change them to rotate about the x-axis (forward-backward).

## Architecture

### Current Configuration

```
Hip Joint (j${leg_num}1):
- Type: revolute
- Axis: <axis xyz="0 0 -1"/>  (z-axis rotation)
- Parent: l${leg_num} (prismatic link)
- Child: l${leg_num}1 (hip link)
- Function: Hip Abduction/Adduction (HAA)
```

### Target Configuration

```
Hip Joint (j${leg_num}1):
- Type: revolute
- Axis: <axis xyz="1 0 0"/>  (x-axis rotation)
- Parent: l${leg_num} (prismatic link)
- Child: l${leg_num}1 (hip link)
- Function: Modified hip motion
```

### Affected Components

1. **URDF Definition** (`src/dog2_description/urdf/dog2.urdf.xacro`)
   - Joint axis definition
   - Joint origin transformation (RPY)
   - Visual mesh origin (RPY)
   - Collision mesh origin (RPY)

2. **Visual Meshes**
   - `src/dog2_description/meshes/l11.STL`
   - `src/dog2_description/meshes/l21.STL`
   - `src/dog2_description/meshes/l31.STL`
   - `src/dog2_description/meshes/l41.STL`

3. **Collision Meshes**
   - `src/dog2_description/meshes/collision/l11_collision.STL`
   - `src/dog2_description/meshes/collision/l21_collision.STL`
   - `src/dog2_description/meshes/collision/l31_collision.STL`
   - `src/dog2_description/meshes/collision/l41_collision.STL`

4. **Kinematics Solvers**
   - `src/dog2_kinematics/dog2_kinematics/leg_ik_4dof.py`
   - `src/dog2_kinematics/src/leg_ik_4dof.cpp`
   - `src/dog2_kinematics/include/dog2_kinematics/leg_ik_4dof.hpp`

## Components and Interfaces

### Component 1: URDF Joint Axis Modifier

**Purpose**: Update the joint axis definition in the URDF macro.

**Location**: `src/dog2_description/urdf/dog2.urdf.xacro`

**Changes**:
```xml
<!-- Current -->
<joint name="j${leg_num}1" type="revolute">
  <origin rpy="${hip_joint_rpy}" xyz="${hip_joint_xyz}"/>
  <parent link="l${leg_num}"/>
  <child link="l${leg_num}1"/>
  <axis xyz="0 0 -1"/>  <!-- Z-axis -->
  <limit effort="${hip_effort}" lower="${hip_lower_limit}" upper="${hip_upper_limit}" velocity="${hip_velocity}"/>
</joint>

<!-- Target -->
<joint name="j${leg_num}1" type="revolute">
  <origin rpy="${hip_joint_rpy}" xyz="${hip_joint_xyz}"/>
  <parent link="l${leg_num}"/>
  <child link="l${leg_num}1"/>
  <axis xyz="1 0 0"/>  <!-- X-axis -->
  <limit effort="${hip_effort}" lower="${hip_lower_limit}" upper="${hip_upper_limit}" velocity="${hip_velocity}"/>
</joint>
```

### Component 2: Visual Mesh Orientation Handler

**Purpose**: Adjust visual mesh orientation to match new joint axis.

**Approach Options**:

**Option A: Modify URDF Visual Origin (Recommended)**
- Pros: No mesh file modification, easy to revert, fast
- Cons: Adds complexity to URDF

```xml
<!-- Add rotation to visual origin -->
<link name="l${leg_num}1">
  <visual>
    <origin rpy="0 0 1.5708" xyz="0 0 0"/>  <!-- Rotate 90° around Z -->
    <geometry>
      <mesh filename="package://dog2_description/meshes/l${leg_num}1.STL"/>
    </geometry>
  </visual>
</link>
```

**Option B: Rotate Mesh Files in Blender**
- Pros: Clean URDF, mesh matches joint axis naturally
- Cons: Requires Blender, modifies original files, harder to revert

**Decision**: Use Option A (URDF visual origin) for initial implementation, with Option B as future enhancement.

### Component 3: Collision Mesh Orientation Handler

**Purpose**: Update collision geometry to match visual mesh orientation.

**Implementation**: Same approach as visual meshes - adjust collision origin in URDF.

```xml
<link name="l${leg_num}1">
  <collision>
    <origin rpy="0 0 1.5708" xyz="0 0 0"/>  <!-- Match visual rotation -->
    <geometry>
      <mesh filename="package://dog2_description/meshes/collision/l${leg_num}1_collision.STL"/>
    </geometry>
  </collision>
</link>
```

### Component 4: Kinematics Solver Updater

**Purpose**: Update IK/FK solvers to work with new joint axis configuration.

**Current HAA Calculation** (z-axis rotation):
```python
# HAA controls leg in Y-Z plane
haa_to_foot = foot_position - haa_pos
haa = atan2(haa_to_foot.z, haa_to_foot.y)
```

**Updated HAA Calculation** (x-axis rotation):
```python
# HAA now controls leg in Y-Z plane differently
# Need to recalculate based on x-axis rotation
haa_to_foot = foot_position - haa_pos
haa = atan2(haa_to_foot.y, haa_to_foot.z)  # Swapped for x-axis
```

**Files to Update**:
1. `leg_ik_4dof.py` - Python implementation
2. `leg_ik_4dof.cpp` - C++ implementation
3. `leg_ik_4dof.hpp` - C++ header

### Component 5: Backup and Restore System

**Purpose**: Create backups before modifications to allow easy rollback.

**Implementation**:
```bash
#!/bin/bash
# Backup URDF
cp src/dog2_description/urdf/dog2.urdf.xacro \
   src/dog2_description/urdf/dog2.urdf.xacro.backup_$(date +%Y%m%d_%H%M%S)

# Backup meshes (if modifying)
for leg in 1 2 3 4; do
  cp src/dog2_description/meshes/l${leg}1.STL \
     src/dog2_description/meshes/l${leg}1.STL.backup
  cp src/dog2_description/meshes/collision/l${leg}1_collision.STL \
     src/dog2_description/meshes/collision/l${leg}1_collision.STL.backup
done
```

## Data Models

### Joint Configuration

```python
@dataclass
class HipJointConfig:
    """Configuration for a hip joint"""
    joint_name: str          # e.g., "j11"
    axis: Tuple[float, float, float]  # (1, 0, 0) for x-axis
    origin_rpy: Tuple[float, float, float]
    origin_xyz: Tuple[float, float, float]
    effort_limit: float
    velocity_limit: float
    position_lower: float
    position_upper: float
```

### Mesh Transformation

```python
@dataclass
class MeshTransform:
    """Transformation to apply to mesh or visual origin"""
    rotation_rpy: Tuple[float, float, float]  # Roll, Pitch, Yaw
    translation_xyz: Tuple[float, float, float]
    apply_to_mesh: bool  # True: rotate mesh file, False: rotate visual origin
```

### Kinematics Parameters

```python
@dataclass
class LegGeometry:
    """Geometric parameters for leg kinematics"""
    base_to_prismatic_offset: np.ndarray  # [x, y, z]
    prismatic_to_haa_offset: np.ndarray
    haa_to_hfe_offset: np.ndarray
    thigh_length: float
    shin_length: float
    haa_axis: str  # "x", "y", or "z"  # NEW: track which axis HAA rotates about
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Joint Axis Consistency

*For any* hip joint (j11, j21, j31, j41), the joint axis definition in the URDF SHALL be "1 0 0" (x-axis).

**Validates: Requirements 1.1, 1.2, 1.3, 1.4**

### Property 2: Visual-Collision Alignment

*For any* hip link (l11, l21, l31, l41), the visual origin RPY and collision origin RPY SHALL be identical.

**Validates: Requirements 5.1, 6.1**

### Property 3: Kinematics Round-Trip Consistency

*For any* valid foot position within the workspace, computing FK then IK SHALL return joint angles that produce a foot position within 1mm of the original position.

**Validates: Requirements 4.1, 4.2, 4.3**

### Property 4: Joint Limit Preservation

*For any* hip joint, the effort limit SHALL be 50 Nm, velocity limit SHALL be 20 rad/s, and position limits SHALL be within ±2.618 rad.

**Validates: Requirements 3.1, 3.2, 3.3**

### Property 5: Zero-Angle Neutral Position

*For any* hip joint, when the joint angle is zero, the child link SHALL be in its neutral position as defined by the visual mesh orientation.

**Validates: Requirements 2.3, 5.4**

### Property 6: Simulation Controllability

*For any* hip joint, sending a position command via ROS 2 topic SHALL result in the joint rotating about the x-axis in Gazebo.

**Validates: Requirements 7.1, 7.2**

### Property 7: Visual Appearance Consistency

*For any* hip joint, the visual appearance in RViz SHALL match the visual appearance in Gazebo when the joint is at the same angle.

**Validates: Requirements 7.5**

## Error Handling

### Invalid Joint Axis Detection

**Error**: Joint axis is not (1, 0, 0) after modification.

**Handling**:
1. Parse URDF and extract joint axis
2. Compare with expected value
3. If mismatch, raise error with joint name and actual axis
4. Provide rollback instructions

### Kinematics Solver Failure

**Error**: IK solver cannot find solution for valid foot position.

**Handling**:
1. Log foot position and joint configuration
2. Check if foot position is within workspace
3. If within workspace, indicate solver bug
4. Provide diagnostic information for debugging

### Mesh Orientation Mismatch

**Error**: Visual mesh appears incorrectly oriented in simulation.

**Handling**:
1. Check visual origin RPY in URDF
2. Verify mesh file hasn't been corrupted
3. Compare with backup files
4. Provide correction suggestions

### Collision Detection False Positives

**Error**: Robot reports collisions when links are not actually touching.

**Handling**:
1. Verify collision origin matches visual origin
2. Check collision mesh geometry
3. Adjust collision mesh origin if needed
4. Test with simple geometric primitives if mesh is problematic

## Testing Strategy

### Unit Tests

**Test 1: URDF Joint Axis Verification**
- Parse URDF file
- Extract j11, j21, j31, j41 axis definitions
- Assert each is (1, 0, 0)

**Test 2: Visual-Collision Origin Match**
- Parse URDF file
- Extract visual and collision origins for l11, l21, l31, l41
- Assert RPY values match

**Test 3: Joint Limit Verification**
- Parse URDF file
- Extract joint limits for j11, j21, j31, j41
- Assert effort = 50, velocity = 20, position = ±2.618

### Property-Based Tests

**Test 4: Kinematics Round-Trip Property**
- Generate random valid foot positions
- Compute IK to get joint angles
- Compute FK with those joint angles
- Assert foot position error < 1mm
- **Feature: hip-joint-axis-change, Property 3: Kinematics Round-Trip Consistency**

**Test 5: Zero-Angle Neutral Position Property**
- For each leg, set all joint angles to zero
- Compute FK to get link positions
- Assert links are in expected neutral positions
- **Feature: hip-joint-axis-change, Property 5: Zero-Angle Neutral Position**

### Integration Tests

**Test 6: RViz Visualization Test**
- Launch RViz with updated URDF
- Command each hip joint through range of motion
- Manually verify visual appearance is correct
- Check for mesh orientation issues

**Test 7: Gazebo Simulation Test**
- Launch Gazebo with updated URDF
- Command each hip joint through range of motion
- Verify joint rotates about x-axis
- Check for collision detection issues

**Test 8: Standing Posture Test**
- Load robot in Gazebo
- Command standing posture
- Verify robot stands stably
- Check all joints are within limits

**Test 9: Walking Gait Test**
- Load robot in Gazebo
- Execute simple walking gait
- Verify locomotion works with new joint configuration
- Monitor for any kinematic issues

### Validation Checklist

- [ ] URDF parses without errors
- [ ] All hip joints have x-axis rotation
- [ ] Visual meshes appear correctly in RViz
- [ ] Visual meshes appear correctly in Gazebo
- [ ] Collision detection works without false positives
- [ ] IK solver produces valid solutions
- [ ] FK solver produces correct foot positions
- [ ] Robot can stand stably
- [ ] Robot can walk with new configuration
- [ ] Joint limits are respected
- [ ] Backup files are created

## Implementation Notes

### Coordinate System Conventions

**Current (Z-axis rotation)**:
- Positive rotation: counterclockwise when viewed from above
- Motion plane: Y-Z plane
- Primary function: Leg abduction/adduction

**Target (X-axis rotation)**:
- Positive rotation: counterclockwise when viewed from front
- Motion plane: Y-Z plane (but different orientation)
- Primary function: Modified hip motion

### Mesh Rotation Calculations

If rotating meshes in Blender (Option B):
- Rotation needed: 90° around Z-axis (or equivalent)
- Blender script: `bpy.ops.transform.rotate(value=1.5708, orient_axis='Z')`
- Export as STL with same name

### URDF Origin Adjustments

If adjusting URDF origins (Option A - Recommended):
- Add RPY to visual origin: `rpy="0 0 1.5708"`
- Add same RPY to collision origin: `rpy="0 0 1.5708"`
- Keep mesh files unchanged

### Kinematics Solver Updates

Key changes needed:
1. Update HAA calculation to use x-axis rotation
2. Update coordinate transformations
3. Update Jacobian calculations (if used)
4. Update workspace calculations

### Backward Compatibility

To maintain backward compatibility:
- Keep backup files
- Document changes in URDF comments
- Provide rollback script
- Update documentation to reflect new configuration

## Dependencies

- ROS 2 (Humble or later)
- Gazebo Fortress
- RViz2
- Python 3.8+
- NumPy
- Blender 3.0+ (if rotating meshes)
- trimesh (if rotating meshes programmatically)

## Migration Path

1. **Backup Phase**: Create backups of all files
2. **URDF Update Phase**: Modify joint axis and origins
3. **Kinematics Update Phase**: Update IK/FK solvers
4. **Testing Phase**: Run unit and integration tests
5. **Validation Phase**: Test in RViz and Gazebo
6. **Documentation Phase**: Update all documentation

## Rollback Plan

If issues are encountered:
1. Restore URDF from backup
2. Restore mesh files from backup (if modified)
3. Restore kinematics solver files from backup
4. Rebuild and test
5. Document issues encountered

## Future Enhancements

1. **Mesh File Rotation**: Implement Option B to rotate actual mesh files
2. **Automatic Validation**: Create automated tests for visual appearance
3. **Performance Optimization**: Optimize kinematics solvers for new configuration
4. **Documentation**: Create detailed migration guide for similar changes
