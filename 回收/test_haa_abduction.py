#!/usr/bin/env python3
"""
测试 HAA 关节的外展/内收功能
验证 HAA 关节是否能控制腿部左右摆动（垂直于腿部平面）
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import time
import math

class HAAAbductionTest(Node):
    def __init__(self):
        super().__init__('haa_abduction_test')
        self.publisher = self.create_publisher(JointState, '/joint_states', 10)
        
        # 等待 RViz 启动
        time.sleep(2)
        
        print("=" * 60)
        print("HAA 关节外展/内收测试")
        print("=" * 60)
        print("\n测试说明：")
        print("- HAA 关节应该控制腿部的外展/内收（左右摆动）")
        print("- 观察腿部是否垂直于身体平面摆动")
        print("- 如果腿部在身体平面内旋转，说明配置错误")
        print("\n" + "=" * 60)
        
    def test_haa_motion(self):
        """测试 HAA 关节的运动"""
        joint_state = JointState()
        joint_state.header.stamp = self.get_clock().now().to_msg()
        
        # 所有关节名称
        joint_state.name = [
            'j1', 'lf_haa_joint', 'lf_hfe_joint', 'lf_kfe_joint',
            'j2', 'rf_haa_joint', 'rf_hfe_joint', 'rf_kfe_joint',
            'j3', 'lh_haa_joint', 'lh_hfe_joint', 'lh_kfe_joint',
            'j4', 'rh_haa_joint', 'rh_hfe_joint', 'rh_kfe_joint'
        ]
        
        # 测试序列
        test_angles = [0.0, 0.3, 0.6, 0.3, 0.0, -0.3, -0.6, -0.3, 0.0]
        
        print("\n开始测试 HAA 关节...")
        print("观察前左腿 (lf) 的运动\n")
        
        for i, angle in enumerate(test_angles):
            print(f"步骤 {i+1}/{len(test_angles)}: HAA 角度 = {angle:.2f} rad ({math.degrees(angle):.1f}°)")
            
            # 设置所有关节位置
            joint_state.position = [
                0.0,  # j1 (prismatic)
                angle,  # lf_haa_joint - 测试外展/内收
                0.0,  # lf_hfe_joint
                0.0,  # lf_kfe_joint
                0.0,  # j2
                0.0,  # rf_haa_joint
                0.0,  # rf_hfe_joint
                0.0,  # rf_kfe_joint
                0.0,  # j3
                0.0,  # lh_haa_joint
                0.0,  # lh_hfe_joint
                0.0,  # lh_kfe_joint
                0.0,  # j4
                0.0,  # rh_haa_joint
                0.0,  # rh_hfe_joint
                0.0,  # rh_kfe_joint
            ]
            
            joint_state.header.stamp = self.get_clock().now().to_msg()
            self.publisher.publish(joint_state)
            time.sleep(1.0)
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("\n预期结果：")
        print("✓ 前左腿应该左右摆动（外展/内收）")
        print("✓ 腿部运动应该垂直于身体平面")
        print("✓ 大腿和小腿应该保持直线，整条腿一起摆动")
        print("\n如果腿部在身体平面内旋转，说明 HAA 配置错误")
        print("=" * 60)

def main():
    rclpy.init()
    node = HAAAbductionTest()
    
    try:
        node.test_haa_motion()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
