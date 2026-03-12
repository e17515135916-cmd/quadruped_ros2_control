"""
ROS2 Data Collector Module

This module provides functionality to collect data from ROS2 topics during
simulation and save it to CSV format for later visualization and analysis.
"""

import time
import threading
from typing import Dict, List, Type, Optional, Any
from collections import defaultdict
import numpy as np
import pandas as pd

try:
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False
    Node = object  # Fallback for when ROS2 is not available

from .config_manager import ConfigManager
from .data_models import TimeSeriesData
from .logger import get_logger

logger = get_logger(__name__)


class ROS2DataCollector(Node if ROS2_AVAILABLE else object):
    """
    Collects data from ROS2 topics and saves to CSV format.
    
    This class subscribes to specified ROS2 topics, records timestamped data,
    and provides methods to export the collected data to CSV files or pandas
    DataFrames for further analysis.
    """
    
    # Maximum buffer size to prevent memory overflow
    MAX_BUFFER_SIZE = 10000
    
    def __init__(self, config: ConfigManager):
        """
        Initialize ROS2 node and data collection structures.
        
        Args:
            config: ConfigManager instance with data source configuration
        """
        self.config = config
        self.data_sources = config.get_data_sources()
        
        # Data storage: {topic_name: [(timestamp, data_dict), ...]}
        self._data_buffer: Dict[str, List[tuple]] = defaultdict(list)
        
        # Subscription tracking
        self._subscriptions: Dict[str, Any] = {}
        
        # Recording state
        self._is_recording = False
        self._recording_start_time = None
        self._recording_duration = None
        self._recording_thread = None
        
        # Lock for thread-safe data access
        self._data_lock = threading.Lock()
        
        if not ROS2_AVAILABLE:
            logger.warning("ROS2 not available. ROS2DataCollector will operate in mock mode.")
            self._mock_mode = True
        else:
            # Try to initialize ROS2 node
            try:
                super().__init__('presentation_viz_data_collector')
                self._mock_mode = False
                logger.info("ROS2DataCollector initialized with ROS2 support")
            except Exception as e:
                logger.warning(f"Failed to initialize ROS2 node: {e}. Operating in mock mode.")
                self._mock_mode = True
        
        logger.info("ROS2DataCollector initialized")
    
    def subscribe_topic(self, topic_name: str, msg_type: Type, 
                       callback: Optional[callable] = None) -> bool:
        """
        Subscribe to a ROS2 topic.
        
        Args:
            topic_name: Name of the topic to subscribe to
            msg_type: Message type class (e.g., sensor_msgs.msg.JointState)
            callback: Optional custom callback function. If None, uses default.
        
        Returns:
            True if subscription successful, False otherwise
        """
        if self._mock_mode:
            logger.warning(f"Mock mode: Cannot subscribe to topic {topic_name}")
            return False
        
        try:
            # Create QoS profile for reliable data collection
            qos_profile = QoSProfile(
                reliability=ReliabilityPolicy.RELIABLE,
                history=HistoryPolicy.KEEP_LAST,
                depth=10
            )
            
            # Use custom callback or default
            if callback is None:
                callback = lambda msg: self._default_callback(topic_name, msg)
            
            # Create subscription
            subscription = self.create_subscription(
                msg_type,
                topic_name,
                callback,
                qos_profile
            )
            
            self._subscriptions[topic_name] = subscription
            logger.info(f"Subscribed to topic: {topic_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to subscribe to topic {topic_name}: {e}")
            return False
    
    def _default_callback(self, topic_name: str, msg: Any) -> None:
        """
        Default callback for topic messages.
        
        Args:
            topic_name: Name of the topic
            msg: Received message
        """
        if not self._is_recording:
            return
        
        # Get current timestamp
        if self._mock_mode:
            timestamp = time.time() - self._recording_start_time
        else:
            timestamp = self.get_clock().now().nanoseconds / 1e9 - self._recording_start_time
        
        # Extract data from message
        data_dict = self._extract_message_data(msg)
        
        # Store data with thread safety
        with self._data_lock:
            # Check buffer size to prevent overflow
            if len(self._data_buffer[topic_name]) >= self.MAX_BUFFER_SIZE:
                logger.warning(
                    f"Buffer overflow protection: dropping oldest data for {topic_name}"
                )
                self._data_buffer[topic_name].pop(0)
            
            self._data_buffer[topic_name].append((timestamp, data_dict))
    
    def _extract_message_data(self, msg: Any) -> Dict[str, Any]:
        """
        Extract data from a ROS2 message into a dictionary.
        
        Args:
            msg: ROS2 message object
        
        Returns:
            Dictionary of field names to values
        """
        data_dict = {}
        
        # Handle different message types
        msg_type = type(msg).__name__
        
        try:
            if msg_type == 'JointState':
                # Extract joint states
                for i, name in enumerate(msg.name):
                    if i < len(msg.position):
                        data_dict[f'joint_{name}_pos'] = msg.position[i]
                    if i < len(msg.velocity):
                        data_dict[f'joint_{name}_vel'] = msg.velocity[i]
                    if i < len(msg.effort):
                        data_dict[f'joint_{name}_eff'] = msg.effort[i]
            
            elif msg_type == 'Imu':
                # Extract IMU data
                data_dict['imu_ax'] = msg.linear_acceleration.x
                data_dict['imu_ay'] = msg.linear_acceleration.y
                data_dict['imu_az'] = msg.linear_acceleration.z
                data_dict['imu_gx'] = msg.angular_velocity.x
                data_dict['imu_gy'] = msg.angular_velocity.y
                data_dict['imu_gz'] = msg.angular_velocity.z
            
            elif msg_type == 'Odometry':
                # Extract odometry data
                data_dict['odom_x'] = msg.pose.pose.position.x
                data_dict['odom_y'] = msg.pose.pose.position.y
                data_dict['odom_z'] = msg.pose.pose.position.z
                data_dict['odom_qx'] = msg.pose.pose.orientation.x
                data_dict['odom_qy'] = msg.pose.pose.orientation.y
                data_dict['odom_qz'] = msg.pose.pose.orientation.z
                data_dict['odom_qw'] = msg.pose.pose.orientation.w
            
            else:
                # Generic extraction for unknown types
                for field in msg.get_fields_and_field_types():
                    try:
                        value = getattr(msg, field)
                        if isinstance(value, (int, float, bool)):
                            data_dict[field] = value
                    except:
                        pass
        
        except Exception as e:
            logger.error(f"Error extracting message data: {e}")
        
        return data_dict
    
    def start_recording(self, duration: Optional[float] = None) -> None:
        """
        Start recording data from subscribed topics.
        
        Args:
            duration: Optional recording duration in seconds. If None, records until stop_recording() is called.
        """
        if self._is_recording:
            logger.warning("Recording already in progress")
            return
        
        self._is_recording = True
        self._recording_duration = duration
        
        if self._mock_mode:
            self._recording_start_time = time.time()
        else:
            self._recording_start_time = self.get_clock().now().nanoseconds / 1e9
        
        logger.info(f"Started recording (duration: {duration if duration else 'unlimited'}s)")
        
        # If duration specified, start timer thread
        if duration is not None:
            self._recording_thread = threading.Timer(duration, self.stop_recording)
            self._recording_thread.start()
    
    def stop_recording(self) -> None:
        """Stop recording data."""
        if not self._is_recording:
            logger.warning("No recording in progress")
            return
        
        self._is_recording = False
        
        # Cancel timer thread if exists
        if self._recording_thread and self._recording_thread.is_alive():
            self._recording_thread.cancel()
        
        # Calculate statistics
        total_samples = sum(len(data) for data in self._data_buffer.values())
        logger.info(f"Stopped recording. Total samples collected: {total_samples}")
        
        for topic, data in self._data_buffer.items():
            logger.info(f"  {topic}: {len(data)} samples")
    
    def get_data_frame(self) -> pd.DataFrame:
        """
        Get collected data as a pandas DataFrame.
        
        Returns:
            DataFrame with timestamp index and columns for each data field
        """
        with self._data_lock:
            if not self._data_buffer:
                logger.warning("No data collected")
                return pd.DataFrame()
            
            # Combine all data from different topics
            all_data = []
            
            for topic_name, data_list in self._data_buffer.items():
                for timestamp, data_dict in data_list:
                    row = {'timestamp': timestamp}
                    row.update(data_dict)
                    all_data.append(row)
            
            # Create DataFrame
            df = pd.DataFrame(all_data)
            
            # Sort by timestamp
            if 'timestamp' in df.columns:
                df = df.sort_values('timestamp').reset_index(drop=True)
            
            return df
    
    def get_time_series_data(self) -> TimeSeriesData:
        """
        Get collected data as TimeSeriesData object.
        
        Returns:
            TimeSeriesData object with timestamps and variables
        """
        df = self.get_data_frame()
        
        if df.empty:
            return TimeSeriesData()
        
        # Extract timestamps
        timestamps = df['timestamp'].values
        
        # Extract variables (all columns except timestamp)
        variables = {}
        for col in df.columns:
            if col != 'timestamp':
                variables[col] = df[col].values
        
        # Create metadata
        metadata = {
            'collection_start': self._recording_start_time,
            'num_samples': len(timestamps),
            'topics': list(self._subscriptions.keys())
        }
        
        return TimeSeriesData(
            timestamps=timestamps,
            variables=variables,
            metadata=metadata
        )
    
    def save_to_csv(self, output_path: str) -> bool:
        """
        Save collected data to CSV file.
        
        Args:
            output_path: Path to output CSV file
        
        Returns:
            True if save successful, False otherwise
        """
        try:
            df = self.get_data_frame()
            
            if df.empty:
                logger.warning("No data to save")
                return False
            
            # Save to CSV
            df.to_csv(output_path, index=False)
            logger.info(f"Data saved to {output_path} ({len(df)} rows, {len(df.columns)} columns)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save data to CSV: {e}")
            return False
    
    def clear_buffer(self) -> None:
        """Clear all collected data from buffer."""
        with self._data_lock:
            self._data_buffer.clear()
        logger.info("Data buffer cleared")
    
    def get_buffer_size(self) -> Dict[str, int]:
        """
        Get current buffer sizes for each topic.
        
        Returns:
            Dictionary mapping topic names to number of samples
        """
        with self._data_lock:
            return {topic: len(data) for topic, data in self._data_buffer.items()}
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            if hasattr(self, '_is_recording') and self._is_recording:
                self.stop_recording()
            
            if hasattr(self, '_mock_mode') and not self._mock_mode and ROS2_AVAILABLE:
                try:
                    self.destroy_node()
                except:
                    pass
        except:
            pass  # Silently ignore cleanup errors
