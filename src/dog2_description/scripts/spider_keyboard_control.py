#!/usr/bin/env python3
import sys
import termios
import tty
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class SpiderKeyboardControl(Node):
    def __init__(self):
        super().__init__('spider_keyboard_control')
        
        # 腿部关节控制器
        self.joint_pub = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )
        
        # 导轨关节控制器
        self.rail_pub = self.create_publisher(
            JointTrajectory,
            '/rail_position_controller/joint_trajectory',
            10
        )
        
        self.joint_names = [
            'lf_haa_joint', 'lf_hfe_joint', 'lf_kfe_joint',
            'rf_haa_joint', 'rf_hfe_joint', 'rf_kfe_joint',
            'lh_haa_joint', 'lh_hfe_joint', 'lh_kfe_joint',
            'rh_haa_joint', 'rh_hfe_joint', 'rh_kfe_joint'
        ]
        
        self.rail_names = ['j1', 'j2', 'j3', 'j4']
        
        # 初始姿态
        self.haa = 0.0
        self.hfe = 0.6
        self.kfe = 1.2
        self.rail = 0.0
        
        self.print_usage()

    def print_usage(self):
        msg = """
蜘蛛机器人键盘控制
---------------------------
腿部姿态控制:
    W / S : 大腿关节 (HFE) +/-
    A / D : 侧摆关节 (HAA) +/-
    Q / E : 膝盖关节 (KFE) +/-

导轨控制:
    U / J : 导轨位置 (Rail) +/-

其他:
    SPACE : 恢复默认站立姿态
    X     : 退出
---------------------------
        """
        self.get_logger().info(msg)

    def get_key(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key

    def publish_pose(self):
        # 发布腿部关节
        jt = JointTrajectory()
        jt.joint_names = self.joint_names
        p = JointTrajectoryPoint()
        p.positions = [
            self.haa, self.hfe, self.kfe, # LF
            self.haa, self.hfe, self.kfe, # RF
            self.haa, self.hfe, self.kfe, # LH
            self.haa, self.hfe, self.kfe  # RH
        ]
        p.time_from_start = Duration(sec=0, nanosec=100000000) # 0.1s
        jt.points = [p]
        self.joint_pub.publish(jt)
        
        # 发布导轨关节 (注意左右限位不同)
        rt = JointTrajectory()
        rt.joint_names = self.rail_names
        rp = JointTrajectoryPoint()
        # j1/j3 范围 [-0.111, 0], j2/j4 范围 [0, 0.111]
        rail_val = max(0.0, min(0.111, self.rail))
        rp.positions = [-rail_val, rail_val, -rail_val, rail_val]
        rp.time_from_start = Duration(sec=0, nanosec=100000000)
        rt.points = [rp]
        self.rail_pub.publish(rt)

    def run(self):
        try:
            while True:
                key = self.get_key()
                if key == 'w': self.hfe += 0.05
                elif key == 's': self.hfe -= 0.05
                elif key == 'a': self.haa += 0.05
                elif key == 'd': self.haa -= 0.05
                elif key == 'q': self.kfe += 0.05
                elif key == 'e': self.kfe -= 0.05
                elif key == 'u': self.rail += 0.01
                elif key == 'j': self.rail -= 0.01
                elif key == ' ':
                    self.haa, self.hfe, self.kfe, self.rail = 0.0, 0.6, 1.2, 0.0
                elif key == 'x':
                    break
                
                self.publish_pose()
                print(f"\rPose: HAA={self.haa:.2f}, HFE={self.hfe:.2f}, KFE={self.kfe:.2f}, Rail={self.rail:.3f}", end="")
                
        except Exception as e:
            print(e)
        finally:
            self.publish_pose()

def main(args=None):
    rclpy.init(args=args)
    node = SpiderKeyboardControl()
    node.run()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
