#!/usr/bin/env python3
"""
验证零角度时的腿部方向
确认腿向下延伸（狗式）而不是向外（蜘蛛式）
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import time

class ZeroAngleVerifier(Node):
    def __init__(self):
        super().__init__('zero_angle_verifier')
        
        # 创建发布器
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # 等待发布器准备好
        time.sleep(1)
        
        self.get_logger().info('========================================')
        self.get_logger().info('零角度腿部方向验证')
        self.get_logger().info('========================================')
        self.get_logger().info('')
        
    def verify_zero_angle_orientation(self):
        """验证零角度时的腿部方向"""
        
        self.get_logger().info('设置所有关节角度为零...')
        self.get_logger().info('')
        
        # 发布零角度
        self.publish_all_zero()
        time.sleep(3)
        
        self.get_logger().info('========================================')
        self.get_logger().info('验证结果：')
        self.get_logger().info('========================================')
        self.get_logger().info('')
        self.get_logger().info('请在RViz中确认：')
        self.get_logger().info('')
        self.get_logger().info('✓ 腿部方向：')
        self.get_logger().info('  - 腿应该向下延伸（狗式）')
        self.get_logger().info('  - 不应该向外延伸（蜘蛛式）')
        self.get_logger().info('')
        self.get_logger().info('✓ 髋关节支架：')
        self.get_logger().info('  - 支架显示为两个box（垂直体 + 水平平台）')
        self.get_logger().info('  - 水平平台平行于地面')
        self.get_logger().info('')
        self.get_logger().info('✓ 关节轴：')
        self.get_logger().info('  - 髋关节旋转轴应该是X轴（红色）')
        self.get_logger().info('  - 旋转时腿做前后运动，不是左右运动')
        self.get_logger().info('')
        self.get_logger().info('========================================')
        self.get_logger().info('如果以上都正确，说明已成功从蜘蛛式改为狗式！')
        self.get_logger().info('========================================')
        self.get_logger().info('')
        self.get_logger().info('现在可以截图保存用于文档')
        self.get_logger().info('')
        
    def publish_all_zero(self):
        """发布所有关节为零角度"""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        
        # 所有关节名称
        msg.name = [
            'j1', 'j11', 'j111',  # 腿1
            'j2', 'j21', 'j211',  # 腿2
            'j3', 'j31', 'j311',  # 腿3
            'j4', 'j41', 'j411',  # 腿4
        ]
        
        # 所有关节位置设为0
        msg.position = [0.0] * 12
        
        self.joint_pub.publish(msg)

def main():
    rclpy.init()
    
    verifier = ZeroAngleVerifier()
    
    try:
        # 运行验证
        verifier.verify_zero_angle_orientation()
        
        # 保持节点运行以便观察
        verifier.get_logger().info('按 Ctrl+C 退出...')
        time.sleep(10)  # 保持10秒用于观察和截图
        
    except KeyboardInterrupt:
        verifier.get_logger().info('验证中断')
    finally:
        verifier.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
