# 需求文档

## 简介

本文档定义了将URDF模型参数与MPC（模型预测控制）和WBC（全身控制）代码同步的需求。

**背景**: URDF文件已经过大幅优化以适应越障任务：
- 总质量从30.76 kg减轻到11.8 kg（减轻61.6%）
- base_link惯性缩放到原来的30.6%
- 小腿惯性缩放到原来的44.4%
- 足端惯性缩放到原来的40%

由于这些参数的大幅变化，MPC/WBC代码中所有硬编码的质量和惯性值都必须更新，以确保控制算法使用正确的机器人模型参数。

## 术语表

- **URDF**: 统一机器人描述格式（Unified Robot Description Format），定义机器人的物理参数
- **MPC_Controller**: 模型预测控制器，负责生成最优控制输入
- **WBC_Controller**: 全身控制器，负责将高层命令转换为关节级控制
- **Inertia_Tensor**: 惯性张量，描述物体旋转惯性的3x3矩阵
- **Dog2_Model**: dog2机器人的动力学模型类
- **Parameter_Synchronization**: 参数同步，确保URDF与代码中的参数值一致

## 需求

### 需求 1: 机器人总质量同步

**用户故事:** 作为机器人控制工程师，我希望MPC控制器使用正确的机器人总质量，以便动力学计算、重力补偿和控制力计算准确无误。

#### 验收标准

1. WHEN MPC控制器初始化时 THEN THE MPC_Controller SHALL 使用与Gazebo仿真URDF一致的机器人总质量（约11.34 kg，基于dog2_gazebo.urdf）
2. WHEN 计算重力补偿时 THEN THE MPC_Controller SHALL 使用正确的质量值进行计算
3. WHEN 质量参数不一致时 THEN THE Parameter_Synchronization SHALL 检测并报告错误
4. WHEN 更新质量参数后 THEN THE MPC_Controller SHALL 在所有相关文件中保持一致的质量值
5. THE MPC_Controller SHALL 在以下文件中使用正确的质量值：mpc_node.cpp、mpc_node_complete.cpp、mpc_node_16d.cpp、mpc_params.yaml、complete_simulation.launch.py
6. THE Parameter_Synchronization SHALL 优先使用dog2_gazebo.urdf作为参考，因为其质量更适合越障任务

### 需求 2: 惯性张量同步

**用户故事:** 作为机器人控制工程师，我希望MPC控制器使用正确的惯性张量参数，以便角加速度计算和姿态控制准确。

#### 验收标准

1. WHEN MPC控制器初始化时 THEN THE MPC_Controller SHALL 使用与原始URDF一致的惯性张量值（已按质量比例缩放：ixx=0.0153, iyy=0.052, izz=0.044, ixy=0.00011）
2. WHEN 计算角加速度时 THEN THE MPC_Controller SHALL 使用正确的惯性张量进行计算
3. WHEN 惯性张量参数不一致时 THEN THE Parameter_Synchronization SHALL 检测并报告错误
4. WHEN 更新惯性张量后 THEN THE MPC_Controller SHALL 在所有MPC节点文件中保持一致的惯性张量值
5. THE MPC_Controller SHALL 使用与质量成比例的惯性值（质量缩放因子约0.306）

### 需求 3: 腿部几何参数验证

**用户故事:** 作为机器人控制工程师，我希望验证WBC控制器中的腿部几何参数是否与URDF一致，以便逆运动学计算准确。

#### 验收标准

1. WHEN WBC控制器初始化时 THEN THE WBC_Controller SHALL 使用与URDF一致的腿部长度参数
2. WHEN 从URDF解析关节位置时 THEN THE Parameter_Synchronization SHALL 计算实际的大腿长度（l1）和小腿长度（l2）
3. WHEN 腿部几何参数不一致时 THEN THE Parameter_Synchronization SHALL 报告差异并提供正确值
4. WHEN 更新腿部参数后 THEN THE WBC_Controller SHALL 在wbc_controller.hpp和wbc_node_complete.cpp中使用一致的值
5. THE WBC_Controller SHALL 使用正确的髋关节偏移量（hip_offset_x和hip_offset_y）

### 需求 4: 参数自动读取机制

**用户故事:** 作为系统架构师，我希望实现从URDF自动读取参数的机制，以便避免硬编码错误并确保长期的参数一致性。

#### 验收标准

1. WHEN MPC或WBC控制器初始化时 THEN THE Dog2_Model SHALL 从URDF文件读取机器人参数
2. WHEN URDF文件更新时 THEN THE Parameter_Synchronization SHALL 自动使用新的参数值而无需修改代码
3. WHEN URDF文件不存在或损坏时 THEN THE Dog2_Model SHALL 返回描述性错误消息
4. WHEN 参数读取成功时 THEN THE Dog2_Model SHALL 提供访问质量、惯性张量和几何参数的接口
5. THE Dog2_Model SHALL 支持从标准URDF路径或自定义路径读取参数

### 需求 5: 测试文件参数同步

**用户故事:** 作为测试工程师，我希望所有测试文件使用正确的机器人参数，以便测试结果反映真实的机器人行为。

#### 验收标准

1. WHEN 运行MPC测试时 THEN THE Test_Files SHALL 使用与URDF一致的质量和惯性张量参数
2. WHEN 测试文件使用硬编码参数时 THEN THE Parameter_Synchronization SHALL 更新所有test_*.cpp文件中的参数值
3. WHEN 参数不一致时 THEN THE Test_Files SHALL 在测试失败时提供清晰的错误信息
4. WHEN 更新参数后 THEN THE Test_Files SHALL 通过所有现有的单元测试和集成测试
5. THE Test_Files SHALL 包含参数验证测试以检测未来的不一致问题

### 需求 6: 配置文件参数同步

**用户故事:** 作为系统集成工程师，我希望配置文件和启动文件使用正确的机器人参数，以便仿真和实际运行时行为一致。

#### 验收标准

1. WHEN 加载MPC配置时 THEN THE mpc_params.yaml SHALL 包含与URDF一致的质量参数
2. WHEN 启动仿真时 THEN THE complete_simulation.launch.py SHALL 使用正确的机器人参数
3. WHEN 配置参数不一致时 THEN THE Parameter_Synchronization SHALL 在启动时检测并警告
4. WHEN 更新配置文件后 THEN THE System SHALL 在运行时正确加载和应用新参数
5. THE Configuration_Files SHALL 提供参数来源的文档说明（URDF路径或硬编码值）

### 需求 7: 参数一致性验证工具

**用户故事:** 作为开发者，我希望有一个工具可以验证URDF与代码中参数的一致性，以便快速发现和修复不一致问题。

#### 验收标准

1. WHEN 运行验证工具时 THEN THE Validation_Tool SHALL 比较URDF与所有代码文件中的参数值
2. WHEN 发现不一致时 THEN THE Validation_Tool SHALL 生成详细的差异报告
3. WHEN 所有参数一致时 THEN THE Validation_Tool SHALL 返回成功状态
4. WHEN 验证完成时 THEN THE Validation_Tool SHALL 提供修复建议和受影响文件列表
5. THE Validation_Tool SHALL 支持作为CI/CD流程的一部分自动运行
