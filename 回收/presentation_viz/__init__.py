"""
Presentation Visualization System

A tool for automatically generating professional visualizations for robotics presentations,
including kinematic diagrams, workspace analysis, ROS graphs, state machines, keyframes, and data plots.
"""

__version__ = "0.1.0"
__author__ = "Dog2 Robotics Team"

from .config_manager import ConfigManager
from .logger import setup_logger
from .data_models import Joint, Link, URDFModel, TimeSeriesData, WorkspaceData
from .ros2_data_collector import ROS2DataCollector

__all__ = [
    "ConfigManager",
    "setup_logger",
    "Joint",
    "Link",
    "URDFModel",
    "TimeSeriesData",
    "WorkspaceData",
    "ROS2DataCollector",
]
