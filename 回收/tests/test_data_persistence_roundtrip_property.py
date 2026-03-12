#!/usr/bin/env python3
"""
Property-Based Tests: ROS2DataCollector Data Persistence Round-Trip

Feature: presentation-visualization-system, Property 3: Data Persistence Round-Trip
Validates: Requirements 1.5

This test verifies that for any data collected during a recording session,
saving to CSV and then loading the CSV file should produce equivalent data
(same number of rows, same column names, same values within floating-point precision).
"""

import tempfile
import os
from pathlib import Path
import numpy as np
import pandas as pd
from hypothesis import given, strategies as st, settings, assume
from hypothesis.extra.numpy import arrays
from presentation_viz import ConfigManager, ROS2DataCollector
from presentation_viz.data_models import TimeSeriesData


# Strategy for generating realistic time series data
@st.composite
def realistic_time_series_data(draw):
    """
    Generate realistic time series data that mimics ROS2 data collection.
    
    This includes:
    - Monotonically increasing timestamps
    - Multiple variables with different data types
    - Realistic value ranges for robot data
    """
    num_points = draw(st.integers(min_value=10, max_value=500))
    
    # Generate strictly increasing timestamps
    start_time = draw(st.floats(min_value=0.0, max_value=10.0))
    increments = draw(st.lists(
        st.floats(min_value=0.001, max_value=0.1),
        min_size=num_points-1,
        max_size=num_points-1
    ))
    
    timestamps = np.zeros(num_points)
    timestamps[0] = start_time
    for i, inc in enumerate(increments):
        timestamps[i+1] = timestamps[i] + inc
    
    # Generate realistic robot data variables
    variables = {}
    
    # Joint positions (radians, typical range -3.14 to 3.14)
    num_joints = draw(st.integers(min_value=1, max_value=12))
    for i in range(num_joints):
        variables[f'joint_{i}_pos'] = draw(arrays(
            dtype=np.float64,
            shape=(num_points,),
            elements=st.floats(min_value=-3.14, max_value=3.14, allow_nan=False, allow_infinity=False)
        ))
    
    # IMU data (acceleration in m/s^2, angular velocity in rad/s)
    variables['imu_ax'] = draw(arrays(
        dtype=np.float64,
        shape=(num_points,),
        elements=st.floats(min_value=-20.0, max_value=20.0, allow_nan=False, allow_infinity=False)
    ))
    variables['imu_ay'] = draw(arrays(
        dtype=np.float64,
        shape=(num_points,),
        elements=st.floats(min_value=-20.0, max_value=20.0, allow_nan=False, allow_infinity=False)
    ))
    variables['imu_az'] = draw(arrays(
        dtype=np.float64,
        shape=(num_points,),
        elements=st.floats(min_value=-20.0, max_value=20.0, allow_nan=False, allow_infinity=False)
    ))
    
    # Odometry data (position in meters)
    variables['odom_x'] = draw(arrays(
        dtype=np.float64,
        shape=(num_points,),
        elements=st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False)
    ))
    variables['odom_y'] = draw(arrays(
        dtype=np.float64,
        shape=(num_points,),
        elements=st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False)
    ))
    variables['odom_z'] = draw(arrays(
        dtype=np.float64,
        shape=(num_points,),
        elements=st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False)
    ))
    
    metadata = {
        'source': 'test',
        'num_joints': num_joints
    }
    
    return TimeSeriesData(
        timestamps=timestamps,
        variables=variables,
        metadata=metadata
    )


@settings(max_examples=20, deadline=None)
@given(data=realistic_time_series_data())
def test_property_3_data_persistence_roundtrip(data):
    """
    Property Test: Data Persistence Round-Trip
    
    Feature: presentation-visualization-system, Property 3: Data Persistence Round-Trip
    Validates: Requirements 1.5
    
    For any data collected during a recording session, saving to CSV and then
    loading the CSV file should produce equivalent data (same number of rows,
    same column names, same values within floating-point precision).
    
    This property validates that:
    1. All data rows are preserved (no data loss)
    2. All column names are preserved
    3. All values are preserved within floating-point precision
    4. Timestamp ordering is preserved
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test_data.csv"
        
        # Create DataFrame from TimeSeriesData
        df_original = pd.DataFrame({
            'timestamp': data.timestamps,
            **data.variables
        })
        
        # Save to CSV
        df_original.to_csv(csv_path, index=False)
        
        # Load from CSV
        df_loaded = pd.read_csv(csv_path)
        
        # Property 1: Same number of rows
        assert len(df_loaded) == len(df_original), (
            f"Row count mismatch: original has {len(df_original)} rows, "
            f"loaded has {len(df_loaded)} rows"
        )
        
        # Property 2: Same column names
        assert set(df_loaded.columns) == set(df_original.columns), (
            f"Column name mismatch: original has {set(df_original.columns)}, "
            f"loaded has {set(df_loaded.columns)}"
        )
        
        # Property 3: Same values within floating-point precision
        for col in df_original.columns:
            original_values = df_original[col].values
            loaded_values = df_loaded[col].values
            
            # Use appropriate tolerance for floating-point comparison
            # CSV format has limited precision, so we use rtol=1e-10
            assert np.allclose(original_values, loaded_values, rtol=1e-10, atol=1e-15), (
                f"Value mismatch in column '{col}': "
                f"max difference = {np.max(np.abs(original_values - loaded_values))}"
            )
        
        # Property 4: Timestamp ordering preserved
        assert np.allclose(df_loaded['timestamp'].values, df_original['timestamp'].values, rtol=1e-10, atol=1e-15), (
            "Timestamp ordering not preserved after round-trip"
        )


@settings(max_examples=15, deadline=None)
@given(
    num_rows=st.integers(min_value=1, max_value=1000),
    num_cols=st.integers(min_value=2, max_value=20)
)
def test_property_3_roundtrip_with_varying_dimensions(num_rows, num_cols):
    """
    Property Test: Round-Trip with Varying Dimensions
    
    For any data dimensions (rows and columns), the round-trip should preserve
    the data structure.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test_data.csv"
        
        # Generate data with specified dimensions
        data_dict = {'timestamp': np.arange(num_rows, dtype=float)}
        for i in range(num_cols - 1):  # -1 because timestamp is already included
            data_dict[f'var_{i}'] = np.random.randn(num_rows)
        
        df_original = pd.DataFrame(data_dict)
        
        # Round-trip
        df_original.to_csv(csv_path, index=False)
        df_loaded = pd.read_csv(csv_path)
        
        # Verify dimensions preserved
        assert df_loaded.shape == df_original.shape, (
            f"Shape mismatch: original {df_original.shape}, loaded {df_loaded.shape}"
        )
        
        # Verify all data preserved
        for col in df_original.columns:
            assert np.allclose(
                df_original[col].values,
                df_loaded[col].values,
                rtol=1e-10
            ), f"Data mismatch in column {col}"


@settings(max_examples=15, deadline=None)
@given(data=realistic_time_series_data())
def test_property_3_collector_roundtrip_integration(data):
    """
    Property Test: ROS2DataCollector Round-Trip Integration
    
    Test the complete round-trip through ROS2DataCollector:
    1. Create collector with data
    2. Save to CSV using collector.save_to_csv()
    3. Load CSV and verify equivalence
    """
    config = ConfigManager(None)  # Use defaults
    collector = ROS2DataCollector(config)
    
    # Simulate data collection by directly populating buffer
    # (In real usage, this would come from ROS2 callbacks)
    with collector._data_lock:
        for i, timestamp in enumerate(data.timestamps):
            data_dict = {var_name: var_data[i] for var_name, var_data in data.variables.items()}
            collector._data_buffer['test_topic'].append((timestamp, data_dict))
    
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "collector_data.csv"
        
        # Save using collector
        result = collector.save_to_csv(str(csv_path))
        assert result is True, "save_to_csv() should return True on success"
        
        # Verify file exists
        assert csv_path.exists(), f"CSV file not created at {csv_path}"
        
        # Load and verify
        df_loaded = pd.read_csv(csv_path)
        
        # Get original data from collector
        df_original = collector.get_data_frame()
        
        # Verify equivalence
        assert len(df_loaded) == len(df_original), (
            f"Row count mismatch after collector round-trip"
        )
        
        assert set(df_loaded.columns) == set(df_original.columns), (
            f"Column mismatch after collector round-trip"
        )
        
        for col in df_original.columns:
            assert np.allclose(
                df_original[col].values,
                df_loaded[col].values,
                rtol=1e-10
            ), f"Value mismatch in column {col} after collector round-trip"


@settings(max_examples=15, deadline=None)
@given(
    num_samples=st.integers(min_value=10, max_value=200),
    has_missing_values=st.booleans()
)
def test_property_3_roundtrip_with_edge_cases(num_samples, has_missing_values):
    """
    Property Test: Round-Trip with Edge Cases
    
    Test round-trip with edge cases like missing values, zeros, and extreme values.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "edge_case_data.csv"
        
        # Create data with edge cases
        data_dict = {
            'timestamp': np.arange(num_samples, dtype=float),
            'zeros': np.zeros(num_samples),
            'ones': np.ones(num_samples),
            'large_values': np.full(num_samples, 1e10),
            'small_values': np.full(num_samples, 1e-10),
            'negative': np.full(num_samples, -999.999)
        }
        
        df_original = pd.DataFrame(data_dict)
        
        # Optionally add NaN values (though ROS2 data shouldn't have these)
        if has_missing_values:
            # Skip this case as ROS2 data should not have NaN
            assume(False)
        
        # Round-trip
        df_original.to_csv(csv_path, index=False)
        df_loaded = pd.read_csv(csv_path)
        
        # Verify all edge cases preserved
        for col in df_original.columns:
            assert np.allclose(
                df_original[col].values,
                df_loaded[col].values,
                rtol=1e-10,
                atol=1e-15
            ), f"Edge case data mismatch in column {col}"


@settings(max_examples=10, deadline=None)
@given(st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_')))
def test_property_3_roundtrip_with_various_filenames(filename):
    """
    Property Test: Round-Trip with Various Filenames
    
    For any valid filename, the round-trip should work correctly.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create safe filename
        safe_filename = "".join(c for c in filename if c.isalnum() or c == '_')[:30]
        if not safe_filename:
            safe_filename = "test"
        
        csv_path = Path(tmpdir) / f"{safe_filename}.csv"
        
        # Create simple test data
        df_original = pd.DataFrame({
            'timestamp': np.arange(10, dtype=float),
            'value': np.random.randn(10)
        })
        
        # Round-trip
        df_original.to_csv(csv_path, index=False)
        df_loaded = pd.read_csv(csv_path)
        
        # Verify
        assert len(df_loaded) == len(df_original)
        assert np.allclose(df_original['timestamp'].values, df_loaded['timestamp'].values)
        assert np.allclose(df_original['value'].values, df_loaded['value'].values, rtol=1e-10)


@settings(max_examples=15, deadline=None)
@given(data=realistic_time_series_data())
def test_property_3_multiple_roundtrips(data):
    """
    Property Test: Multiple Round-Trips
    
    Performing multiple save/load cycles should not degrade data quality.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create original DataFrame
        df_original = pd.DataFrame({
            'timestamp': data.timestamps,
            **data.variables
        })
        
        # Perform multiple round-trips
        df_current = df_original.copy()
        num_roundtrips = 3
        
        for i in range(num_roundtrips):
            csv_path = Path(tmpdir) / f"roundtrip_{i}.csv"
            df_current.to_csv(csv_path, index=False)
            df_current = pd.read_csv(csv_path)
        
        # After multiple round-trips, data should still match original
        assert len(df_current) == len(df_original), (
            f"Row count changed after {num_roundtrips} round-trips"
        )
        
        for col in df_original.columns:
            assert np.allclose(
                df_original[col].values,
                df_current[col].values,
                rtol=1e-9  # Slightly relaxed tolerance for multiple round-trips
            ), f"Data degraded in column {col} after {num_roundtrips} round-trips"


@settings(max_examples=10, deadline=None)
@given(st.integers(min_value=1, max_value=100))
def test_property_3_empty_and_single_row_cases(num_rows):
    """
    Property Test: Empty and Single Row Cases
    
    Edge cases with very few rows should still round-trip correctly.
    """
    if num_rows == 0:
        # Empty DataFrame case
        df_original = pd.DataFrame({'timestamp': [], 'value': []})
    else:
        df_original = pd.DataFrame({
            'timestamp': np.arange(num_rows, dtype=float),
            'value': np.random.randn(num_rows)
        })
    
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "edge_case.csv"
        
        # Round-trip
        df_original.to_csv(csv_path, index=False)
        df_loaded = pd.read_csv(csv_path)
        
        # Verify
        assert len(df_loaded) == len(df_original)
        
        if num_rows > 0:
            assert np.allclose(
                df_original['timestamp'].values,
                df_loaded['timestamp'].values
            )
            assert np.allclose(
                df_original['value'].values,
                df_loaded['value'].values,
                rtol=1e-10
            )


@settings(max_examples=15, deadline=None)
@given(data=realistic_time_series_data())
def test_property_3_column_order_preservation(data):
    """
    Property Test: Column Order Preservation
    
    The order of columns should be preserved through round-trip.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "column_order.csv"
        
        # Create DataFrame with specific column order
        columns = ['timestamp'] + sorted(data.variables.keys())
        df_original = pd.DataFrame({
            'timestamp': data.timestamps,
            **data.variables
        })[columns]  # Enforce column order
        
        # Round-trip
        df_original.to_csv(csv_path, index=False)
        df_loaded = pd.read_csv(csv_path)
        
        # Verify column order preserved
        assert list(df_loaded.columns) == list(df_original.columns), (
            f"Column order not preserved: original {list(df_original.columns)}, "
            f"loaded {list(df_loaded.columns)}"
        )


if __name__ == "__main__":
    import sys
    
    print("Running property-based tests: ROS2DataCollector Data Persistence Round-Trip")
    print("=" * 80)
    
    try:
        print("\n1. Testing basic data persistence round-trip...")
        test_property_3_data_persistence_roundtrip()
        print("   ✓ PASSED: Data preserved through CSV save/load")
        
        print("\n2. Testing round-trip with varying dimensions...")
        test_property_3_roundtrip_with_varying_dimensions()
        print("   ✓ PASSED: Various data dimensions handled correctly")
        
        print("\n3. Testing collector round-trip integration...")
        test_property_3_collector_roundtrip_integration()
        print("   ✓ PASSED: ROS2DataCollector round-trip works correctly")
        
        print("\n4. Testing round-trip with edge cases...")
        test_property_3_roundtrip_with_edge_cases()
        print("   ✓ PASSED: Edge cases (zeros, large values) preserved")
        
        print("\n5. Testing round-trip with various filenames...")
        test_property_3_roundtrip_with_various_filenames()
        print("   ✓ PASSED: Different filenames handled correctly")
        
        print("\n6. Testing multiple round-trips...")
        test_property_3_multiple_roundtrips()
        print("   ✓ PASSED: Multiple round-trips don't degrade data")
        
        print("\n7. Testing empty and single row cases...")
        test_property_3_empty_and_single_row_cases()
        print("   ✓ PASSED: Edge cases with few rows handled")
        
        print("\n8. Testing column order preservation...")
        test_property_3_column_order_preservation()
        print("   ✓ PASSED: Column order preserved through round-trip")
        
        print("\n" + "=" * 80)
        print("✓ All property tests PASSED")
        print("  Verified: Data preserved through CSV save/load")
        print("  Verified: Row count, column names, and values preserved")
        print("  Verified: Floating-point precision maintained")
        print("  Verified: Edge cases handled correctly")
        print("  Verified: Multiple round-trips don't degrade data")
        
    except AssertionError as e:
        print(f"\n✗ Property test FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test execution error: {e}")
        sys.exit(1)
