# Design Document

## Overview

This design document describes the approach to fix incorrect inertia origin positions for specific links in the Dog2 quadruped robot's URDF model. The current xacro-based URDF uses a single macro to generate all four legs with identical inertia parameters. However, legs 3 and 4 require individualized inertia corrections due to manufacturing variations or design differences.

The solution modifies the existing xacro macro to support optional per-link inertia overrides while maintaining backward compatibility and code reusability.

## Architecture

### Current Structure

```
dog2.urdf.xacro
├── Properties (joint limits, efforts, velocities)
├── Base link definition
└── Leg macro (generates 4 identical legs)
    ├── Hip link (l${leg_num})
    ├── Thigh link (l${leg_num}1)
    ├── Upper leg link (l${leg_num}11)  ← Needs correction for leg 3
    └── Lower leg link (l${leg_num}111) ← Needs correction for legs 3 and 4
```

### Proposed Structure

```
dog2.urdf.xacro
├── Properties (joint limits, efforts, velocities)
├── Inertia override properties (new)
│   ├── leg3_thigh_inertia_xyz
│   ├── leg3_shin_inertia_xyz
│   └── leg4_shin_inertia_xyz
├── Base link definition
└── Enhanced leg macro (supports inertia overrides)
    ├── Parameters: leg_num, origin_xyz, origin_rpy, prismatic_lower, prismatic_upper
    ├── New parameters: thigh_inertia_xyz, shin_inertia_xyz (optional)
    └── Logic: Use override if provided, else use default
```

## Components and Interfaces

### 1. Inertia Override Properties

**Purpose**: Define corrected inertia origin positions for specific legs

**Location**: Top of dog2.urdf.xacro file, after existing properties

**Definition**:
```xml
<!-- Inertia corrections for legs 3 and 4 -->
<!-- Source: [CAD model / Physical measurement / Estimation] -->

<!-- Leg 3 thigh (l311) corrected inertia origin -->
<xacro:property name="leg3_thigh_inertia_xyz" value="[TO_BE_DETERMINED]"/>
<xacro:property name="leg3_thigh_inertia_rpy" value="0 0 0"/>

<!-- Leg 3 shin (l3111) corrected inertia origin -->
<xacro:property name="leg3_shin_inertia_xyz" value="[TO_BE_DETERMINED]"/>
<xacro:property name="leg3_shin_inertia_rpy" value="0 0 0"/>

<!-- Leg 4 shin (l4111) corrected inertia origin -->
<xacro:property name="leg4_shin_inertia_xyz" value="[TO_BE_DETERMINED]"/>
<xacro:property name="leg4_shin_inertia_rpy" value="0 0 0"/>

<!-- Default inertia origins (used for legs 1, 2, and uncorrected links) -->
<xacro:property name="default_thigh_inertia_xyz" value="0.026 -0.0760041259902766 0.0649874821212071"/>
<xacro:property name="default_shin_inertia_xyz" value="0.0254901816398352 -0.143524743603395 -0.0694046953395906"/>
```

### 2. Enhanced Leg Macro

**Purpose**: Generate leg structure with optional inertia overrides

**Signature**:
```xml
<xacro:macro name="leg" params="leg_num origin_xyz origin_rpy prismatic_lower prismatic_upper
                                 thigh_inertia_xyz:=${default_thigh_inertia_xyz}
                                 shin_inertia_xyz:=${default_shin_inertia_xyz}">
```

**Parameters**:
- `leg_num`: Leg identifier (1, 2, 3, or 4)
- `origin_xyz`: Prismatic joint origin position
- `origin_rpy`: Prismatic joint origin orientation
- `prismatic_lower`: Lower limit for prismatic joint
- `prismatic_upper`: Upper limit for prismatic joint
- `thigh_inertia_xyz`: Inertia origin for thigh link (l${leg_num}11) - optional, defaults to `default_thigh_inertia_xyz`
- `shin_inertia_xyz`: Inertia origin for shin link (l${leg_num}111) - optional, defaults to `default_shin_inertia_xyz`

**Implementation Strategy**:
1. Add default parameter values using xacro's `:=` syntax
2. Use `${thigh_inertia_xyz}` and `${shin_inertia_xyz}` in inertial origin tags
3. Maintain all other link properties unchanged

### 3. Leg Instantiations

**Purpose**: Instantiate four legs with appropriate inertia overrides

**Leg 1 (unchanged)**:
```xml
<xacro:leg leg_num="1" 
           origin_xyz="1.1026 -0.80953 0.2649" 
           origin_rpy="1.5708 0 0"
           prismatic_lower="-0.1" 
           prismatic_upper="0.1"/>
```

**Leg 2 (unchanged)**:
```xml
<xacro:leg leg_num="2" 
           origin_xyz="1.1026 -0.80953 0.2649" 
           origin_rpy="1.5708 0 0"
           prismatic_lower="-0.1" 
           prismatic_upper="0.1"/>
```

**Leg 3 (with inertia corrections)**:
```xml
<xacro:leg leg_num="3" 
           origin_xyz="1.1026 -0.80953 0.2649" 
           origin_rpy="1.5708 0 0"
           prismatic_lower="-0.1" 
           prismatic_upper="0.1"
           thigh_inertia_xyz="${leg3_thigh_inertia_xyz}"
           shin_inertia_xyz="${leg3_shin_inertia_xyz}"/>
```

**Leg 4 (with shin inertia correction only)**:
```xml
<xacro:leg leg_num="4" 
           origin_xyz="1.1026 -0.80953 0.2649" 
           origin_rpy="1.5708 0 0"
           prismatic_lower="-0.1" 
           prismatic_upper="0.1"
           shin_inertia_xyz="${leg4_shin_inertia_xyz}"/>
```

## Data Models

### Inertia Origin Structure

```python
@dataclass
class InertiaOrigin:
    """Represents an inertia origin in URDF"""
    xyz: Tuple[float, float, float]  # Position (x, y, z) in meters
    rpy: Tuple[float, float, float]  # Orientation (roll, pitch, yaw) in radians
    
    def to_string(self) -> str:
        """Convert to URDF attribute string"""
        xyz_str = " ".join(f"{v:.16f}" for v in self.xyz)
        rpy_str = " ".join(f"{v:.16f}" for v in self.rpy)
        return f'xyz="{xyz_str}" rpy="{rpy_str}"'
```

### Current vs Corrected Inertia Values

| Link | Current XYZ | Corrected XYZ | Source |
|------|-------------|---------------|--------|
| l311 (leg 3 thigh) | 0.026 -0.076 0.065 | **[TO_BE_DETERMINED]** | [CAD/Measurement] |
| l3111 (leg 3 shin) | 0.025 -0.144 -0.069 | **[TO_BE_DETERMINED]** | [CAD/Measurement] |
| l4111 (leg 4 shin) | 0.025 -0.144 -0.069 | **[TO_BE_DETERMINED]** | [CAD/Measurement] |

**Note**: The corrected values need to be provided based on:
- CAD model center of mass calculations
- Physical measurements of the actual robot
- Estimation based on geometry and mass distribution

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Inertia Override Application

*For any* leg instantiation with explicit inertia override parameters, the generated URDF link should use the override values rather than default values

**Validates: Requirements 2.3, 3.1, 3.2, 4.1**

### Property 2: Default Inertia Preservation

*For any* leg instantiation without explicit inertia override parameters, the generated URDF link should use the default inertia values

**Validates: Requirements 2.2, 7.1, 7.2, 7.3**

### Property 3: Leg 1 and 2 Unchanged

*For any* comparison between original and modified URDF, legs 1 and 2 inertia parameters should remain identical

**Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**

### Property 4: Leg 3 Thigh Correction Applied

*For any* generated URDF from the modified xacro, the l311 link inertia origin should match the specified leg3_thigh_inertia_xyz property

**Validates: Requirements 3.1, 3.3**

### Property 5: Leg 3 Shin Correction Applied

*For any* generated URDF from the modified xacro, the l3111 link inertia origin should match the specified leg3_shin_inertia_xyz property

**Validates: Requirements 3.2, 3.4**

### Property 6: Leg 4 Shin Correction Applied

*For any* generated URDF from the modified xacro, the l4111 link inertia origin should match the specified leg4_shin_inertia_xyz property

**Validates: Requirements 4.1, 4.2**

### Property 7: Leg 4 Thigh Unchanged

*For any* generated URDF from the modified xacro, the l411 link inertia origin should match the default thigh inertia values

**Validates: Requirements 4.3**

### Property 8: XML Validity Preservation

*For any* generated URDF from the modified xacro, the XML should be well-formed and parseable

**Validates: Requirements 8.1**

### Property 9: Inertia Tensor Positive Definiteness

*For any* link with modified inertia origin, the inertia tensor should remain positive definite (all eigenvalues > 0)

**Validates: Requirements 5.1**

### Property 10: Gazebo Load Success

*For any* generated URDF from the modified xacro, loading the model in Gazebo should succeed without errors

**Validates: Requirements 8.1, 8.2**

## Error Handling

### Error Scenarios

1. **Invalid Inertia Origin Values**
   - **Scenario**: Provided inertia xyz values are outside reasonable bounds
   - **Detection**: Validate that xyz values are within ±1.0 meters of link origin
   - **Handling**: Raise error with clear message indicating which value is out of bounds

2. **Xacro Processing Errors**
   - **Scenario**: Xacro fails to process the modified macro
   - **Detection**: xacro command returns non-zero exit code
   - **Handling**: Display xacro error message and suggest checking syntax

3. **URDF Validation Errors**
   - **Scenario**: Generated URDF fails check_urdf validation
   - **Detection**: check_urdf command returns errors
   - **Handling**: Display validation errors and suggest corrections

4. **Gazebo Load Errors**
   - **Scenario**: Gazebo fails to load the modified URDF
   - **Detection**: Gazebo error messages in console
   - **Handling**: Check for common issues (file paths, inertia values, joint limits)

5. **Inertia Tensor Invalid**
   - **Scenario**: Modified inertia origin causes invalid inertia tensor
   - **Detection**: Negative eigenvalues or NaN values in inertia calculations
   - **Handling**: Warn user and suggest reverting to default values

### Validation Workflow

```python
def validate_inertia_corrections():
    """Validate all inertia corrections before applying"""
    errors = []
    
    # 1. Check inertia origin bounds
    for link_name, xyz in [("l311", leg3_thigh_xyz), 
                           ("l3111", leg3_shin_xyz),
                           ("l4111", leg4_shin_xyz)]:
        if not is_within_bounds(xyz, max_distance=1.0):
            errors.append(f"{link_name}: Inertia origin {xyz} exceeds reasonable bounds")
    
    # 2. Generate URDF from xacro
    try:
        urdf_content = generate_urdf_from_xacro("dog2.urdf.xacro")
    except Exception as e:
        errors.append(f"Xacro processing failed: {e}")
        return False, errors
    
    # 3. Validate URDF syntax
    if not validate_urdf_syntax(urdf_content):
        errors.append("Generated URDF has invalid XML syntax")
    
    # 4. Check inertia tensors
    for link in ["l311", "l3111", "l4111"]:
        if not is_inertia_valid(urdf_content, link):
            errors.append(f"{link}: Inertia tensor is not positive definite")
    
    return len(errors) == 0, errors
```

## Testing Strategy

### Unit Tests

Test individual components in isolation:

1. **Xacro Macro Parameter Handling**
   - Test default parameter values are used when not specified
   - Test override parameters replace defaults correctly
   - Test all four leg instantiations generate correct output

2. **Inertia Origin Extraction**
   - Test extracting inertia origin from generated URDF
   - Test comparing inertia origins between URDFs
   - Test detecting differences in inertia values

3. **URDF Validation**
   - Test XML syntax validation
   - Test inertia tensor validation
   - Test link existence checks

### Integration Tests

Test the complete workflow:

1. **URDF Generation Test**
   - Input: Modified dog2.urdf.xacro with inertia corrections
   - Process: Run xacro to generate URDF
   - Verify: Generated URDF contains corrected inertia values for legs 3 and 4
   - Verify: Legs 1 and 2 remain unchanged

2. **Gazebo Load Test**
   - Input: Generated URDF with corrections
   - Process: Load model in Gazebo
   - Verify: Model loads without errors
   - Verify: All joints are properly connected
   - Verify: Robot maintains stable pose

3. **Controller Integration Test**
   - Input: Generated URDF with corrections
   - Process: Start MPC and WBC controllers
   - Verify: Controllers initialize successfully
   - Verify: Controllers compute valid commands
   - Verify: Robot responds to control inputs

### Property-Based Tests

Verify universal properties across all scenarios:

1. **Property 1 Test: Inertia Override Application**
   ```python
   def test_inertia_override_application():
       """For any leg with override, generated URDF uses override values"""
       # Generate URDF with leg 3 overrides
       urdf = generate_urdf(leg3_thigh_xyz="0.030 -0.080 0.070",
                           leg3_shin_xyz="0.028 -0.150 -0.075")
       
       # Extract actual values from generated URDF
       actual_thigh = extract_inertia_origin(urdf, "l311")
       actual_shin = extract_inertia_origin(urdf, "l3111")
       
       # Verify override values are used
       assert actual_thigh == "0.030 -0.080 0.070"
       assert actual_shin == "0.028 -0.150 -0.075"
   ```

2. **Property 3 Test: Legs 1 and 2 Unchanged**
   ```python
   def test_legs_1_2_unchanged():
       """For any modifications, legs 1 and 2 remain identical to original"""
       original_urdf = generate_urdf_from_xacro("dog2.urdf.xacro.original")
       modified_urdf = generate_urdf_from_xacro("dog2.urdf.xacro.modified")
       
       # Extract inertia for legs 1 and 2
       for leg in ["1", "2"]:
           for link in ["11", "111"]:
               link_name = f"l{leg}{link}"
               original_inertia = extract_inertia_origin(original_urdf, link_name)
               modified_inertia = extract_inertia_origin(modified_urdf, link_name)
               
               assert original_inertia == modified_inertia, \
                      f"{link_name} inertia changed unexpectedly"
   ```

3. **Property 4-7 Tests: Specific Leg Corrections**
   ```python
   def test_leg3_corrections_applied():
       """For any generated URDF, leg 3 corrections are applied"""
       urdf = generate_urdf_from_xacro("dog2.urdf.xacro")
       
       # Verify leg 3 thigh correction
       l311_inertia = extract_inertia_origin(urdf, "l311")
       assert l311_inertia == leg3_thigh_inertia_xyz
       
       # Verify leg 3 shin correction
       l3111_inertia = extract_inertia_origin(urdf, "l3111")
       assert l3111_inertia == leg3_shin_inertia_xyz
   
   def test_leg4_corrections_applied():
       """For any generated URDF, leg 4 shin correction is applied"""
       urdf = generate_urdf_from_xacro("dog2.urdf.xacro")
       
       # Verify leg 4 shin correction
       l4111_inertia = extract_inertia_origin(urdf, "l4111")
       assert l4111_inertia == leg4_shin_inertia_xyz
       
       # Verify leg 4 thigh uses default
       l411_inertia = extract_inertia_origin(urdf, "l411")
       assert l411_inertia == default_thigh_inertia_xyz
   ```

4. **Property 9 Test: Inertia Tensor Validity**
   ```python
   def test_inertia_tensor_positive_definite():
       """For any link with modified inertia, tensor remains positive definite"""
       urdf = generate_urdf_from_xacro("dog2.urdf.xacro")
       
       for link in ["l311", "l3111", "l4111"]:
           inertia_tensor = extract_inertia_tensor(urdf, link)
           eigenvalues = compute_eigenvalues(inertia_tensor)
           
           assert all(ev > 0 for ev in eigenvalues), \
                  f"{link} inertia tensor is not positive definite"
   ```

### Test Configuration

- **Unit tests**: pytest, run independently
- **Integration tests**: pytest + ROS 2 launch framework
- **Property tests**: Minimum 100 iterations per property
- **Test data**: Use actual dog2.urdf.xacro file
- **CI/CD**: All tests must pass before merging

### Manual Testing Checklist

After applying corrections:

- [ ] Generate URDF from xacro: `xacro dog2.urdf.xacro > dog2_generated.urdf`
- [ ] Validate URDF: `check_urdf dog2_generated.urdf`
- [ ] Load in RViz: `ros2 launch dog2_description view_dog2_xacro.launch.py`
- [ ] Load in Gazebo: `ros2 launch dog2_description gazebo_dog2.launch.py`
- [ ] Start controllers: `ros2 launch dog2_mpc mpc_wbc_simulation.launch.py`
- [ ] Test standing: Robot maintains stable balance
- [ ] Test walking: Robot walks smoothly without oscillations
- [ ] Check logs: No warnings or errors related to inertia

## Implementation Notes

### Determining Correct Inertia Values

The corrected inertia origin values should be determined using one of these methods:

1. **CAD Model Analysis** (Most Accurate)
   - Export leg meshes to CAD software (SolidWorks, Fusion 360, etc.)
   - Assign material properties (density)
   - Use CAD's mass properties tool to compute center of mass
   - Extract xyz coordinates relative to link origin

2. **Physical Measurement** (Accurate but Labor-Intensive)
   - Disassemble robot to isolate leg components
   - Use balance point method or suspension method
   - Measure center of mass position with calipers
   - Convert measurements to link coordinate frame

3. **Geometric Estimation** (Quick but Less Accurate)
   - Analyze STL mesh files to estimate volume distribution
   - Assume uniform density
   - Calculate approximate center of mass
   - Validate against simulation behavior

### Xacro Best Practices

1. **Use Default Parameters**: Leverage xacro's `:=` syntax for optional parameters
2. **Document Overrides**: Add comments explaining why specific legs need corrections
3. **Maintain Consistency**: Keep parameter naming consistent across all legs
4. **Version Control**: Commit xacro changes separately from generated URDF

### Validation Workflow

```bash
# 1. Backup current xacro
cp dog2.urdf.xacro dog2.urdf.xacro.backup

# 2. Apply modifications
# (Edit dog2.urdf.xacro with inertia corrections)

# 3. Generate URDF
xacro dog2.urdf.xacro > dog2_test.urdf

# 4. Validate syntax
check_urdf dog2_test.urdf

# 5. Compare with original
python3 scripts/compare_inertia.py dog2.urdf dog2_test.urdf

# 6. Test in Gazebo
ros2 launch dog2_description gazebo_dog2.launch.py urdf_file:=dog2_test.urdf

# 7. If successful, replace original
mv dog2_test.urdf dog2.urdf
```

## Next Steps

1. **Determine Correct Inertia Values**: Use CAD model or physical measurements to find accurate center of mass positions for l311, l3111, and l4111
2. **Update Properties**: Fill in `[TO_BE_DETERMINED]` placeholders with actual values
3. **Implement Macro Changes**: Modify leg macro to accept optional inertia parameters
4. **Update Leg Instantiations**: Add inertia overrides for legs 3 and 4
5. **Generate and Validate**: Create URDF and run all validation tests
6. **Test in Simulation**: Verify corrections improve simulation accuracy
