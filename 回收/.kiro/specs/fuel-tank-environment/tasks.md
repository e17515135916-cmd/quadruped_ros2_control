# Implementation Plan: Fuel Tank Environment

## Overview

本实现计划将创建一个飞机油箱内部仿真环境，包含Python生成器脚本、Gazebo世界文件和ROS2启动文件集成。

## Tasks

- [x] 1. 创建配置数据结构和验证逻辑
  - [x] 1.1 创建 FuelTankConfig 数据类
    - 定义所有配置参数（油箱尺寸、桁条参数、穿越孔参数、起始位置）
    - 设置合理的默认值
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  - [x] 1.2 实现配置验证函数
    - 验证参数为正数
    - 验证桁条间距大于桁条宽度
    - 验证穿越孔尺寸合理
    - _Requirements: 4.1, 4.2, 4.3_
  - [x] 1.3 编写配置验证的属性测试
    - **Property 1: Configuration Round-Trip**
    - **Validates: Requirements 1.3, 4.1, 4.2, 4.3**

- [x] 2. 实现SDF模型生成器
  - [x] 2.1 实现底板生成函数
    - 生成带碰撞和视觉属性的底板SDF
    - 设置金属材质外观
    - _Requirements: 1.1, 1.4_
  - [x] 2.2 实现桁条网格生成函数
    - 生成横向和纵向交错的桁条
    - 按配置间距排列
    - _Requirements: 1.2, 1.3, 1.4_
  - [x] 2.3 编写桁条网格的属性测试
    - **Property 2: Stringer Grid Pattern Validity**
    - **Validates: Requirements 1.2, 2.4, 5.2**
  - [x] 2.4 实现穿越孔面板生成函数
    - 生成带中央孔洞的面板结构
    - 支持配置孔洞尺寸
    - _Requirements: 2.1, 2.2, 2.4_
  - [x] 2.5 编写元素计数的属性测试
    - **Property 3: Element Count Correctness**
    - **Validates: Requirements 4.4, 4.5**

- [x] 3. 实现完整世界文件生成器
  - [x] 3.1 实现世界文件框架生成
    - 生成SDF头部和世界元素
    - 添加光源配置
    - 添加物理引擎配置
    - _Requirements: 3.1, 3.4_
  - [x] 3.2 整合所有模型到世界文件
    - 组合底板、桁条、面板模型
    - 设置相机视角
    - _Requirements: 3.1, 3.5_
  - [x] 3.3 编写SDF结构有效性的属性测试
    - **Property 4: SDF Structure Validity**
    - **Validates: Requirements 3.1, 3.4, 3.5**
  - [x] 3.4 实现文件保存功能
    - 保存到指定路径
    - 处理目录创建
    - _Requirements: 3.1_

- [x] 4. Checkpoint - 验证生成器功能
  - 确保所有测试通过，如有问题请询问用户

- [x] 5. 创建ROS2启动文件集成
  - [x] 5.1 创建 dog2_fuel_tank.launch.py
    - 加载fuel_tank.world
    - 配置机器人起始位置
    - 集成现有Dog2控制器
    - _Requirements: 3.2, 5.1, 5.3_
  - [x] 5.2 更新CMakeLists.txt安装配置
    - 添加世界文件安装
    - 添加启动文件安装
    - _Requirements: 3.2_

- [x] 6. 创建便捷启动脚本
  - [x] 6.1 创建 start_dog2_fuel_tank.sh
    - 一键启动油箱环境和Dog2
    - 提供使用说明
    - _Requirements: 3.2, 3.3_

- [x] 7. Final Checkpoint - 完整功能验证
  - 确保所有测试通过，如有问题请询问用户
  - 验证Gazebo能正确加载环境
  - 验证Dog2能在环境中正常运行

## Notes

- 所有测试任务均为必需
- 属性测试使用 hypothesis 库
- 世界文件将保存到 `src/champ/champ_gazebo/worlds/fuel_tank.world`
- 启动文件将添加到 `src/dog2_champ_config/launch/`
