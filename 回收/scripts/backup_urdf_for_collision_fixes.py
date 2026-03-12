#!/usr/bin/env python3
"""
Backup URDF files before collision mesh fixes

This script creates timestamped backups of the current URDF files
before applying collision mesh modifications.

Requirements: 10.1
"""

import os
import shutil
from datetime import datetime
from pathlib import Path


def backup_urdf_files():
    """
    Create timestamped backups of URDF files
    
    Returns:
        dict: Paths to backed up files
    """
    # Get timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Define source files
    workspace_root = Path(__file__).parent.parent
    urdf_dir = workspace_root / "src" / "dog2_description" / "urdf"
    
    source_files = {
        'xacro': urdf_dir / "dog2.urdf.xacro",
        'urdf': urdf_dir / "dog2.urdf"
    }
    
    # Create backup directory
    backup_dir = workspace_root / "backups" / f"urdf_collision_fixes_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Backup files
    backed_up_files = {}
    for file_type, source_path in source_files.items():
        if source_path.exists():
            # Create backup filename with timestamp
            backup_filename = f"{source_path.stem}.backup_{timestamp}{source_path.suffix}"
            backup_path = backup_dir / backup_filename
            
            # Copy file
            shutil.copy2(source_path, backup_path)
            backed_up_files[file_type] = backup_path
            print(f"✓ Backed up {source_path.name} to {backup_path}")
        else:
            print(f"⚠ Warning: {source_path} not found, skipping")
    
    # Create README
    readme_path = backup_dir / "README.md"
    readme_content = f"""# URDF Backup - Collision Mesh Fixes

## Backup Information

- **Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Purpose**: Pre-collision mesh fixes backup
- **Spec**: gazebo-collision-mesh-fixes

## Backed Up Files

"""
    
    for file_type, backup_path in backed_up_files.items():
        readme_content += f"- `{backup_path.name}` - {file_type.upper()} file\n"
    
    readme_content += f"""
## Original Locations

- Xacro: `src/dog2_description/urdf/dog2.urdf.xacro`
- URDF: `src/dog2_description/urdf/dog2.urdf`

## Restoration

To restore these files:

```bash
cp {backup_dir.name}/dog2.urdf.xacro.backup_{timestamp} src/dog2_description/urdf/dog2.urdf.xacro
cp {backup_dir.name}/dog2.urdf.backup_{timestamp} src/dog2_description/urdf/dog2.urdf
```

Or use the restoration script:

```bash
python scripts/restore_urdf_from_backup.py {backup_dir.name}
```

## Changes Applied After This Backup

This backup was created before applying collision mesh fixes:
1. Replace STL mesh collision geometry with primitives (cylinders/boxes)
2. Truncate shin collision bodies to prevent foot overlap
3. Configure collision filtering for adjacent links
4. Adjust contact parameters for stability
"""
    
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"\n✓ Created README at {readme_path}")
    print(f"\n{'='*60}")
    print(f"Backup completed successfully!")
    print(f"Backup directory: {backup_dir}")
    print(f"{'='*60}\n")
    
    return {
        'backup_dir': str(backup_dir),
        'files': {k: str(v) for k, v in backed_up_files.items()},
        'timestamp': timestamp
    }


if __name__ == "__main__":
    result = backup_urdf_files()
    
    # Print summary
    print("Backup Summary:")
    print(f"  Directory: {result['backup_dir']}")
    print(f"  Timestamp: {result['timestamp']}")
    print(f"  Files backed up: {len(result['files'])}")
    for file_type, path in result['files'].items():
        print(f"    - {file_type}: {Path(path).name}")
