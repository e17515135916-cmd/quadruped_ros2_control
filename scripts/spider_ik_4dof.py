#!/usr/bin/env python3
"""
Parameterized 4-DOF spider-leg IK utility.
Model: [rail d] + [hip yaw] + [thigh pitch] + [knee pitch]

This is intended as a fast validation tool for the new spider-style stance.
It does not replace the full whole-body controller.
"""

import argparse
import math
from typing import Tuple


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def solve_spider_leg_ik(
    px: float,
    py: float,
    pz: float,
    d: float,
    l1: float,
    l2: float,
    hip_x: float,
    hip_y: float,
    hip_z: float,
) -> Tuple[float, float, float]:
    """Solve [hip_yaw, thigh_pitch, knee_pitch] with rail position d.

    Target and hip offsets are expressed in body frame.
    Rail is assumed to translate along body +X.
    """

    # 1) Translate to the 3R chain base after prismatic rail movement.
    hx = hip_x + d
    hy = hip_y
    hz = hip_z

    vx = px - hx
    vy = py - hy
    vz = pz - hz

    # 2) Hip yaw decouples the lateral direction.
    hip_yaw = math.atan2(vy, vx)

    # 3) Planar 2R solve in yaw-aligned sagittal plane.
    r = math.hypot(vx, vy)
    z = vz
    dist = math.hypot(r, z)
    dist = clamp(dist, 1e-6, l1 + l2 - 1e-6)

    cos_knee = clamp((l1 * l1 + l2 * l2 - dist * dist) / (2.0 * l1 * l2), -1.0, 1.0)
    knee_pitch = math.pi - math.acos(cos_knee)

    phi = math.atan2(z, r)
    psi = math.atan2(l2 * math.sin(knee_pitch), l1 + l2 * math.cos(knee_pitch))
    thigh_pitch = phi - psi

    return hip_yaw, thigh_pitch, knee_pitch


def main() -> None:
    parser = argparse.ArgumentParser(description='4-DOF spider leg IK quick solver')
    parser.add_argument('--target', nargs=3, type=float, required=True, metavar=('PX', 'PY', 'PZ'))
    parser.add_argument('--rail', type=float, required=True, help='Prismatic rail position d (m)')
    parser.add_argument('--links', nargs=2, type=float, default=[0.20, 0.20], metavar=('L1', 'L2'))
    parser.add_argument('--hip', nargs=3, type=float, default=[0.0, 0.0, 0.0], metavar=('HX', 'HY', 'HZ'))
    args = parser.parse_args()

    q_yaw, q_thigh, q_knee = solve_spider_leg_ik(
        px=args.target[0],
        py=args.target[1],
        pz=args.target[2],
        d=args.rail,
        l1=args.links[0],
        l2=args.links[1],
        hip_x=args.hip[0],
        hip_y=args.hip[1],
        hip_z=args.hip[2],
    )

    print('hip_yaw   = {:.6f} rad'.format(q_yaw))
    print('thigh     = {:.6f} rad'.format(q_thigh))
    print('knee      = {:.6f} rad'.format(q_knee))


if __name__ == '__main__':
    main()
