#!/usr/bin/env python3
"""
离线越障分析脚本

输出指标：
- 导轨使用率（归一化行程占比）
- IK失败率
- 关节速度峰值（导轨 m/s，旋转 rad/s）

可用于快速比较不同 ik_regularization 参数在窗框/台阶场景下的表现。
"""

import argparse
import csv
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

from dog2_motion_control.config_loader import ConfigLoader
from dog2_motion_control.gait_generator import GaitGenerator
from dog2_motion_control.kinematics_solver import create_kinematics_solver


def _step_obstacle_adjustment(
    leg_id: str,
    t: float,
    scenario: str,
    stride_length: float,
) -> Tuple[float, float, float]:
    """为离线场景注入额外足端位移扰动。"""
    if scenario == "flat":
        return (0.0, 0.0, 0.0)

    cycle = t % 2.0

    if scenario == "window":
        # 模拟穿越窗框：在中段抬脚并微调横向
        if 0.6 <= cycle <= 1.3:
            dz = 0.04 + 0.02 * math.sin((cycle - 0.6) / 0.7 * math.pi)
            dy = 0.01 if leg_id in ("lf", "lh") else -0.01
            return (0.0, dy, dz)
        return (0.0, 0.0, 0.0)

    if scenario == "high_step":
        # 模拟高落差台阶：后半程前探 + 抬高
        if cycle >= 1.0:
            dx = 0.35 * stride_length
            dz = 0.06
            return (dx, 0.0, dz)
        return (0.0, 0.0, 0.0)

    raise ValueError(f"Unsupported scenario: {scenario}")


def run_analysis(
    config_path: Optional[str],
    scenario: str,
    duration: float,
    dt: float,
    csv_path: str = "",
) -> Dict[str, float]:
    loader = ConfigLoader(config_path)
    loader.load()
    gait_cfg = loader.get_gait_config()

    solver = create_kinematics_solver()
    solver.configure_regularization(loader.get_ik_regularization())

    # 使用与模块化离线分析一致的固定站立角度标定名义落脚点，避免
    # 默认 nominal_pos 与当前机器人几何/腿序不一致导致 IK 频繁失配。
    standing_angles = {
        "lf": (0.0, 0.0, 0.3000, -0.5000),
        "rf": (0.0, 0.0, 0.3000, -0.5000),
        "lh": (0.0, 0.0, 0.3000, -0.5000),
        "rh": (0.0, 0.0, 0.3000, -0.5000),
    }
    nominal_positions = {
        leg_id: np.array(solver.solve_fk(leg_id, angles), dtype=float)
        for leg_id, angles in standing_angles.items()
    }

    gait = GaitGenerator(gait_cfg, nominal_positions)

    sim_time = 0.0
    total_samples = 0
    ik_failures = 0

    prev_joint: Dict[str, Tuple[float, float, float, float]] = {}
    peak_rail_vel = 0.0
    peak_rot_vel = 0.0

    rail_usage_norm: List[float] = []
    records = []

    velocity_cmd = (0.08, 0.0, 0.10)

    while sim_time < duration:
        gait.update(dt, velocity_cmd)
        for leg_id, leg_params in solver.leg_params.items():
            foot = gait.get_foot_target(leg_id)
            phase_scalar = gait.get_phase_progress_scalar(leg_id)
            rail_min, rail_max = leg_params.joint_limits["rail"]
            rail_mid = 0.5 * (rail_min + rail_max)
            rail_half = 0.5 * (rail_max - rail_min)
            rail_hint = rail_mid + phase_scalar * rail_half

            dx, dy, dz = _step_obstacle_adjustment(
                leg_id=leg_id,
                t=sim_time,
                scenario=scenario,
                stride_length=gait_cfg.stride_length,
            )
            foot_target = (foot[0] + dx, foot[1] + dy, foot[2] + dz)

            ik = solver.solve_ik(leg_id, foot_target, rail_offset=rail_hint)
            total_samples += 1
            if ik is None:
                ik_failures += 1
                continue

            s_m, coxa, femur, tibia = ik
            rail_span = max(rail_max - rail_min, 1e-9)
            rail_usage_norm.append(abs((s_m - rail_mid) / (0.5 * rail_span)))

            if leg_id in prev_joint:
                p = prev_joint[leg_id]
                rail_vel = abs((s_m - p[0]) / dt)
                rot_vel = max(abs((coxa - p[1]) / dt), abs((femur - p[2]) / dt), abs((tibia - p[3]) / dt))
                peak_rail_vel = max(peak_rail_vel, rail_vel)
                peak_rot_vel = max(peak_rot_vel, rot_vel)

            prev_joint[leg_id] = ik

            if csv_path:
                records.append({
                    "t": sim_time,
                    "leg": leg_id,
                    "rail_m": s_m,
                    "coxa_rad": coxa,
                    "femur_rad": femur,
                    "tibia_rad": tibia,
                    "target_x": foot_target[0],
                    "target_y": foot_target[1],
                    "target_z": foot_target[2],
                })

        sim_time += dt

    ik_failure_rate = (ik_failures / total_samples) if total_samples > 0 else 0.0
    avg_rail_usage = float(np.mean(rail_usage_norm)) if rail_usage_norm else 0.0
    p95_rail_usage = float(np.percentile(rail_usage_norm, 95)) if rail_usage_norm else 0.0

    result = {
        "scenario": scenario,
        "duration_s": duration,
        "dt_s": dt,
        "samples": float(total_samples),
        "ik_failure_rate": ik_failure_rate,
        "avg_rail_usage_norm": avg_rail_usage,
        "p95_rail_usage_norm": p95_rail_usage,
        "peak_rail_velocity_mps": peak_rail_vel,
        "peak_rot_velocity_radps": peak_rot_vel,
    }

    if csv_path:
        out = Path(csv_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0].keys()) if records else [
                "t", "leg", "rail_m", "coxa_rad", "femur_rad", "tibia_rad", "target_x", "target_y", "target_z"
            ])
            writer.writeheader()
            writer.writerows(records)

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="离线越障分析")
    parser.add_argument("--config", default="", help="配置文件路径（默认使用包内gait_params.yaml）")
    parser.add_argument("--scenario", default="window", choices=["flat", "window", "high_step"], help="离线场景")
    parser.add_argument("--duration", type=float, default=12.0, help="仿真时长（秒）")
    parser.add_argument("--dt", type=float, default=0.02, help="离散步长（秒）")
    parser.add_argument("--csv", default="", help="可选，导出逐样本CSV")
    args = parser.parse_args()

    summary = run_analysis(
        config_path=args.config if args.config else None,
        scenario=args.scenario,
        duration=args.duration,
        dt=args.dt,
        csv_path=args.csv,
    )

    print("=" * 64)
    print("Offline Obstacle Analysis Summary")
    print("=" * 64)
    for k, v in summary.items():
        if isinstance(v, float):
            print(f"{k:28s}: {v:.6f}")
        else:
            print(f"{k:28s}: {v}")


if __name__ == "__main__":
    main()
