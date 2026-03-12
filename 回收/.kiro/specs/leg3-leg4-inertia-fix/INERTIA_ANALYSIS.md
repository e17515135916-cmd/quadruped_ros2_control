# Inertia Position Analysis

## Current Inertia Values (from dog2.urdf.xacro)

All legs currently use the same inertia values defined in the xacro macro:

### Thigh Link (l*11)
- **Current xyz**: `0.026 -0.0760041259902766 0.0649874821212071`
- **Current rpy**: `0 0 0`
- **Mass**: 0.4 kg

### Shin Link (l*111)
- **Current xyz**: `0.0254901816398352 -0.143524743603395 -0.0694046953395906`
- **Current rpy**: `0 0 0`
- **Mass**: 0.5 kg

## Links Requiring Correction

Based on user input, the following links have incorrect inertia positions:

1. **l311** (Leg 3 Thigh)
2. **l3111** (Leg 3 Shin)
3. **l4111** (Leg 4 Shin)

## Corrected Inertia Values

### Method Used
- [x] CAD Model Analysis (STL mesh analysis)
- [ ] Physical Measurement
- [ ] Geometric Estimation
- [ ] Other: _______________

**Analysis Date**: 2026-01-27
**Tool Used**: Python script `calculate_stl_center_of_mass.py`
**Method**: Volume-weighted centroid calculation from STL triangular meshes

### Leg 3 Thigh (l311)
- **Corrected xyz**: `-0.0259999985992546 -0.0760041263454303 0.0649874816053539`
- **Corrected rpy**: `0 0 0`
- **Source**: STL mesh analysis (l311.STL)
- **Notes**: X coordinate is NEGATIVE (mirrored geometry compared to legs 1 and 2)
- **Current (incorrect) value**: `0.026 -0.0760041259902766 0.0649874821212071`
- **Key difference**: Sign of X coordinate is wrong in current URDF

### Leg 3 Shin (l3111)
- **Corrected xyz**: `-0.0265089672547710 -0.1429895138560395 -0.0691152554666486`
- **Corrected rpy**: `0 0 0`
- **Source**: STL mesh analysis (l3111.STL)
- **Notes**: X coordinate is NEGATIVE, Y and Z also differ slightly from current values
- **Current (incorrect) value**: `0.0254901816398352 -0.143524743603395 -0.0694046953395906`
- **Key difference**: Sign of X coordinate is wrong, Y and Z values also incorrect

### Leg 4 Shin (l4111)
- **Corrected xyz**: `-0.0265089672547710 -0.1429895138560395 -0.0691152554666486`
- **Corrected rpy**: `0 0 0`
- **Source**: STL mesh analysis (l4111.STL)
- **Notes**: Identical to l3111 (same mesh geometry)
- **Current (incorrect) value**: `0.0254901816398352 -0.143524743603395 -0.0694046953395906`
- **Key difference**: Sign of X coordinate is wrong, Y and Z values also incorrect

### Key Findings

1. **Mirrored Geometry**: Leg 3 has mirrored geometry compared to legs 1 and 2
   - Legs 1, 2: X = +0.026 (positive)
   - Leg 3: X = -0.026 (negative)
   
2. **Significant Error**: The current URDF uses positive X values for all legs, but leg 3 should have negative X values

3. **Distance from Reference**: 
   - Leg 3 shin vs Leg 1 shin: 0.1588 units difference
   - Leg 4 shin vs Leg 2 shin: 0.1588 units difference

4. **Impact**: This error causes incorrect mass distribution in the physics simulation, affecting:
   - Balance calculations
   - Joint torque computations
   - MPC/WBC controller accuracy

## Available Resources

### STL Mesh Files
- `src/dog2_description/meshes/l311.STL` (39,484 bytes)
- `src/dog2_description/meshes/l3111.STL` (87,984 bytes)
- `src/dog2_description/meshes/l4111.STL` (exists)

### Backup URDF Files
- `dog2.urdf.backup_20260112_170119` (earliest backup)
- `dog2.urdf.backup_20260126_171703`
- `dog2.urdf.backup_xacro_migration`

## Next Steps

1. **Determine the correct inertia positions** using one of these methods:
   - Import STL meshes into CAD software and calculate center of mass
   - Use physical measurements from the actual robot
   - Estimate based on geometry and mass distribution
   
2. **Fill in the corrected xyz values** in this document

3. **Document the source and method** used to obtain the values

4. **Proceed with implementation** once values are confirmed
