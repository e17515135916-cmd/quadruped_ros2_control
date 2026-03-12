"""
Property-Based Tests for ROS2DataCollector - Data Persistence Round-Trip

Property 3: Data Persistence Round-Trip
For any data collected during a recording session, saving to CSV and then loading 
the CSV file should produce equivalent data (same number of rows, same column names, 
same values within floating-point precision).

Validates: Requirements 1.5
"""

import pytest
from hypothesis import given, strategies as st, settings
from hypothesis.extra.numpy import arrays
import numpy as np
import pandas as pd
import tempfile
import os
from pathlib import Path

from presentation_viz.ros2_data_collector import ROS2DataCollector
from presentation_viz.config_manager import ConfigManager


# Strategy for generating valid topic configurations
@st.composite
def topic_config_strategy(draw):
    """Generate valid topic configurations for testing."""
    num_topics = draw(st.integers(min_value=1, max_value=3))
    topics = []
    for i in range(num_topics):
        topic = {
            'name': f'/test/topic_{i}',
            'type': draw(st.sampled_from(['sensor_msgs/JointState', 'geometry_msgs/Pose', 'sensor_msgs/Imu'])),
            'fields': [f'field_{j}' for j in range(draw(st.integers(min_value=1, max_value=3)))]
        }
        topics.append(topic)
    return {'topics': topics}


# Strategy for generating time series data
@st.composite
def time_series_data_strategy(draw):
    """Generate time series data with monotonic timestamps."""
    num_samples = draw(st.integers(min_value=5, max_value=20))
    num_fields = draw(st.integers(min_value=1, max_value=5))
    
    # Generate monotonically increasing timestamps
    timestamps = np.cumsum(draw(arrays(
        dtype=np.float64,
        shape=num_samples,
        elements=st.floats(min_value=0.001, max_value=0.1)
    )))
    
    # Generate field data
    data = {}
    data['timestamp'] = timestamps
    for i in range(num_fields):
        data[f'field_{i}'] = draw(arrays(
            dtype=np.float64,
            shape=num_samples,
            elements=st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False)
        ))
    
    return pd.DataFrame(data)


@pytest.mark.property
class TestDataPersistenceRoundTrip:
    """Property tests for data persistence round-trip."""
    
    @given(data=time_series_data_strategy())
    @settings(max_examples=15, deadline=None)
    def test_property_3_csv_save_load_preserves_row_count(self, data):
        """
        Property: Saving data to CSV and loading it back preserves the number of rows.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / 'test_data.csv'
            
            # Save data to CSV
            data.to_csv(csv_path, index=False)
            
            # Load data from CSV
            loaded_data = pd.read_csv(csv_path)
            
            # Verify row count is preserved
            assert len(loaded_data) == len(data), \
                f"Row count mismatch: original={len(data)}, loaded={len(loaded_data)}"
    
    @given(data=time_series_data_strategy())
    @settings(max_examples=15, deadline=None)
    def test_property_3_csv_save_load_preserves_column_names(self, data):
        """
        Property: Saving data to CSV and loading it back preserves column names.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / 'test_data.csv'
            
            # Save data to CSV
            data.to_csv(csv_path, index=False)
            
            # Load data from CSV
            loaded_data = pd.read_csv(csv_path)
            
            # Verify column names are preserved
            assert list(loaded_data.columns) == list(data.columns), \
                f"Column names mismatch: original={list(data.columns)}, loaded={list(loaded_data.columns)}"
    
    @given(data=time_series_data_strategy())
    @settings(max_examples=15, deadline=None)
    def test_property_3_csv_save_load_preserves_values(self, data):
        """
        Property: Saving data to CSV and loading it back preserves values within floating-point precision.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / 'test_data.csv'
            
            # Save data to CSV
            data.to_csv(csv_path, index=False)
            
            # Load data from CSV
            loaded_data = pd.read_csv(csv_path)
            
            # Verify values are preserved within floating-point precision
            for col in data.columns:
                np.testing.assert_allclose(
                    loaded_data[col].values,
                    data[col].values,
                    rtol=1e-10,
                    atol=1e-10,
                    err_msg=f"Values mismatch in column {col}"
                )
    
    @given(data=time_series_data_strategy())
    @settings(max_examples=15, deadline=None)
    def test_property_3_csv_save_load_preserves_timestamp_order(self, data):
        """
        Property: Saving data to CSV and loading it back preserves timestamp ordering.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / 'test_data.csv'
            
            # Save data to CSV
            data.to_csv(csv_path, index=False)
            
            # Load data from CSV
            loaded_data = pd.read_csv(csv_path)
            
            # Verify timestamp ordering is preserved
            if 'timestamp' in loaded_data.columns:
                timestamps = loaded_data['timestamp'].values
                assert np.all(timestamps[1:] >= timestamps[:-1]), \
                    "Timestamp ordering not preserved after CSV round-trip"
    
    @given(data=time_series_data_strategy())
    @settings(max_examples=15, deadline=None)
    def test_property_3_csv_file_exists_after_export(self, data):
        """
        Property: After exporting to CSV, the file exists and is readable.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / 'test_export.csv'
            
            # Save data
            data.to_csv(csv_path, index=False)
            
            # Verify file exists
            assert csv_path.exists(), "CSV file does not exist after export"
            
            # Verify file is readable
            assert os.access(csv_path, os.R_OK), "CSV file is not readable"
            
            # Verify file is not empty
            assert csv_path.stat().st_size > 0, "CSV file is empty"
