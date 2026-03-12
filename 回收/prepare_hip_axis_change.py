#!/usr/bin/env python3
"""
Backup and Preparation Script for Hip Joint Axis Change

This script creates a timestamped backup of the dog2.urdf.xacro file
and prepares the test output directory for the hip joint axis modification.

Requirements: 5.3, 5.4
"""

import os
import shutil
from datetime import datetime
from pathlib import Path


def create_backup(source_file: str, backup_dir: str = "backups") -> str:
    """
    Create a timestamped backup of the source file.
    
    Args:
        source_file: Path to the file to backup
        backup_dir: Directory to store backups
        
    Returns:
        Path to the created backup file
        
    Raises:
        FileNotFoundError: If source file doesn't exist
        PermissionError: If file is not readable
    """
    # Verify source file exists and is readable
    source_path = Path(source_file)
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_file}")
    
    if not os.access(source_file, os.R_OK):
        raise PermissionError(f"Source file is not readable: {source_file}")
    
    # Create backup directory if it doesn't exist
    backup_path = Path(backup_dir)
    backup_path.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create backup filename
    backup_filename = f"{source_path.stem}.backup_{timestamp}{source_path.suffix}"
    backup_file = backup_path / backup_filename
    
    # Copy file with metadata preservation
    shutil.copy2(source_file, backup_file)
    
    print(f"✓ Backup created: {backup_file}")
    print(f"  Original file: {source_file}")
    print(f"  Backup size: {backup_file.stat().st_size} bytes")
    
    return str(backup_file)


def verify_source_file(source_file: str) -> dict:
    """
    Verify the source file exists and is readable.
    
    Args:
        source_file: Path to the file to verify
        
    Returns:
        Dictionary with verification results
    """
    source_path = Path(source_file)
    
    results = {
        "exists": source_path.exists(),
        "readable": False,
        "writable": False,
        "size": 0,
        "path": str(source_path.absolute())
    }
    
    if results["exists"]:
        results["readable"] = os.access(source_file, os.R_OK)
        results["writable"] = os.access(source_file, os.W_OK)
        results["size"] = source_path.stat().st_size
    
    return results


def create_test_output_directory(test_dir: str = "test_outputs") -> str:
    """
    Create test output directory for storing test results.
    
    Args:
        test_dir: Name of the test output directory
        
    Returns:
        Path to the created directory
    """
    test_path = Path(test_dir)
    test_path.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories for different test types
    (test_path / "urdf").mkdir(exist_ok=True)
    (test_path / "rviz").mkdir(exist_ok=True)
    (test_path / "gazebo").mkdir(exist_ok=True)
    
    print(f"✓ Test output directory created: {test_path.absolute()}")
    print(f"  - {test_path / 'urdf'}")
    print(f"  - {test_path / 'rviz'}")
    print(f"  - {test_path / 'gazebo'}")
    
    return str(test_path.absolute())


def main():
    """Main execution function."""
    print("=" * 60)
    print("Hip Joint Axis Change - Backup and Preparation")
    print("=" * 60)
    print()
    
    # Define source file path
    source_file = "src/dog2_description/urdf/dog2.urdf.xacro"
    
    # Step 1: Verify source file
    print("Step 1: Verifying source file...")
    verification = verify_source_file(source_file)
    
    if not verification["exists"]:
        print(f"✗ ERROR: Source file not found: {source_file}")
        return 1
    
    if not verification["readable"]:
        print(f"✗ ERROR: Source file is not readable: {source_file}")
        return 1
    
    print(f"✓ Source file verified:")
    print(f"  Path: {verification['path']}")
    print(f"  Size: {verification['size']} bytes")
    print(f"  Readable: {verification['readable']}")
    print(f"  Writable: {verification['writable']}")
    print()
    
    # Step 2: Create backup
    print("Step 2: Creating backup...")
    try:
        backup_file = create_backup(source_file)
        print()
    except Exception as e:
        print(f"✗ ERROR: Failed to create backup: {e}")
        return 1
    
    # Step 3: Create test output directory
    print("Step 3: Creating test output directory...")
    try:
        test_dir = create_test_output_directory()
        print()
    except Exception as e:
        print(f"✗ ERROR: Failed to create test directory: {e}")
        return 1
    
    # Summary
    print("=" * 60)
    print("Preparation Complete!")
    print("=" * 60)
    print(f"Backup file: {backup_file}")
    print(f"Test directory: {test_dir}")
    print()
    print("Next steps:")
    print("1. Run parameter modification script")
    print("2. Verify URDF syntax and structure")
    print("3. Test in RViz and Gazebo")
    print()
    
    return 0


if __name__ == "__main__":
    exit(main())
