#!/usr/bin/env python3
"""PyBullet contact filtering helpers.

For staged foot-based locomotion tests, the terrain contact should be carried
by configured foot links only.  This prevents thigh/shin/knee collision meshes
from becoming accidental support contacts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping


def configured_foot_links(robot_config: Mapping[str, Any]) -> List[str]:
    foot_links = []
    for leg_name in ("FL", "FR", "RL", "RR"):
        foot_link = str(((robot_config.get("legs") or {}).get(leg_name, {}) or {}).get("foot_link", "") or "")
        if foot_link:
            foot_links.append(foot_link)
    return foot_links


def enable_foot_only_ground_contact(
    pybullet_client: Any,
    body_id: int,
    ground_id: int,
    link_name_to_index: Mapping[str, int],
    robot_config: Mapping[str, Any],
    keep_base_collision: bool = False,
) -> None:
    """Disable robot-ground contacts except configured foot links.

    This only filters the robot against the terrain object.  Self-collisions and
    non-ground contacts are left untouched.
    """
    allowed_link_indices = {
        link_name_to_index[link_name]
        for link_name in configured_foot_links(robot_config)
        if link_name in link_name_to_index
    }
    if keep_base_collision:
        allowed_link_indices.add(-1)

    pybullet_client.setCollisionFilterPair(
        body_id,
        ground_id,
        -1,
        -1,
        1 if -1 in allowed_link_indices else 0,
    )
    for link_index in range(pybullet_client.getNumJoints(body_id)):
        pybullet_client.setCollisionFilterPair(
            body_id,
            ground_id,
            link_index,
            -1,
            1 if link_index in allowed_link_indices else 0,
        )


def ground_contact_link_names(pybullet_client: Any, body_id: int, ground_id: int) -> Dict[str, int]:
    """Return a count of active contact points per robot link name."""
    counts: Dict[str, int] = {}
    for contact in pybullet_client.getContactPoints(body_id, ground_id):
        link_index = contact[3]
        if link_index == -1:
            link_name = "base"
        else:
            link_name = pybullet_client.getJointInfo(body_id, link_index)[12].decode("utf-8")
        counts[link_name] = counts.get(link_name, 0) + 1
    return counts


__all__ = ["configured_foot_links", "enable_foot_only_ground_contact", "ground_contact_link_names"]
