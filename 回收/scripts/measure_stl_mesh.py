#!/usr/bin/env python3
"""
STL Mesh Measurement Tool

Measures the bounding box dimensions and center of mass of STL mesh files.
Used to calculate appropriate collision primitive sizes for URDF configuration.

Requirements: 4.1
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Tuple

try:
    import numpy as np
    from stl import mesh
except ImportError:
    print("Error: Required libraries not found.", file=sys.stderr)
    print("Please install: pip install numpy-stl numpy", file=sys.stderr)
    sys.exit(1)


def measure_stl_mesh(stl_path: str) -> Dict:
    """
    Measure STL Mesh bounding box and center of mass.
    
    Args:
        stl_path: Path to the STL file
        
    Returns:
        Dictionary containing:
            - length: Main axis length (meters)
            - width: Cross-section width (meters)
            - height: Cross-section height (meters)
            - center: Center of mass position (x, y, z) in meters
            - min_bounds: Minimum bounds (x, y, z)
            - max_bounds: Maximum bounds (x, y, z)
            
    Raises:
        FileNotFoundError: If STL file doesn't exist
        ValueError: If STL file is invalid or empty
    """
    stl_path = Path(stl_path)
    
    if not stl_path.exists():
        raise FileNotFoundError(f"STL file not found: {stl_path}")
    
    # Load the STL mesh
    try:
        stl_mesh = mesh.Mesh.from_file(str(stl_path))
    except Exception as e:
        raise ValueError(f"Failed to load STL file: {e}")
    
    if len(stl_mesh.vectors) == 0:
        raise ValueError(f"STL file is empty: {stl_path}")
    
    # Get all vertices from the mesh
    vertices = stl_mesh.vectors.reshape(-1, 3)
    
    # Calculate bounding box
    min_bounds = vertices.min(axis=0)
    max_bounds = vertices.max(axis=0)
    dimensions = max_bounds - min_bounds
    
    # Calculate center of mass (geometric center of bounding box)
    center = (min_bounds + max_bounds) / 2.0
    
    # Sort dimensions to identify length (longest), width, height
    sorted_dims = np.sort(dimensions)[::-1]  # Descending order
    
    return {
        'length': float(sorted_dims[0]),
        'width': float(sorted_dims[1]),
        'height': float(sorted_dims[2]),
        'center': {
            'x': float(center[0]),
            'y': float(center[1]),
            'z': float(center[2])
        },
        'min_bounds': {
            'x': float(min_bounds[0]),
            'y': float(min_bounds[1]),
            'z': float(min_bounds[2])
        },
        'max_bounds': {
            'x': float(max_bounds[0]),
            'y': float(max_bounds[1]),
            'z': float(max_bounds[2])
        },
        'dimensions': {
            'x': float(dimensions[0]),
            'y': float(dimensions[1]),
            'z': float(dimensions[2])
        }
    }


def main():
    """Main entry point for the STL measurement tool."""
    parser = argparse.ArgumentParser(
        description='Measure STL mesh bounding box dimensions and center of mass'
    )
    parser.add_argument(
        'stl_file',
        type=str,
        help='Path to the STL file to measure'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output JSON file path (default: print to stdout)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print JSON output'
    )
    
    args = parser.parse_args()
    
    try:
        # Measure the STL mesh
        measurements = measure_stl_mesh(args.stl_file)
        
        # Add metadata
        result = {
            'file': str(Path(args.stl_file).resolve()),
            'measurements': measurements
        }
        
        # Format JSON output
        indent = 2 if args.pretty else None
        json_output = json.dumps(result, indent=indent)
        
        # Output results
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json_output)
            print(f"Measurements saved to: {output_path}")
        else:
            print(json_output)
            
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
