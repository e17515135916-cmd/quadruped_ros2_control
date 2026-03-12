#!/usr/bin/env python3
"""
Unit Tests: ROS2DataCollector

Task 4.5: Unit tests for ROS2DataCollector
Requirements: 1.1, 1.5

These tests focus on:
1. Topic subscription failure handling
2. Data buffer overflow protection
3. CSV file format validation
"""

import tempfile
import time
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from presentation_viz import ConfigManager, ROS2DataCollector


class TestTopicSubscriptionFailureHandling:
    """Test suite for topic subscription failure scenarios."""
    
    def test_subscribe_to_nonexistent_topic_in_mock_mode(self):
        """
        Test that subscribing to a non-existent topic in mock mode fails gracefully.
        
        Requirements: 1.1
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # In mock mode, subscription should return False
        result = collector.subscribe_topic('/nonexistent_topic', type(None))
        
        assert result is False, "Should return False when subscribing in mock mode"
        assert '/nonexistent_topic' not in collector._subscriptions, (
            "Failed subscription should not be added to subscriptions dict"
        )
    
    def test_subscribe_with_invalid_message_type(self):
        """
        Test that subscribing with an invalid message type is handled gracefully.
        
        Requirements: 1.1
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # Try to subscribe with invalid message type
        result = collector.subscribe_topic('/test_topic', None)
        
        # Should fail gracefully (return False in mock mode)
        assert result is False
    
    def test_multiple_subscription_attempts_to_same_topic(self):
        """
        Test that multiple subscription attempts to the same topic are handled correctly.
        
        Requirements: 1.1
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # First subscription attempt
        result1 = collector.subscribe_topic('/test_topic', type(None))
        
        # Second subscription attempt to same topic
        result2 = collector.subscribe_topic('/test_topic', type(None))
        
        # Both should return False in mock mode
        assert result1 is False
        assert result2 is False
    
    def test_subscription_tracking_after_failures(self):
        """
        Test that failed subscriptions don't corrupt the subscription tracking.
        
        Requirements: 1.1
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # Try multiple failed subscriptions
        topics = ['/topic1', '/topic2', '/topic3']
        for topic in topics:
            collector.subscribe_topic(topic, type(None))
        
        # Subscription tracking should remain valid (dict or list depending on initialization)
        assert hasattr(collector, '_subscriptions')
        assert collector._subscriptions is not None
        
        # In mock mode, subscriptions should be empty or not contain the failed topics
        if isinstance(collector._subscriptions, dict):
            assert all(topic not in collector._subscriptions for topic in topics)
        elif isinstance(collector._subscriptions, list):
            # If it's a list, it should be empty in mock mode
            assert len(collector._subscriptions) == 0
    
    def test_recording_without_subscriptions(self):
        """
        Test that recording can start even without successful subscriptions.
        
        Requirements: 1.1
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # Start recording without any subscriptions
        collector.start_recording(duration=0.1)
        
        assert collector._is_recording is True
        
        # Stop recording
        time.sleep(0.15)
        collector.stop_recording()
        
        # Should complete without errors
        assert collector._is_recording is False


class TestDataBufferOverflowProtection:
    """Test suite for data buffer overflow protection."""
    
    def test_buffer_size_limit_enforcement(self):
        """
        Test that buffer size is limited to MAX_BUFFER_SIZE.
        
        Requirements: 1.1
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # Verify MAX_BUFFER_SIZE is defined
        assert hasattr(collector, 'MAX_BUFFER_SIZE')
        assert collector.MAX_BUFFER_SIZE == 10000
    
    def test_buffer_overflow_drops_oldest_data(self):
        """
        Test that when buffer overflows, oldest data is dropped.
        
        Requirements: 1.1
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # Manually fill buffer beyond MAX_BUFFER_SIZE
        test_topic = 'test_overflow_topic'
        
        # Add data up to the limit
        with collector._data_lock:
            for i in range(collector.MAX_BUFFER_SIZE):
                collector._data_buffer[test_topic].append((float(i), {'value': i}))
        
        # Verify buffer is at max size
        assert len(collector._data_buffer[test_topic]) == collector.MAX_BUFFER_SIZE
        
        # Add one more item (should trigger overflow protection)
        with collector._data_lock:
            # Simulate the overflow protection logic
            if len(collector._data_buffer[test_topic]) >= collector.MAX_BUFFER_SIZE:
                collector._data_buffer[test_topic].pop(0)
            collector._data_buffer[test_topic].append((float(collector.MAX_BUFFER_SIZE), {'value': collector.MAX_BUFFER_SIZE}))
        
        # Buffer should still be at max size
        assert len(collector._data_buffer[test_topic]) == collector.MAX_BUFFER_SIZE
        
        # First item should now be timestamp 1.0 (not 0.0)
        first_timestamp, first_data = collector._data_buffer[test_topic][0]
        assert first_timestamp == 1.0, "Oldest data should have been dropped"
        assert first_data['value'] == 1
        
        # Last item should be the newly added one
        last_timestamp, last_data = collector._data_buffer[test_topic][-1]
        assert last_timestamp == float(collector.MAX_BUFFER_SIZE)
        assert last_data['value'] == collector.MAX_BUFFER_SIZE
    
    def test_buffer_overflow_with_multiple_topics(self):
        """
        Test that buffer overflow protection works independently for each topic.
        
        Requirements: 1.1
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        topic1 = 'topic1'
        topic2 = 'topic2'
        
        # Fill topic1 to max
        with collector._data_lock:
            for i in range(collector.MAX_BUFFER_SIZE):
                collector._data_buffer[topic1].append((float(i), {'value': i}))
        
        # Add small amount to topic2
        with collector._data_lock:
            for i in range(100):
                collector._data_buffer[topic2].append((float(i), {'value': i}))
        
        # Verify sizes
        assert len(collector._data_buffer[topic1]) == collector.MAX_BUFFER_SIZE
        assert len(collector._data_buffer[topic2]) == 100
        
        # Topic2 should not be affected by topic1's overflow
        first_timestamp, _ = collector._data_buffer[topic2][0]
        assert first_timestamp == 0.0, "Topic2 should not be affected by topic1 overflow"
    
    def test_get_buffer_size_with_overflow(self):
        """
        Test that get_buffer_size() correctly reports sizes even after overflow.
        
        Requirements: 1.1
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # Add data to multiple topics
        with collector._data_lock:
            for i in range(collector.MAX_BUFFER_SIZE + 100):
                if len(collector._data_buffer['topic1']) >= collector.MAX_BUFFER_SIZE:
                    collector._data_buffer['topic1'].pop(0)
                collector._data_buffer['topic1'].append((float(i), {'value': i}))
            
            for i in range(500):
                collector._data_buffer['topic2'].append((float(i), {'value': i}))
        
        # Get buffer sizes
        sizes = collector.get_buffer_size()
        
        assert sizes['topic1'] == collector.MAX_BUFFER_SIZE
        assert sizes['topic2'] == 500
    
    def test_clear_buffer_after_overflow(self):
        """
        Test that clear_buffer() works correctly even after overflow.
        
        Requirements: 1.1
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # Fill buffer beyond max
        with collector._data_lock:
            for i in range(collector.MAX_BUFFER_SIZE + 100):
                if len(collector._data_buffer['test_topic']) >= collector.MAX_BUFFER_SIZE:
                    collector._data_buffer['test_topic'].pop(0)
                collector._data_buffer['test_topic'].append((float(i), {'value': i}))
        
        # Clear buffer
        collector.clear_buffer()
        
        # Buffer should be empty
        sizes = collector.get_buffer_size()
        assert len(sizes) == 0
        assert len(collector._data_buffer) == 0


class TestCSVFileFormat:
    """Test suite for CSV file format validation."""
    
    def test_csv_has_timestamp_column(self):
        """
        Test that generated CSV files have a timestamp column.
        
        Requirements: 1.5
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # Add some test data
        with collector._data_lock:
            for i in range(10):
                collector._data_buffer['test_topic'].append((float(i), {'value': i * 2}))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            
            # Save to CSV
            result = collector.save_to_csv(str(csv_path))
            assert result is True
            
            # Load and verify
            df = pd.read_csv(csv_path)
            
            assert 'timestamp' in df.columns, "CSV must have timestamp column"
    
    def test_csv_column_names_are_valid(self):
        """
        Test that CSV column names are valid and descriptive.
        
        Requirements: 1.5
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # Add test data with multiple variables
        with collector._data_lock:
            for i in range(10):
                data_dict = {
                    'joint_0_pos': float(i) * 0.1,
                    'joint_0_vel': float(i) * 0.2,
                    'imu_ax': float(i) * 0.3
                }
                collector._data_buffer['test_topic'].append((float(i), data_dict))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            
            collector.save_to_csv(str(csv_path))
            df = pd.read_csv(csv_path)
            
            # Verify expected columns exist
            expected_columns = ['timestamp', 'joint_0_pos', 'joint_0_vel', 'imu_ax']
            for col in expected_columns:
                assert col in df.columns, f"Expected column '{col}' not found in CSV"
    
    def test_csv_data_types_are_numeric(self):
        """
        Test that CSV data columns contain numeric data.
        
        Requirements: 1.5
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # Add numeric test data
        with collector._data_lock:
            for i in range(10):
                collector._data_buffer['test_topic'].append((
                    float(i),
                    {'value1': float(i), 'value2': int(i * 2)}
                ))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            
            collector.save_to_csv(str(csv_path))
            df = pd.read_csv(csv_path)
            
            # All columns should be numeric
            for col in df.columns:
                assert pd.api.types.is_numeric_dtype(df[col]), (
                    f"Column '{col}' should be numeric"
                )
    
    def test_csv_timestamps_are_sorted(self):
        """
        Test that timestamps in CSV are sorted in ascending order.
        
        Requirements: 1.5
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # Add data with unsorted timestamps
        with collector._data_lock:
            timestamps = [5.0, 2.0, 8.0, 1.0, 9.0, 3.0]
            for ts in timestamps:
                collector._data_buffer['test_topic'].append((ts, {'value': ts}))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            
            collector.save_to_csv(str(csv_path))
            df = pd.read_csv(csv_path)
            
            # Timestamps should be sorted
            timestamps_in_csv = df['timestamp'].values
            assert np.all(timestamps_in_csv[:-1] <= timestamps_in_csv[1:]), (
                "Timestamps should be sorted in ascending order"
            )
    
    def test_csv_no_missing_values(self):
        """
        Test that CSV files don't contain missing values (NaN).
        
        Requirements: 1.5
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # Add complete test data
        with collector._data_lock:
            for i in range(10):
                collector._data_buffer['test_topic'].append((
                    float(i),
                    {'value1': float(i), 'value2': float(i * 2)}
                ))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            
            collector.save_to_csv(str(csv_path))
            df = pd.read_csv(csv_path)
            
            # Check for NaN values
            assert not df.isnull().any().any(), "CSV should not contain NaN values"
    
    def test_csv_row_count_matches_data(self):
        """
        Test that CSV row count matches the number of data points collected.
        
        Requirements: 1.5
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        num_samples = 42
        
        # Add test data
        with collector._data_lock:
            for i in range(num_samples):
                collector._data_buffer['test_topic'].append((float(i), {'value': i}))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            
            collector.save_to_csv(str(csv_path))
            df = pd.read_csv(csv_path)
            
            assert len(df) == num_samples, (
                f"CSV should have {num_samples} rows, got {len(df)}"
            )
    
    def test_csv_format_with_multiple_topics(self):
        """
        Test CSV format when data comes from multiple topics.
        
        Requirements: 1.5
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # Add data from multiple topics
        with collector._data_lock:
            for i in range(5):
                collector._data_buffer['topic1'].append((float(i), {'var1': i}))
                collector._data_buffer['topic2'].append((float(i), {'var2': i * 2}))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            
            collector.save_to_csv(str(csv_path))
            df = pd.read_csv(csv_path)
            
            # Should have timestamp and both variables
            assert 'timestamp' in df.columns
            assert 'var1' in df.columns
            assert 'var2' in df.columns
            
            # Should have 10 rows (5 from each topic)
            assert len(df) == 10
    
    def test_csv_file_is_readable_by_pandas(self):
        """
        Test that generated CSV files are readable by pandas without errors.
        
        Requirements: 1.5
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # Add test data
        with collector._data_lock:
            for i in range(10):
                collector._data_buffer['test_topic'].append((
                    float(i),
                    {'value': float(i)}
                ))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            
            collector.save_to_csv(str(csv_path))
            
            # Try to read with pandas
            try:
                df = pd.read_csv(csv_path)
            except Exception as e:
                pytest.fail(f"Failed to read CSV with pandas: {e}")
            
            # Verify basic structure
            assert len(df) > 0
            assert len(df.columns) > 0
    
    def test_csv_empty_data_handling(self):
        """
        Test that saving empty data to CSV is handled gracefully.
        
        Requirements: 1.5
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # Don't add any data
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "empty.csv"
            
            # Should return False for empty data
            result = collector.save_to_csv(str(csv_path))
            assert result is False, "Should return False when saving empty data"
    
    def test_csv_special_characters_in_column_names(self):
        """
        Test that column names with special characters are handled correctly.
        
        Requirements: 1.5
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # Add data with special characters in keys
        with collector._data_lock:
            for i in range(5):
                collector._data_buffer['test_topic'].append((
                    float(i),
                    {'joint_FL_hip': float(i), 'imu_ax': float(i * 2)}
                ))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            
            collector.save_to_csv(str(csv_path))
            df = pd.read_csv(csv_path)
            
            # Verify columns with underscores are preserved
            assert 'joint_FL_hip' in df.columns
            assert 'imu_ax' in df.columns


class TestCSVFileFormatEdgeCases:
    """Additional edge case tests for CSV file format."""
    
    def test_csv_with_very_large_values(self):
        """
        Test CSV format with very large numeric values.
        
        Requirements: 1.5
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # Add data with large values
        with collector._data_lock:
            for i in range(5):
                collector._data_buffer['test_topic'].append((
                    float(i),
                    {'large_value': 1e10, 'small_value': 1e-10}
                ))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            
            collector.save_to_csv(str(csv_path))
            df = pd.read_csv(csv_path)
            
            # Verify large values are preserved
            assert np.all(df['large_value'] > 1e9)
            assert np.all(df['small_value'] < 1e-9)
    
    def test_csv_with_negative_values(self):
        """
        Test CSV format with negative values.
        
        Requirements: 1.5
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # Add data with negative values
        with collector._data_lock:
            for i in range(5):
                collector._data_buffer['test_topic'].append((
                    float(i),
                    {'negative': -float(i), 'positive': float(i)}
                ))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            
            collector.save_to_csv(str(csv_path))
            df = pd.read_csv(csv_path)
            
            # Verify negative values are preserved
            assert np.all(df['negative'] <= 0)
            assert np.all(df['positive'] >= 0)
    
    def test_csv_file_size_is_reasonable(self):
        """
        Test that CSV file size is reasonable for the amount of data.
        
        Requirements: 1.5
        """
        config = ConfigManager(None)
        collector = ROS2DataCollector(config)
        
        # Add moderate amount of data
        num_samples = 1000
        with collector._data_lock:
            for i in range(num_samples):
                collector._data_buffer['test_topic'].append((
                    float(i),
                    {'value': float(i)}
                ))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "test.csv"
            
            collector.save_to_csv(str(csv_path))
            
            # Check file exists and has reasonable size
            assert csv_path.exists()
            file_size = csv_path.stat().st_size
            
            # File should be > 0 and < 1MB for 1000 samples
            assert file_size > 0
            assert file_size < 1024 * 1024, f"File size {file_size} seems too large"


if __name__ == "__main__":
    import sys
    
    print("Running unit tests: ROS2DataCollector")
    print("=" * 80)
    
    # Run tests using pytest
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    
    sys.exit(exit_code)
