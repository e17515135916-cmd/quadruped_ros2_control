# Design Document: Gazebo Fortress Migration

## Overview

This document describes the design for migrating the dog2 quadruped robot project from Gazebo Classic to Gazebo Fortress (Ignition). The migration addresses persistent GUI crashes while maintaining full ros2_control functionality with minimal code changes.

Gazebo Fortress provides better ROS 2 integration, improved stability, and modern architecture. Since the project already uses ros2_control, the migration primarily involves updating plugin references and launch configurations.

## Architecture

### Current Architecture (Gazebo Classic)
```
┌─────────────────────────────────────────────────────────┐
│                    ROS 2 Humble                         │
├─────────────────────────────────────────────────────────┤
│  robot_state_publisher  │  controller_manager           │
├─────────────────────────────────────────────────────────┤
│           gazebo_ros2_control plugin                    │
├─────────────────────────────────────────────────────────┤
│              Gazebo Classic (GUI crashes)               │
└─────────────────────────────────────────────────────────┘
```

### Target Architecture (Gazebo Fortress)
```
┌─────────────────────────────────────────────────────────┐
│                    ROS 2 Humble                         │
├─────────────────────────────────────────────────────────┤
│  robot_state_publisher  │  controller_manager           │
├─────────────────────────────────────────────────────────┤
│           ign_ros2_control plugin                       │
├─────────────────────────────────────────────────────────┤
│           Gazebo Fortress (stable GUI)                  │
└─────────────────────────────────────────────────────────┘
```

The architecture remains largely unchanged - only the simulator and its plugin are replaced.

## Components and Interfaces

### 1. Installation Script

**Purpose**: Automate installation of Gazebo Fortress and ROS 2 bridge packages

**Implementation**:
- Bash script: `install_gazebo_fortress.sh`
- Add Gazebo Fortress repository
- Install packages: `gz-fortress`, `ros-humble-ros-gz-sim`, `ros-humble-ros-gz-bridge`
- Verify installation with `gz --version`
- Check for `libign_ros2_control-system.so` plugin

**Dependencies**:
- Ubuntu 22.04 (Jammy)
- ROS 2 Humble
- Internet connection for package downloads

### 2. URDF/Xacro Migration Script

**Purpose**: Update robot description files to use Gazebo Fortress plugins

**Implementation**:
- Python script: `migrate_urdf_to_fortress.py`
- Backup original files with timestamp
- Replace plugin references:
  - `gazebo_ros2_control/GazeboSystem` → `ign_ros2_control/IgnitionSystem`
  - `libgazebo_ros2_control.so` → `libign_ros2_control-system.so`
- Preserve all ros2_control configuration
- Validate with `xacro` command

**Key Changes**:
```xml
<!-- Before (Gazebo Classic) -->
<ros2_control name="GazeboSystem" type="system">
  <hardware>
    <plugin>gazebo_ros2_control/GazeboSystem</plugin>
  </hardware>
  ...
</ros2_control>

<gazebo>
  <plugin filename="libgazebo_ros2_control.so" name="gazebo_ros2_control">
    <parameters>$(find dog2_description)/config/ros2_controllers.yaml</parameters>
  </plugin>
</gazebo>

<!-- After (Gazebo Fortress) -->
<ros2_control name="IgnitionSystem" type="system">
  <hardware>
    <plugin>ign_ros2_control/IgnitionSystem</plugin>
  </hardware>
  ...
</ros2_control>

<gazebo>
  <plugin filename="libign_ros2_control-system.so" name="ign_ros2_control">
    <parameters>$(find dog2_description)/config/ros2_controllers.yaml</parameters>
  </plugin>
</gazebo>
```

### 3. Launch File Migration Script

**Purpose**: Update launch files to use ros_gz_sim instead of gazebo_ros

**Implementation**:
- Python script: `migrate_launch_to_fortress.py`
- Backup original launch files
- Update imports:
  - `from gazebo_ros import ...` → `from ros_gz_sim import ...`
- Replace nodes:
  - `gazebo.launch.py` → `gz_sim.launch.py`
  - `spawn_entity.py` (gazebo_ros) → `create` (ros_gz_sim)
- Update world file paths if needed

**Key Changes**:
```python
# Before (Gazebo Classic)
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

gazebo_ros = get_package_share_directory('gazebo_ros')
gazebo = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
        os.path.join(gazebo_ros, 'launch', 'gazebo.launch.py')
    )
)

spawn_entity = Node(
    package='gazebo_ros',
    executable='spawn_entity.py',
    arguments=['-entity', 'dog2', '-topic', 'robot_description']
)

# After (Gazebo Fortress)
from ros_gz_sim.actions import GzServer

gz_server = GzServer(
    world_sdf_file=world_path,
    world_sdf_string='',
    server_required=True,
    gui_required=False
)

spawn_entity = Node(
    package='ros_gz_sim',
    executable='create',
    arguments=['-name', 'dog2', '-topic', 'robot_description'],
    output='screen'
)
```

### 4. Verification Tests

**Purpose**: Ensure migration maintains functionality

**Test Suite**:
1. Installation verification
2. URDF processing validation
3. Launch file syntax check
4. Simulation startup test
5. ros2_control connectivity test
6. Joint command/state test

## Data Models

### Configuration Files

**ros2_controllers.yaml**: Unchanged - same controller configuration works with both simulators

**URDF Structure**: Preserved - only plugin references change

**Launch Parameters**: Mostly preserved - world files may need SDF format updates

### Backup Structure
```
backups/
  gazebo_fortress_migration_YYYYMMDD_HHMMSS/
    urdf/
      dog2.urdf.xacro.backup
    launch/
      gazebo_dog2.launch.py.backup
      ...
    README.md  # Migration details
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system - essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Plugin Reference Replacement
*For any* URDF file processed by the migration script, all occurrences of `gazebo_ros2_control/GazeboSystem` should be replaced with `ign_ros2_control/IgnitionSystem`, and all occurrences of `libgazebo_ros2_control.so` should be replaced with `libign_ros2_control-system.so`

**Validates: Requirements 2.1**

### Property 2: ros2_control Configuration Preservation
*For any* URDF file before and after migration, the set of joint names, command interfaces, and state interfaces in the ros2_control section should be identical

**Validates: Requirements 2.2, 2.4**

### Property 3: Launch Import Replacement
*For any* launch file processed by the migration script, all imports from `gazebo_ros` should be replaced with equivalent imports from `ros_gz_sim`, and no `gazebo_ros` imports should remain

**Validates: Requirements 3.1**

### Property 4: Spawner Configuration Preservation
*For any* launch file before and after migration, the robot entity name and URDF topic arguments passed to the spawner should remain unchanged

**Validates: Requirements 3.4**

### Property 5: Node Type Replacement
*For any* launch file processed by the migration script, all references to `gzserver`, `gzclient`, or `gazebo.launch.py` should be replaced with `GzServer` or `gz_sim.launch.py` equivalents

**Validates: Requirements 3.2**

## Error Handling

### Installation Errors

**Missing Dependencies**:
- Check: Verify Ubuntu version is 22.04
- Action: Display error message with system requirements
- Recovery: Provide manual installation instructions

**Package Installation Failure**:
- Check: Verify internet connectivity
- Action: Retry with apt update
- Recovery: Provide manual apt commands

**Plugin Not Found**:
- Check: Search for libign_ros2_control-system.so
- Action: Install ros-humble-ros-gz-control if missing
- Recovery: Build from source if package unavailable

### Migration Errors

**URDF Parse Failure**:
- Check: Validate XML syntax before migration
- Action: Report line number and error
- Recovery: Skip file and continue with others

**Backup Creation Failure**:
- Check: Verify write permissions
- Action: Request sudo if needed
- Recovery: Abort migration to prevent data loss

**Xacro Processing Failure**:
- Check: Run xacro on migrated file
- Action: Display xacro error output
- Recovery: Restore from backup

### Runtime Errors

**Simulation Startup Failure**:
- Check: Verify gz command works
- Action: Check gz logs for errors
- Recovery: Provide troubleshooting steps

**Controller Manager Connection Failure**:
- Check: Verify plugin is loaded
- Action: Check ros2 control list_hardware_interfaces
- Recovery: Verify URDF plugin configuration

**Joint Command Not Working**:
- Check: Verify topics exist
- Action: Echo joint_states topic
- Recovery: Check controller configuration

## Testing Strategy

### Dual Testing Approach

This project uses both unit tests and property-based tests:
- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across all inputs
- Both are complementary and necessary for comprehensive coverage

### Unit Testing

**Installation Tests**:
- Test gz command availability
- Test package installation verification
- Test plugin file existence
- Test version compatibility checks

**Migration Script Tests**:
- Test backup creation
- Test plugin replacement on sample URDF
- Test launch file import replacement
- Test error handling for malformed files

**Integration Tests**:
- Test simulation startup
- Test robot spawning
- Test controller manager connection
- Test joint command/state communication

### Property-Based Testing

We will use **pytest with Hypothesis** for property-based testing in Python.

**Configuration**: Each property test will run a minimum of 100 iterations.

**Test Tagging**: Each test will include a comment:
```python
# Feature: gazebo-fortress-migration, Property 1: Plugin Reference Replacement
```

**Property Test 1: Plugin Reference Replacement**
- Generate: Random URDF content with gazebo_ros2_control references
- Execute: Run migration script
- Verify: All plugin references are replaced correctly
- **Feature: gazebo-fortress-migration, Property 1: Plugin Reference Replacement**
- **Validates: Requirements 2.1**

**Property Test 2: ros2_control Configuration Preservation**
- Generate: Random ros2_control configurations with various joints
- Execute: Run migration script
- Verify: Joint configurations are identical before and after
- **Feature: gazebo-fortress-migration, Property 2: ros2_control Configuration Preservation**
- **Validates: Requirements 2.2, 2.4**

**Property Test 3: Launch Import Replacement**
- Generate: Random launch files with gazebo_ros imports
- Execute: Run migration script
- Verify: All imports are replaced, none remain
- **Feature: gazebo-fortress-migration, Property 3: Launch Import Replacement**
- **Validates: Requirements 3.1**

**Property Test 4: Spawner Configuration Preservation**
- Generate: Random launch files with spawn_entity nodes
- Execute: Run migration script
- Verify: Entity name and topic arguments are preserved
- **Feature: gazebo-fortress-migration, Property 4: Spawner Configuration Preservation**
- **Validates: Requirements 3.4**

**Property Test 5: Node Type Replacement**
- Generate: Random launch files with Gazebo Classic nodes
- Execute: Run migration script
- Verify: All node types are replaced with Fortress equivalents
- **Feature: gazebo-fortress-migration, Property 5: Node Type Replacement**
- **Validates: Requirements 3.2**

### Test Execution

```bash
# Run all tests
pytest src/dog2_description/test/test_fortress_migration.py -v

# Run property tests with verbose output
pytest src/dog2_description/test/test_fortress_migration.py -v -k property

# Run with coverage
pytest src/dog2_description/test/test_fortress_migration.py --cov=scripts
```

## Migration Workflow

### Phase 1: Preparation
1. Backup entire project
2. Document current Gazebo Classic configuration
3. Test current functionality as baseline

### Phase 2: Installation
1. Run installation script
2. Verify Gazebo Fortress installation
3. Test gz command

### Phase 3: URDF Migration
1. Run URDF migration script
2. Verify xacro processing
3. Compare ros2_control configuration

### Phase 4: Launch File Migration
1. Run launch file migration script
2. Verify Python syntax
3. Test launch file loading

### Phase 5: Verification
1. Launch simulation
2. Verify robot spawns correctly
3. Test ros2_control functionality
4. Run existing test scripts

### Phase 6: Documentation
1. Document all changes
2. Create rollback instructions
3. Update project README

## Rollback Plan

If migration fails or causes issues:

1. **Restore URDF files**:
```bash
cp backups/gazebo_fortress_migration_*/urdf/*.backup src/dog2_description/urdf/
```

2. **Restore launch files**:
```bash
cp backups/gazebo_fortress_migration_*/launch/*.backup src/dog2_description/launch/
```

3. **Uninstall Gazebo Fortress** (optional):
```bash
sudo apt remove gz-fortress ros-humble-ros-gz-*
```

4. **Reinstall Gazebo Classic**:
```bash
sudo apt install ros-humble-gazebo-ros-pkgs
```

## Performance Considerations

- Gazebo Fortress may have different physics performance characteristics
- Monitor simulation real-time factor
- Adjust physics parameters if needed (timestep, iterations)
- GPU rendering may behave differently

## Security Considerations

- Installation script requires sudo privileges
- Verify package sources before installation
- Backup files contain no sensitive data
- Migration scripts only modify local files

## Future Enhancements

1. **Automated Testing**: CI/CD pipeline for migration validation
2. **World File Conversion**: Tool to convert Gazebo Classic worlds to SDF
3. **Plugin Compatibility Layer**: Wrapper for easier migration
4. **Performance Benchmarking**: Compare Gazebo Classic vs Fortress performance
