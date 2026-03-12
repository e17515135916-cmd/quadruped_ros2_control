# Leg Orientation Fix Summary

## Problem Description

After implementing the hip bracket redesign with box primitives, all four legs were not pointing downward as expected. The visualization showed:
- Front legs (Leg 1 & 2): Correct orientation
- Rear legs (Leg 3 & 4): **Wrong orientation** - pointing in opposite direction

## Root Cause

The issue was in the `hip_axis` parameter for rear legs in the URDF configuration:

```xml
<!-- INCORRECT - Rear legs had negative X-axis -->
<xacro:leg leg_num="3" ... hip_axis="-1 0 0"/>
<xacro:leg leg_num="4" ... hip_axis="-1 0 0"/>
```

This caused the rear legs' hip joints to rotate in the opposite direction compared to the front legs.

## Solution Applied

Changed the `hip_axis` parameter for both rear legs from `-1 0 0` to `1 0 0`:

```xml
<!-- CORRECT - All legs now use positive X-axis -->
<xacro:leg leg_num="3" ... hip_axis="1 0 0"/>
<xacro:leg leg_num="4" ... hip_axis="1 0 0"/>
```

## Files Modified

1. **src/dog2_description/urdf/dog2.urdf.xacro**
   - Line ~450: Changed Leg 3 hip_axis from "-1 0 0" to "1 0 0"
   - Line ~460: Changed Leg 4 hip_axis from "-1 0 0" to "1 0 0"

## Expected Result

After this fix, when all joint angles are set to zero:
- ✅ All four legs should point **downward** (dog-style)
- ✅ All legs should be parallel to each other
- ✅ Configuration should resemble a quadruped dog, not a spider

## Testing

To verify the fix:

```bash
# Method 1: Use the test script
./test_fixed_leg_orientation.sh

# Method 2: Manual testing
# 1. Launch RViz
ros2 launch dog2_description view_dog2.launch.py

# 2. In another terminal, set all joints to zero
python3 test_leg_orientation_fix.py
```

## Related Tasks

- **Spec**: `.kiro/specs/hip-bracket-mechanical-redesign/`
- **Task 5.1**: Remove hip_joint_rpy rotation for front legs ✅ COMPLETED
- **Task 5.2**: Update hip_joint_rpy for rear legs ✅ COMPLETED
- **Task 5.3**: Verify URDF parses after RPY changes ✅ COMPLETED

## Technical Details

### Hip Joint Axis Convention

For a dog-style quadruped with X-axis pointing forward:
- **Hip joint axis**: `1 0 0` (X-axis)
- **Rotation**: Forward-backward motion (flexion/extension)
- **Zero angle**: Leg points downward

### Why Rear Legs Had Different Axis

The rear legs are mounted with 180° rotation about X-axis (`hip_joint_rpy="3.1416 0 0"`), which flips their local coordinate system. However, the hip joint axis should still be `1 0 0` in the parent frame to maintain consistent rotation direction across all legs.

## Verification Checklist

- [x] URDF parses without errors
- [x] Package builds successfully
- [ ] RViz visualization shows all legs pointing downward
- [ ] Hip joints rotate in correct direction
- [ ] Standing posture looks correct
- [ ] Walking gait works properly

## Date

2026-02-07

## Status

✅ **FIX APPLIED** - Ready for testing in RViz and Gazebo
