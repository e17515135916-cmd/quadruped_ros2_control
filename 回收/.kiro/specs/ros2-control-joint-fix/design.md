# Design Document: ros2-control-joint-fix

## Overview

This design addresses the missing fourth joint (KFE knee joint) in the DOG2 robot's URDF xacro file. The robot's control system correctly expects 4 joints per leg (16 total), but the current xacro leg macro only generates 3 joints per leg. Additionally, the j111 joint is incorrectly labeled as "Knee joint" when it should be "Hip flexion/extension (HFE)".

The solution involves:
1. Adding the missing fourth link (l${leg_num}1111 - foot/shin) to the leg macro
2. Adding the missing fourth joint (j${leg_num}1111 - KFE knee) to the leg macro
3. Correcting the joint labels and comments for clarity
4. Using the correct inertial properties from the original dog2.urdf file
5. Ensuring Gazebo friction configuration is applied to the foot link

## Architecture

### Current Structure (Incorrect - 3 joints per leg)

```
base_link
  └─ j1 (prismatic) → l1 (rail link)
      └─ j11 (revolute, HAA) → l11 (hip link)
          └─ j111 (revolute, HFE - mislabeled as "Knee") → l111 (thigh link)
              └─ [MISSING: j1111 (revolute, KFE) → l1111 (foot/shin link)]
```

### Target Structure (Correct - 4 joints per leg)

```
base_link
  └─ j1 (prismatic) → l1 (rail link)
      └─ j11 (revolute, HAA) → l11 (hip link)
          └─ j111 (revolute, HFE) → l111 (thigh link)
              └─ j1111 (revolute, KFE) → l1111 (foot/shin link)
```

### Joint Naming Convention

| Joint Name | Type | Physical Function | Description |
|------------|------|-------------------|-------------|
| j${leg_num} | prismatic | Rail | Linear sliding joint for leg positioning |
| j${leg_num}1 | revolute | HAA | Hip Abduction/Adduction (lateral movement) |
| j${leg_num}11 | revolute | HFE | Hip Flexion/Extension (forward/backward swing) |
| j${leg_num}111 | revolute | KFE | Knee Flexion/Extension (shin bending) |

## Components and Interfaces

### 1. Leg Macro Modification

**File**: `src/dog2_description/urdf/dog2.urdf.xacro`

**Changes Required**:
- Add fourth link definition (l${leg_num}1111) after the current l${leg_num}111 link
- Add fourth joint definition (j${leg_num}1111) after the current j${leg_num}111 joint
- Update comment for j${leg_num}11 from "Knee joint" to "Hip flexion/extension (HFE)"
- Add comment for j${leg_num}1111 as "Knee joint (KFE)"
- Add Gazebo friction configuration for l${leg_num}1111

### 2. Inertial Properties Source

**Reference File**: `src/dog2_description/urdf/dog2.urdf`

The fourth link (l1111) inertial properties from the original file:
```xml
<inertial>
  <origin rpy="0 0 0" xyz="0.0254901816398352 -0.143524743603395 -0.0694046953395906"/>
  <mass value="0.5"/>
  <inertia ixx="0.004517" ixy="0.00000870" ixz="0.00000420" 
           iyy="0.000975" iyz="-0.00176971" izz="0.003666"/>
</inertial>
```

**Note**: For legs 3 and 4 (rear legs), the inertia X-coordinate should be negated to account for mirrored geometry, similar to how it's done for the thigh and shin links.

### 3. Joint Configuration

**Fourth Joint (j${leg_num}1111) Configuration**:
```xml
<joint name="j${leg_num}1111" type="revolute">
  <origin rpy="0 0 0" xyz="0 -0.15201 0.12997"/>
  <parent link="l${leg_num}111"/>
  <child link="l${leg_num}1111"/>
  <axis xyz="-1 0 0"/>
  <limit effort="50" lower="-2.8" upper="0.0" velocity="20"/>
</joint>
```

### 4. Mesh Files

**Available Mesh Files** (already exist):
- `l1111.STL` - Leg 1 foot
- `l2111.STL` - Leg 2 foot
- `l3111.STL` - Leg 3 foot
- `l4111.STL` - Leg 4 foot

### 5. Gazebo Configuration

**Friction Configuration for Foot Link**:
```xml
<gazebo reference="l${leg_num}1111">
  <mu1>1.0</mu1>
  <mu2>1.0</mu2>
  <kp>1000000.0</kp>
  <kd>100.0</kd>
  <minDepth>0.001</minDepth>
  <maxVel>0.1</maxVel>
  <material>Gazebo/Grey</material>
</gazebo>
```

This configuration prevents the "ice skating" bug by providing appropriate friction coefficients.

## Data Models

### Leg Macro Parameters

The leg macro already has the necessary parameters. No new parameters are required for adding the fourth joint.

**Existing Parameters Used**:
- `leg_num`: Leg number (1-4)
- `origin_xyz`, `origin_rpy`: Position and orientation of the prismatic joint
- `prismatic_lower`, `prismatic_upper`: Prismatic joint limits
- `thigh_inertia_xyz`, `shin_inertia_xyz`: Inertial properties for thigh and shin

**New Inertial Property Needed**:
- `foot_inertia_xyz`: Inertial center of mass for the foot link (l${leg_num}1111)

### Inertial Properties for Each Leg

Based on the pattern from thigh and shin inertias:

**Legs 1 & 2 (Front legs - positive X)**:
```
foot_inertia_xyz = "0.0254901816398352 -0.143524743603395 -0.0694046953395906"
```

**Leg 3 (Rear left - negative X, mirrored)**:
```
foot_inertia_xyz = "-0.0265098183601649 -0.143524743603395 -0.0694046953395908"
```

**Leg 4 (Rear right - negative X, mirrored)**:
```
foot_inertia_xyz = "-0.0265089672547710 -0.1429895138560395 -0.0691152554666486"
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Complete Joint Structure
*For any* leg instantiation (leg_num 1-4), the generated URDF should contain exactly 4 joints: j${leg_num}, j${leg_num}1, j${leg_num}11, j${leg_num}111

**Validates: Requirements 1.2, 1.3**

### Property 2: Complete Link Structure  
*For any* leg instantiation (leg_num 1-4), the generated URDF should contain exactly 5 links: l${leg_num}, l${leg_num}1, l${leg_num}11, l${leg_num}111, l${leg_num}1111

**Validates: Requirements 1.5, 3.1**

### Property 3: Joint-Link Connectivity
*For any* leg, each joint should connect exactly two links in the correct parent-child relationship following the kinematic chain

**Validates: Requirements 3.2**

### Property 4: ros2_control Consistency
*For any* joint defined in the URDF, there should be a corresponding entry in the ros2_control block with appropriate command and state interfaces

**Validates: Requirements 4.1, 4.2**

### Property 5: Controller Configuration Consistency
*For any* joint defined in the URDF ros2_control block, there should be a corresponding entry in the ros2_controllers.yaml file

**Validates: Requirements 2.1, 2.3**

### Property 6: Mesh File Existence
*For any* link with visual or collision geometry, the referenced mesh file should exist in the meshes directory

**Validates: Requirements 3.6**

### Property 7: Inertial Property Mirroring
*For any* rear leg (leg 3 or 4), the inertial X-coordinate should be negative (mirrored) compared to front legs

**Validates: Requirements 3.1**

### Property 8: Gazebo Friction Configuration
*For any* foot link (l${leg_num}1111), there should be a Gazebo reference block with friction parameters defined

**Validates: Requirements 3.7**

## Error Handling

### Missing Mesh Files
- **Error**: Mesh file not found during URDF processing
- **Handling**: Validate mesh file existence before building
- **Recovery**: Use placeholder geometry or fail with clear error message

### Invalid Joint Limits
- **Error**: Joint limits violate physical constraints
- **Handling**: Validate joint limits against known safe ranges
- **Recovery**: Use conservative default limits

### Inertial Property Errors
- **Error**: Invalid or missing inertial properties
- **Handling**: Validate inertial tensors are positive definite
- **Recovery**: Use minimal valid inertial properties with warning

### Gazebo Launch Failures
- **Error**: Gazebo fails to load robot model
- **Handling**: Check Gazebo error logs for specific joint/link issues
- **Recovery**: Provide diagnostic script to identify problematic joints

## Testing Strategy

### Unit Tests

Unit tests will verify specific examples and edge cases:

1. **Test URDF Generation**: Verify xacro processes without errors
2. **Test Joint Count**: Verify exactly 16 joints are generated (4 legs × 4 joints)
3. **Test Link Count**: Verify exactly 21 links are generated (1 base + 4 legs × 5 links)
4. **Test Mesh File References**: Verify all mesh files exist
5. **Test ros2_control Block**: Verify all 16 joints have control interfaces
6. **Test Controller YAML**: Verify all 16 joints are listed in controller configuration

### Property-Based Tests

Property-based tests will verify universal properties across all inputs:

1. **Property Test: Joint Structure Completeness**
   - Generate random leg numbers (1-4)
   - Verify each leg has exactly 4 joints with correct naming pattern
   - **Validates: Requirements 1.2, 1.3**

2. **Property Test: Link Structure Completeness**
   - Generate random leg numbers (1-4)
   - Verify each leg has exactly 5 links with correct naming pattern
   - **Validates: Requirements 1.5, 3.1**

3. **Property Test: Joint-Link Connectivity**
   - For all joints in the URDF
   - Verify parent and child links exist and form valid kinematic chain
   - **Validates: Requirements 3.2**

4. **Property Test: Control Configuration Consistency**
   - For all joints in URDF
   - Verify corresponding entries exist in ros2_control block and YAML file
   - **Validates: Requirements 2.1, 2.3, 4.1**

5. **Property Test: Inertial Mirroring**
   - For all rear legs (3, 4)
   - Verify inertial X-coordinates are negative
   - **Validates: Requirements 3.1**

### Integration Tests

1. **Gazebo Launch Test**: Launch Gazebo and verify robot loads without errors
2. **Joint State Test**: Verify joint_state_broadcaster publishes all 16 joint states
3. **Control Test**: Send effort commands to all 16 joints and verify acceptance

### Validation Script

Create a Python validation script that:
- Parses the generated URDF
- Validates joint and link structure
- Compares URDF with ros2_control block
- Compares URDF with ros2_controllers.yaml
- Reports any mismatches or missing elements

This script can be run as part of the build process or manually for debugging.
