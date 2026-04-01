#!/usr/bin/env python3
"""
离线越障分析脚本

在不依赖ROS运行时的情况下，复用 GaitGenerator 与 KinematicsSolver
生成足端目标并统计导轨利用率、IK失败率与关节连续性指标。
"""

import argparse
import csv
from dataclasses import dataclass
from typing import Dict, Tuple, List
import numpy as np

from dog2_motion_control.config_loader import ConfigLoader
from dog2_motion_control.gait_generator import GaitGenerator, GaitConfig
from dog2_motion_control.kinematics_solver import create_kinematics_solver


@dataclass
class ObstacleConfig:
    step_x: float
    step_height: float
    window_x_start: float
    window_x_end: float
    window_height: float


LEG_IDS = ["lf", "rf", "lh", "rh"]


def _compute_nominal_positions(solver, standing_angles: Dict[str, Tuple[float, float, float, float]]):
    return {
        leg_id: np.array(solver.solve_fk(leg_id, angles), dtype=float)
        for leg_id, angles in standing_angles.items()
    }


def _apply_obstacle_profile(pos: np.ndarray, cfg: ObstacleConfig) -> np.ndarray:
    adjusted = pos.copy()

    # Step obstacle: when x exceeds threshold, raise z target
    if adjusted[0] > cfg.step_x:
        adjusted[2] += cfg.step_height

    # Window frame: if x in [start, end], lift to pass through
    if cfg.window_x_start <= adjusted[0] <= cfg.window_x_end:
        adjusted[2] += cfg.window_height

    return adjusted


def _rail_stats(rail_positions: List[float], rail_min: float, rail_max: float):
    rail_mid = 0.5 * (rail_min + rail_max)
    rail_span = max(rail_max - rail_min, 1e-6)
    rail_norm = [(s - rail_mid) / rail_span for s in rail_positions]
    return {
        "mean_abs": float(np.mean(np.abs(rail_norm))) if rail_norm else 0.0,
        "max_abs": float(np.max(np.abs(rail_norm))) if rail_norm else 0.0,
        "mean": float(np.mean(rail_norm)) if rail_norm else 0.0,
    }


def _scenario_from_name(name: str, args) -> ObstacleConfig:
    scenario = name.strip().lower()
    if scenario == "flat":
        return ObstacleConfig(
            step_x=1e9,
            step_height=0.0,
            window_x_start=1e9,
            window_x_end=1e9 + 1.0,
            window_height=0.0,
        )
    if scenario == "step":
        return ObstacleConfig(
            step_x=args.step_x,
            step_height=args.step_height,
            window_x_start=1e9,
            window_x_end=1e9 + 1.0,
            window_height=0.0,
        )
    if scenario == "window":
        return ObstacleConfig(
            step_x=1e9,
            step_height=0.0,
            window_x_start=args.window_x_start,
            window_x_end=args.window_x_end,
            window_height=args.window_height,
        )
    if scenario == "mixed":
        return ObstacleConfig(
            step_x=args.step_x,
            step_height=args.step_height,
            window_x_start=args.window_x_start,
            window_x_end=args.window_x_end,
            window_height=args.window_height,
        )
    raise ValueError(f"Unsupported scenario '{name}', choose from flat/step/window/mixed")


def _analyze_single_scenario(
    args,
    solver,
    gait,
    obstacle_cfg: ObstacleConfig,
    scenario_name: str,
):
    rail_records: Dict[str, List[float]] = {leg: [] for leg in LEG_IDS}
    joint_delta_records: Dict[str, List[float]] = {leg: [] for leg in LEG_IDS}
    ik_failures = {leg: 0 for leg in LEG_IDS}
    last_q: Dict[str, Tuple[float, float, float, float]] = {}

    steps = int(args.duration / args.dt)

    for _ in range(steps):
        gait.update(args.dt, (args.vx, args.vy, args.omega))
        for leg_id in LEG_IDS:
            target = np.array(gait.get_foot_target(leg_id), dtype=float)
            target = _apply_obstacle_profile(target, obstacle_cfg)

            phase_scalar = gait.get_phase_progress_scalar(leg_id)
            leg_params = solver.leg_params[leg_id]
            rail_min, rail_max = leg_params.joint_limits['rail']
            rail_mid = 0.5 * (rail_min + rail_max)
            rail_half_span = 0.5 * (rail_max - rail_min)
            rail_hint = rail_mid + phase_scalar * rail_half_span

            ik = solver.solve_ik(leg_id, tuple(target), rail_offset=rail_hint)
            if ik is None:
                ik_failures[leg_id] += 1
                continue

            rail_records[leg_id].append(ik[0])
            if leg_id in last_q:
                dq = np.array(ik) - np.array(last_q[leg_id])
                joint_delta_records[leg_id].append(float(np.linalg.norm(dq)))
            last_q[leg_id] = ik

    rows: List[Dict[str, float]] = []
    for leg_id in LEG_IDS:
        rail_min, rail_max = solver.leg_params[leg_id].joint_limits['rail']
        rail_stats = _rail_stats(rail_records[leg_id], rail_min, rail_max)
        mean_dq = float(np.mean(joint_delta_records[leg_id])) if joint_delta_records[leg_id] else 0.0
        max_dq = float(np.max(joint_delta_records[leg_id])) if joint_delta_records[leg_id] else 0.0
        rows.append(
            {
                "scenario": scenario_name,
                "leg": leg_id,
                "ik_failures": ik_failures[leg_id],
                "rail_mean_abs_norm": rail_stats["mean_abs"],
                "rail_max_abs_norm": rail_stats["max_abs"],
                "rail_mean_norm": rail_stats["mean"],
                "joint_mean_dq": mean_dq,
                "joint_max_dq": max_dq,
            }
        )
    return rows


def _print_report(args, all_rows: List[Dict[str, float]]):
    print("\n=== 离线越障分析报告 ===")
    print(f"duration: {args.duration:.2f}s, dt: {args.dt:.3f}s")
    print(f"velocity: vx={args.vx:.2f} vy={args.vy:.2f} omega={args.omega:.2f}")
    print(f"step(default): x>{args.step_x:.2f} z+{args.step_height:.3f}m")
    print(f"window(default): x in [{args.window_x_start:.2f}, {args.window_x_end:.2f}] z+{args.window_height:.3f}m\n")

    for scenario in sorted(set(r["scenario"] for r in all_rows)):
        print(f"--- scenario: {scenario} ---")
        rows = [r for r in all_rows if r["scenario"] == scenario]
        for row in rows:
            leg_id = row["leg"]
            print(f"[{leg_id}] IK failures: {int(row['ik_failures'])}")
            print(
                f"[{leg_id}] rail mean|norm|: {row['rail_mean_abs_norm']:.3f}, "
                f"max|norm|: {row['rail_max_abs_norm']:.3f}"
            )
            print(f"[{leg_id}] rail mean norm: {row['rail_mean_norm']:.3f}")
            print(f"[{leg_id}] mean |dq|: {row['joint_mean_dq']:.4f}, max |dq|: {row['joint_max_dq']:.4f}\n")


def _write_csv(csv_path: str, rows: List[Dict[str, float]]):
    fieldnames = [
        "scenario",
        "leg",
        "ik_failures",
        "rail_mean_abs_norm",
        "rail_max_abs_norm",
        "rail_mean_norm",
        "joint_mean_dq",
        "joint_max_dq",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def run_analysis(args):
    cfg_loader = ConfigLoader(args.config)
    cfg_loader.load()

    gait_cfg = cfg_loader.get_gait_config()
    gait_cfg.stride_length = args.stride_length
    gait_cfg.stride_height = args.stride_height
    gait_cfg.cycle_time = args.cycle_time

    solver = create_kinematics_solver()
    solver.configure_regularization(cfg_loader.get_ik_regularization())

    standing_angles = {
        "lf": (0.0, 0.0, 0.3000, -0.5000),
        "lh": (0.0, 0.0, 0.3000, -0.5000),
        "rh": (0.0, 0.0, 0.3000, -0.5000),
        "rf": (0.0, 0.0, 0.3000, -0.5000),
    }
    nominal_positions = _compute_nominal_positions(solver, standing_angles)
    all_rows: List[Dict[str, float]] = []

    if args.batch:
        scenarios = [s.strip() for s in args.scenarios.split(",") if s.strip()]
    else:
        scenarios = ["custom"]

    for scenario_name in scenarios:
        if scenario_name == "custom":
            obstacle_cfg = ObstacleConfig(
                step_x=args.step_x,
                step_height=args.step_height,
                window_x_start=args.window_x_start,
                window_x_end=args.window_x_end,
                window_height=args.window_height,
            )
        else:
            obstacle_cfg = _scenario_from_name(scenario_name, args)

        gait = GaitGenerator(GaitConfig(**gait_cfg.__dict__), nominal_positions)
        rows = _analyze_single_scenario(args, solver, gait, obstacle_cfg, scenario_name)
        all_rows.extend(rows)

    _print_report(args, all_rows)
    if args.csv_out:
        _write_csv(args.csv_out, all_rows)
        print(f"CSV exported to: {args.csv_out}")


def main():
    parser = argparse.ArgumentParser(description="Offline obstacle analysis for rail-augmented IK")
    parser.add_argument("--config", type=str, default=None, help="YAML config path (optional)")
    parser.add_argument("--duration", type=float, default=10.0)
    parser.add_argument("--dt", type=float, default=0.02)
    parser.add_argument("--vx", type=float, default=0.06)
    parser.add_argument("--vy", type=float, default=0.0)
    parser.add_argument("--omega", type=float, default=0.0)
    parser.add_argument("--stride-length", type=float, default=0.06)
    parser.add_argument("--stride-height", type=float, default=0.03)
    parser.add_argument("--cycle-time", type=float, default=2.0)
    parser.add_argument("--step-x", type=float, default=0.15)
    parser.add_argument("--step-height", type=float, default=0.05)
    parser.add_argument("--window-x-start", type=float, default=-0.05)
    parser.add_argument("--window-x-end", type=float, default=0.05)
    parser.add_argument("--window-height", type=float, default=0.04)
    parser.add_argument("--batch", action="store_true", help="run multiple presets defined in --scenarios")
    parser.add_argument(
        "--scenarios",
        type=str,
        default="flat,step,window,mixed",
        help="comma separated preset scenarios: flat/step/window/mixed",
    )
    parser.add_argument("--csv-out", type=str, default=None, help="export metrics to CSV file path")

    args = parser.parse_args()
    run_analysis(args)


if __name__ == "__main__":
    main()
