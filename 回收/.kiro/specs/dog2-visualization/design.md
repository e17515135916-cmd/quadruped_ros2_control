# Design Document: Dog2 可视化系统

## Overview

本设计为 Dog2 四足机器人创建一个完整的可视化系统，包括 RViz2 3D 可视化、Gazebo 环境增强、实时数据图表和性能监控。系统将通过 ROS 2 话题订阅现有的控制数据，并使用 RViz2 Marker 和自定义消息类型进行可视化展示。

### 设计目标

1. **直观性**：用户能够一眼看出机器人的状态和行为
2. **实时性**：可视化延迟 < 100ms
3. **可配置性**：支持不同的可视化模式和参数
4. **易用性**：一键启动所有可视化组件
5. **性能**：可视化不影响控制系统性能

## Architecture

系统采用分层架构：

```
┌─────────────────────────────────────────────────────────┐
│                   用户界面层                              │
│  RViz2 GUI  │  Gazebo GUI  │  PlotJuggler  │  终端输出   │
└─────────────────────────────────────────────────────────┘
                            ↑
┌─────────────────────────────────────────────────────────┐
│                   可视化节点层                            │
│  Marker Publisher  │  TF Broadcaster  │  Status Monitor │
└─────────────────────────────────────────────────────────┘
                            ↑
┌─────────────────────────────────────────────────────────┐
│                   ROS 2 话题层                           │
│  /dog2/odom  │  /joint_states  │  /dog2/mpc/foot_forces │
└─────────────────────────────────────────────────────────┘
                            ↑
┌─────────────────────────────────────────────────────────┐
│                   控制系统层                              │
│      MPC Controller      │      WBC Controller          │
└─────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### Component 1: VisualizationNode

**职责**：订阅控制数据并发布 RViz2 Marker

**输入接口**：
- `/dog2/odom` (nav_msgs/Odometry): 机器人位姿和速度
- `/joint_states` (sensor_msgs/JointState): 关节状态
- `/dog2/mpc/foot_forces` (std_msgs/Float64MultiArray): 足端力
- `/dog2/mpc/contact_states` (std_msgs/Int32MultiArray): 接触状态

**输出接口**：
- `/dog2/visualization/foot_forces` (visualization_msgs/MarkerArray): 足端力箭头
- `/dog2/visualization/trajectory` (visualization_msgs/Marker): 轨迹线
- `/dog2/visualization/contact_markers` (visualization_msgs/MarkerArray): 接触状态球体
- `/dog2/visualization/sliding_status` (visualization_msgs/MarkerArray): 滑动副状态
- `/dog2/visualization/performance_text` (visualization_msgs/Marker): 性能文本面板

**关键方法**：

- `publishFootForceMarkers()`: 创建足端力箭头 Marker
- `publishTrajectoryMarker()`: 绘制历史轨迹
- `publishContactMarkers()`: 显示接触状态球体
- `publishSlidingStatusMarkers()`: 显示滑动副状态条
- `publishPerformanceText()`: 显示性能监控文本

### Component 2: RVizConfigManager

**职责**：管理 RViz2 配置文件

**功能**：
- 提供预配置的 RViz2 视角（俯视图、侧视图、跟随视图）
- 配置显示面板（TF、Marker、Grid等）
- 保存和加载用户自定义配置

**配置文件**：
- `dog2_walking.rviz`: 行走模式配置
- `dog2_crossing.rviz`: 越障模式配置
- `dog2_debug.rviz`: 调试模式配置（显示所有数据）

### Component 3: GazeboWorldGenerator

**职责**：生成增强的 Gazebo 世界文件

**功能**：
- 添加网格地面
- 生成距离标记
- 创建窗框障碍物模型
- 支持多种地形（平地、斜坡、台阶）

**世界文件**：
- `dog2_flat.world`: 平地环境
- `dog2_crossing.world`: 带窗框的越障环境
- `dog2_terrain.world`: 复杂地形环境

### Component 4: CrossingVisualizationNode

**职责**：专门用于越障过程的可视化

**输入接口**：
- `/dog2/crossing/state` (std_msgs/Int32): 当前越障阶段
- `/dog2/crossing/window_position` (geometry_msgs/Point): 窗框位置

**输出接口**：
- `/dog2/visualization/crossing_stage` (visualization_msgs/Marker): 阶段文本
- `/dog2/visualization/window_marker` (visualization_msgs/Marker): 窗框模型
- `/dog2/visualization/leg_highlight` (visualization_msgs/MarkerArray): 高亮正在穿越的腿

## Data Models

### FootForceMarker

```cpp
struct FootForceMarker {
    int leg_id;                    // 腿编号 (0-3)
    Eigen::Vector3d position;      // 足端位置
    Eigen::Vector3d force;         // 力向量
    double magnitude;              // 力的大小
    std_msgs::ColorRGBA color;     // 颜色（基于力大小）
};
```

### TrajectoryPoint

```cpp
struct TrajectoryPoint {
    double timestamp;
    Eigen::Vector3d position;
    bool is_reference;  // true=规划轨迹, false=历史轨迹
};
```

### ContactMarker

```cpp
struct ContactMarker {
    int leg_id;
    Eigen::Vector3d position;
    bool in_contact;
    double contact_force;  // 用于调整球体大小
};
```

### SlidingStatus

```cpp
struct SlidingStatus {
    int joint_id;              // 滑动副编号 (0-3)
    double position;           // 当前位置 [-0.1, 0.1]
    double velocity;           // 当前速度
    double position_limit_min; // -0.1
    double position_limit_max; // 0.1
    WarningLevel warning;      // NORMAL, WARNING, DANGER
};

enum WarningLevel {
    NORMAL,   // 绿色
    WARNING,  // 黄色（接近限位）
    DANGER    // 红色（达到限位）
};
```

### PerformanceMetrics

```cpp
struct PerformanceMetrics {
    double mpc_solve_time_ms;
    double wbc_solve_time_ms;
    double control_frequency_hz;
    double current_height_m;
    Eigen::Vector3d current_velocity;
    std::array<bool, 4> contact_states;
    bool constraints_satisfied;
    double uptime_seconds;
};
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Joint angle visualization updates

*For any* joint state message received, the RViz2 robot model SHALL update to reflect the new joint angles within 100ms.

**Validates: Requirements 1.2, 1.3**

### Property 2: Foot force arrow visualization

*For any* foot force vector published by MPC, the visualization system SHALL display a corresponding arrow marker with length proportional to force magnitude.

**Validates: Requirements 2.1, 2.2**

### Property 3: Force color encoding

*For any* foot force magnitude F, the arrow color SHALL be:
- Green if F < 30N
- Yellow if 30N ≤ F < 60N  
- Red if F ≥ 60N

**Validates: Requirements 2.3**

### Property 4: Non-contact force hiding

*For any* foot that is not in contact (contact_state = false), the force arrow SHALL be either hidden or rendered with 30% opacity.

**Validates: Requirements 2.4**

### Property 5: Force value labels

*For any* foot force marker, there SHALL be a text label displaying the force magnitude in Newtons with one decimal place.

**Validates: Requirements 2.5**

### Property 6: Trajectory point accumulation

*For any* robot position update, a new trajectory point SHALL be added to the history buffer.

**Validates: Requirements 3.1**

### Property 7: Reference trajectory visualization

*For any* MPC reference trajectory published, the visualization SHALL display the future path as a green line.

**Validates: Requirements 3.2**

### Property 8: Trajectory color distinction

*For any* trajectory marker, the color SHALL be blue if it represents history and green if it represents the reference path.

**Validates: Requirements 3.3**

### Property 9: Foot trajectory tracking

*For any* foot position update, a trajectory point SHALL be added to that foot's trajectory buffer.

**Validates: Requirements 3.4**

### Property 10: Trajectory buffer management

*For any* trajectory buffer exceeding 100 points, the oldest points SHALL be removed to maintain exactly 100 points.

**Validates: Requirements 3.5**

### Property 11: Contact marker color

*For any* foot with contact_state = true, the marker SHALL be a green sphere; for contact_state = false, the marker SHALL be a red sphere.

**Validates: Requirements 4.1, 4.2**

### Property 12: Contact state updates

*For any* change in contact state, the corresponding marker SHALL update its color within 100ms.

**Validates: Requirements 4.3**

### Property 13: Sliding joint position display

*For any* sliding joint state, there SHALL be a text marker displaying its position in meters with three decimal places.

**Validates: Requirements 6.1**

### Property 14: Sliding joint warning colors

*For any* sliding joint position d:
- Green if |d| < 0.08m (normal)
- Yellow if 0.08m ≤ |d| < 0.095m (warning)
- Red if |d| ≥ 0.095m (danger)

**Validates: Requirements 6.2, 6.3**

### Property 15: Crossing stage visualization

*For any* crossing stage number N (1-8), there SHALL be a text marker displaying "Stage N: [stage_name]" with a color corresponding to the stage.

**Validates: Requirements 9.1, 9.2**

### Property 16: Leg highlight during crossing

*For any* leg currently crossing the window, its links SHALL be rendered with increased brightness or a highlight color.

**Validates: Requirements 9.4**

### Property 17: Performance metrics update rate

*For any* 1-second time window, the performance text panel SHALL update at least once.

**Validates: Requirements 10.2**

### Property 18: MPC failure warning

*For any* MPC solve failure event, the performance panel text SHALL change to red color within 100ms.

**Validates: Requirements 10.3**


## Error Handling

### Visualization Node Errors

1. **Missing Robot Description**
   - Error: URDF not loaded in robot_state_publisher
   - Handling: Log error and wait for robot description to become available
   - Recovery: Retry every 5 seconds

2. **Topic Timeout**
   - Error: No data received on subscribed topics for > 5 seconds
   - Handling: Display warning marker in RViz2
   - Recovery: Continue listening, remove warning when data resumes

3. **Invalid Marker Data**
   - Error: Received data with invalid dimensions or NaN values
   - Handling: Skip the invalid marker, log warning
   - Recovery: Continue processing next valid data

4. **RViz2 Connection Lost**
   - Error: Marker publisher has no subscribers
   - Handling: Continue publishing (RViz2 may reconnect)
   - Recovery: Automatic when RViz2 reconnects

### Launch File Errors

1. **Missing Configuration Files**
   - Error: RViz config file not found
   - Handling: Launch RViz2 with default configuration
   - Recovery: User can manually load config

2. **Gazebo World File Missing**
   - Error: Specified world file doesn't exist
   - Handling: Fall back to empty world
   - Recovery: Log error with available world files

3. **Node Startup Failure**
   - Error: Visualization node fails to start
   - Handling: Log detailed error message
   - Recovery: User must fix configuration and restart

## Testing Strategy

### Unit Tests

Unit tests will verify specific examples and edge cases:

1. **Marker Creation Tests**
   - Test creating arrow markers with known force values
   - Test color calculation for boundary force values (29.9N, 30.0N, 30.1N)
   - Test text marker formatting

2. **Buffer Management Tests**
   - Test trajectory buffer with exactly 100 points
   - Test trajectory buffer with 101 points (should remove oldest)
   - Test empty buffer behavior

3. **Configuration File Tests**
   - Test loading each RViz config file
   - Test loading each Gazebo world file
   - Test launch file parameter parsing

4. **Color Encoding Tests**
   - Test force-to-color mapping at boundaries
   - Test sliding joint warning level calculation
   - Test crossing stage color assignment

### Property-Based Tests

Property tests will verify universal properties across all inputs:

1. **Property Test: Force Arrow Scaling**
   - Generate random foot forces (0-150N)
   - Verify arrow length is proportional to force
   - Verify color matches force magnitude range
   - **Feature: dog2-visualization, Property 2: Foot force arrow visualization**
   - **Feature: dog2-visualization, Property 3: Force color encoding**

2. **Property Test: Trajectory Buffer Management**
   - Generate random sequences of trajectory points (50-200 points)
   - Verify buffer never exceeds 100 points
   - Verify oldest points are removed first (FIFO)
   - **Feature: dog2-visualization, Property 10: Trajectory buffer management**

3. **Property Test: Contact Marker Colors**
   - Generate random contact states (true/false for 4 legs)
   - Verify green markers for contact, red for non-contact
   - Verify marker count equals 4
   - **Feature: dog2-visualization, Property 11: Contact marker color**

4. **Property Test: Sliding Joint Warning Levels**
   - Generate random sliding joint positions (-0.15 to 0.15m)
   - Verify warning level matches position thresholds
   - Verify color matches warning level
   - **Feature: dog2-visualization, Property 14: Sliding joint warning colors**

5. **Property Test: Update Latency**
   - Generate random state updates at various rates
   - Measure time from data receipt to marker publication
   - Verify latency < 100ms for 95% of updates
   - **Feature: dog2-visualization, Property 1: Joint angle visualization updates**

### Integration Tests

1. **Full System Test**
   - Launch complete visualization system
   - Verify all nodes start successfully
   - Verify RViz2 displays robot model
   - Verify Gazebo loads world file

2. **Walking Visualization Test**
   - Start walking mode
   - Send velocity commands
   - Verify trajectory is drawn
   - Verify contact markers alternate correctly

3. **Crossing Visualization Test**
   - Start crossing mode
   - Trigger crossing sequence
   - Verify stage markers update through all 8 stages
   - Verify window obstacle is visible

### Performance Tests

1. **Marker Publication Rate**
   - Measure marker publication frequency
   - Target: 20Hz for all markers
   - Verify no dropped frames

2. **Memory Usage**
   - Monitor trajectory buffer memory
   - Verify no memory leaks over 10-minute run
   - Verify buffer size stays bounded

3. **CPU Usage**
   - Measure visualization node CPU usage
   - Target: < 5% CPU on typical hardware
   - Verify no impact on control system performance

### Test Configuration

- Minimum 100 iterations per property test
- Use ROS 2 bag files for repeatable testing
- Test on Ubuntu 22.04 with ROS 2 Humble
- Test with both real-time and recorded data

