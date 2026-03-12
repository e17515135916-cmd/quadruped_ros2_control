# URDF Backup - Collision Mesh Fixes

## Backup Information

- **Date**: 2026-01-29 14:23:24
- **Purpose**: Pre-collision mesh fixes backup
- **Spec**: gazebo-collision-mesh-fixes

## Backed Up Files

- `dog2.urdf.backup_20260129_142324.xacro` - XACRO file
- `dog2.backup_20260129_142324.urdf` - URDF file

## Original Locations

- Xacro: `src/dog2_description/urdf/dog2.urdf.xacro`
- URDF: `src/dog2_description/urdf/dog2.urdf`

## Restoration

To restore these files:

```bash
cp urdf_collision_fixes_20260129_142324/dog2.urdf.xacro.backup_20260129_142324 src/dog2_description/urdf/dog2.urdf.xacro
cp urdf_collision_fixes_20260129_142324/dog2.urdf.backup_20260129_142324 src/dog2_description/urdf/dog2.urdf
```

Or use the restoration script:

```bash
python scripts/restore_urdf_from_backup.py urdf_collision_fixes_20260129_142324
```

## Changes Applied After This Backup

This backup was created before applying collision mesh fixes:
1. Replace STL mesh collision geometry with primitives (cylinders/boxes)
2. Truncate shin collision bodies to prevent foot overlap
3. Configure collision filtering for adjacent links
4. Adjust contact parameters for stability
