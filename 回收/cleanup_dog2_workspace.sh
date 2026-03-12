#!/bin/bash

echo "=========================================="
echo "Dog2越障项目工作区清理脚本"
echo "=========================================="
echo ""

# 统计清理前的大小
echo "📊 统计清理前的大小..."
BEFORE_SIZE=$(du -sh . 2>/dev/null | cut -f1)
echo "清理前总大小: $BEFORE_SIZE"
echo ""

# 1. 删除CHAMP相关包
echo "🗑️  删除CHAMP相关包..."
rm -rf src/champ
rm -rf src/champ_teleop
rm -rf src/dog2_champ_config
rm -rf build/champ*
rm -rf install/champ*
echo "  ✓ CHAMP包已删除"

# 2. 删除演示包
echo "🗑️  删除演示包..."
rm -rf src/dog2_demos
rm -rf build/dog2_demos
rm -rf install/dog2_demos
echo "  ✓ 演示包已删除"

# 3. 删除src下的冗余目录
echo "🗑️  删除src下的冗余目录..."
rm -rf src/build
rm -rf src/install
rm -rf src/log
rm -rf src/src
rm -rf src/.vscode
echo "  ✓ 冗余目录已删除"

# 4. 删除旧的测试脚本
echo "🗑️  删除旧的测试脚本..."
rm -f test_dog2_gazebo_fixed.sh
rm -f test_dog2_movement_simple.sh
rm -f test_dog2_joints.py
rm -f test_fuel_tank_generator.py
echo "  ✓ 旧测试脚本已删除"

# 5. 删除旧的工具脚本
echo "🗑️  删除旧的工具脚本..."
rm -f create_dog2_champ_urdf.py
rm -f fix_dog2_urdf.py
rm -f fix_numpy_version.sh
rm -f cleanup_workspace.sh
echo "  ✓ 旧工具脚本已删除"

# 6. 删除旧的文档
echo "🗑️  删除旧的文档..."
rm -f CLEANUP_SUMMARY.md
rm -f DEVELOPMENT_ROADMAP.md
rm -f DOG2_PPT_DETAILED_CONTENT.md
rm -f DOG2_PROJECT_PRESENTATION.md
rm -f MPC_PROGRESS_SUMMARY.md
rm -f MPC_WBC_PLANNING_REVIEW.md
rm -f SESSION_SUMMARY_*.md
echo "  ✓ 旧文档已删除"

# 7. 删除归档目录
echo "🗑️  删除归档目录..."
rm -rf archive_20260119_143803
echo "  ✓ 归档目录已删除"

# 8. 删除Python缓存
echo "🗑️  删除Python缓存..."
rm -rf __pycache__
rm -rf .pytest_cache
rm -rf .hypothesis
echo "  ✓ Python缓存已删除"

# 9. 删除测试图片
echo "🗑️  删除测试图片..."
rm -f srbd_model_test.png
echo "  ✓ 测试图片已删除"

# 统计清理后的大小
echo ""
echo "📊 统计清理后的大小..."
AFTER_SIZE=$(du -sh . 2>/dev/null | cut -f1)
echo "清理后总大小: $AFTER_SIZE"
echo ""

echo "=========================================="
echo "✅ 清理完成！"
echo "=========================================="
echo ""
echo "保留的核心包："
echo "  ✓ dog2_dynamics (动力学模型)"
echo "  ✓ dog2_mpc (MPC控制器)"
echo "  ✓ dog2_wbc (WBC控制器)"
echo "  ✓ dog2_movement_control (基础运动控制)"
echo "  ✓ dog2_interfaces (接口定义)"
echo "  ✓ dog2_state_estimation (状态估计)"
echo "  ✓ dog2_gait_planner (步态规划)"
echo "  ✓ dog2_description (URDF模型)"
echo ""
echo "保留的核心文档："
echo "  ✓ DOG2_MPC_DEVELOPMENT_GUIDE.md"
echo "  ✓ DOG2_MPC_WBC_ARCHITECTURE.md"
echo "  ✓ MPC_WBC_IMPLEMENTATION_LOG.md"
echo "  ✓ README.md"
echo "  ✓ START_HERE.md"
echo ""
echo "保留的核心测试："
echo "  ✓ test_dog2_dynamics.py"
echo "  ✓ test_srbd_model.py"
echo "  ✓ test_osqp_interface.py"
echo "  ✓ verify_installation.py"
echo ""
echo "⚠️  下一步操作："
echo "  1. 重新编译核心包："
echo "     colcon build --packages-select dog2_dynamics dog2_mpc dog2_movement_control"
echo ""
echo "  2. 运行测试验证："
echo "     python3 test_dog2_dynamics.py"
echo "     python3 test_srbd_model.py"
echo ""
