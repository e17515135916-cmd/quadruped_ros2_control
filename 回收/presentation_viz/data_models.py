"""
Data models for the Presentation Visualization System.

This module defines the core data structures used throughout the system,
including URDF models, time series data, and workspace data.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional
import numpy as np


@dataclass
class Joint:
    """
    Represents a joint in a URDF model.
    
    Attributes:
        name: Unique identifier for the joint
        type: Joint type (revolute, prismatic, fixed, continuous, etc.)
        parent: Name of the parent link
        child: Name of the child link
        origin: 6D pose [x, y, z, roll, pitch, yaw] relative to parent
        axis: 3D axis of rotation/translation [x, y, z]
        limits: Joint limits as (lower, upper) tuple
    """
    name: str
    type: str
    parent: str
    child: str
    origin: np.ndarray = field(default_factory=lambda: np.zeros(6))
    axis: np.ndarray = field(default_factory=lambda: np.array([1.0, 0.0, 0.0]))
    limits: Tuple[float, float] = (-np.pi, np.pi)
    
    def __post_init__(self):
        """Validate and convert fields after initialization."""
        # Ensure origin is a numpy array
        if not isinstance(self.origin, np.ndarray):
            self.origin = np.array(self.origin, dtype=np.float64)
        
        # Ensure axis is a numpy array
        if not isinstance(self.axis, np.ndarray):
            self.axis = np.array(self.axis, dtype=np.float64)
        
        # Validate joint type
        valid_types = ['revolute', 'prismatic', 'fixed', 'continuous', 'floating', 'planar']
        if self.type not in valid_types:
            raise ValueError(f"Invalid joint type '{self.type}'. Must be one of {valid_types}")
        
        # Validate origin shape
        if self.origin.shape != (6,):
            raise ValueError(f"Origin must be a 6-element array, got shape {self.origin.shape}")
        
        # Validate axis shape
        if self.axis.shape != (3,):
            raise ValueError(f"Axis must be a 3-element array, got shape {self.axis.shape}")
        
        # Validate limits
        if self.limits[0] > self.limits[1]:
            raise ValueError(f"Lower limit {self.limits[0]} must be <= upper limit {self.limits[1]}")


@dataclass
class Link:
    """
    Represents a link in a URDF model.
    
    Attributes:
        name: Unique identifier for the link
        visual_mesh: Path to the visual mesh file (optional)
        collision_mesh: Path to the collision mesh file (optional)
        inertial: Dictionary containing inertial properties (mass, inertia matrix, center of mass)
    """
    name: str
    visual_mesh: Optional[str] = None
    collision_mesh: Optional[str] = None
    inertial: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate fields after initialization."""
        # Ensure inertial is a dictionary
        if not isinstance(self.inertial, dict):
            raise ValueError("Inertial must be a dictionary")
        
        # Validate inertial properties if present
        if self.inertial:
            if 'mass' in self.inertial:
                mass = self.inertial['mass']
                if not isinstance(mass, (int, float)) or mass < 0:
                    raise ValueError(f"Mass must be a non-negative number, got {mass}")


@dataclass
class URDFModel:
    """
    Container for a complete URDF robot model.
    
    Attributes:
        joints: Dictionary mapping joint names to Joint objects
        links: Dictionary mapping link names to Link objects
        joint_tree: Dictionary mapping parent link names to lists of child joint names
    """
    joints: Dict[str, Joint] = field(default_factory=dict)
    links: Dict[str, Link] = field(default_factory=dict)
    joint_tree: Dict[str, List[str]] = field(default_factory=dict)
    
    def add_joint(self, joint: Joint) -> None:
        """
        Add a joint to the model and update the joint tree.
        
        Args:
            joint: Joint object to add
        """
        if joint.name in self.joints:
            raise ValueError(f"Joint '{joint.name}' already exists in the model")
        
        self.joints[joint.name] = joint
        
        # Update joint tree
        if joint.parent not in self.joint_tree:
            self.joint_tree[joint.parent] = []
        self.joint_tree[joint.parent].append(joint.name)
    
    def add_link(self, link: Link) -> None:
        """
        Add a link to the model.
        
        Args:
            link: Link object to add
        """
        if link.name in self.links:
            raise ValueError(f"Link '{link.name}' already exists in the model")
        
        self.links[link.name] = link
    
    def get_joint(self, name: str) -> Optional[Joint]:
        """
        Get a joint by name.
        
        Args:
            name: Name of the joint
            
        Returns:
            Joint object or None if not found
        """
        return self.joints.get(name)
    
    def get_link(self, name: str) -> Optional[Link]:
        """
        Get a link by name.
        
        Args:
            name: Name of the link
            
        Returns:
            Link object or None if not found
        """
        return self.links.get(name)
    
    def get_children_joints(self, parent_link: str) -> List[str]:
        """
        Get all child joints of a given parent link.
        
        Args:
            parent_link: Name of the parent link
            
        Returns:
            List of child joint names
        """
        return self.joint_tree.get(parent_link, [])
    
    def get_root_link(self) -> Optional[str]:
        """
        Find the root link of the robot (link with no parent joints).
        
        Returns:
            Name of the root link or None if not found
        """
        # Find all child links
        child_links = set()
        for joint in self.joints.values():
            child_links.add(joint.child)
        
        # Root link is one that appears in links but not as a child
        for link_name in self.links.keys():
            if link_name not in child_links:
                return link_name
        
        return None
    
    def validate(self) -> bool:
        """
        Validate the URDF model for consistency.
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        # Check that all parent and child links referenced in joints exist
        for joint in self.joints.values():
            if joint.parent not in self.links:
                raise ValueError(f"Joint '{joint.name}' references non-existent parent link '{joint.parent}'")
            if joint.child not in self.links:
                raise ValueError(f"Joint '{joint.name}' references non-existent child link '{joint.child}'")
        
        # Check for cycles in the joint tree
        visited = set()
        
        def has_cycle(link_name: str, path: set) -> bool:
            if link_name in path:
                return True
            if link_name in visited:
                return False
            
            visited.add(link_name)
            path.add(link_name)
            
            for joint_name in self.get_children_joints(link_name):
                joint = self.joints[joint_name]
                if has_cycle(joint.child, path):
                    return True
            
            path.remove(link_name)
            return False
        
        root = self.get_root_link()
        if root and has_cycle(root, set()):
            raise ValueError("URDF model contains cycles in the joint tree")
        
        return True
    
    def __len__(self) -> int:
        """Return the number of joints in the model."""
        return len(self.joints)
    
    def __repr__(self) -> str:
        """Return a string representation of the model."""
        return (f"URDFModel(joints={len(self.joints)}, "
                f"links={len(self.links)}, "
                f"root={self.get_root_link()})")


@dataclass
class TimeSeriesData:
    """
    Container for time-series data collected from ROS topics.
    
    Attributes:
        timestamps: Array of timestamps
        variables: Dictionary mapping variable names to data arrays
        metadata: Additional metadata about the data
    """
    timestamps: np.ndarray = field(default_factory=lambda: np.array([]))
    variables: Dict[str, np.ndarray] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate fields after initialization."""
        # Ensure timestamps is a numpy array
        if not isinstance(self.timestamps, np.ndarray):
            self.timestamps = np.array(self.timestamps, dtype=np.float64)
        
        # Validate that all variables have the same length as timestamps
        if len(self.timestamps) > 0:
            for name, data in self.variables.items():
                if not isinstance(data, np.ndarray):
                    self.variables[name] = np.array(data, dtype=np.float64)
                if len(data) != len(self.timestamps):
                    raise ValueError(
                        f"Variable '{name}' has length {len(data)} "
                        f"but timestamps has length {len(self.timestamps)}"
                    )
    
    def get_variable(self, name: str) -> np.ndarray:
        """
        Get data for a specific variable.
        
        Args:
            name: Name of the variable
            
        Returns:
            Data array for the variable
            
        Raises:
            KeyError: If variable does not exist
        """
        if name not in self.variables:
            raise KeyError(f"Variable '{name}' not found in time series data")
        return self.variables[name]
    
    def get_time_range(self, start: float, end: float) -> 'TimeSeriesData':
        """
        Extract data within a specific time range.
        
        Args:
            start: Start time
            end: End time
            
        Returns:
            New TimeSeriesData object with filtered data
        """
        mask = (self.timestamps >= start) & (self.timestamps <= end)
        filtered_timestamps = self.timestamps[mask]
        filtered_variables = {
            name: data[mask] for name, data in self.variables.items()
        }
        return TimeSeriesData(
            timestamps=filtered_timestamps,
            variables=filtered_variables,
            metadata=self.metadata.copy()
        )
    
    def resample(self, frequency: float) -> 'TimeSeriesData':
        """
        Resample the time series data to a new frequency.
        
        Args:
            frequency: Target frequency in Hz
            
        Returns:
            New TimeSeriesData object with resampled data
        """
        if len(self.timestamps) == 0:
            return TimeSeriesData(metadata=self.metadata.copy())
        
        # Create new time array
        start_time = self.timestamps[0]
        end_time = self.timestamps[-1]
        dt = 1.0 / frequency
        new_timestamps = np.arange(start_time, end_time, dt)
        
        # Interpolate each variable
        new_variables = {}
        for name, data in self.variables.items():
            new_variables[name] = np.interp(new_timestamps, self.timestamps, data)
        
        return TimeSeriesData(
            timestamps=new_timestamps,
            variables=new_variables,
            metadata=self.metadata.copy()
        )


@dataclass
class WorkspaceData:
    """
    Container for workspace analysis data.
    
    Attributes:
        points: Nx3 array of reachable workspace points
        boundary: Mx3 array of boundary points (convex hull)
        volume: Workspace volume in cubic meters
        rail_position: Rail extension position in meters
    """
    points: np.ndarray = field(default_factory=lambda: np.array([]).reshape(0, 3))
    boundary: np.ndarray = field(default_factory=lambda: np.array([]).reshape(0, 3))
    volume: float = 0.0
    rail_position: float = 0.0
    
    def __post_init__(self):
        """Validate fields after initialization."""
        # Ensure points is a numpy array with correct shape
        if not isinstance(self.points, np.ndarray):
            self.points = np.array(self.points, dtype=np.float64)
        
        if self.points.size > 0 and self.points.ndim != 2:
            raise ValueError(f"Points must be a 2D array, got shape {self.points.shape}")
        
        if self.points.size > 0 and self.points.shape[1] != 3:
            raise ValueError(f"Points must have 3 columns (x, y, z), got {self.points.shape[1]}")
        
        # Ensure boundary is a numpy array with correct shape
        if not isinstance(self.boundary, np.ndarray):
            self.boundary = np.array(self.boundary, dtype=np.float64)
        
        if self.boundary.size > 0 and self.boundary.ndim != 2:
            raise ValueError(f"Boundary must be a 2D array, got shape {self.boundary.shape}")
        
        if self.boundary.size > 0 and self.boundary.shape[1] != 3:
            raise ValueError(f"Boundary must have 3 columns (x, y, z), got {self.boundary.shape[1]}")
        
        # Validate volume
        if self.volume < 0:
            raise ValueError(f"Volume must be non-negative, got {self.volume}")
    
    def project_to_plane(self, plane: str) -> np.ndarray:
        """
        Project workspace points to a 2D plane.
        
        Args:
            plane: Plane to project to ('xy', 'xz', or 'yz')
            
        Returns:
            Nx2 array of projected points
        """
        if plane not in ['xy', 'xz', 'yz']:
            raise ValueError(f"Invalid plane '{plane}'. Must be 'xy', 'xz', or 'yz'")
        
        if self.points.size == 0:
            return np.array([]).reshape(0, 2)
        
        if plane == 'xy':
            return self.points[:, [0, 1]]
        elif plane == 'xz':
            return self.points[:, [0, 2]]
        else:  # yz
            return self.points[:, [1, 2]]
