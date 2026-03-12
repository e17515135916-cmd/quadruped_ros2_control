#!/usr/bin/env python3
"""
Main visualization node for Dog2 quadruped robot

This node subscribes to control data and publishes RViz2 markers for:
- Foot forces (arrows with color coding)
- Trajectories (history and reference)
- Contact states (colored spheres)
- Sliding joint status (text with warning levels)
- Performance metrics (text panel)
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray
from visualization_msgs.msg import MarkerArray

from dog2_visualization.foot_force_visualizer import FootForceVisualizer


class VisualizationNode(Node):
    """Main visualization node for Dog2 visualization system"""
    
    def __init__(self):
        super().__init__('visualization_node')
        
        # Parameters
        self.declare_parameter('update_rate', 20.0)  # Hz
        
        self.update_rate = self.get_parameter('update_rate').value
        
        # State variables
        self.current_odom = None
        self.current_joint_states = None
        self.current_foot_forces = None
        self.odom_received = False
        self.joint_states_received = False
        self.foot_forces_received = False
        
        # Initialize visualizers
        self.foot_force_viz = FootForceVisualizer(frame_id='base_link')
        
        # Initialize subscribers
        self._init_subscribers()
        
        # Initialize publishers
        self._init_publishers()
        
        # Create timer for periodic visualization updates
        timer_period = 1.0 / self.update_rate
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        self.get_logger().info(f'Dog2 Visualization Node initialized at {self.update_rate} Hz')
        self.get_logger().info('Waiting for data from /dog2/odom, /joint_states, /dog2/mpc/foot_forces...')
    
    def _init_subscribers(self):
        """Initialize all subscribers"""
        self.odom_sub = self.create_subscription(
            Odometry,
            '/dog2/odom',
            self.odom_callback,
            10
        )
        
        self.joint_states_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_states_callback,
            10
        )
        
        self.foot_forces_sub = self.create_subscription(
            Float64MultiArray,
            '/dog2/mpc/foot_forces',
            self.foot_forces_callback,
            10
        )
    
    def _init_publishers(self):
        """Initialize all publishers"""
        self.foot_force_markers_pub = self.create_publisher(
            MarkerArray,
            '/dog2/visualization/foot_forces',
            10
        )
        
        self.trajectory_markers_pub = self.create_publisher(
            MarkerArray,
            '/dog2/visualization/trajectory',
            10
        )
        
        self.contact_markers_pub = self.create_publisher(
            MarkerArray,
            '/dog2/visualization/contact_markers',
            10
        )
        
        self.sliding_status_pub = self.create_publisher(
            MarkerArray,
            '/dog2/visualization/sliding_status',
            10
        )
        
        self.performance_text_pub = self.create_publisher(
            MarkerArray,
            '/dog2/visualization/performance_text',
            10
        )
    
    def odom_callback(self, msg):
        """Callback for odometry data"""
        self.current_odom = msg
        if not self.odom_received:
            self.odom_received = True
            self.get_logger().info('Received first odometry message')
    
    def joint_states_callback(self, msg):
        """Callback for joint states"""
        self.current_joint_states = msg
        if not self.joint_states_received:
            self.joint_states_received = True
            self.get_logger().info('Received first joint states message')
    
    def foot_forces_callback(self, msg):
        """Callback for foot forces from MPC"""
        if len(msg.data) != 12:
            self.get_logger().warn(f'Expected 12 foot forces, got {len(msg.data)}')
            return
        
        self.current_foot_forces = msg
        if not self.foot_forces_received:
            self.foot_forces_received = True
            self.get_logger().info('Received first foot forces message')
    
    def timer_callback(self):
        """Periodic callback to update visualizations"""
        # Check if we have all required data
        if not (self.odom_received and self.joint_states_received and self.foot_forces_received):
            return
        
        # Update foot force visualization
        self._update_foot_force_visualization()
        
        # TODO: Update other visualizations
        # - Task 4: Trajectory visualization
        # - Task 6: Contact marker visualization
        # - Task 7: Sliding joint visualization
        # - Task 8: Performance monitoring
    
    def _update_foot_force_visualization(self):
        """Update foot force arrow markers"""
        try:
            # Extract foot forces
            foot_forces = list(self.current_foot_forces.data)
            
            # TODO: Get actual contact states from MPC or gait planner
            # For now, assume all feet in contact
            contact_states = [True, True, True, True]
            
            # Create markers
            marker_array = self.foot_force_viz.create_markers(
                foot_forces,
                contact_states
            )
            
            # Publish markers
            self.foot_force_markers_pub.publish(marker_array)
            
        except Exception as e:
            self.get_logger().error(f'Error updating foot force visualization: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = VisualizationNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
