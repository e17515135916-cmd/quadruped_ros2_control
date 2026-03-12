#!/usr/bin/env python3
"""
Measure All Leg Mesh Files

Measures all thigh and shin STL mesh files and saves the results to a configuration file.
This script is used for task 2 of the gazebo-collision-mesh-fixes spec.

Requirements: 4.1
"""

import json
import sys
from pathlib import Path
from typing import Dict

# Import the measurement function from the existing script
sys.path.insert(0, str(Path(__file__).parent))
from measure_stl_mesh import measure_stl_mesh


def measure_all_leg_meshes(mesh_dir: Path) -> Dict:
    """
    Measure all thigh and shin mesh files.
    
    Args:
        mesh_dir: Directory containing the STL mesh files
        
    Returns:
        Dictionary containing measurements for all leg meshes
    """
    results = {
        'thighs': {},
        'shins': {}
    }
    
    # Thigh meshes: l111.STL, l211.STL, l311.STL, l411.STL
    thigh_files = ['l111.STL', 'l211.STL', 'l311.STL', 'l411.STL']
    
    # Shin meshes: l1111.STL, l2111.STL, l3111.STL, l4111.STL
    shin_files = ['l1111.STL', 'l2111.STL', 'l3111.STL', 'l4111.STL']
    
    print("Measuring thigh meshes...")
    for thigh_file in thigh_files:
        mesh_path = mesh_dir / thigh_file
        print(f"  Measuring {thigh_file}...")
        try:
            measurements = measure_stl_mesh(str(mesh_path))
            results['thighs'][thigh_file] = measurements
            print(f"    ✓ Length: {measurements['length']:.4f}m, "
                  f"Width: {measurements['width']:.4f}m, "
                  f"Height: {measurements['height']:.4f}m")
        except Exception as e:
            print(f"    ✗ Error: {e}", file=sys.stderr)
            results['thighs'][thigh_file] = {'error': str(e)}
    
    print("\nMeasuring shin meshes...")
    for shin_file in shin_files:
        mesh_path = mesh_dir / shin_file
        print(f"  Measuring {shin_file}...")
        try:
            measurements = measure_stl_mesh(str(mesh_path))
            results['shins'][shin_file] = measurements
            print(f"    ✓ Length: {measurements['length']:.4f}m, "
                  f"Width: {measurements['width']:.4f}m, "
                  f"Height: {measurements['height']:.4f}m")
        except Exception as e:
            print(f"    ✗ Error: {e}", file=sys.stderr)
            results['shins'][shin_file] = {'error': str(e)}
    
    return results


def main():
    """Main entry point."""
    # Determine mesh directory
    script_dir = Path(__file__).parent.parent
    mesh_dir = script_dir / 'src' / 'dog2_description' / 'meshes'
    
    if not mesh_dir.exists():
        print(f"Error: Mesh directory not found: {mesh_dir}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Mesh directory: {mesh_dir}\n")
    
    # Measure all meshes
    results = measure_all_leg_meshes(mesh_dir)
    
    # Save to configuration file
    config_dir = script_dir / '.kiro' / 'specs' / 'gazebo-collision-mesh-fixes'
    config_file = config_dir / 'mesh_measurements.json'
    
    config_dir.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Measurements saved to: {config_file}")
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    thigh_count = sum(1 for v in results['thighs'].values() if 'error' not in v)
    shin_count = sum(1 for v in results['shins'].values() if 'error' not in v)
    
    print(f"Thighs measured: {thigh_count}/4")
    print(f"Shins measured: {shin_count}/4")
    
    if thigh_count < 4 or shin_count < 4:
        print("\n⚠ Warning: Some measurements failed. Check errors above.")
        sys.exit(1)
    else:
        print("\n✓ All measurements completed successfully!")


if __name__ == '__main__':
    main()
