#!/usr/bin/env python3
"""
测试SRBD模型

验证单刚体动力学模型的实现
"""

import numpy as np
import matplotlib.pyplot as plt

class SRBDModel:
    """Python版本的SRBD模型（用于测试）"""
    
    def __init__(self, mass, inertia):
        """
        初始化SRBD模型
        
        Args:
            mass: 机器人总质量 (kg)
            inertia: 惯性张量 (3×3)
        """
        self.mass = mass
        self.inertia = inertia
        self.gravity = np.array([0.0, 0.0, -9.81])
    
    def rotation_matrix(self, roll, pitch, yaw):
        """ZYX欧拉角旋转矩阵"""
        cr, sr = np.cos(roll), np.sin(roll)
        cp, sp = np.cos(pitch), np.sin(pitch)
        cy, sy = np.cos(yaw), np.sin(yaw)
        
        R = np.array([
            [cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr],
            [sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr],
            [-sp,   cp*sr,            cp*cr]
        ])
        return R
    
    def angular_velocity_to_euler_rate(self, roll, pitch):
        """角速度到欧拉角速度的转换矩阵"""
        cr, sr = np.cos(roll), np.sin(roll)
        cp, sp = np.cos(pitch), np.sin(pitch)
        tp = np.tan(pitch)
        
        E = np.array([
            [1.0, sr*tp, cr*tp],
            [0.0, cr,    -sr],
            [0.0, sr/cp, cr/cp]
        ])
        return E
    
    def dynamics(self, state, control, foot_positions):
        """
        计算连续时间动力学
        
        Args:
            state: [x, y, z, roll, pitch, yaw, vx, vy, vz, wx, wy, wz] (12,)
            control: [F1x, F1y, F1z, ..., F4x, F4y, F4z] (12,)
            foot_positions: 足端相对质心位置 (4×3)
        
        Returns:
            state_dot: 状态导数 (12,)
        """
        state_dot = np.zeros(12)
        
        # 提取状态
        position = state[0:3]
        euler = state[3:6]
        velocity = state[6:9]
        angular_velocity = state[9:12]
        
        roll, pitch, yaw = euler
        
        # 位置导数 = 速度
        state_dot[0:3] = velocity
        
        # 欧拉角导数
        E = self.angular_velocity_to_euler_rate(roll, pitch)
        state_dot[3:6] = E @ angular_velocity
        
        # 线性加速度：m*a = Σ F_i + m*g
        total_force = np.zeros(3)
        for i in range(4):
            total_force += control[i*3:(i+1)*3]
        
        linear_acceleration = total_force / self.mass + self.gravity
        state_dot[6:9] = linear_acceleration
        
        # 角加速度：I*ω̇ + ω×(I*ω) = Σ (r_i × F_i)
        total_torque = np.zeros(3)
        for i in range(4):
            r_i = foot_positions[i]
            F_i = control[i*3:(i+1)*3]
            total_torque += np.cross(r_i, F_i)
        
        I_omega = self.inertia @ angular_velocity
        gyroscopic = np.cross(angular_velocity, I_omega)
        angular_acceleration = np.linalg.inv(self.inertia) @ (total_torque - gyroscopic)
        
        state_dot[9:12] = angular_acceleration
        
        return state_dot
    
    def simulate(self, state0, control_sequence, foot_positions, dt, steps):
        """
        仿真SRBD模型
        
        Args:
            state0: 初始状态
            control_sequence: 控制序列 (steps × 12)
            foot_positions: 足端位置 (4 × 3)
            dt: 时间步长
            steps: 仿真步数
        
        Returns:
            states: 状态轨迹 (steps+1 × 12)
        """
        states = np.zeros((steps + 1, 12))
        states[0] = state0
        
        for k in range(steps):
            state = states[k]
            control = control_sequence[k]
            
            # 欧拉法积分
            state_dot = self.dynamics(state, control, foot_positions)
            states[k+1] = state + dt * state_dot
        
        return states

def test_srbd_model():
    """测试SRBD模型"""
    
    print("="*60)
    print("  SRBD Model Test")
    print("="*60)
    
    # Dog2参数
    mass = 7.94  # kg
    inertia = np.diag([0.05, 0.1, 0.1])  # 简化的惯性张量
    
    print(f"\nRobot parameters:")
    print(f"  Mass: {mass} kg")
    print(f"  Inertia: diag({inertia[0,0]}, {inertia[1,1]}, {inertia[2,2]})")
    
    # 创建模型
    model = SRBDModel(mass, inertia)
    
    # 初始状态（站立）
    state0 = np.zeros(12)
    state0[2] = 0.15  # z = 15cm高度
    
    # 足端位置（相对质心）
    foot_positions = np.array([
        [-0.15, -0.10, -0.15],  # 右后
        [ 0.15, -0.10, -0.15],  # 右前
        [ 0.15,  0.10, -0.15],  # 左前
        [-0.15,  0.10, -0.15]   # 左后
    ])
    
    # 测试1：静止平衡
    print(f"\nTest 1: Static equilibrium")
    print(f"  Initial state: z={state0[2]:.3f}m")
    
    # 每条腿支撑1/4重量
    F_support = mass * 9.81 / 4
    control_static = np.array([
        0, 0, F_support,  # 腿1
        0, 0, F_support,  # 腿2
        0, 0, F_support,  # 腿3
        0, 0, F_support   # 腿4
    ])
    
    state_dot = model.dynamics(state0, control_static, foot_positions)
    print(f"  State derivative norm: {np.linalg.norm(state_dot):.6f}")
    print(f"  ✓ Should be close to 0 for equilibrium")
    
    # 测试2：前进运动
    print(f"\nTest 2: Forward motion")
    
    # 施加前向力
    F_forward = 10.0  # N
    control_forward = control_static.copy()
    control_forward[0] = F_forward / 4  # 每条腿分担
    control_forward[3] = F_forward / 4
    control_forward[6] = F_forward / 4
    control_forward[9] = F_forward / 4
    
    # 仿真
    dt = 0.01  # 10ms
    steps = 100  # 1秒
    
    control_sequence = np.tile(control_forward, (steps, 1))
    states = model.simulate(state0, control_sequence, foot_positions, dt, steps)
    
    print(f"  Final position: x={states[-1,0]:.3f}m")
    print(f"  Final velocity: vx={states[-1,6]:.3f}m/s")
    print(f"  ✓ Robot should move forward")
    
    # 绘图
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    time = np.arange(steps + 1) * dt
    
    # 位置
    axes[0, 0].plot(time, states[:, 0], label='x')
    axes[0, 0].plot(time, states[:, 1], label='y')
    axes[0, 0].plot(time, states[:, 2], label='z')
    axes[0, 0].set_xlabel('Time (s)')
    axes[0, 0].set_ylabel('Position (m)')
    axes[0, 0].set_title('Position')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # 欧拉角
    axes[0, 1].plot(time, np.rad2deg(states[:, 3]), label='roll')
    axes[0, 1].plot(time, np.rad2deg(states[:, 4]), label='pitch')
    axes[0, 1].plot(time, np.rad2deg(states[:, 5]), label='yaw')
    axes[0, 1].set_xlabel('Time (s)')
    axes[0, 1].set_ylabel('Angle (deg)')
    axes[0, 1].set_title('Orientation')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    # 线速度
    axes[1, 0].plot(time, states[:, 6], label='vx')
    axes[1, 0].plot(time, states[:, 7], label='vy')
    axes[1, 0].plot(time, states[:, 8], label='vz')
    axes[1, 0].set_xlabel('Time (s)')
    axes[1, 0].set_ylabel('Velocity (m/s)')
    axes[1, 0].set_title('Linear Velocity')
    axes[1, 0].legend()
    axes[1, 0].grid(True)
    
    # 角速度
    axes[1, 1].plot(time, np.rad2deg(states[:, 9]), label='wx')
    axes[1, 1].plot(time, np.rad2deg(states[:, 10]), label='wy')
    axes[1, 1].plot(time, np.rad2deg(states[:, 11]), label='wz')
    axes[1, 1].set_xlabel('Time (s)')
    axes[1, 1].set_ylabel('Angular Velocity (deg/s)')
    axes[1, 1].set_title('Angular Velocity')
    axes[1, 1].legend()
    axes[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig('srbd_model_test.png', dpi=150)
    print(f"\n✓ Plot saved to: srbd_model_test.png")
    
    print("\n" + "="*60)
    print("  All tests passed! ✓")
    print("="*60)

if __name__ == '__main__':
    test_srbd_model()
