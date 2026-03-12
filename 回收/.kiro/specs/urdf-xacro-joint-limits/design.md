# Design Document: URDF Xacro Joint Limits Parameterization

## Overview

This design transforms the Dog2 robot's URDF from hardcoded `continuous` joints to a parameterized Xacro-based system with realistic `revolute` joint limits. The current implementation allows unlimited 360° rotation, which is physically impossible and causes MPC/WBC solvers to compute unrealistic trajectories (e.g., "knee reversal"). 

The solution introduces Xacro macros and properties to:
- Define joint limits centrally (±150° for hips, ±160° for knees)
- Ensure consistency across all four legs
- Enable easy parameter tuning for obstacle-crossing experiments
- Maintain backward compatibility with existing controllers

## Architecture

### File Structure

```
src/dog2_description/urdf/
├── dog2.urdf.xacro          # Single Xacro file (source of truth)
│                            # Contains: properties, macros, robot definition
└── dog2.urdf                # Generated URDF (build artifact)
```

**Rationale for Single File**:
- Simpler to maintain (no need to track multiple includes)
- Easier to understand (all logic in one place)
- Sufficient for this project size (4 legs, ~500 lines)
- Faster to edit (no jumping between files)

### Component Hierarchy

```
dog2.urdf.xacro (single file)
├── Section 1: Properties (joint limits)
├── Section 2: Leg macro definition
├── Section 3: Base link
├── Section 4: Leg instantiations × 4
│   ├── Leg 1 (front-right): j1, j11, j111
│   ├── Leg 2 (front-left):  j2, j21, j211
│   ├── Leg 3 (rear-left):   j3, j31, j311
│   └── Leg 4 (rear-right):  j4, j41, j411
└── Section 5: ROS 2 Control & Gazebo configs
```

## Current State Analysis

### Existing Files

1. **dog2.urdf** (1000+ lines): Complete robot definition
   - Contains: world link, base_link, 4 complete legs (16 links, 12 joints)
   - All hip/knee joints are `type="continuous"` ❌
   - Includes ROS 2 Control configuration
   - This is the **source of truth** currently used by the system

2. **dog2.urdf.xacro** (40 lines): Incomplete Xacro wrapper
   - Only defines base_link
   - Includes `links.xacro` for leg definitions
   - Missing: world link, ROS 2 Control, complete Gazebo config
   - **Not currently used** by the system

3. **links.xacro** (150 lines): Partial leg definition
   - Only defines Leg 1 (l1, l11, l111)
   - Missing: Legs 2, 3, 4
   - Has `type="continuous"` joints ❌

### Strategy Decision

We will **rewrite dog2.urdf.xacro** to be a complete, self-contained file that:
- Incorporates all content from dog2.urdf
- Adds Xacro parameterization
- Converts continuous → revolute joints
- Generates dog2.urdf as a build artifact

We will **not use** the existing links.xacro (it's incomplete).

## Components and Interfaces

### 1. Parameter Definitions (Section 1 of dog2.urdf.xacro)

**Purpose**: Central repository for all joint limit parameters at the top of the file.

**Properties**:
```xml
<!-- Hip joint limits: ±150° = ±2.618 rad -->
<xacro:property name="hip_lower_limit" value="-2.618"/>
<xacro:property name="hip_upper_limit" value="2.618"/>
<xacro:property name="hip_effort" value="50"/>
<xacro:property name="hip_velocity" value="20"/>

<!-- Knee joint limits: ±160° = ±2.8 rad -->
<xacro:property name="knee_lower_limit" value="-2.8"/>
<xacro:property name="knee_upper_limit" value="2.8"/>
<xacro:property name="knee_effort" value="50"/>
<xacro:property name="knee_velocity" value="20"/>

<!-- Prismatic joint limits (unchanged) -->
<xacro:property name="prismatic_effort" value="100"/>
<xacro:property name="prismatic_velocity" value="5"/>
```

**Rationale**:
- Hip ±150°: Covers vertical (0°), forward swing (+90°), backward swing (-90°), extreme retraction (±150°)
- Knee ±160°: Enables bidirectional folding through 0° singularity (elbow: -160°, straight: 0°, knee: +160°)

### 2. Leg Macro (Section 2 of dog2.urdf.xacro)

**Purpose**: Reusable template for generating identical leg structures.

**Macro Signature**:

```xml
<xacro:macro name="leg" params="leg_num leg_side parent_link origin_xyz origin_rpy prismatic_lower prismatic_upper">
  <!-- Parameters:
       leg_num: 1-4 (leg identifier)
       leg_side: "right" or "left" (for mesh mirroring)
       parent_link: "base_link"
       origin_xyz: "x y z" (attachment point)
       origin_rpy: "r p y" (attachment orientation)
       prismatic_lower: lower limit for prismatic joint
       prismatic_upper: upper limit for prismatic joint
  -->
  
  <!-- Prismatic joint (vertical sliding) -->
  <joint name="j${leg_num}" type="prismatic">
    <origin xyz="${origin_xyz}" rpy="${origin_rpy}"/>
    <parent link="${parent_link}"/>
    <child link="l${leg_num}"/>
    <axis xyz="-1 0 0"/>
    <limit lower="${prismatic_lower}" upper="${prismatic_upper}" 
           effort="${prismatic_effort}" velocity="${prismatic_velocity}"/>
  </joint>
  
  <!-- Hip joint (revolute, replaces continuous) -->
  <joint name="j${leg_num}1" type="revolute">
    <origin xyz="..." rpy="..."/>
    <parent link="l${leg_num}"/>
    <child link="l${leg_num}1"/>
    <axis xyz="-1 0 0"/>
    <limit lower="${hip_lower_limit}" upper="${hip_upper_limit}"
           effort="${hip_effort}" velocity="${hip_velocity}"/>
  </joint>
  
  <!-- Knee joint (revolute, replaces continuous) -->
  <joint name="j${leg_num}11" type="revolute">
    <origin xyz="..." rpy="..."/>
    <parent link="l${leg_num}1"/>
    <child link="l${leg_num}11"/>
    <axis xyz="-1 0 0"/>
    <limit lower="${knee_lower_limit}" upper="${knee_upper_limit}"
           effort="${knee_effort}" velocity="${knee_velocity}"/>
  </joint>
  
  <!-- Links and transmissions omitted for brevity -->
</xacro:macro>
```

**Key Design Decisions**:
1. **Parameterized origins**: Each leg has different attachment points, passed as parameters
2. **Shared limits**: All legs reference the same global properties
3. **Unique naming**: `leg_num` ensures unique joint/link names (j11, j21, j31, j41)

### 3. Main Robot Definition (Sections 3-6 of dog2.urdf.xacro)

**Structure**:
```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="dog2">
  
  <!-- ============================================ -->
  <!-- SECTION 1: PROPERTY DEFINITIONS              -->
  <!-- ============================================ -->
  
  <!-- Hip joint limits: ±150° = ±2.618 rad -->
  <xacro:property name="hip_lower_limit" value="-2.618"/>
  <xacro:property name="hip_upper_limit" value="2.618"/>
  <xacro:property name="hip_effort" value="50"/>
  <xacro:property name="hip_velocity" value="20"/>

  <!-- Knee joint limits: ±160° = ±2.8 rad -->
  <xacro:property name="knee_lower_limit" value="-2.8"/>
  <xacro:property name="knee_upper_limit" value="2.8"/>
  <xacro:property name="knee_effort" value="50"/>
  <xacro:property name="knee_velocity" value="20"/>

  <!-- Prismatic joint limits -->
  <xacro:property name="prismatic_effort" value="100"/>
  <xacro:property name="prismatic_velocity" value="5"/>
  
  <!-- ============================================ -->
  <!-- SECTION 2: LEG MACRO DEFINITION              -->
  <!-- ============================================ -->
  
  <xacro:macro name="leg" params="leg_num leg_side parent_link origin_xyz origin_rpy prismatic_lower prismatic_upper">
    <!-- Macro content here (see previous section) -->
  </xacro:macro>
  
  <!-- ============================================ -->
  <!-- SECTION 3: WORLD AND BASE LINKS              -->
  <!-- ============================================ -->
  
  <link name="world"/>
  
  <joint name="world_joint" type="fixed">
    <parent link="world"/>
    <child link="base_link"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
  </joint>
  
  <link name="base_link">
    <!-- Use parameters from dog2.urdf: mass=6.0, xyz="1.2272 -0.7470 0.2649" -->
  </link>
  
  <!-- ============================================ -->
  <!-- SECTION 4: LEG INSTANTIATIONS                -->
  <!-- ============================================ -->
  
  <xacro:leg leg_num="1" leg_side="right" parent_link="base_link"
             origin_xyz="1.1026 -0.80953 0.2649" origin_rpy="1.5708 0 0"
             prismatic_lower="-0.111" prismatic_upper="0.008"/>
  
  <xacro:leg leg_num="2" leg_side="left" parent_link="base_link"
             origin_xyz="1.3491 -0.80953 0.2649" origin_rpy="1.5708 0 0"
             prismatic_lower="-0.008" prismatic_upper="0.111"/>
  
  <xacro:leg leg_num="3" leg_side="left" parent_link="base_link"
             origin_xyz="1.3491 -0.68953 0.2649" origin_rpy="1.5708 0 -3.1416"
             prismatic_lower="-0.111" prismatic_upper="0.008"/>
  
  <xacro:leg leg_num="4" leg_side="right" parent_link="base_link"
             origin_xyz="1.1071 -0.68953 0.2649" origin_rpy="1.5708 0 -3.1416"
             prismatic_lower="-0.008" prismatic_upper="0.111"/>
  
  <!-- ============================================ -->
  <!-- SECTION 5: ROS 2 CONTROL                     -->
  <!-- ============================================ -->
  
  <ros2_control name="GazeboSystem" type="system">
    <hardware>
      <plugin>gazebo_ros2_control/GazeboSystem</plugin>
    </hardware>
    
    <!-- All 12 joints (j1-j4, j11-j41, j111-j411) -->
    <!-- Each with: command_interface (effort, position) -->
    <!--            state_interface (position, velocity, effort) -->
  </ros2_control>
  
  <!-- ============================================ -->
  <!-- SECTION 6: GAZEBO PLUGIN                     -->
  <!-- ============================================ -->
  
  <gazebo>
    <plugin filename="libgazebo_ros2_control.so" name="gazebo_ros2_control">
      <robot_param>robot_description</robot_param>
      <robot_param_node>robot_state_publisher</robot_param_node>
    </plugin>
  </gazebo>
</robot>
```

## Data Models

### Joint Limit Configuration

```python
@dataclass
class JointLimits:
    lower: float  # radians
    upper: float  # radians
    effort: float  # Nm
    velocity: float  # rad/s
    
    def validate(self):
        assert self.lower < self.upper, "Lower must be < upper"
        assert self.effort > 0, "Effort must be positive"
        assert self.velocity > 0, "Velocity must be positive"

hip_limits = JointLimits(
    lower=-2.618,  # -150°
    upper=2.618,   # +150°
    effort=50,
    velocity=20
)

knee_limits = JointLimits(
    lower=-2.8,    # -160°
    upper=2.8,     # +160°
    effort=50,
    velocity=20
)
```

### Leg Configuration

```python
@dataclass
class LegConfig:
    leg_num: int  # 1-4
    leg_side: str  # "right" or "left"
    origin_xyz: Tuple[float, float, float]
    origin_rpy: Tuple[float, float, float]
    prismatic_lower: float
    prismatic_upper: float

legs = [
    LegConfig(1, "right", (1.1026, -0.80953, 0.2649), (1.5708, 0, 0), -0.111, 0.008),
    LegConfig(2, "left",  (1.3491, -0.80953, 0.2649), (1.5708, 0, 0), -0.008, 0.111),
    LegConfig(3, "left",  (1.3491, -0.68953, 0.2649), (1.5708, 0, -3.1416), -0.111, 0.008),
    LegConfig(4, "right", (1.1071, -0.68953, 0.2649), (1.5708, 0, -3.1416), -0.008, 0.111),
]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: All revolute joints have correct type and limits

*For any* generated URDF, all hip joints (j11, j21, j31, j41) and knee joints (j111, j211, j311, j411) should have type="revolute" and their limit values should match the Xacro properties (hip: ±2.618 rad, knee: ±2.8 rad).

**Validates: Requirements 2.1, 2.2, 2.3, 2.5, 3.1, 3.2, 3.3, 3.5, 8.1, 8.2**

### Property 2: No continuous joints exist

*For any* generated URDF, no joint should have type="continuous".

**Validates: Requirements 8.3**

### Property 3: All legs have identical joint limits

*For any* pair of legs (i, j) where i ≠ j, the hip joint limits of leg i should equal the hip joint limits of leg j, and the knee joint limits of leg i should equal the knee joint limits of leg j.

**Validates: Requirements 2.4, 3.4, 8.4**

### Property 4: Knee range includes zero

*For any* knee joint, the lower limit should be negative and the upper limit should be positive, ensuring 0° (straight leg) is a valid configuration.

**Validates: Requirements 3.6**

### Property 5: Backward compatibility - names preserved

*For any* generated URDF, the set of link names and joint names should be identical to the original URDF.

**Validates: Requirements 5.1, 5.2**

### Property 6: Backward compatibility - structure preserved

*For any* generated URDF, all transmission definitions, Gazebo plugin configurations, and coordinate frame transformations (origin xyz/rpy) should match the original URDF within numerical tolerance (1e-6).

**Validates: Requirements 5.3, 5.4, 5.5**

### Property 7: Xacro property substitution

*For any* revolute joint in the generated URDF, if it is a hip joint, its limit values should equal the hip_lower_limit and hip_upper_limit properties; if it is a knee joint, its limit values should equal the knee_lower_limit and knee_upper_limit properties.

**Validates: Requirements 2.5, 3.5**

## Error Handling

### Xacro Processing Errors

**Error Type**: Invalid property reference
```xml
<limit lower="${hip_lower_limt}"/>  <!-- Typo in property name -->
```
**Handling**: Xacro processor will fail with clear error message indicating undefined property.

**Error Type**: Invalid limit values
```xml
<xacro:property name="hip_lower_limit" value="2.8"/>
<xacro:property name="hip_upper_limit" value="-2.8"/>
```
**Handling**: Validation script detects lower > upper and reports error before build.

### Build System Errors

**Error Type**: Missing Xacro file
**Handling**: CMakeLists.txt checks for file existence, reports clear error if missing.

**Error Type**: Xacro to URDF conversion failure
**Handling**: Build system captures stderr, displays Xacro error messages to user.

### Runtime Validation Errors

**Error Type**: Inconsistent leg limits
**Handling**: Validation script compares all 4 legs, reports which legs have mismatched limits.

**Error Type**: Continuous joints detected
**Handling**: Validation script scans for type="continuous", reports joint names that need fixing.

## Testing Strategy

### Unit Tests

Unit tests verify specific examples and edge cases:

1. **Xacro Property Parsing**: Verify properties file defines all required parameters
2. **Macro Invocation**: Verify leg macro generates correct number of links/joints
3. **Documentation Presence**: Verify required comments exist in Xacro files
4. **Build System Integration**: Verify CMakeLists.txt processes Xacro correctly
5. **Validation Script**: Verify script detects common errors (continuous joints, mismatched limits)

### Property-Based Tests

Property tests verify universal correctness across all inputs using a PBT library (e.g., Hypothesis for Python, fast-check for TypeScript):

Each test should run minimum 100 iterations and be tagged with:
```python
# Feature: urdf-xacro-joint-limits, Property N: [property text]
```

**Test 1: All revolute joints have correct limits**
- Generate URDF from Xacro
- Parse all joints
- For each hip/knee joint, assert type="revolute" and limits match properties
- **Feature: urdf-xacro-joint-limits, Property 1: All revolute joints have correct type and limits**

**Test 2: No continuous joints**
- Generate URDF from Xacro
- Parse all joints
- Assert no joint has type="continuous"
- **Feature: urdf-xacro-joint-limits, Property 2: No continuous joints exist**

**Test 3: Leg symmetry**
- Generate URDF from Xacro
- Parse all leg joints
- For each pair of legs, assert hip limits are equal and knee limits are equal
- **Feature: urdf-xacro-joint-limits, Property 3: All legs have identical joint limits**

**Test 4: Zero in knee range**
- Generate URDF from Xacro
- Parse all knee joints
- For each knee, assert lower < 0 and upper > 0
- **Feature: urdf-xacro-joint-limits, Property 4: Knee range includes zero**

**Test 5: Name preservation**
- Generate URDF from Xacro
- Parse link and joint names
- Compare with original URDF
- Assert sets are equal
- **Feature: urdf-xacro-joint-limits, Property 5: Backward compatibility - names preserved**

**Test 6: Structure preservation**
- Generate URDF from Xacro
- Parse transmissions, Gazebo plugins, origins
- Compare with original URDF
- Assert all match within tolerance
- **Feature: urdf-xacro-joint-limits, Property 6: Backward compatibility - structure preserved**

**Test 7: Property substitution correctness**
- Modify Xacro properties (e.g., hip_lower_limit = -3.0)
- Regenerate URDF
- Parse hip joints
- Assert all hip joints have lower limit = -3.0
- **Feature: urdf-xacro-joint-limits, Property 7: Xacro property substitution**

### Integration Tests

1. **Gazebo Loading**: Launch Gazebo with generated URDF, verify no errors
2. **ROS 2 Control**: Verify controllers can command all joints
3. **MPC/WBC Compatibility**: Run existing MPC/WBC nodes, verify no crashes
4. **Visualization**: Load URDF in RViz, verify robot appears correctly

### Validation Script

Create `scripts/validate_urdf_limits.py`:
```python
#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import sys

def validate_urdf(urdf_path):
    tree = ET.parse(urdf_path)
    root = tree.getroot()
    
    errors = []
    
    # Check for continuous joints
    for joint in root.findall('.//joint[@type="continuous"]'):
        errors.append(f"Continuous joint found: {joint.get('name')}")
    
    # Check hip joints
    hip_joints = ['j11', 'j21', 'j31', 'j41']
    hip_limits = []
    for name in hip_joints:
        joint = root.find(f'.//joint[@name="{name}"]')
        if joint is None:
            errors.append(f"Hip joint not found: {name}")
            continue
        if joint.get('type') != 'revolute':
            errors.append(f"Hip joint {name} is not revolute")
        limit = joint.find('limit')
        hip_limits.append((float(limit.get('lower')), float(limit.get('upper'))))
    
    # Check hip symmetry
    if len(set(hip_limits)) > 1:
        errors.append(f"Hip joints have inconsistent limits: {hip_limits}")
    
    # Similar checks for knee joints...
    
    if errors:
        print("Validation FAILED:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("Validation PASSED")
        sys.exit(0)

if __name__ == '__main__':
    validate_urdf(sys.argv[1])
```

## Build System Integration

### CMakeLists.txt Modifications

```cmake
# Find xacro
find_package(xacro REQUIRED)

# Generate URDF from Xacro
add_custom_command(
  OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/urdf/dog2.urdf
  COMMAND xacro ${CMAKE_CURRENT_SOURCE_DIR}/urdf/dog2.urdf.xacro -o ${CMAKE_CURRENT_SOURCE_DIR}/urdf/dog2.urdf
  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/urdf/dog2.urdf.xacro
  COMMENT "Generating URDF from Xacro"
)

add_custom_target(generate_urdf ALL DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/urdf/dog2.urdf)

# Validate generated URDF
add_custom_command(
  TARGET generate_urdf POST_BUILD
  COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/scripts/validate_urdf_limits.py ${CMAKE_CURRENT_SOURCE_DIR}/urdf/dog2.urdf
  COMMENT "Validating generated URDF"
)

# Install URDF
install(FILES urdf/dog2.urdf DESTINATION share/${PROJECT_NAME}/urdf)
```

### Launch File Compatibility

Existing launch files should work without modification:
```python
robot_description = Command(['xacro ', urdf_file])
# OR
robot_description = open(urdf_file).read()
```

Both approaches will work since we generate `dog2.urdf` as a build artifact.

## Migration Strategy

### Phase 1: Backup and Preparation
1. Backup current `dog2.urdf` → `dog2.urdf.backup_xacro_migration`
2. Backup current `dog2.urdf.xacro` → `dog2.urdf.xacro.old`
3. Document current system state (which files are used by launch files)

### Phase 2: Create Complete Xacro File (No Functional Changes)
1. Copy all content from `dog2.urdf` into new `dog2.urdf.xacro`
2. Add Xacro namespace: `xmlns:xacro="http://www.ros.org/wiki/xacro"`
3. Add property definitions at top (but keep continuous joints initially)
4. Generate URDF: `xacro dog2.urdf.xacro > dog2_generated.urdf`
5. Verify: `diff dog2.urdf dog2_generated.urdf` (should be minimal/whitespace only)

### Phase 3: Add Leg Macro (Still No Functional Changes)
1. Extract one leg's definition into a macro
2. Replace all 4 legs with macro invocations
3. Regenerate and verify diff (should still match functionally)

### Phase 4: Convert to Revolute Joints
1. Update properties: hip ±2.618 rad, knee ±2.8 rad
2. Change joint type from `continuous` to `revolute` in macro
3. Add `lower` and `upper` attributes to limit tags
4. Regenerate URDF
5. Run validation script
6. Test in Gazebo (expect different behavior - this is the goal!)

### Phase 5: Cleanup and Integration
1. Update CMakeLists.txt to auto-generate URDF from Xacro
2. Remove `dog2.urdf` from version control (add to .gitignore)
3. Update documentation
4. Verify all launch files work with generated URDF

## Documentation

### Header Comment Template

```xml
<?xml version="1.0"?>
<!--
  Dog2 Robot Description (Xacro Source)
  
  This file defines the Dog2 quadruped robot with parameterized joint limits.
  All configuration is in this single file for simplicity.
  
  JOINT LIMITS:
  - Hip joints (j11, j21, j31, j41): ±150° (±2.618 rad)
    * 0°: Leg vertical (default stance)
    * +90°: Leg forward (climbing phase)
    * -90°: Leg backward (retraction phase)
    * ±150°: Extreme folding for morphing
  
  - Knee joints (j111, j211, j311, j411): ±160° (±2.8 rad)
    * 0°: Leg straight (singularity point during morphing)
    * -160°: Elbow configuration (shin behind thigh)
    * +160°: Knee configuration (shin in front of thigh)
    * WARNING: 0° is a singularity - controller must handle carefully
  
  MODIFYING LIMITS:
  1. Edit the properties section at the top of this file
  2. Run: colcon build --packages-select dog2_description
  3. Verify: scripts/validate_urdf_limits.py urdf/dog2.urdf
  
  OBSTACLE CROSSING PHASES:
  - Phase 1 (Approach): Hip 0° to +45°, knee -90° (elbow)
  - Phase 2 (Climb): Hip +45° to +90°, knee -90° to 0° (straightening)
  - Phase 3 (Morph): Hip +90°, knee 0° to +90° (elbow → knee transition)
  - Phase 4 (Descend): Hip +90° to 0°, knee +90° (knee configuration)
-->
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="dog2">
```

This design provides a robust, maintainable solution for managing joint limits while preserving backward compatibility and enabling easy parameter tuning for obstacle-crossing experiments.
