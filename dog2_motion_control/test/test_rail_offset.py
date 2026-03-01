"""
导轨位移功能测试

验证导轨位移在IK和FK中正确工作
"""

import pytest
import numpy as np
from dog2_motion_control.kinematics_solver import create_kinematics_solver


class TestRailOffset:
    """导轨位移测试类"""
    
    @pytest.fixture
    def solver(self):
        """创建运动学求解器实例"""
        return create_kinematics_solver()
    
    def test_rail_offset_zero(self, solver):
        """测试导轨位移为0时的IK->FK round-trip"""
        leg_id = 'lf'
        target_pos = (1.0, -0.9, 0.0)
        rail_offset = 0.0
        
        # 逆运动学
        joint_angles = solver.solve_ik(leg_id, target_pos, rail_offset=rail_offset)
        assert joint_angles is not None
        
        s_m, _, _, _ = joint_angles
        assert s_m == rail_offset, f"导轨位移应该是{rail_offset}，实际: {s_m}"
        
        # 正运动学
        result_pos = solver.solve_fk(leg_id, joint_angles)
        
        # 验证round-trip
        error = np.linalg.norm(np.array(result_pos) - np.array(target_pos))
        assert error < 0.001, f"Round-trip误差应该<1mm，实际: {error*1000:.3f}mm"
    
    def test_rail_offset_positive(self, solver):
        """测试正向导轨位移的IK->FK round-trip"""
        leg_id = 'rf'  # 前右腿，导轨可以正向移动
        target_pos = (1.4, -0.9, 0.0)
        rail_offset = 0.05  # 50mm正向位移
        
        # 逆运动学
        joint_angles = solver.solve_ik(leg_id, target_pos, rail_offset=rail_offset)
        assert joint_angles is not None
        
        s_m, _, _, _ = joint_angles
        assert abs(s_m - rail_offset) < 1e-10, f"导轨位移应该是{rail_offset}，实际: {s_m}"
        
        # 正运动学
        result_pos = solver.solve_fk(leg_id, joint_angles)
        
        # 验证round-trip
        error = np.linalg.norm(np.array(result_pos) - np.array(target_pos))
        assert error < 0.001, f"Round-trip误差应该<1mm，实际: {error*1000:.3f}mm"
    
    def test_rail_offset_negative(self, solver):
        """测试负向导轨位移的IK->FK round-trip"""
        leg_id = 'lf'  # 前左腿，导轨可以负向移动
        target_pos = (1.0, -0.9, 0.0)
        rail_offset = -0.05  # 50mm负向位移
        
        # 逆运动学
        joint_angles = solver.solve_ik(leg_id, target_pos, rail_offset=rail_offset)
        assert joint_angles is not None
        
        s_m, _, _, _ = joint_angles
        assert abs(s_m - rail_offset) < 1e-10, f"导轨位移应该是{rail_offset}，实际: {s_m}"
        
        # 正运动学
        result_pos = solver.solve_fk(leg_id, joint_angles)
        
        # 验证round-trip
        error = np.linalg.norm(np.array(result_pos) - np.array(target_pos))
        assert error < 0.001, f"Round-trip误差应该<1mm，实际: {error*1000:.3f}mm"
    
    def test_rail_offset_extends_workspace(self, solver):
        """测试导轨位移扩展工作空间"""
        leg_id = 'rf'
        
        # 选择一个在导轨锁定时可能无解的位置
        target_pos = (1.5, -0.9, 0.0)
        
        # 不使用导轨位移
        joint_angles_no_rail = solver.solve_ik(leg_id, target_pos, rail_offset=0.0)
        
        # 使用导轨位移
        joint_angles_with_rail = solver.solve_ik(leg_id, target_pos, rail_offset=0.08)
        
        # 至少有一个应该有解（导轨位移扩展了工作空间）
        assert joint_angles_no_rail is not None or joint_angles_with_rail is not None
        
        # 如果使用导轨位移有解，验证round-trip
        if joint_angles_with_rail is not None:
            result_pos = solver.solve_fk(leg_id, joint_angles_with_rail)
            error = np.linalg.norm(np.array(result_pos) - np.array(target_pos))
            assert error < 0.001, f"Round-trip误差应该<1mm，实际: {error*1000:.3f}mm"
    
    def test_rail_offset_comparison(self, solver):
        """测试不同导轨位移对同一目标位置的影响"""
        leg_id = 'lf'
        target_pos = (1.0, -0.9, 0.0)
        
        # 测试不同的导轨位移
        rail_offsets = [0.0, -0.03, -0.06]
        
        for rail_offset in rail_offsets:
            joint_angles = solver.solve_ik(leg_id, target_pos, rail_offset=rail_offset)
            
            if joint_angles is not None:
                s_m, theta_haa, theta_hfe, theta_kfe = joint_angles
                
                # 验证导轨位移正确
                assert abs(s_m - rail_offset) < 1e-10
                
                # 验证FK
                result_pos = solver.solve_fk(leg_id, joint_angles)
                error = np.linalg.norm(np.array(result_pos) - np.array(target_pos))
                assert error < 0.001, f"rail_offset={rail_offset}: Round-trip误差应该<1mm"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
