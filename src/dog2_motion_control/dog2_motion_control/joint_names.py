"""dog2 关节命名与拓扑语义映射。

URDF 的关节字符串必须稳定（ros2_control / Gazebo / 控制器配置依赖它）。
控制算法内部则统一使用拓扑语义：`rail / hip_roll / hip_pitch / knee_pitch`，
避免出现外包式 `joint1/joint2` 模糊命名。
"""

from __future__ import annotations

from typing import Dict, List, Literal

LegId = Literal["lf", "lh", "rh", "rf"]
LegIndex = Literal[1, 2, 3, 4]

# 腿编号到 URDF 前缀的映射（与 URDF 拓扑一致）
LEG_PREFIX_MAP: Dict[int, LegId] = {1: "lf", 2: "lh", 3: "rh", 4: "rf"}
PREFIX_TO_LEG_MAP: Dict[LegId, int] = {"lf": 1, "lh": 2, "rh": 3, "rf": 4}

# 代码内部统一的拓扑语义关节角色
JointRole = Literal["rail", "hip_roll", "hip_pitch", "knee_pitch"]
JOINT_ROLES: List[JointRole] = ["rail", "hip_roll", "hip_pitch", "knee_pitch"]

# URDF 实际使用的旋转关节类型（历史命名：coxa/femur/tibia）
UrdfRevoluteJointType = Literal["coxa", "femur", "tibia"]
REVOLUTE_JOINT_TYPES: List[UrdfRevoluteJointType] = ["coxa", "femur", "tibia"]

# 拓扑语义 -> URDF 关节类型映射（保持 URDF 字符串不变）
ROLE_TO_URDF_REVOLUTE: Dict[JointRole, UrdfRevoluteJointType] = {
    "hip_roll": "coxa",
    "hip_pitch": "femur",
    "knee_pitch": "tibia",
    # "rail" 为 prismatic，不走该表
}


def leg_prefix(leg_num: int) -> LegId:
    if leg_num not in LEG_PREFIX_MAP:
        raise ValueError(f"Invalid leg number: {leg_num}. Must be 1-4.")
    return LEG_PREFIX_MAP[leg_num]


def get_rail_joint_name(leg_num: int) -> str:
    return f"{leg_prefix(leg_num)}_rail_joint"


def get_urdf_revolute_joint_name(leg_num: int, joint_type: UrdfRevoluteJointType) -> str:
    if joint_type not in REVOLUTE_JOINT_TYPES:
        raise ValueError(f"Invalid revolute joint type: {joint_type}.")
    return f"{leg_prefix(leg_num)}_{joint_type}_joint"


def get_joint_name(leg_num: int, role: JointRole) -> str:
    """按拓扑语义获取 URDF 关节字符串。"""
    if role == "rail":
        return get_rail_joint_name(leg_num)
    return get_urdf_revolute_joint_name(leg_num, ROLE_TO_URDF_REVOLUTE[role])


def get_all_joint_names() -> List[str]:
    """按 ros2_control 常见排序输出 16 通道关节名（每腿 rail + 3R）。"""
    names: List[str] = []
    for leg_num in (1, 2, 3, 4):
        for role in JOINT_ROLES:
            names.append(get_joint_name(leg_num, role))
    return names


def get_leg_joint_names(leg_num: int) -> Dict[JointRole, str]:
    """获取单腿 4 个关节的 URDF 名称（以拓扑语义为键）。"""
    return {role: get_joint_name(leg_num, role) for role in JOINT_ROLES}


ALL_JOINT_NAMES: List[str] = get_all_joint_names()
