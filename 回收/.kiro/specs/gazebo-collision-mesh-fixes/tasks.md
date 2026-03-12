# 实施计划：Gazebo 碰撞网格修复

## 概述

本实施计划将修复 DOG2 机器人在 Gazebo 仿真中因碰撞网格重叠导致的"炸飞"问题。核心策略是用简单的碰撞原语替换复杂的 STL Mesh，截断小腿碰撞体，并配置碰撞过滤。

## 任务

- [x] 1. 创建 STL Mesh 测量工具
  - 编写 Python 脚本测量 STL 文件的边界框尺寸
  - 支持计算长度、宽度、高度和质心位置
  - 输出 JSON 格式的测量结果
  - _Requirements: 4.1_

- [x] 2. 测量现有 STL Mesh 文件
  - 测量大腿 Mesh (l111.STL, l211.STL, l311.STL, l411.STL)
  - 测量小腿 Mesh (l1111.STL, l2111.STL, l3111.STL, l4111.STL)
  - 记录每个 Mesh 的边界框尺寸到配置文件
  - _Requirements: 4.1_

- [x] 3. 备份当前 URDF 文件
  - 创建带时间戳的备份文件
  - 备份到 backups/ 目录
  - 记录备份文件路径
  - _Requirements: 10.1_

- [x] 4. 修改大腿 Link 碰撞几何体
  - [x] 4.1 将大腿 collision 标签从 mesh 改为 cylinder
    - 计算 cylinder 半径（Mesh 横截面半径 × 0.9）
    - 计算 cylinder 长度（Mesh 长度 × 0.85）
    - 设置 cylinder 原点偏移使其居中
    - 保留 visual 标签使用 STL Mesh
    - _Requirements: 1.1, 1.3, 1.4_

  - [x] 4.2 编写属性测试验证大腿碰撞原语
    - **Property 1: 碰撞原语使用**
    - **Validates: Requirements 1.1**

- [-] 5. 修改小腿 Link 碰撞几何体
  - [x] 5.1 将小腿 collision 标签从 mesh 改为 cylinder
    - 计算 cylinder 半径（Mesh 横截面半径 × 0.9）
    - 计算 cylinder 长度（Mesh 长度 - 0.03 米）
    - 设置 cylinder 原点偏移，使末端距离足端 >= 10mm
    - 保留 visual 标签使用 STL Mesh
    - _Requirements: 1.2, 2.1, 2.2, 2.3_

  - [ ]* 5.2 编写属性测试验证小腿碰撞体截断
    - **Property 7: 小腿碰撞体截断**
    - **Validates: Requirements 2.1, 2.2**

- [ ] 6. 移除 collision 标签中的 scale 属性
  - 检查所有 Link 的 collision 标签
  - 移除任何 scale 属性
  - _Requirements: 1.5_

- [ ]* 7. 编写属性测试验证 Visual Mesh 保留
  - **Property 2: Visual Mesh 保留**
  - **Validates: Requirements 1.4**

- [ ]* 8. 编写属性测试验证 Scale 属性移除
  - **Property 3: Scale 属性移除**
  - **Validates: Requirements 1.5**

- [ ] 9. 配置碰撞过滤
  - [ ] 9.1 在 Xacro 宏中添加碰撞过滤配置
    - 为每条腿禁用大腿-小腿碰撞
    - 为每条腿禁用小腿-足端碰撞
    - 使用 Gazebo 的 disable_link_collision 或 SDF 配置
    - _Requirements: 3.1, 3.2_

  - [ ]* 9.2 编写属性测试验证碰撞过滤配置
    - **Property 8: 碰撞过滤配置**
    - **Validates: Requirements 3.2, 3.5**

- [ ] 10. 调整足端接触参数
  - 将足端 kp 从 1000000.0 降低到 10000.0
  - 将足端 mu1 和 mu2 从 1.5 调整到 1.0
  - 保持 kd=100.0, minDepth=0.001, maxVel=0.1
  - _Requirements: 6.1, 6.2, 6.3_

- [ ] 11. Checkpoint - 验证 URDF 语法
  - 使用 check_urdf 工具验证 URDF 语法
  - 使用 xacro 命令生成完整 URDF
  - 检查是否有错误或警告
  - 如有问题，询问用户

- [ ]* 12. 编写碰撞体间隙验证脚本
  - [ ]* 12.1 实现几何距离计算函数
    - 计算 cylinder 之间的最小距离
    - 计算 cylinder 与 sphere 之间的最小距离
    - 考虑 Link 的位置和旋转变换
    - _Requirements: 7.1, 7.2_

  - [ ]* 12.2 编写属性测试验证相邻 Link 间隙
    - **Property 5: 相邻 Link 间隙**
    - **Validates: Requirements 1.6, 8.2**

  - [ ]* 12.3 编写属性测试验证小腿足端间隙
    - **Property 6: 小腿足端间隙**
    - **Validates: Requirements 2.3, 8.3**

- [ ]* 13. 编写属性测试验证碰撞体尺寸比例
  - **Property 4: 碰撞体尺寸比例**
  - **Validates: Requirements 1.3, 4.2, 4.3, 4.4**

- [ ] 14. 在 RViz 中可视化碰撞几何体
  - 创建 launch 文件显示碰撞几何体
  - 验证碰撞体位置和尺寸正确
  - 检查是否有明显的重叠或间隙不足
  - _Requirements: 7.4_

- [ ] 15. Checkpoint - Gazebo 加载测试
  - 启动 Gazebo 仿真
  - 加载修改后的机器人模型
  - 检查是否有错误或警告
  - 如有问题，询问用户

- [ ] 16. Gazebo 稳定性测试
  - 在 Gazebo 中生成机器人
  - 运行 10 秒仿真
  - 监控基座位置和速度
  - 验证机器人不会"炸飞"或剧烈抖动
  - _Requirements: 9.1, 9.2, 9.3_

- [ ] 17. 创建回滚脚本
  - 编写脚本从备份恢复原始 URDF
  - 测试回滚功能
  - _Requirements: 10.4_

- [ ] 18. 更新文档
  - 记录碰撞体尺寸和偏移量
  - 说明为什么使用碰撞原语而非 Mesh
  - 记录测试结果和验证数据
  - _Requirements: 10.2, 10.3, 10.5_

## 注意事项

- 标记 `*` 的任务是可选的测试任务，可以跳过以加快 MVP 开发
- 每个 checkpoint 任务都需要确保测试通过后再继续
- 如果 Gazebo 测试失败，需要调整碰撞体尺寸或偏移量
- 属性测试应该运行至少 100 次迭代以验证配置一致性
