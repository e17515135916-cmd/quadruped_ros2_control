"""Shared Dog2 joint semantic contract.

This module centralizes the local-axis and fixed-origin conventions that the
URDF and motion-control geometry are expected to share.
"""

from __future__ import annotations

import math
import numpy as np


HALF_PI = math.pi / 2.0

# Fixed leg-root orientation used by the normalized rail joints.
LEG_BASE_RPY = np.array([HALF_PI, 0.0, 0.0], dtype=float)

# Fixed revolute joint origin rotations shared by all four legs.
COXA_ORIGIN_RPY = np.array([0.0, 0.0, HALF_PI], dtype=float)
FEMUR_ORIGIN_RPY = np.array([HALF_PI, HALF_PI, 0.0], dtype=float)
TIBIA_ORIGIN_RPY = np.array([0.0, 0.0, 0.0], dtype=float)

# Local joint axes after the rail semantic cleanup.
JOINT_AXIS_LOCAL = {
    "rail": np.array([1.0, 0.0, 0.0], dtype=float),
    "coxa": np.array([-1.0, 0.0, 0.0], dtype=float),
    "femur": np.array([-1.0, 0.0, 0.0], dtype=float),
    "tibia": np.array([-1.0, 0.0, 0.0], dtype=float),
}

# Per-leg prismatic limits after flipping the rail semantic to "+q = +X".
RAIL_LIMITS_BY_LEG = {
    "lf": (0.0, 0.111),
    "lh": (-0.111, 0.0),
    "rh": (0.0, 0.111),
    "rf": (-0.111, 0.0),
}

# Human-readable contract for code review / logging / future regression checks.
JOINT_SEMANTICS = {
    "rail": "+q translates along base_link +X (semantic chassis-forward axis)",
    "coxa": "+q follows the shared coxa local axis; effective family axis is consistent across legs",
    "femur": "+q follows the shared femur local axis; effective family axis is consistent across legs",
    "tibia": "+q follows the shared tibia local axis; effective family axis is consistent across legs",
}
