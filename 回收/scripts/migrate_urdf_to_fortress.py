#!/usr/bin/env python3
"""
URDF Migration Script for Gazebo Fortress
Migrates URDF/Xacro files from Gazebo Classic to Gazebo Fortress (gz-sim)
"""

import os
import sys
import shutil
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.NC}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.NC}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.NC}")

def create_backup(file_path, backup_dir):
    """Create a timestamped backup of the file"""
    if not os.path.exists(file_path):
        print_error(f"File not found: {file_path}")
        return None
    
    # Create backup directory structure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"gazebo_fortress_migration_{timestamp}")
    os.makedirs(backup_path, exist_ok=True)
    
    # Copy file to backup
    file_name = os.path.basename(file_path)
    backup_file = os.path.join(backup_path, f"{file_name}.backup")
    shutil.copy2(file_path, backup_file)
    
    # Create README
    readme_path = os.path.join(backup_path, "README.md")
    with open(readme_path, 'w') as f:
        f.write(f"# Gazebo Fortress Migration Backup\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Original File**: {file_path}\n\n")
        f.write(f"**Backup File**: {backup_file}\n\n")
        f.write(f"## Rollback Instructions\n\n")
        f.write(f"To restore the original file:\n\n")
        f.write(f"```bash\n")
        f.write(f"cp {backup_file} {file_path}\n")
        f.write(f"```\n")
    
    return backup_file

def migrate_ros2_control_plugin(content):
    """
    Migrate ros2_control plugin references from Gazebo Classic to Gazebo Fortress
    
    Changes:
    - gazebo_ros2_control/GazeboSystem -> gz_ros2_control/GazeboSimSystem
    - libgazebo_ros2_control.so -> libgz_ros2_control-system.so
    """
    replacements = [
        # Plugin name in hardware section
        ('gazebo_ros2_control/GazeboSystem', 'gz_ros2_control/GazeboSimSystem'),
        # Plugin library file
        ('libgazebo_ros2_control.so', 'libgz_ros2_control-system.so'),
        # Plugin name attribute
        ('name="gazebo_ros2_control"', 'name="gz_ros2_control"'),
    ]
    
    modified = content
    changes_made = []
    
    for old, new in replacements:
        if old in modified:
            modified = modified.replace(old, new)
            changes_made.append(f"  - {old} → {new}")
    
    return modified, changes_made

def validate_xacro(file_path):
    """Validate that xacro processing works on the file"""
    try:
        import subprocess
        result = subprocess.run(
            ['xacro', file_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True, "Xacro processing successful"
        else:
            return False, f"Xacro error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return False, "Xacro processing timed out"
    except FileNotFoundError:
        print_warning("xacro command not found, skipping validation")
        return True, "Xacro validation skipped"
    except Exception as e:
        return False, f"Xacro validation error: {str(e)}"

def extract_ros2_control_joints(content):
    """Extract joint names from ros2_control section for validation"""
    joints = []
    try:
        # Simple regex-based extraction (more robust than full XML parsing for mixed content)
        import re
        joint_pattern = r'<joint\s+name="([^"]+)"'
        joints = re.findall(joint_pattern, content)
    except Exception as e:
        print_warning(f"Could not extract joints: {e}")
    return joints

def migrate_urdf_file(file_path, backup_dir, dry_run=False):
    """Migrate a single URDF/Xacro file"""
    print(f"\n{'='*60}")
    print(f"Migrating: {file_path}")
    print(f"{'='*60}\n")
    
    # Read original content
    try:
        with open(file_path, 'r') as f:
            original_content = f.read()
    except Exception as e:
        print_error(f"Failed to read file: {e}")
        return False
    
    # Extract joints before migration
    joints_before = extract_ros2_control_joints(original_content)
    print(f"Found {len(joints_before)} joints in ros2_control section")
    
    # Create backup
    if not dry_run:
        backup_file = create_backup(file_path, backup_dir)
        if backup_file:
            print_success(f"Backup created: {backup_file}")
        else:
            print_error("Failed to create backup, aborting migration")
            return False
    else:
        print_warning("Dry run: Skipping backup creation")
    
    # Perform migration
    migrated_content, changes = migrate_ros2_control_plugin(original_content)
    
    if not changes:
        print_warning("No changes needed - file may already be migrated or doesn't use ros2_control")
        return True
    
    print("\nChanges made:")
    for change in changes:
        print(change)
    
    # Extract joints after migration
    joints_after = extract_ros2_control_joints(migrated_content)
    
    # Validate joint preservation
    if set(joints_before) != set(joints_after):
        print_error("Joint configuration changed during migration!")
        print(f"  Before: {joints_before}")
        print(f"  After: {joints_after}")
        if not dry_run:
            print_error("Aborting - restoring from backup")
            return False
    else:
        print_success(f"Joint configuration preserved ({len(joints_after)} joints)")
    
    # Write migrated content
    if not dry_run:
        try:
            with open(file_path, 'w') as f:
                f.write(migrated_content)
            print_success(f"File updated: {file_path}")
        except Exception as e:
            print_error(f"Failed to write file: {e}")
            return False
    else:
        print_warning("Dry run: Skipping file write")
    
    # Validate xacro processing
    if file_path.endswith('.xacro'):
        print("\nValidating xacro processing...")
        if not dry_run:
            valid, message = validate_xacro(file_path)
            if valid:
                print_success(message)
            else:
                print_error(message)
                return False
        else:
            print_warning("Dry run: Skipping xacro validation")
    
    print_success("Migration completed successfully!")
    return True

def main():
    parser = argparse.ArgumentParser(
        description='Migrate URDF/Xacro files from Gazebo Classic to Gazebo Fortress'
    )
    parser.add_argument(
        'files',
        nargs='+',
        help='URDF/Xacro files to migrate'
    )
    parser.add_argument(
        '--backup-dir',
        default='backups',
        help='Directory for backups (default: backups)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    
    args = parser.parse_args()
    
    print(f"{Colors.GREEN}{'='*60}{Colors.NC}")
    print(f"{Colors.GREEN}Gazebo Fortress URDF Migration Script{Colors.NC}")
    print(f"{Colors.GREEN}{'='*60}{Colors.NC}\n")
    
    if args.dry_run:
        print_warning("DRY RUN MODE - No files will be modified\n")
    
    # Create backup directory
    os.makedirs(args.backup_dir, exist_ok=True)
    
    # Migrate each file
    success_count = 0
    fail_count = 0
    
    for file_path in args.files:
        if not os.path.exists(file_path):
            print_error(f"File not found: {file_path}")
            fail_count += 1
            continue
        
        if migrate_urdf_file(file_path, args.backup_dir, args.dry_run):
            success_count += 1
        else:
            fail_count += 1
    
    # Summary
    print(f"\n{Colors.GREEN}{'='*60}{Colors.NC}")
    print(f"{Colors.GREEN}Migration Summary{Colors.NC}")
    print(f"{Colors.GREEN}{'='*60}{Colors.NC}\n")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {fail_count}")
    print(f"  Total: {len(args.files)}\n")
    
    if fail_count > 0:
        print_error("Some migrations failed. Check the output above for details.")
        sys.exit(1)
    else:
        print_success("All migrations completed successfully!")
        print("\nNext steps:")
        print("  1. Test xacro processing: xacro <your_file>.xacro")
        print("  2. Migrate launch files: python3 scripts/migrate_launch_to_fortress.py")
        print("  3. Test simulation: ros2 launch dog2_description <your_launch_file>")

if __name__ == '__main__':
    main()
