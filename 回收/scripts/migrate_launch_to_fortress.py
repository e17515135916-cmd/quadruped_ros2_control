#!/usr/bin/env python3
"""
Launch File Migration Script for Gazebo Fortress
Migrates ROS 2 launch files from Gazebo Classic to Gazebo Fortress (gz-sim)
"""

import os
import sys
import shutil
import argparse
import re
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
    backup_path = os.path.join(backup_dir, f"gazebo_fortress_launch_migration_{timestamp}")
    os.makedirs(backup_path, exist_ok=True)
    
    # Copy file to backup
    file_name = os.path.basename(file_path)
    backup_file = os.path.join(backup_path, f"{file_name}.backup")
    shutil.copy2(file_path, backup_file)
    
    # Create README
    readme_path = os.path.join(backup_path, "README.md")
    with open(readme_path, 'w') as f:
        f.write(f"# Gazebo Fortress Launch Migration Backup\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Original File**: {file_path}\n\n")
        f.write(f"**Backup File**: {backup_file}\n\n")
        f.write(f"## Rollback Instructions\n\n")
        f.write(f"To restore the original file:\n\n")
        f.write(f"```bash\n")
        f.write(f"cp {backup_file} {file_path}\n")
        f.write(f"```\n")
    
    return backup_file

def migrate_imports(content):
    """Migrate import statements from gazebo_ros to ros_gz_sim"""
    replacements = [
        # Package imports
        ('from gazebo_ros', 'from ros_gz_sim'),
        ("'gazebo_ros'", "'ros_gz_sim'"),
        ('"gazebo_ros"', '"ros_gz_sim"'),
        # get_package_share_directory calls
        ("get_package_share_directory('gazebo_ros')", "get_package_share_directory('ros_gz_sim')"),
        ('get_package_share_directory("gazebo_ros")', 'get_package_share_directory("ros_gz_sim")'),
    ]
    
    modified = content
    changes_made = []
    
    for old, new in replacements:
        if old in modified:
            count = modified.count(old)
            modified = modified.replace(old, new)
            changes_made.append(f"  - {old} → {new} ({count} occurrence(s))")
    
    return modified, changes_made

def migrate_launch_files(content):
    """Migrate launch file references"""
    replacements = [
        # Launch file references
        ("'gazebo.launch.py'", "'gz_sim.launch.py'"),
        ('"gazebo.launch.py"', '"gz_sim.launch.py"'),
        ("'gzserver.launch.py'", "'gz_sim.launch.py'"),
        ('"gzserver.launch.py"', '"gz_sim.launch.py"'),
        ("'gzclient.launch.py'", "'gz_sim.launch.py'"),
        ('"gzclient.launch.py"', '"gz_sim.launch.py"'),
    ]
    
    modified = content
    changes_made = []
    
    for old, new in replacements:
        if old in modified:
            count = modified.count(old)
            modified = modified.replace(old, new)
            changes_made.append(f"  - {old} → {new} ({count} occurrence(s))")
    
    return modified, changes_made

def migrate_spawn_entity(content):
    """Migrate spawn_entity node from gazebo_ros to ros_gz_sim"""
    changes_made = []
    
    # Replace package name in spawn_entity nodes
    if "package='gazebo_ros'" in content or 'package="gazebo_ros"' in content:
        content = content.replace("package='gazebo_ros'", "package='ros_gz_sim'")
        content = content.replace('package="gazebo_ros"', 'package="ros_gz_sim"')
        changes_made.append("  - spawn_entity package: gazebo_ros → ros_gz_sim")
    
    # Replace executable (spawn_entity.py → create)
    if 'spawn_entity.py' in content:
        content = content.replace("'spawn_entity.py'", "'create'")
        content = content.replace('"spawn_entity.py"', '"create"')
        changes_made.append("  - spawn_entity executable: spawn_entity.py → create")
    
    # Update arguments format
    # Gazebo Fortress uses -name instead of -entity
    if "'-entity'" in content or '"-entity"' in content:
        content = content.replace("'-entity'", "'-name'")
        content = content.replace('"-entity"', '"-name"')
        changes_made.append("  - spawn argument: -entity → -name")
    
    return content, changes_made

def migrate_environment_variables(content):
    """Update environment variable names"""
    changes_made = []
    
    # GAZEBO_MODEL_PATH → GZ_SIM_RESOURCE_PATH
    if 'GAZEBO_MODEL_PATH' in content:
        content = content.replace('GAZEBO_MODEL_PATH', 'GZ_SIM_RESOURCE_PATH')
        changes_made.append("  - Environment variable: GAZEBO_MODEL_PATH → GZ_SIM_RESOURCE_PATH")
    
    return content, changes_made

def validate_python_syntax(file_path):
    """Validate Python syntax"""
    try:
        with open(file_path, 'r') as f:
            compile(f.read(), file_path, 'exec')
        return True, "Python syntax valid"
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def migrate_launch_file(file_path, backup_dir, dry_run=False):
    """Migrate a single launch file"""
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
    
    # Perform migrations
    migrated_content = original_content
    all_changes = []
    
    # 1. Migrate imports
    migrated_content, changes = migrate_imports(migrated_content)
    all_changes.extend(changes)
    
    # 2. Migrate launch file references
    migrated_content, changes = migrate_launch_files(migrated_content)
    all_changes.extend(changes)
    
    # 3. Migrate spawn_entity
    migrated_content, changes = migrate_spawn_entity(migrated_content)
    all_changes.extend(changes)
    
    # 4. Migrate environment variables
    migrated_content, changes = migrate_environment_variables(migrated_content)
    all_changes.extend(changes)
    
    if not all_changes:
        print_warning("No changes needed - file may already be migrated or doesn't use Gazebo")
        return True
    
    print("\nChanges made:")
    for change in all_changes:
        print(change)
    
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
    
    # Validate Python syntax
    print("\nValidating Python syntax...")
    if not dry_run:
        valid, message = validate_python_syntax(file_path)
        if valid:
            print_success(message)
        else:
            print_error(message)
            return False
    else:
        print_warning("Dry run: Skipping syntax validation")
    
    print_success("Migration completed successfully!")
    return True

def main():
    parser = argparse.ArgumentParser(
        description='Migrate launch files from Gazebo Classic to Gazebo Fortress'
    )
    parser.add_argument(
        'files',
        nargs='+',
        help='Launch files to migrate'
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
    print(f"{Colors.GREEN}Gazebo Fortress Launch File Migration Script{Colors.NC}")
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
        
        if not file_path.endswith('.launch.py'):
            print_warning(f"Skipping non-launch file: {file_path}")
            continue
        
        if migrate_launch_file(file_path, args.backup_dir, args.dry_run):
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
        print("  1. Review migrated launch files")
        print("  2. Test launch files: ros2 launch dog2_description <your_launch_file>")
        print("  3. Verify simulation starts correctly")

if __name__ == '__main__':
    main()
