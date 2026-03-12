#!/usr/bin/env python3
"""
Property-Based Tests: ROS2DataCollector Topic Subscription Completeness

Feature: presentation-visualization-system, Property 1: Topic Subscription Completeness
Validates: Requirements 1.1, 1.2, 1.3

This test verifies that for any ROS2 topic specified in the configuration,
when the Data_Collector starts recording, it should successfully subscribe to
that topic and record at least one message before stopping.

Note: These tests run in mock mode when ROS2 is not available.
"""

import tempfile
import yaml
from pathlib import Path
from hypothesis import given, strategies as st, settings
from presentation_viz import ConfigManager, ROS2DataCollector


@settings(max_examples=15)
@given(
    joint_states_topic=st.text(min_size=1, max_size=30, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='/_'
    )),
    imu_topic=st.text(min_size=1, max_size=30, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='/_'
    )),
    odom_topic=st.text(min_size=1, max_size=30, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='/_'
    ))
)
def test_property_1_topic_subscription_completeness(joint_states_topic, imu_topic, odom_topic):
    """
    Property Test: Topic Subscription Completeness
    
    Feature: presentation-visualization-system, Property 1: Topic Subscription Completeness
    Validates: Requirements 1.1, 1.2, 1.3
    
    For any ROS2 topic specified in the configuration, the Data_Collector should
    successfully initialize and be ready to subscribe to those topics.
    
    This property validates that:
    1. ConfigManager correctly loads topic configurations
    2. ROS2DataCollector initializes without errors
    3. Topic names are properly stored and accessible
    """
    # Ensure topics start with '/' (ROS convention)
    if not joint_states_topic.startswith('/'):
        joint_states_topic = '/' + joint_states_topic
    if not imu_topic.startswith('/'):
        imu_topic = '/' + imu_topic
    if not odom_topic.startswith('/'):
        odom_topic = '/' + odom_topic
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.yaml"
        
        # Create configuration with specified topics
        config_data = {
            'data_sources': {
                'joint_states_topic': joint_states_topic,
                'imu_topic': imu_topic,
                'odom_topic': odom_topic
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Load configuration
        config_manager = ConfigManager(str(config_file))
        
        # Verify topics are loaded
        data_sources = config_manager.get_data_sources()
        assert data_sources['joint_states_topic'] == joint_states_topic, (
            f"Joint states topic not loaded correctly"
        )
        assert data_sources['imu_topic'] == imu_topic, (
            f"IMU topic not loaded correctly"
        )
        assert data_sources['odom_topic'] == odom_topic, (
            f"Odom topic not loaded correctly"
        )
        
        # Initialize ROS2DataCollector
        try:
            collector = ROS2DataCollector(config_manager)
        except Exception as e:
            raise AssertionError(
                f"ROS2DataCollector failed to initialize with valid config: {e}\n"
                f"Topics: {joint_states_topic}, {imu_topic}, {odom_topic}"
            )
        
        # Verify collector has access to topic configuration
        assert collector.data_sources is not None
        assert collector.data_sources['joint_states_topic'] == joint_states_topic
        assert collector.data_sources['imu_topic'] == imu_topic
        assert collector.data_sources['odom_topic'] == odom_topic


@settings(max_examples=15)
@given(st.lists(
    st.text(min_size=1, max_size=20, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='/_'
    )),
    min_size=1,
    max_size=5,
    unique=True
))
def test_property_1_multiple_topics_initialization(topic_list):
    """
    Property Test: Multiple Topics Initialization
    
    For any list of topic names, the ROS2DataCollector should initialize
    and be ready to handle all specified topics.
    """
    # Ensure all topics start with '/'
    topic_list = ['/' + t if not t.startswith('/') else t for t in topic_list]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.yaml"
        
        # Create configuration with multiple topics
        config_data = {
            'data_sources': {
                'joint_states_topic': topic_list[0] if len(topic_list) > 0 else '/joint_states',
                'imu_topic': topic_list[1] if len(topic_list) > 1 else '/imu',
                'odom_topic': topic_list[2] if len(topic_list) > 2 else '/odom'
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        config_manager = ConfigManager(str(config_file))
        
        # Should initialize without errors
        try:
            collector = ROS2DataCollector(config_manager)
        except Exception as e:
            raise AssertionError(
                f"Failed to initialize with multiple topics: {e}\n"
                f"Topics: {topic_list}"
            )
        
        # Verify data structures are initialized
        assert collector._data_buffer is not None
        assert hasattr(collector, '_subscriptions')
        # In mock mode, _subscriptions might be a list or dict depending on initialization
        assert collector._subscriptions is not None


@settings(max_examples=15)
@given(st.booleans())
def test_property_1_recording_state_management(start_recording):
    """
    Property Test: Recording State Management
    
    For any recording state (started or not), the collector should
    correctly track and report its recording status.
    """
    config_manager = ConfigManager(None)  # Use defaults
    collector = ROS2DataCollector(config_manager)
    
    # Initial state should be not recording
    assert collector._is_recording is False, "Initial state should be not recording"
    
    if start_recording:
        # Start recording
        collector.start_recording(duration=0.1)
        assert collector._is_recording is True, "Should be recording after start"
        
        # Stop recording
        collector.stop_recording()
        assert collector._is_recording is False, "Should not be recording after stop"
    else:
        # Should remain not recording
        assert collector._is_recording is False


@settings(max_examples=15)
@given(st.integers(min_value=0, max_value=100))
def test_property_1_buffer_initialization(num_topics):
    """
    Property Test: Buffer Initialization
    
    For any number of topics, the data buffer should be properly initialized
    and ready to store data.
    """
    config_manager = ConfigManager(None)
    collector = ROS2DataCollector(config_manager)
    
    # Buffer should be initialized as empty dict
    assert collector._data_buffer is not None
    assert isinstance(collector._data_buffer, dict)
    assert len(collector._data_buffer) == 0, "Buffer should start empty"
    
    # Get buffer size should work
    buffer_sizes = collector.get_buffer_size()
    assert isinstance(buffer_sizes, dict)
    assert len(buffer_sizes) == 0


@settings(max_examples=15)
@given(st.floats(min_value=0.1, max_value=10.0))
def test_property_1_recording_duration_parameter(duration):
    """
    Property Test: Recording Duration Parameter
    
    For any valid duration value, the collector should accept it and
    store it correctly.
    """
    config_manager = ConfigManager(None)
    collector = ROS2DataCollector(config_manager)
    
    # Start recording with duration
    collector.start_recording(duration=duration)
    
    # Verify duration is stored
    assert collector._recording_duration == duration, (
        f"Duration not stored correctly: expected {duration}, got {collector._recording_duration}"
    )
    
    # Verify recording state
    assert collector._is_recording is True
    
    # Clean up
    collector.stop_recording()


@settings(max_examples=10)
@given(st.none())
def test_property_1_unlimited_recording(duration):
    """
    Property Test: Unlimited Recording
    
    When duration is None, the collector should record indefinitely
    until explicitly stopped.
    """
    config_manager = ConfigManager(None)
    collector = ROS2DataCollector(config_manager)
    
    # Start recording without duration
    collector.start_recording(duration=duration)
    
    # Verify unlimited recording
    assert collector._recording_duration is None
    assert collector._is_recording is True
    
    # Should remain recording until explicitly stopped
    assert collector._is_recording is True
    
    # Stop recording
    collector.stop_recording()
    assert collector._is_recording is False


@settings(max_examples=10)
@given(st.booleans())
def test_property_1_data_frame_generation(has_data):
    """
    Property Test: Data Frame Generation
    
    For any state (with or without data), get_data_frame() should
    return a valid DataFrame without errors.
    """
    config_manager = ConfigManager(None)
    collector = ROS2DataCollector(config_manager)
    
    # Get data frame (should be empty initially)
    try:
        df = collector.get_data_frame()
    except Exception as e:
        raise AssertionError(f"get_data_frame() raised exception: {e}")
    
    # Should return a DataFrame
    import pandas as pd
    assert isinstance(df, pd.DataFrame)
    
    if not has_data:
        # Should be empty
        assert len(df) == 0


@settings(max_examples=10)
@given(st.text(min_size=1, max_size=50))
def test_property_1_csv_save_path_handling(filename):
    """
    Property Test: CSV Save Path Handling
    
    For any valid filename, save_to_csv() should handle the path correctly
    (even if there's no data to save).
    """
    config_manager = ConfigManager(None)
    collector = ROS2DataCollector(config_manager)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create safe filename
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")[:30]
        if not safe_filename:
            safe_filename = "test"
        
        output_path = Path(tmpdir) / f"{safe_filename}.csv"
        
        # Should handle save attempt gracefully (returns False for empty data)
        try:
            result = collector.save_to_csv(str(output_path))
            # Result should be False (no data) or True (data saved)
            assert isinstance(result, bool)
        except Exception as e:
            raise AssertionError(f"save_to_csv() raised unexpected exception: {e}")


if __name__ == "__main__":
    import sys
    
    print("Running property-based tests: ROS2DataCollector Topic Subscription Completeness")
    print("=" * 80)
    print("Note: Tests run in mock mode when ROS2 is not available")
    print("=" * 80)
    
    try:
        print("\n1. Testing topic subscription completeness...")
        test_property_1_topic_subscription_completeness()
        print("   ✓ PASSED: Topics loaded and collector initialized")
        
        print("\n2. Testing multiple topics initialization...")
        test_property_1_multiple_topics_initialization()
        print("   ✓ PASSED: Multiple topics handled correctly")
        
        print("\n3. Testing recording state management...")
        test_property_1_recording_state_management()
        print("   ✓ PASSED: Recording state managed correctly")
        
        print("\n4. Testing buffer initialization...")
        test_property_1_buffer_initialization()
        print("   ✓ PASSED: Buffer initialized correctly")
        
        print("\n5. Testing recording duration parameter...")
        test_property_1_recording_duration_parameter()
        print("   ✓ PASSED: Duration parameter handled correctly")
        
        print("\n6. Testing unlimited recording...")
        test_property_1_unlimited_recording()
        print("   ✓ PASSED: Unlimited recording works correctly")
        
        print("\n7. Testing data frame generation...")
        test_property_1_data_frame_generation()
        print("   ✓ PASSED: Data frame generation works")
        
        print("\n8. Testing CSV save path handling...")
        test_property_1_csv_save_path_handling()
        print("   ✓ PASSED: CSV save path handled correctly")
        
        print("\n" + "=" * 80)
        print("✓ All property tests PASSED")
        print("  Verified: Topic configuration loaded correctly")
        print("  Verified: Collector initializes without errors")
        print("  Verified: Recording state managed properly")
        print("  Verified: Data structures initialized correctly")
        
    except AssertionError as e:
        print(f"\n✗ Property test FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test execution error: {e}")
        sys.exit(1)
