#!/usr/bin/env python3
"""
Script to verify inertia positions in RViz by publishing markers
showing the center of mass for each leg link.
"""

import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point
from std_msgs.msg import ColorRGBA
import xml.etree.ElementTree as ET


class InertiaVisualizationNode(Node):
    def __init__(self):
        super().__init__('inertia_visualization')
        
        # Publisher for markers
        self.marker_pub = self.create_publisher(MarkerArray, 'inertia_markers', 10)
        
        # Timer to publish markers
        self.timer = self.create_timer(1.0, self.publish_markers)
        
        # Load URDF and extract inertia positions
        self.inertia_positions = self.load_inertia_positions()
        
        self.get_logger().info('Inertia visualization node started')
        self.get_logger().info(f'Found {len(self.inertia_positions)} links with inertia')

    def load_inertia_positions(self):
        """Load inertia positions from the modified URDF"""
        urdf_path = 'src/dog2_description/urdf/dog2_modified.urdf'
        
        try:
            tree = ET.parse(urdf_path)
            root = tree.getroot()
            
            positions = {}
            
            # Links we're interested in
            target_links = ['l111', 'l1111', 'l211', 'l2111', 'l311', 'l3111', 'l411', 'l4111']
            
            for link_name in target_links:
                link = root.find(f".//link[@name='{link_name}']")
                if link is not None:
                    inertial = link.find('inertial')
                    if inertial is not None:
                        origin = inertial.find('origin')
                        if origin is not None:
                            xyz_str = origin.get('xyz')
                            if xyz_str:
                                xyz = [float(x) for x in xyz_str.split()]
                                positions[link_name] = xyz
                                
            return positions
            
        except Exception as e:
            self.get_logger().error(f'Failed to load URDF: {e}')
            return {}

    def publish_markers(self):
        """Publish markers showing center of mass positions"""
        marker_array = MarkerArray()
        
        for i, (link_name, xyz) in enumerate(self.inertia_positions.items()):
            marker = Marker()
            marker.header.frame_id = link_name
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = "inertia_centers"
            marker.id = i
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD
            
            # Position at center of mass
            marker.pose.position.x = xyz[0]
            marker.pose.position.y = xyz[1] 
            marker.pose.position.z = xyz[2]
            marker.pose.orientation.w = 1.0
            
            # Size
            marker.scale.x = 0.02
            marker.scale.y = 0.02
            marker.scale.z = 0.02
            
            # Color based on leg
            if 'l3' in link_name:
                # Red for leg 3 (corrected)
                marker.color = ColorRGBA(r=1.0, g=0.0, b=0.0, a=0.8)
            elif 'l4111' in link_name:
                # Orange for leg 4 shin (corrected)
                marker.color = ColorRGBA(r=1.0, g=0.5, b=0.0, a=0.8)
            else:
                # Green for reference legs (1 and 2)
                marker.color = ColorRGBA(r=0.0, g=1.0, b=0.0, a=0.8)
            
            marker.lifetime.sec = 2
            marker_array.markers.append(marker)
            
        # Add text labels
        for i, (link_name, xyz) in enumerate(self.inertia_positions.items()):
            text_marker = Marker()
            text_marker.header.frame_id = link_name
            text_marker.header.stamp = self.get_clock().now().to_msg()
            text_marker.ns = "inertia_labels"
            text_marker.id = i + 100
            text_marker.type = Marker.TEXT_VIEW_FACING
            text_marker.action = Marker.ADD
            
            # Position slightly offset from center of mass
            text_marker.pose.position.x = xyz[0] + 0.03
            text_marker.pose.position.y = xyz[1] + 0.03
            text_marker.pose.position.z = xyz[2] + 0.03
            text_marker.pose.orientation.w = 1.0
            
            # Text content
            text_marker.text = f"{link_name}\nX:{xyz[0]:.3f}"
            
            # Size and color
            text_marker.scale.z = 0.015
            text_marker.color = ColorRGBA(r=1.0, g=1.0, b=1.0, a=1.0)
            
            text_marker.lifetime.sec = 2
            marker_array.markers.append(text_marker)
        
        self.marker_pub.publish(marker_array)


def main(args=None):
    rclpy.init(args=args)
    
    node = InertiaVisualizationNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()