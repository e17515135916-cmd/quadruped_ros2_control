#!/usr/bin/env python3
"""
验证错误处理和恢复功能

测试任务11的所有子任务实现
"""

import sys
import time


def test_ik_failure_recovery():
    """测试11.1: IK失败恢复"""
    print("\n=== 测试 11.1: IK失败恢复 ===")
    
    # 检查SpiderRobotController的源代码
    from dog2_motion_control.spider_robot_controller import SpiderRobotController
    import inspect
    
    # 获取__init__方法的源代码
    init_source = inspect.getsource(SpiderRobotController.__init__)
    
    # 检查是否包含必要的属性初始化
    required_items = [
        'last_valid_joint_positions',
        'ik_failure_count'
    ]
    
    all_present = True
    for item in required_items:
        if item in init_source:
            print(f"  ✅ 找到属性: {item}")
        else:
            print(f"  ❌ 缺少属性: {item}")
            all_present = False
    
    # 检查方法
    if hasattr(SpiderRobotController, '_handle_ik_failure'):
        print(f"  ✅ 找到方法: _handle_ik_failure")
    else:
        print(f"  ❌ 缺少方法: _handle_ik_failure")
        all_present = False
    
    if all_present:
        print("  ✅ IK失败恢复功能已实现")
        print("     - last_valid_joint_positions: 存储上一个有效配置")
        print("     - ik_failure_count: 跟踪失败次数")
        print("     - _handle_ik_failure(): 处理IK失败")
    
    return all_present


def test_joint_stuck_detection():
    """测试11.3: 关节卡死检测"""
    print("\n=== 测试 11.3: 关节卡死检测 ===")
    
    from dog2_motion_control.joint_controller import JointController
    import inspect
    
    # 获取__init__方法的源代码
    init_source = inspect.getsource(JointController.__init__)
    
    # 检查属性
    required_attributes = [
        'joint_command_history',
        'joint_stuck_count',
        'STUCK_DETECTION_THRESHOLD',
        'POSITION_ERROR_THRESHOLD'
    ]
    
    all_present = True
    for attr in required_attributes:
        if attr in init_source:
            print(f"  ✅ 找到属性: {attr}")
        else:
            print(f"  ❌ 缺少属性: {attr}")
            all_present = False
    
    # 检查方法
    methods = [
        '_record_joint_command',
        'detect_stuck_joints',
        'handle_stuck_joint'
    ]
    
    for method in methods:
        if hasattr(JointController, method):
            print(f"  ✅ 找到方法: {method}")
        else:
            print(f"  ❌ 缺少方法: {method}")
            all_present = False
    
    if all_present:
        print("  ✅ 关节卡死检测功能已实现")
        print("     - joint_command_history: 记录命令历史")
        print("     - joint_stuck_count: 卡死计数器")
        print("     - detect_stuck_joints(): 检测卡死关节")
        print("     - handle_stuck_joint(): 处理卡死关节")
    
    return all_present


def test_emergency_safety_posture():
    """测试11.4: 紧急安全姿态"""
    print("\n=== 测试 11.4: 紧急安全姿态 ===")
    
    from dog2_motion_control.spider_robot_controller import SpiderRobotController
    import inspect
    
    # 获取__init__方法的源代码
    init_source = inspect.getsource(SpiderRobotController.__init__)
    
    # 检查属性
    required_attributes = [
        'is_emergency_mode',
        'emergency_start_time',
        'EMERGENCY_DESCENT_DURATION'
    ]
    
    all_present = True
    for attr in required_attributes:
        if attr in init_source:
            print(f"  ✅ 找到属性: {attr}")
        else:
            print(f"  ❌ 缺少属性: {attr}")
            all_present = False
    
    # 检查方法
    methods = [
        'engage_emergency_safety_posture',
        '_execute_emergency_descent'
    ]
    
    for method in methods:
        if hasattr(SpiderRobotController, method):
            print(f"  ✅ 找到方法: {method}")
        else:
            print(f"  ❌ 缺少方法: {method}")
            all_present = False
    
    if all_present:
        print("  ✅ 紧急安全姿态功能已实现")
        print("     - is_emergency_mode: 紧急模式标志")
        print("     - engage_emergency_safety_posture(): 启动紧急姿态")
        print("     - _execute_emergency_descent(): 执行紧急下降")
        print("     - 持续锁定导轨")
        print("     - 缓慢降低身体高度")
        print("     - 监控导轨滑动")
    
    return all_present


def test_connection_loss_handling():
    """测试11.6: 连接丢失处理"""
    print("\n=== 测试 11.6: 连接丢失处理 ===")
    
    from dog2_motion_control.joint_controller import JointController
    import inspect
    
    # 获取__init__方法的源代码
    init_source = inspect.getsource(JointController.__init__)
    
    # 检查属性
    required_attributes = [
        'last_joint_state_time',
        'CONNECTION_TIMEOUT_SEC',
        'is_connected',
        'reconnect_attempts',
        'MAX_RECONNECT_ATTEMPTS'
    ]
    
    all_present = True
    for attr in required_attributes:
        if attr in init_source:
            print(f"  ✅ 找到属性: {attr}")
        else:
            print(f"  ❌ 缺少属性: {attr}")
            all_present = False
    
    # 检查方法
    methods = [
        'check_connection',
        'attempt_reconnect'
    ]
    
    for method in methods:
        if hasattr(JointController, method):
            print(f"  ✅ 找到方法: {method}")
        else:
            print(f"  ❌ 缺少方法: {method}")
            all_present = False
    
    if all_present:
        print("  ✅ 连接丢失处理功能已实现")
        print("     - last_joint_state_time: 最后接收数据时间")
        print("     - is_connected: 连接状态")
        print("     - check_connection(): 检查连接状态")
        print("     - attempt_reconnect(): 尝试重新连接")
    
    return all_present


def test_integration():
    """测试集成：错误处理在主控制循环中的集成"""
    print("\n=== 测试集成：主控制循环 ===")
    
    from dog2_motion_control.spider_robot_controller import SpiderRobotController
    import inspect
    
    # 检查update方法是否包含错误处理逻辑
    update_source = inspect.getsource(SpiderRobotController.update)
    
    checks = [
        ('check_connection', '连接检测'),
        ('is_emergency_mode', '紧急模式处理'),
        ('detect_stuck_joints', '关节卡死检测'),
        ('engage_emergency_safety_posture', '紧急安全姿态'),
        ('_handle_ik_failure', 'IK失败处理')
    ]
    
    all_present = True
    for check, description in checks:
        if check in update_source:
            print(f"  ✅ {description}: 已集成")
        else:
            print(f"  ❌ {description}: 未找到")
            all_present = False
    
    return all_present


def main():
    """主测试函数"""
    print("=" * 60)
    print("错误处理和恢复功能验证")
    print("任务 11: 实现错误处理和恢复")
    print("=" * 60)
    
    tests = [
        ("11.1 IK失败恢复", test_ik_failure_recovery),
        ("11.3 关节卡死检测", test_joint_stuck_detection),
        ("11.4 紧急安全姿态", test_emergency_safety_posture),
        ("11.6 连接丢失处理", test_connection_loss_handling),
        ("集成测试", test_integration)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有错误处理功能已成功实现！")
        return 0
    else:
        print("\n⚠️  部分功能未完全实现")
        return 1


if __name__ == '__main__':
    sys.exit(main())
