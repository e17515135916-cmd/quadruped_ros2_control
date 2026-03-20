"""
运动学求解器

实现腿部的逆运动学(IK)和正运动学(FK)求解
支持4条腿的坐标系转换
"""

from typing import Optional, Tuple, Dict
import logging
import numpy as np
from .leg_parameters import LegParameters


class KinematicsSolver:
    """
    运动学求解器

    负责计算腿部的逆运动学和正运动学。
    当前阶段：导轨默认锁定在0.0米，但保留 rail_offset 接口。
    IK 使用与 FK 一致的几何链进行数值求解（阻尼最小二乘）。
    """

    def __init__(self, leg_params: Dict[str, LegParameters]):
        self.leg_params = leg_params
        self.logger = logging.getLogger(__name__)

    def _rotation_matrix_from_rpy(self, roll: float, pitch: float, yaw: float) -> np.ndarray:
        """从RPY角度创建旋转矩阵。"""
        Rx = np.array([
            [1.0, 0.0, 0.0],
            [0.0, np.cos(roll), -np.sin(roll)],
            [0.0, np.sin(roll), np.cos(roll)]
        ])
        Ry = np.array([
            [np.cos(pitch), 0.0, np.sin(pitch)],
            [0.0, 1.0, 0.0],
            [-np.sin(pitch), 0.0, np.cos(pitch)]
        ])
        Rz = np.array([
            [np.cos(yaw), -np.sin(yaw), 0.0],
            [np.sin(yaw), np.cos(yaw), 0.0],
            [0.0, 0.0, 1.0]
        ])
        return Rz @ Ry @ Rx

    def _transform_to_leg_frame(self, foot_pos: np.ndarray, leg_id: str) -> np.ndarray:
        """将脚部位置从base_link坐标系转换到腿部局部坐标系。"""
        params = self.leg_params[leg_id]
        pos_relative = foot_pos - params.base_position
        roll, pitch, yaw = params.base_rotation
        R = self._rotation_matrix_from_rpy(roll, pitch, yaw)
        return R.T @ pos_relative

    def _transform_from_leg_frame(self, pos_local: np.ndarray, leg_id: str) -> np.ndarray:
        """将位置从腿部局部坐标系转换到base_link坐标系。"""
        params = self.leg_params[leg_id]
        roll, pitch, yaw = params.base_rotation
        R = self._rotation_matrix_from_rpy(roll, pitch, yaw)
        return R @ pos_local + params.base_position

    def _homogeneous(self, R: np.ndarray, t: np.ndarray) -> np.ndarray:
        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = t
        return T

    def _rot_axis_angle(self, axis: np.ndarray, angle: float) -> np.ndarray:
        axis = axis / (np.linalg.norm(axis) + 1e-12)
        x, y, z = axis
        c = np.cos(angle)
        s = np.sin(angle)
        C = 1 - c
        return np.array([
            [c + x * x * C, x * y * C - z * s, x * z * C + y * s],
            [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
            [z * x * C - y * s, z * y * C + x * s, c + z * z * C]
        ])

    def _forward_local(self, params: LegParameters, s_m: float, q: np.ndarray) -> np.ndarray:
        """在腿局部坐标系中计算脚点位置。"""
        theta_haa, theta_hfe, theta_kfe = q

        # rail_joint: prismatic along local X
        T = self._homogeneous(np.eye(3), np.array([s_m, 0.0, 0.0]))

        # coxa_joint origin and rotation（完全由参数提供，不做腿别硬编码）
        T = T @ self._homogeneous(self._rotation_matrix_from_rpy(*params.hip_rpy), params.hip_offset)
        T = T @ self._homogeneous(self._rot_axis_angle(np.array([-1.0, 0.0, 0.0]), theta_haa), np.zeros(3))

        # femur_joint origin and rotation
        T = T @ self._homogeneous(self._rotation_matrix_from_rpy(*params.knee_rpy), params.knee_offset)
        T = T @ self._homogeneous(self._rot_axis_angle(np.array([-1.0, 0.0, 0.0]), theta_hfe), np.zeros(3))

        # tibia_joint origin and rotation
        T = T @ self._homogeneous(self._rotation_matrix_from_rpy(*params.tibia_rpy), params.tibia_offset)
        T = T @ self._homogeneous(self._rot_axis_angle(np.array([-1.0, 0.0, 0.0]), theta_kfe), np.zeros(3))

        # 脚端 = tibia_joint 坐标系中的 shin_xyz 偏移（tibia_link 接触代理位置）
        shin = np.asarray(params.shin_xyz)
        p = T @ np.array([shin[0], shin[1], shin[2], 1.0])
        return p[:3]

    def _check_joint_limits(self, leg_id: str, theta_haa: float, theta_hfe: float, theta_kfe: float) -> bool:
        params = self.leg_params[leg_id]
        limits = params.joint_limits

        coxa_min, coxa_max = limits['coxa']
        femur_min, femur_max = limits['femur']
        tibia_min, tibia_max = limits['tibia']

        if theta_haa < coxa_min or theta_haa > coxa_max:
            return False
        if theta_hfe < femur_min or theta_hfe > femur_max:
            return False
        if theta_kfe < tibia_min or theta_kfe > tibia_max:
            return False
        return True

    def solve_ik(
        self,
        leg_id: str,
        foot_pos: Tuple[float, float, float],
        rail_offset: float = 0.0
    ) -> Optional[Tuple[float, float, float, float]]:
        """
        求解逆运动学（数值法）。

        Returns:
            (s_m, theta_haa, theta_hfe, theta_kfe) 或 None
        """
        params = self.leg_params[leg_id]
        s_m = rail_offset

        rail_min, rail_max = params.joint_limits['rail']
        if s_m < rail_min or s_m > rail_max:
            return None

        target_local = self._transform_to_leg_frame(np.array(foot_pos), leg_id)

        # FK 标定的站立角度（index 0 = 主初始猜测值）
        # 通过 calibrate_standing_pose.py 扫描 (hfe, kfe) 空间得到，
        # 满足脚端 z = -0.13 m (±5mm)，hfe > 0，kfe < 0
        # Requirements: 2.1, 2.2
        _STANDING_ANGLES = {
            'lf': np.array([0.0, 0.3000, -0.5000]),
            'lh': np.array([0.0, 0.3000, -0.5000]),
            'rh': np.array([0.0, 0.3000, -0.5000]),
            'rf': np.array([0.0, 0.3000, -0.5000]),
        }

        initial_guesses = [
            # index 0: FK 标定的站立角度（主初始猜测值）
            _STANDING_ANGLES[leg_id],
            # 原有中等弯曲初值（备用）
            np.array([0.0, 0.7, -1.2]),
            np.array([0.0, 0.5, -1.0]),
            np.array([0.0, 1.0, -1.4]),
            np.array([0.3, 0.7, -1.0]),
            np.array([-0.3, 0.7, -1.0]),
            # 新增深蹲初值，提升低高度目标收敛率
            np.array([0.0, 1.3, -2.3]),
            np.array([0.0, 1.5, -2.5]),
            np.array([0.0, 1.6, -2.6]),
            np.array([0.3, 1.4, -2.4]),
            np.array([-0.3, 1.4, -2.4]),
            np.array([0.6, 1.5, -2.5]),
            np.array([-0.6, 1.5, -2.5]),
        ]

        best_q = None
        best_err = float('inf')
        best_seed = None

        for q0 in initial_guesses:
            q = q0.copy()
            for _ in range(80):
                cur = self._forward_local(params, s_m, q)
                err_vec = target_local - cur
                err = float(np.linalg.norm(err_vec))
                if err < 1e-4:
                    if self._check_joint_limits(leg_id, q[0], q[1], q[2]):
                        return (s_m, float(q[0]), float(q[1]), float(q[2]))
                    break

                eps = 1e-6
                J = np.zeros((3, 3))
                for i in range(3):
                    dq = np.zeros(3)
                    dq[i] = eps
                    p2 = self._forward_local(params, s_m, q + dq)
                    J[:, i] = (p2 - cur) / eps

                # Damped Least Squares
                lam = 1e-3
                JT = J.T
                H = JT @ J + lam * np.eye(3)
                try:
                    dq = np.linalg.solve(H, JT @ err_vec)
                except np.linalg.LinAlgError:
                    break

                dq = np.clip(dq, -0.2, 0.2)
                q = q + dq

                # 软限位夹紧，避免发散
                limits = params.joint_limits
                q[0] = np.clip(q[0], limits['coxa'][0], limits['coxa'][1])
                q[1] = np.clip(q[1], limits['femur'][0], limits['femur'][1])
                q[2] = np.clip(q[2], limits['tibia'][0], limits['tibia'][1])

            final_err = float(np.linalg.norm(target_local - self._forward_local(params, s_m, q)))
            if final_err < best_err and self._check_joint_limits(leg_id, q[0], q[1], q[2]):
                best_err = final_err
                best_q = q.copy()
                best_seed = q0.copy()

        if best_q is not None and best_err < 5e-3:
            return (s_m, float(best_q[0]), float(best_q[1]), float(best_q[2]))

        self.logger.warning(
            "IK failed leg=%s rail=%.4f target_local=%s best_err=%.6f best_q=%s best_seed=%s",
            leg_id,
            s_m,
            np.array2string(target_local, precision=5, suppress_small=True),
            best_err,
            None if best_q is None else np.array2string(best_q, precision=5, suppress_small=True),
            None if best_seed is None else np.array2string(best_seed, precision=5, suppress_small=True),
        )

        return None

    def solve_fk(
        self,
        leg_id: str,
        joint_positions: Tuple[float, float, float, float]
    ) -> Tuple[float, float, float]:
        """求解正运动学。"""
        params = self.leg_params[leg_id]
        s_m, theta_haa_rad, theta_hfe_rad, theta_kfe_rad = joint_positions

        pos_local = self._forward_local(
            params,
            s_m,
            np.array([theta_haa_rad, theta_hfe_rad, theta_kfe_rad])
        )
        pos_global = self._transform_from_leg_frame(pos_local, leg_id)
        return (float(pos_global[0]), float(pos_global[1]), float(pos_global[2]))


def create_kinematics_solver() -> KinematicsSolver:
    from .leg_parameters import LEG_PARAMETERS
    return KinematicsSolver(LEG_PARAMETERS)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    solver = create_kinematics_solver()

    # 仅用于离线快速验证，不依赖ROS节点
    from .gait_generator import GaitConfig, GaitGenerator

    gait = GaitGenerator(GaitConfig())
    gait.update(0.0, (0.0, 0.0, 0.0))  # 静止工况

    test_legs = ['lf', 'rf', 'lh', 'rh']
    fk_seed = (0.0, 0.0, 0.7, -1.4)

    print("\n=== IK离线验证：FK->IK Ground Truth ===")
    for leg_id in test_legs:
        fk_target = solver.solve_fk(leg_id, fk_seed)
        ik_res = solver.solve_ik(leg_id, fk_target)

        if ik_res is None:
            print(f"[{leg_id}] FK->IK: FAIL target={fk_target}")
            continue

        fk_back = solver.solve_fk(leg_id, ik_res)
        err = float(np.linalg.norm(np.array(fk_back) - np.array(fk_target)))
        print(f"[{leg_id}] FK->IK: OK err={err:.6e} ik={ik_res}")

    print("\n=== IK离线验证：Gait nominal target ===")
    for leg_id in test_legs:
        nominal_target = gait.get_foot_target(leg_id)
        ik_res = solver.solve_ik(leg_id, nominal_target)

        if ik_res is None:
            print(f"[{leg_id}] nominal: FAIL target={nominal_target}")
            continue

        fk_back = solver.solve_fk(leg_id, ik_res)
        err = float(np.linalg.norm(np.array(fk_back) - np.array(nominal_target)))
        print(f"[{leg_id}] nominal: OK err={err:.6e} ik={ik_res}")
