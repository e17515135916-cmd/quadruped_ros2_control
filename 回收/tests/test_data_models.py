"""
Unit tests for data models.

Tests data class creation, access, and transformation methods.
"""

import pytest
import numpy as np
from presentation_viz.data_models import (
    Joint, Link, URDFModel, TimeSeriesData, WorkspaceData
)


class TestJoint:
    """Tests for Joint data class."""
    
    def test_joint_creation_with_defaults(self):
        """Test creating a joint with default values."""
        joint = Joint(
            name="test_joint",
            type="revolute",
            parent="link1",
            child="link2"
        )
        assert joint.name == "test_joint"
        assert joint.type == "revolute"
        assert joint.parent == "link1"
        assert joint.child == "link2"
        assert joint.origin.shape == (6,)
        assert joint.axis.shape == (3,)
        assert np.allclose(joint.origin, np.zeros(6))
        assert np.allclose(joint.axis, np.array([1.0, 0.0, 0.0]))
    
    def test_joint_creation_with_custom_values(self):
        """Test creating a joint with custom values."""
        origin = np.array([0.1, 0.2, 0.3, 0.0, 0.0, 1.57])
        axis = np.array([0.0, 0.0, 1.0])
        limits = (-1.57, 1.57)
        
        joint = Joint(
            name="hip_joint",
            type="revolute",
            parent="base",
            child="thigh",
            origin=origin,
            axis=axis,
            limits=limits
        )
        
        assert joint.name == "hip_joint"
        assert np.allclose(joint.origin, origin)
        assert np.allclose(joint.axis, axis)
        assert joint.limits == limits
    
    def test_joint_invalid_type(self):
        """Test that invalid joint type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid joint type"):
            Joint(
                name="bad_joint",
                type="invalid_type",
                parent="link1",
                child="link2"
            )
    
    def test_joint_invalid_origin_shape(self):
        """Test that invalid origin shape raises ValueError."""
        with pytest.raises(ValueError, match="Origin must be a 6-element array"):
            Joint(
                name="bad_joint",
                type="revolute",
                parent="link1",
                child="link2",
                origin=np.array([1, 2, 3])  # Wrong shape
            )
    
    def test_joint_invalid_limits(self):
        """Test that invalid limits raise ValueError."""
        with pytest.raises(ValueError, match="Lower limit .* must be <= upper limit"):
            Joint(
                name="bad_joint",
                type="revolute",
                parent="link1",
                child="link2",
                limits=(1.0, -1.0)  # Lower > upper
            )


class TestLink:
    """Tests for Link data class."""
    
    def test_link_creation_minimal(self):
        """Test creating a link with minimal information."""
        link = Link(name="base_link")
        assert link.name == "base_link"
        assert link.visual_mesh is None
        assert link.collision_mesh is None
        assert link.inertial == {}
    
    def test_link_creation_with_meshes(self):
        """Test creating a link with mesh paths."""
        link = Link(
            name="thigh",
            visual_mesh="meshes/thigh_visual.stl",
            collision_mesh="meshes/thigh_collision.stl"
        )
        assert link.name == "thigh"
        assert link.visual_mesh == "meshes/thigh_visual.stl"
        assert link.collision_mesh == "meshes/thigh_collision.stl"
    
    def test_link_creation_with_inertial(self):
        """Test creating a link with inertial properties."""
        inertial = {
            'mass': 1.5,
            'com': [0.0, 0.0, 0.1],
            'inertia': np.eye(3)
        }
        link = Link(
            name="thigh",
            inertial=inertial
        )
        assert link.inertial['mass'] == 1.5
        assert link.inertial['com'] == [0.0, 0.0, 0.1]
    
    def test_link_invalid_mass(self):
        """Test that negative mass raises ValueError."""
        with pytest.raises(ValueError, match="Mass must be a non-negative number"):
            Link(
                name="bad_link",
                inertial={'mass': -1.0}
            )


class TestURDFModel:
    """Tests for URDFModel container class."""
    
    def test_urdf_model_creation_empty(self):
        """Test creating an empty URDF model."""
        model = URDFModel()
        assert len(model.joints) == 0
        assert len(model.links) == 0
        assert len(model.joint_tree) == 0
        assert len(model) == 0
    
    def test_urdf_model_add_link(self):
        """Test adding links to the model."""
        model = URDFModel()
        link1 = Link(name="base_link")
        link2 = Link(name="link1")
        
        model.add_link(link1)
        model.add_link(link2)
        
        assert len(model.links) == 2
        assert "base_link" in model.links
        assert "link1" in model.links
    
    def test_urdf_model_add_duplicate_link(self):
        """Test that adding duplicate link raises ValueError."""
        model = URDFModel()
        link = Link(name="base_link")
        model.add_link(link)
        
        with pytest.raises(ValueError, match="Link .* already exists"):
            model.add_link(link)
    
    def test_urdf_model_add_joint(self):
        """Test adding joints to the model."""
        model = URDFModel()
        joint = Joint(
            name="joint1",
            type="revolute",
            parent="base_link",
            child="link1"
        )
        
        model.add_joint(joint)
        
        assert len(model.joints) == 1
        assert "joint1" in model.joints
        assert "base_link" in model.joint_tree
        assert "joint1" in model.joint_tree["base_link"]
    
    def test_urdf_model_get_children_joints(self):
        """Test getting children joints of a link."""
        model = URDFModel()
        model.add_joint(Joint("j1", "revolute", "base", "l1"))
        model.add_joint(Joint("j2", "revolute", "base", "l2"))
        model.add_joint(Joint("j3", "revolute", "l1", "l3"))
        
        base_children = model.get_children_joints("base")
        assert len(base_children) == 2
        assert "j1" in base_children
        assert "j2" in base_children
        
        l1_children = model.get_children_joints("l1")
        assert len(l1_children) == 1
        assert "j3" in l1_children
    
    def test_urdf_model_get_root_link(self):
        """Test finding the root link."""
        model = URDFModel()
        model.add_link(Link("base_link"))
        model.add_link(Link("link1"))
        model.add_link(Link("link2"))
        model.add_joint(Joint("j1", "revolute", "base_link", "link1"))
        model.add_joint(Joint("j2", "revolute", "link1", "link2"))
        
        root = model.get_root_link()
        assert root == "base_link"
    
    def test_urdf_model_validate_success(self):
        """Test validation of a valid model."""
        model = URDFModel()
        model.add_link(Link("base"))
        model.add_link(Link("l1"))
        model.add_joint(Joint("j1", "revolute", "base", "l1"))
        
        assert model.validate() is True
    
    def test_urdf_model_validate_missing_parent(self):
        """Test validation fails for missing parent link."""
        model = URDFModel()
        model.add_link(Link("l1"))
        model.add_joint(Joint("j1", "revolute", "missing_parent", "l1"))
        
        with pytest.raises(ValueError, match="non-existent parent link"):
            model.validate()
    
    def test_urdf_model_validate_missing_child(self):
        """Test validation fails for missing child link."""
        model = URDFModel()
        model.add_link(Link("base"))
        model.add_joint(Joint("j1", "revolute", "base", "missing_child"))
        
        with pytest.raises(ValueError, match="non-existent child link"):
            model.validate()


class TestTimeSeriesData:
    """Tests for TimeSeriesData class."""
    
    def test_time_series_creation_empty(self):
        """Test creating empty time series data."""
        ts = TimeSeriesData()
        assert len(ts.timestamps) == 0
        assert len(ts.variables) == 0
        assert ts.metadata == {}
    
    def test_time_series_creation_with_data(self):
        """Test creating time series with data."""
        timestamps = np.array([0.0, 0.1, 0.2, 0.3])
        variables = {
            'position': np.array([1.0, 1.1, 1.2, 1.3]),
            'velocity': np.array([0.0, 0.1, 0.1, 0.1])
        }
        metadata = {'source': 'test', 'units': 'm'}
        
        ts = TimeSeriesData(
            timestamps=timestamps,
            variables=variables,
            metadata=metadata
        )
        
        assert len(ts.timestamps) == 4
        assert 'position' in ts.variables
        assert 'velocity' in ts.variables
        assert ts.metadata['source'] == 'test'
    
    def test_time_series_mismatched_lengths(self):
        """Test that mismatched lengths raise ValueError."""
        timestamps = np.array([0.0, 0.1, 0.2])
        variables = {'position': np.array([1.0, 1.1])}  # Wrong length
        
        with pytest.raises(ValueError, match="has length .* but timestamps has length"):
            TimeSeriesData(timestamps=timestamps, variables=variables)
    
    def test_time_series_get_variable(self):
        """Test getting a variable from time series."""
        ts = TimeSeriesData(
            timestamps=np.array([0.0, 0.1]),
            variables={'pos': np.array([1.0, 2.0])}
        )
        
        pos_data = ts.get_variable('pos')
        assert np.allclose(pos_data, np.array([1.0, 2.0]))
    
    def test_time_series_get_nonexistent_variable(self):
        """Test that getting nonexistent variable raises KeyError."""
        ts = TimeSeriesData(
            timestamps=np.array([0.0, 0.1]),
            variables={'pos': np.array([1.0, 2.0])}
        )
        
        with pytest.raises(KeyError, match="Variable .* not found"):
            ts.get_variable('nonexistent')
    
    def test_time_series_get_time_range(self):
        """Test extracting a time range."""
        ts = TimeSeriesData(
            timestamps=np.array([0.0, 0.1, 0.2, 0.3, 0.4]),
            variables={'pos': np.array([1.0, 2.0, 3.0, 4.0, 5.0])}
        )
        
        filtered = ts.get_time_range(0.1, 0.3)
        
        assert len(filtered.timestamps) == 3
        assert np.allclose(filtered.timestamps, np.array([0.1, 0.2, 0.3]))
        assert np.allclose(filtered.get_variable('pos'), np.array([2.0, 3.0, 4.0]))
    
    def test_time_series_resample(self):
        """Test resampling time series data."""
        ts = TimeSeriesData(
            timestamps=np.array([0.0, 1.0, 2.0]),
            variables={'pos': np.array([0.0, 1.0, 2.0])}
        )
        
        resampled = ts.resample(frequency=2.0)  # 2 Hz = 0.5s interval
        
        # Should have timestamps at 0.0, 0.5, 1.0, 1.5
        assert len(resampled.timestamps) >= 3
        assert resampled.timestamps[0] == 0.0


class TestWorkspaceData:
    """Tests for WorkspaceData class."""
    
    def test_workspace_creation_empty(self):
        """Test creating empty workspace data."""
        ws = WorkspaceData()
        assert ws.points.shape == (0, 3)
        assert ws.boundary.shape == (0, 3)
        assert ws.volume == 0.0
        assert ws.rail_position == 0.0
    
    def test_workspace_creation_with_points(self):
        """Test creating workspace with points."""
        points = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0]
        ])
        boundary = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0]
        ])
        
        ws = WorkspaceData(
            points=points,
            boundary=boundary,
            volume=0.5,
            rail_position=0.1
        )
        
        assert ws.points.shape == (4, 3)
        assert ws.boundary.shape == (3, 3)
        assert ws.volume == 0.5
        assert ws.rail_position == 0.1
    
    def test_workspace_invalid_points_shape(self):
        """Test that invalid points shape raises ValueError."""
        with pytest.raises(ValueError, match="Points must have 3 columns"):
            WorkspaceData(points=np.array([[1, 2]]))  # Only 2 columns
    
    def test_workspace_negative_volume(self):
        """Test that negative volume raises ValueError."""
        with pytest.raises(ValueError, match="Volume must be non-negative"):
            WorkspaceData(volume=-1.0)
    
    def test_workspace_project_to_xy(self):
        """Test projecting workspace to XY plane."""
        points = np.array([
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0]
        ])
        ws = WorkspaceData(points=points)
        
        projected = ws.project_to_plane('xy')
        
        assert projected.shape == (2, 2)
        assert np.allclose(projected, np.array([[1.0, 2.0], [4.0, 5.0]]))
    
    def test_workspace_project_to_xz(self):
        """Test projecting workspace to XZ plane."""
        points = np.array([
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0]
        ])
        ws = WorkspaceData(points=points)
        
        projected = ws.project_to_plane('xz')
        
        assert projected.shape == (2, 2)
        assert np.allclose(projected, np.array([[1.0, 3.0], [4.0, 6.0]]))
    
    def test_workspace_project_to_yz(self):
        """Test projecting workspace to YZ plane."""
        points = np.array([
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0]
        ])
        ws = WorkspaceData(points=points)
        
        projected = ws.project_to_plane('yz')
        
        assert projected.shape == (2, 2)
        assert np.allclose(projected, np.array([[2.0, 3.0], [5.0, 6.0]]))
    
    def test_workspace_project_invalid_plane(self):
        """Test that invalid plane raises ValueError."""
        ws = WorkspaceData(points=np.array([[1, 2, 3]]))
        
        with pytest.raises(ValueError, match="Invalid plane"):
            ws.project_to_plane('invalid')
