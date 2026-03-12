#!/bin/bash

# Dog2 MPC+WBC 越障仿真（带窗框障碍物）

echo "=========================================="
echo "  Dog2 MPC+WBC 越障仿真（带窗框）"
echo "=========================================="
echo ""
echo "系统组件："
echo "  ✅ Gazebo 仿真环境 + 窗框障碍物"
echo "  ✅ 16维MPC控制器（滑动副约束）"
echo "  ✅ 完整WBC控制器（精确雅可比）"
echo "  ✅ 越障状态机（8阶段）"
echo "  ✅ 混合步态生成器"
echo ""

# 进入工作空间
cd /home/dell/aperfect/carbot_ws

# 设置环境
source install/setup.bash

echo "步骤1: 启动Gazebo并加载窗框障碍物..."
echo ""

# 启动Gazebo（后台运行）
gazebo --verbose &
GAZEBO_PID=$!

echo "等待Gazebo启动..."
sleep 5

echo ""
echo "步骤2: 生成窗框障碍物..."
echo ""

# 在Gazebo中生成窗框（使用gz命令）
# 窗框参数：宽度0.3m，高度0.25m，厚度0.05m，位置x=1.5m
gz model -m window_frame -x 1.5 -y 0 -z 0.125 << 'EOF'
<?xml version="1.0"?>
<sdf version="1.6">
  <model name="window_frame">
    <static>true</static>
    <link name="frame">
      <collision name="top">
        <pose>0 0 0.125 0 0 0</pose>
        <geometry>
          <box>
            <size>0.3 0.05 0.05</size>
          </box>
        </geometry>
      </collision>
      <visual name="top_visual">
        <pose>0 0 0.125 0 0 0</pose>
        <geometry>
          <box>
            <size>0.3 0.05 0.05</size>
          </box>
        </geometry>
        <material>
          <ambient>0.8 0.8 0.8 1</ambient>
          <diffuse>0.8 0.8 0.8 1</diffuse>
        </material>
      </visual>
      
      <collision name="bottom">
        <pose>0 0 -0.125 0 0 0</pose>
        <geometry>
          <box>
            <size>0.3 0.05 0.05</size>
          </box>
        </geometry>
      </collision>
      <visual name="bottom_visual">
        <pose>0 0 -0.125 0 0 0</pose>
        <geometry>
          <box>
            <size>0.3 0.05 0.05</size>
          </box>
        </geometry>
        <material>
          <ambient>0.8 0.8 0.8 1</ambient>
          <diffuse>0.8 0.8 0.8 1</diffuse>
        </material>
      </visual>
      
      <collision name="left">
        <pose>-0.125 0 0 0 0 0</pose>
        <geometry>
          <box>
            <size>0.05 0.05 0.25</size>
          </box>
        </geometry>
      </collision>
      <visual name="left_visual">
        <pose>-0.125 0 0 0 0 0</pose>
        <geometry>
          <box>
            <size>0.05 0.05 0.25</size>
          </box>
        </geometry>
        <material>
          <ambient>0.8 0.8 0.8 1</ambient>
          <diffuse>0.8 0.8 0.8 1</diffuse>
        </material>
      </visual>
      
      <collision name="right">
        <pose>0.125 0 0 0 0 0</pose>
        <geometry>
          <box>
            <size>0.05 0.05 0.25</size>
          </box>
        </geometry>
      </collision>
      <visual name="right_visual">
        <pose>0.125 0 0 0 0 0</pose>
        <geometry>
          <box>
            <size>0.05 0.05 0.25</size>
          </box>
        </geometry>
        <material>
          <ambient>0.8 0.8 0.8 1</ambient>
          <diffuse>0.8 0.8 0.8 1</diffuse>
        </material>
      </visual>
    </link>
  </model>
</sdf>
EOF

sleep 2

echo ""
echo "步骤3: 启动Dog2机器人和控制系统..."
echo ""

# 启动完整仿真（在新终端中）
gnome-terminal -- bash -c "
cd /home/dell/aperfect/carbot_ws
source install/setup.bash
ros2 launch dog2_mpc complete_simulation.launch.py mode:=crossing
exec bash
"

sleep 5

echo ""
echo "=========================================="
echo "  仿真已启动！"
echo "=========================================="
echo ""
echo "当前状态："
echo "  - Gazebo窗口已打开"
echo "  - 窗框障碍物已生成（位置: x=1.5m）"
echo "  - Dog2机器人已加载"
echo "  - MPC+WBC控制器运行中"
echo ""
echo "触发越障："
echo "  在新终端运行："
echo "  ros2 topic pub --once /enable_crossing std_msgs/Bool \"data: true\""
echo ""
echo "监控状态："
echo "  ros2 topic echo /dog2/mpc/state"
echo "  ros2 topic echo /dog2/mpc/foot_forces"
echo ""
echo "按Ctrl+C停止所有进程"
echo "=========================================="

# 等待用户中断
wait $GAZEBO_PID

