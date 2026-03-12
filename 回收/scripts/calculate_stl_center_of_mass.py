#!/usr/bin/env python3
"""
Calculate center of mass from STL mesh files.

This script reads STL files and calculates the approximate center of mass
assuming uniform density. The calculation uses the mesh triangles to compute
the volume-weighted centroid.
"""

import numpy as np
import struct
import sys
from pathlib import Path


def read_stl_binary(filename):
    """
    Read a binary STL file and return vertices and normals.
    
    Args:
        filename: Path to the STL file
        
    Returns:
        vertices: numpy array of shape (n_triangles, 3, 3) containing triangle vertices
        normals: numpy array of shape (n_triangles, 3) containing triangle normals
    """
    with open(filename, 'rb') as f:
        # Skip header (80 bytes)
        header = f.read(80)
        
        # Read number of triangles (4 bytes, unsigned int)
        n_triangles = struct.unpack('I', f.read(4))[0]
        
        vertices = np.zeros((n_triangles, 3, 3))
        normals = np.zeros((n_triangles, 3))
        
        for i in range(n_triangles):
            # Read normal (3 floats)
            normals[i] = struct.unpack('fff', f.read(12))
            
            # Read 3 vertices (9 floats)
            for j in range(3):
                vertices[i, j] = struct.unpack('fff', f.read(12))
            
            # Skip attribute byte count (2 bytes)
            f.read(2)
    
    return vertices, normals


def calculate_triangle_properties(v0, v1, v2):
    """
    Calculate volume contribution and centroid of a tetrahedron formed by
    a triangle and the origin.
    
    Args:
        v0, v1, v2: Vertices of the triangle
        
    Returns:
        volume: Signed volume of the tetrahedron
        centroid: Centroid of the tetrahedron
    """
    # Volume of tetrahedron = (1/6) * |v0 · (v1 × v2)|
    cross = np.cross(v1, v2)
    volume = np.dot(v0, cross) / 6.0
    
    # Centroid of tetrahedron = (v0 + v1 + v2) / 4
    centroid = (v0 + v1 + v2) / 4.0
    
    return volume, centroid


def calculate_center_of_mass(vertices):
    """
    Calculate the center of mass of a mesh assuming uniform density.
    
    Args:
        vertices: numpy array of shape (n_triangles, 3, 3)
        
    Returns:
        center_of_mass: numpy array of shape (3,) containing xyz coordinates
        total_volume: Total volume of the mesh
    """
    total_volume = 0.0
    weighted_centroid = np.zeros(3)
    
    for triangle in vertices:
        v0, v1, v2 = triangle
        volume, centroid = calculate_triangle_properties(v0, v1, v2)
        
        total_volume += volume
        weighted_centroid += volume * centroid
    
    if abs(total_volume) < 1e-10:
        print("Warning: Total volume is near zero!")
        return np.zeros(3), 0.0
    
    center_of_mass = weighted_centroid / total_volume
    
    return center_of_mass, total_volume


def analyze_stl_file(filename):
    """
    Analyze an STL file and print center of mass information.
    
    Args:
        filename: Path to the STL file
    """
    print(f"\nAnalyzing: {filename}")
    print("=" * 60)
    
    try:
        vertices, normals = read_stl_binary(filename)
        print(f"Number of triangles: {len(vertices)}")
        
        # Calculate bounding box
        all_vertices = vertices.reshape(-1, 3)
        bbox_min = all_vertices.min(axis=0)
        bbox_max = all_vertices.max(axis=0)
        bbox_center = (bbox_min + bbox_max) / 2
        bbox_size = bbox_max - bbox_min
        
        print(f"\nBounding Box:")
        print(f"  Min: [{bbox_min[0]:8.4f}, {bbox_min[1]:8.4f}, {bbox_min[2]:8.4f}]")
        print(f"  Max: [{bbox_max[0]:8.4f}, {bbox_max[1]:8.4f}, {bbox_max[2]:8.4f}]")
        print(f"  Center: [{bbox_center[0]:8.4f}, {bbox_center[1]:8.4f}, {bbox_center[2]:8.4f}]")
        print(f"  Size: [{bbox_size[0]:8.4f}, {bbox_size[1]:8.4f}, {bbox_size[2]:8.4f}]")
        
        # Calculate center of mass
        com, volume = calculate_center_of_mass(vertices)
        
        print(f"\nCenter of Mass (assuming uniform density):")
        print(f"  xyz: [{com[0]:8.4f}, {com[1]:8.4f}, {com[2]:8.4f}]")
        print(f"  Volume: {abs(volume):.6f} cubic units")
        
        # Format for URDF
        print(f"\nURDF Format:")
        print(f'  xyz="{com[0]:.16f} {com[1]:.16f} {com[2]:.16f}"')
        
        return com, volume
        
    except Exception as e:
        print(f"Error analyzing file: {e}")
        return None, None


def main():
    """Main function to analyze STL files for legs 3 and 4."""
    
    print("STL Center of Mass Calculator")
    print("=" * 60)
    print("Calculating center of mass for Dog2 leg links...")
    
    # Define the files to analyze
    stl_files = {
        'l311 (Leg 3 Thigh)': 'src/dog2_description/meshes/l311.STL',
        'l3111 (Leg 3 Shin)': 'src/dog2_description/meshes/l3111.STL',
        'l4111 (Leg 4 Shin)': 'src/dog2_description/meshes/l4111.STL',
        # Also analyze reference links for comparison
        'l111 (Leg 1 Shin - Reference)': 'src/dog2_description/meshes/l111.STL',
        'l211 (Leg 2 Shin - Reference)': 'src/dog2_description/meshes/l211.STL',
        'l411 (Leg 4 Thigh - Reference)': 'src/dog2_description/meshes/l411.STL',
    }
    
    results = {}
    
    for name, filepath in stl_files.items():
        if Path(filepath).exists():
            com, volume = analyze_stl_file(filepath)
            if com is not None:
                results[name] = {'com': com, 'volume': volume}
        else:
            print(f"\nWarning: File not found: {filepath}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY - Recommended Inertia Origins")
    print("=" * 60)
    
    if 'l311 (Leg 3 Thigh)' in results:
        com = results['l311 (Leg 3 Thigh)']['com']
        print(f"\nLeg 3 Thigh (l311):")
        print(f'  <xacro:property name="leg3_thigh_inertia_xyz" value="{com[0]:.16f} {com[1]:.16f} {com[2]:.16f}"/>')
    
    if 'l3111 (Leg 3 Shin)' in results:
        com = results['l3111 (Leg 3 Shin)']['com']
        print(f"\nLeg 3 Shin (l3111):")
        print(f'  <xacro:property name="leg3_shin_inertia_xyz" value="{com[0]:.16f} {com[1]:.16f} {com[2]:.16f}"/>')
    
    if 'l4111 (Leg 4 Shin)' in results:
        com = results['l4111 (Leg 4 Shin)']['com']
        print(f"\nLeg 4 Shin (l4111):")
        print(f'  <xacro:property name="leg4_shin_inertia_xyz" value="{com[0]:.16f} {com[1]:.16f} {com[2]:.16f}"/>')
    
    # Comparison with reference links
    print("\n" + "=" * 60)
    print("COMPARISON WITH REFERENCE LINKS")
    print("=" * 60)
    
    if 'l111 (Leg 1 Shin - Reference)' in results and 'l3111 (Leg 3 Shin)' in results:
        com_ref = results['l111 (Leg 1 Shin - Reference)']['com']
        com_l3 = results['l3111 (Leg 3 Shin)']['com']
        diff = com_l3 - com_ref
        print(f"\nLeg 3 Shin vs Leg 1 Shin (Reference):")
        print(f"  Difference: [{diff[0]:8.4f}, {diff[1]:8.4f}, {diff[2]:8.4f}]")
        print(f"  Distance: {np.linalg.norm(diff):.4f}")
    
    if 'l211 (Leg 2 Shin - Reference)' in results and 'l4111 (Leg 4 Shin)' in results:
        com_ref = results['l211 (Leg 2 Shin - Reference)']['com']
        com_l4 = results['l4111 (Leg 4 Shin)']['com']
        diff = com_l4 - com_ref
        print(f"\nLeg 4 Shin vs Leg 2 Shin (Reference):")
        print(f"  Difference: [{diff[0]:8.4f}, {diff[1]:8.4f}, {diff[2]:8.4f}]")
        print(f"  Distance: {np.linalg.norm(diff):.4f}")
    
    print("\n" + "=" * 60)
    print("Note: These values assume uniform density.")
    print("For more accurate results, use CAD software with material properties.")
    print("=" * 60)


if __name__ == '__main__':
    main()
