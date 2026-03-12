# 查看URDF说明

## 命令分析

```bash
cd /home/dell/aperfect/carbot_ws && \
colcon build --packages-select dog2_description --symlink-install && \
killall -9 robot_state_publisher joint_state_publisher rviz2 2>/dev/null; \
sleep 1 && \
source install/setup.bash && \
ros2 launch dog2_description view_dog2.launch.py &
```

## 使用的URDF文件

这个命令打开的是：

**`src/dog2_description/urdf/dog2.urdf.xacro`**

### 详细说明

1. **Launch文件位置**：
   - `src/dog2_description/launch/view_dog2.launch.py`

2. **URDF文件配置**：
   ```python
   xacro_file_name = 'dog2.urdf.xacro'  # 使用xacro文件
   xacro_path = os.path.join(pkg_share, 'urdf', xacro_file_name)
   ```

3. **实际文件路径**：
   - **源文件**：`src/dog2_description/urdf/dog2.urdf.xacro`
   - **安装后**：`install/dog2_description/share/dog2_description/urdf/dog2.urdf.xacro`

4. **处理流程**：
   - Launch文件使用 `xacro` 命令动态处理 `.xacro` 文件
   - 生成最终的URDF内容传递给 `robot_state_publisher`
   - 不会生成独立的 `.urdf` 文件

## 当前URDF状态

- **文件**：`src/dog2_description/urdf/dog2.urdf.xacro`
- **最后修改**：2026-02-02 15:08
- **版本**：从 `backups/urdf_correct_versions/` 恢复的正确版本（2026-01-27）
- **Mesh文件**：
  - l1.STL: 已恢复到正确版本 ✓
  - l2.STL: 已恢复到正确版本 ✓

## 验证方法

### 1. 查看源文件
```bash
cat src/dog2_description/urdf/dog2.urdf.xacro | head -20
```

### 2. 查看安装后的文件
```bash
cat install/dog2_description/share/dog2_description/urdf/dog2.urdf.xacro | head -20
```

### 3. 生成完整URDF（用于调试）
```bash
xacro src/dog2_description/urdf/dog2.urdf.xacro > /tmp/dog2_generated.urdf
cat /tmp/dog2_generated.urdf | grep -A 5 "mesh filename"
```

## Mesh文件引用

URDF文件引用的mesh文件位置：
- **视觉mesh**：`src/dog2_description/meshes/*.STL`
- **碰撞mesh**：`src/dog2_description/meshes/collision/*_collision.STL`

当前使用的L1和L2文件：
- `src/dog2_description/meshes/l1.STL` (MD5: cbe7ec6700ac8bb809002fcde6021fdf)
- `src/dog2_description/meshes/l2.STL` (MD5: 8fa84f39061f9ab4d1dc35dc5c92746f)

## 相关文档

- `URDF_MESH_RESTORE_SUMMARY.md` - URDF和Mesh恢复总结
- `ROS1_URDF_ROS2_GAZEBO_ANALYSIS.md` - URDF分析文档
- `L1旋转完成总结.md` - L1部件修改历史

## 注意事项

1. **编译后才生效**：修改URDF后需要运行 `colcon build` 才能生效
2. **Symlink安装**：使用 `--symlink-install` 可以避免每次都重新复制文件
3. **Mesh文件路径**：URDF中的mesh路径是相对于package的，格式为 `package://dog2_description/meshes/xxx.STL`
