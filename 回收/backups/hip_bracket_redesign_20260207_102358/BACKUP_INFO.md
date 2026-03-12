# Hip Bracket Redesign - Backup Information

**Backup Date:** 2026-02-07 10:23:58

**Purpose:** Backup of original mesh files and URDF configuration before implementing hip bracket mechanical redesign to change from "spider-style" (Z-axis rotation) to "dog-style" (X-axis rotation).

## Backed Up Files

### Visual Mesh Files
- `src/dog2_description/meshes/l11.STL` (91 KB)
- `src/dog2_description/meshes/l21.STL` (91 KB)
- `src/dog2_description/meshes/l31.STL` (91 KB)
- `src/dog2_description/meshes/l41.STL` (91 KB)

### Collision Mesh Files
- `src/dog2_description/meshes/collision/l11_collision.STL` (13 KB)
- `src/dog2_description/meshes/collision/l21_collision.STL` (13 KB)
- `src/dog2_description/meshes/collision/l31_collision.STL` (13 KB)
- `src/dog2_description/meshes/collision/l41_collision.STL` (13 KB)

### URDF Configuration
- `src/dog2_description/urdf/dog2.urdf.xacro` (12 KB)

## Current Hip Bracket Configuration

### Current Joint Configuration (Before Redesign)

**Hip Joint Axis:** Currently configured for X-axis rotation (1 0 0)
- Note: The URDF was already modified on 2026-02-02 to use X-axis rotation
- Visual and collision meshes still have Z-axis rotation compensation (rpy="0 0 1.5708")

**Hip Joint Origins (Default):**
```xml
hip_joint_xyz: "-0.016 0.0199 0.055"
hip_joint_rpy: "0 0 1.5708"
```

**Leg-Specific Overrides:**
- Leg 1 & 2 (Front): Use default values
- Leg 3 (Rear Left): `hip_joint_rpy="3.1416 0 1.5708"`, `knee_joint_xyz="-0.0233 -0.055 -0.0254"`
- Leg 4 (Rear Right): `hip_joint_rpy="3.1416 0 1.5708"`, `hip_joint_xyz="-0.016 0.0199 0.055"`, `knee_joint_xyz="-0.0233 -0.055 -0.0254"`

### Current Bracket Dimensions (Measured from Mesh)

**Hip Link (l${leg_num}1) Properties:**
- Mass: 0.25 kg
- Inertia origin: xyz="-0.0233 -0.0383 0.000879"
- Visual mesh: Rotated 90° around Z-axis (rpy="0 0 1.5708")
- Collision mesh: Rotated 90° around Z-axis (rpy="0 0 1.5708")

**Actual Mesh Dimensions (l11.STL):**
- Triangle count: 1854 triangles
- Bounding box:
  - X: -0.0517 to 0.0051 m (width: 0.0568 m = 56.8 mm)
  - Y: -0.0650 to 0.0100 m (depth: 0.0750 m = 75.0 mm)
  - Z: -0.0244 to 0.0264 m (height: 0.0508 m = 50.8 mm)
- Total envelope: ~57mm × 75mm × 51mm

**Knee Joint Position (relative to hip link):**
```xml
knee_joint_xyz: "-0.0233 -0.055 0.0274"
```

### Current Design Characteristics

**Current Configuration:**
- Hip joint rotates about X-axis (forward-backward motion)
- Visual mesh has 90° Z-rotation to compensate for original Z-axis design
- Collision mesh matches visual orientation
- Joint origin Z-coordinate: 0.055 m (55mm above prismatic link)

**Known Issues:**
- Mesh files are designed for Z-axis rotation (vertical servo mounting)
- Visual/collision meshes require 90° rotation compensation in URDF
- This indicates the physical bracket geometry doesn't match the desired X-axis rotation

## Redesign Goals

### Target Configuration
- Remove need for visual/collision rotation compensation
- Design bracket with horizontal cantilever platform for servo mounting
- Increase Z-coordinate of joint origin to accommodate cantilever height
- Maintain compatibility with existing thigh and shin links

### Expected Changes
1. **New Mesh Files:** Create l11_redesigned.STL, l21_redesigned.STL, l31_redesigned.STL, l41_redesigned.STL
2. **Joint Origin Update:** Increase Z-coordinate from 0.055 to ~0.080 (add 25mm for cantilever)
3. **Remove Rotation Compensation:** Set visual/collision rpy to "0 0 0"
4. **Maintain Mass:** Keep mass within ±20% of 0.25 kg

## Restoration Instructions

To restore the original configuration:

```bash
# Restore visual meshes
cp backups/hip_bracket_redesign_20260207_102358/meshes/l*.STL src/dog2_description/meshes/

# Restore collision meshes
cp backups/hip_bracket_redesign_20260207_102358/meshes/collision/l*_collision.STL src/dog2_description/meshes/collision/

# Restore URDF
cp backups/hip_bracket_redesign_20260207_102358/urdf/dog2.urdf.xacro src/dog2_description/urdf/

# Rebuild
cd ~/aperfect/carbot_ws
colcon build --packages-select dog2_description
source install/setup.bash
```

## Notes

- This backup was created as part of the hip-bracket-mechanical-redesign spec
- The current URDF already has X-axis rotation configured (modified 2026-02-02)
- The mesh files still reflect the original Z-axis rotation design
- This redesign will create new mesh files that match the X-axis rotation natively
- Requirement reference: 3.2 (Create backup copies of original mesh files before modification)
