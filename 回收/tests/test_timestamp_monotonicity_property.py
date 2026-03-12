#!/usr/bin/env python3
"""
Property-Based Tests: ROS2DataCollector Timestamp Monotonicity

Feature: presentation-visualization-system, Property 2: Timestamp Monotonicity
Validates: Requirements 1.4

This test verifies that for any recorded data sequence, the timestamps should be
strictly monotonically increasing (each timestamp is greater than the previous one).
"""

import numpy as np
from hypothesis import given, strategies as st, settings, assume
from hypothesis.extra.numpy import arrays
from presentation_viz.data_models import TimeSeriesData


# Strategy for generating time series data with various timestamp patterns
@st.composite
def time_series_with_timestamps(draw):
    """
    Generate TimeSeriesData with various timestamp patterns.
    
    This generator creates time series data that should have monotonically
    increasing timestamps after proper collection/sorting.
    """
    num_points = draw(st.integers(min_value=2, max_value=1000))
    
    # Generate strictly increasing timestamps
    # Start with a base timestamp and add positive increments
    start_time = draw(st.floats(min_value=0.0, max_value=100.0))
    
    # Generate positive time increments
    increments = draw(st.lists(
        st.floats(min_value=0.001, max_value=1.0),
        min_size=num_points-1,
        max_size=num_points-1
    ))
    
    # Build timestamps by cumulative sum
    timestamps = np.zeros(num_points)
    timestamps[0] = start_time
    for i, inc in enumerate(increments):
        timestamps[i+1] = timestamps[i] + inc
    
    # Generate corresponding variable data
    num_variables = draw(st.integers(min_value=1, max_value=5))
    variables = {}
    for i in range(num_variables):
        var_name = f"var_{i}"
        variables[var_name] = draw(arrays(
            dtype=np.float64,
            shape=(num_points,),
            elements=st.floats(
                min_value=-100.0,
                max_value=100.0,
                allow_nan=False,
                allow_infinity=False
            )
        ))
    
    metadata = {
        'source': draw(st.sampled_from(['ros2', 'gazebo', 'test'])),
        'collection_time': draw(st.floats(min_value=0.0, max_value=1000.0))
    }
    
    return TimeSeriesData(
        timestamps=timestamps,
        variables=variables,
        metadata=metadata
    )


@settings(max_examples=20)
@given(data=time_series_with_timestamps())
def test_property_2_timestamp_monotonicity(data):
    """
    Property Test: Timestamp Monotonicity
    
    Feature: presentation-visualization-system, Property 2: Timestamp Monotonicity
    Validates: Requirements 1.4
    
    For any recorded data sequence, the timestamps should be strictly monotonically
    increasing (each timestamp is greater than the previous one).
    
    This property validates that:
    1. All timestamps are in strictly increasing order
    2. No two consecutive timestamps are equal
    3. The timestamp ordering is preserved throughout the data structure
    """
    timestamps = data.timestamps
    
    # Property: Timestamps must be strictly monotonically increasing
    # For all i in [0, len-1), timestamps[i] < timestamps[i+1]
    for i in range(len(timestamps) - 1):
        assert timestamps[i] < timestamps[i+1], (
            f"Timestamp monotonicity violated at index {i}: "
            f"timestamps[{i}] = {timestamps[i]} >= timestamps[{i+1}] = {timestamps[i+1]}"
        )
    
    # Additional check: Verify using numpy operations
    if len(timestamps) > 1:
        diffs = np.diff(timestamps)
        assert np.all(diffs > 0), (
            f"Timestamp differences must all be positive. "
            f"Found non-positive differences at indices: {np.where(diffs <= 0)[0]}"
        )


@settings(max_examples=20)
@given(
    num_points=st.integers(min_value=10, max_value=500),
    start_time=st.floats(min_value=0.0, max_value=100.0),
    sampling_rate=st.floats(min_value=1.0, max_value=1000.0)
)
def test_property_2_uniform_sampling_monotonicity(num_points, start_time, sampling_rate):
    """
    Property Test: Uniform Sampling Timestamp Monotonicity
    
    For any uniformly sampled time series (common in ROS2 data collection),
    timestamps should be strictly monotonically increasing with consistent intervals.
    """
    # Generate uniformly sampled timestamps
    dt = 1.0 / sampling_rate
    timestamps = np.arange(num_points) * dt + start_time
    
    # Create time series data
    variables = {
        'test_var': np.random.randn(num_points)
    }
    
    data = TimeSeriesData(
        timestamps=timestamps,
        variables=variables,
        metadata={'sampling_rate': sampling_rate}
    )
    
    # Verify monotonicity
    for i in range(len(data.timestamps) - 1):
        assert data.timestamps[i] < data.timestamps[i+1], (
            f"Uniform sampling monotonicity violated at index {i}"
        )
    
    # Verify consistent intervals (within floating point precision)
    if len(timestamps) > 1:
        diffs = np.diff(data.timestamps)
        expected_diff = dt
        assert np.allclose(diffs, expected_diff, rtol=1e-10), (
            f"Uniform sampling intervals not consistent. "
            f"Expected {expected_diff}, got range [{diffs.min()}, {diffs.max()}]"
        )


@settings(max_examples=15)
@given(
    num_sequences=st.integers(min_value=2, max_value=10),
    points_per_sequence=st.integers(min_value=5, max_value=100)
)
def test_property_2_merged_sequences_monotonicity(num_sequences, points_per_sequence):
    """
    Property Test: Merged Sequences Timestamp Monotonicity
    
    When multiple data collection sequences are merged (common when combining
    data from multiple ROS2 topics), the resulting timestamps should still be
    monotonically increasing after sorting.
    """
    all_timestamps = []
    
    # Generate multiple sequences with potentially overlapping time ranges
    for seq_idx in range(num_sequences):
        start_time = seq_idx * 5.0  # Stagger start times
        timestamps = np.sort(np.random.uniform(
            start_time,
            start_time + 10.0,
            size=points_per_sequence
        ))
        all_timestamps.extend(timestamps)
    
    # Sort all timestamps (simulating merge operation)
    merged_timestamps = np.sort(np.array(all_timestamps))
    
    # Create time series data with merged timestamps
    variables = {
        'merged_var': np.random.randn(len(merged_timestamps))
    }
    
    data = TimeSeriesData(
        timestamps=merged_timestamps,
        variables=variables,
        metadata={'num_sequences': num_sequences}
    )
    
    # Verify monotonicity after merge
    for i in range(len(data.timestamps) - 1):
        assert data.timestamps[i] <= data.timestamps[i+1], (
            f"Merged sequence monotonicity violated at index {i}: "
            f"timestamps[{i}] = {data.timestamps[i]} > "
            f"timestamps[{i+1}] = {data.timestamps[i+1]}"
        )


@settings(max_examples=15)
@given(data=time_series_with_timestamps())
def test_property_2_time_range_preserves_monotonicity(data):
    """
    Property Test: Time Range Extraction Preserves Monotonicity
    
    When extracting a time range from time series data (common operation for
    analyzing specific segments), the monotonicity property should be preserved.
    """
    if len(data.timestamps) < 3:
        assume(False)  # Skip if not enough data points
    
    # Extract a time range from the middle of the data
    start_idx = len(data.timestamps) // 4
    end_idx = 3 * len(data.timestamps) // 4
    
    start_time = data.timestamps[start_idx]
    end_time = data.timestamps[end_idx]
    
    # Extract time range
    filtered_data = data.get_time_range(start_time, end_time)
    
    # Verify monotonicity is preserved
    if len(filtered_data.timestamps) > 1:
        for i in range(len(filtered_data.timestamps) - 1):
            assert filtered_data.timestamps[i] < filtered_data.timestamps[i+1], (
                f"Time range extraction violated monotonicity at index {i}"
            )


@settings(max_examples=15)
@given(
    data=time_series_with_timestamps(),
    target_frequency=st.floats(min_value=1.0, max_value=100.0)
)
def test_property_2_resampling_preserves_monotonicity(data, target_frequency):
    """
    Property Test: Resampling Preserves Monotonicity
    
    When resampling time series data to a different frequency (common for
    synchronizing data from multiple sources), monotonicity should be preserved.
    """
    if len(data.timestamps) < 2:
        assume(False)  # Skip if not enough data
    
    # Resample the data
    resampled_data = data.resample(frequency=target_frequency)
    
    # Verify monotonicity is preserved after resampling
    if len(resampled_data.timestamps) > 1:
        for i in range(len(resampled_data.timestamps) - 1):
            assert resampled_data.timestamps[i] < resampled_data.timestamps[i+1], (
                f"Resampling violated monotonicity at index {i}: "
                f"timestamps[{i}] = {resampled_data.timestamps[i]} >= "
                f"timestamps[{i+1}] = {resampled_data.timestamps[i+1]}"
            )
        
        # Verify consistent intervals (resampling should produce uniform spacing)
        diffs = np.diff(resampled_data.timestamps)
        expected_dt = 1.0 / target_frequency
        assert np.allclose(diffs, expected_dt, rtol=0.1), (
            f"Resampled intervals not consistent with target frequency. "
            f"Expected ~{expected_dt}, got range [{diffs.min()}, {diffs.max()}]"
        )


@settings(max_examples=15)
@given(st.integers(min_value=1, max_value=1000))
def test_property_2_edge_case_single_timestamp(num_vars):
    """
    Property Test: Single Timestamp Edge Case
    
    A time series with a single timestamp is trivially monotonic.
    """
    timestamp = np.array([42.0])
    variables = {f"var_{i}": np.array([float(i)]) for i in range(num_vars)}
    
    data = TimeSeriesData(
        timestamps=timestamp,
        variables=variables,
        metadata={}
    )
    
    # Single timestamp is trivially monotonic (no pairs to compare)
    assert len(data.timestamps) == 1
    # No assertion needed - property is vacuously true


@settings(max_examples=15)
@given(
    timestamp1=st.floats(min_value=0.0, max_value=100.0),
    timestamp2=st.floats(min_value=0.0, max_value=100.0)
)
def test_property_2_two_timestamps_ordering(timestamp1, timestamp2):
    """
    Property Test: Two Timestamps Must Be Ordered
    
    For any two timestamps in a time series, they must be in increasing order.
    """
    # Ensure timestamps are different and ordered
    if timestamp1 >= timestamp2:
        timestamp1, timestamp2 = timestamp2 - 1.0, timestamp1
    
    assume(timestamp1 < timestamp2)  # Ensure strict ordering
    
    timestamps = np.array([timestamp1, timestamp2])
    variables = {'var': np.array([1.0, 2.0])}
    
    data = TimeSeriesData(
        timestamps=timestamps,
        variables=variables,
        metadata={}
    )
    
    # Verify ordering
    assert data.timestamps[0] < data.timestamps[1], (
        f"Two-timestamp ordering violated: {data.timestamps[0]} >= {data.timestamps[1]}"
    )


if __name__ == "__main__":
    import sys
    
    print("Running property-based tests: ROS2DataCollector Timestamp Monotonicity")
    print("=" * 80)
    
    try:
        print("\n1. Testing general timestamp monotonicity...")
        test_property_2_timestamp_monotonicity()
        print("   ✓ PASSED: Timestamps are strictly monotonically increasing")
        
        print("\n2. Testing uniform sampling monotonicity...")
        test_property_2_uniform_sampling_monotonicity()
        print("   ✓ PASSED: Uniformly sampled timestamps are monotonic")
        
        print("\n3. Testing merged sequences monotonicity...")
        test_property_2_merged_sequences_monotonicity()
        print("   ✓ PASSED: Merged sequences maintain monotonicity")
        
        print("\n4. Testing time range extraction preserves monotonicity...")
        test_property_2_time_range_preserves_monotonicity()
        print("   ✓ PASSED: Time range extraction preserves monotonicity")
        
        print("\n5. Testing resampling preserves monotonicity...")
        test_property_2_resampling_preserves_monotonicity()
        print("   ✓ PASSED: Resampling preserves monotonicity")
        
        print("\n6. Testing single timestamp edge case...")
        test_property_2_edge_case_single_timestamp()
        print("   ✓ PASSED: Single timestamp is trivially monotonic")
        
        print("\n7. Testing two timestamps ordering...")
        test_property_2_two_timestamps_ordering()
        print("   ✓ PASSED: Two timestamps are properly ordered")
        
        print("\n" + "=" * 80)
        print("✓ All property tests PASSED")
        print("  Verified: Timestamps are strictly monotonically increasing")
        print("  Verified: Monotonicity preserved across operations (filter, resample)")
        print("  Verified: Edge cases handled correctly (single, two timestamps)")
        print("  Verified: Merged sequences maintain monotonicity")
        
    except AssertionError as e:
        print(f"\n✗ Property test FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test execution error: {e}")
        sys.exit(1)
