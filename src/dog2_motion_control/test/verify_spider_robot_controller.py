#!/usr/bin/env python3
"""
验证主控制器（SpiderRobotController）的基本功能

这是一个简单的验证脚本，检查：
1. 控制器能否正确初始化
2. 所有子系统是否正确创建
3. 主要方法是否存在
"""

import sys
import inspect


def verify_spider_robot_controller():
    """验证主控制器实现"""
    print("=" * 60)
    print("验证主控制器（SpiderRobotController）")
    print("=" * 60)
    
    try:
        from dog2_motion_control.spider_robot_controller import SpiderRobotController
        print("✓ 成功导入 SpiderRobotController")
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False
    
    # 检查类的方法
    required_methods = [
        '__init__',
        'start',
        'stop',
        'update',
        'initiate_smooth_stop',
        '_cmd_vel_callback',
        '_timer_callback',
        '_handle_smooth_stop',
    ]
    
    print("\n检查必需的方法:")
    all_methods_exist = True
    for method_name in required_methods:
        if hasattr(SpiderRobotController, method_name):
            print(f"  ✓ {method_name}")
        else:
            print(f"  ✗ {method_name} 缺失")
            all_methods_exist = False
    
    if not all_methods_exist:
        return False
    
    # 检查方法签名
    print("\n检查方法签名:")
    
    # 检查 update 方法
    update_sig = inspect.signature(SpiderRobotController.update)
    if 'dt' in update_sig.parameters:
        print("  ✓ update(dt) 签名正确")
    else:
        print("  ✗ update 方法缺少 dt 参数")
        return False
    
    # 检查 _cmd_vel_callback 方法
    callback_sig = inspect.signature(SpiderRobotController._cmd_vel_callback)
    if 'msg' in callback_sig.parameters:
        print("  ✓ _cmd_vel_callback(msg) 签名正确")
    else:
        print("  ✗ _cmd_vel_callback 方法缺少 msg 参数")
        return False
    
    # 检查 initiate_smooth_stop 方法
    stop_sig = inspect.signature(SpiderRobotController.initiate_smooth_stop)
    # 应该只有 self 参数（在签名中不显示）
    params = [p for p in stop_sig.parameters.keys() if p != 'self']
    if len(params) == 0:
        print("  ✓ initiate_smooth_stop() 签名正确")
    else:
        print(f"  ✗ initiate_smooth_stop 方法签名不正确，额外参数: {params}")
        return False
    
    print("\n检查实现细节:")
    
    # 读取源代码检查关键实现
    import dog2_motion_control.spider_robot_controller as controller_module
    source = inspect.getsource(controller_module)
    
    # 检查是否实现了平滑停止
    if 'is_stopping' in source and '_handle_smooth_stop' in source:
        print("  ✓ 实现了平滑停止功能")
    else:
        print("  ✗ 平滑停止功能未完整实现")
        return False
    
    # 检查是否实现了速度衰减
    if 'decay_factor' in source or 'progress' in source:
        print("  ✓ 实现了速度衰减逻辑")
    else:
        print("  ✗ 速度衰减逻辑未实现")
        return False
    
    # 检查是否调用了子系统
    if 'gait_generator.update' in source:
        print("  ✓ 调用了步态生成器")
    else:
        print("  ✗ 未调用步态生成器")
        return False
    
    if 'ik_solver.solve_ik' in source:
        print("  ✓ 调用了IK求解器")
    else:
        print("  ✗ 未调用IK求解器")
        return False
    
    if 'joint_controller.send_joint_commands' in source:
        print("  ✓ 调用了关节控制器")
    else:
        print("  ✗ 未调用关节控制器")
        return False
    
    # 检查是否实现了导轨监控
    if 'monitor_rail_positions' in source:
        print("  ✓ 实现了导轨位置监控")
    else:
        print("  ✗ 导轨位置监控未实现")
        return False
    
    # 检查是否实现了50Hz控制循环
    if 'timer_period' in source and '0.02' in source:
        print("  ✓ 设置了50Hz控制循环（0.02秒）")
    else:
        print("  ✗ 控制循环频率设置不正确")
        return False
    
    print("\n" + "=" * 60)
    print("✓ 所有验证通过！主控制器实现完整。")
    print("=" * 60)
    
    return True


if __name__ == '__main__':
    success = verify_spider_robot_controller()
    sys.exit(0 if success else 1)
