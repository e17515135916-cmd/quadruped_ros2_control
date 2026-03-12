Hip Bracket Redesign Backup
============================

Date: 2026-02-07 10:23:58

This backup contains the original mesh files and URDF configuration
before implementing the hip bracket mechanical redesign.

Contents:
---------
- meshes/l11.STL, l21.STL, l31.STL, l41.STL (visual meshes)
- meshes/collision/l*_collision.STL (collision meshes)
- urdf/dog2.urdf.xacro (URDF configuration)
- BACKUP_INFO.md (detailed documentation)

To restore:
-----------
See BACKUP_INFO.md for detailed restoration instructions.

Quick restore:
cp meshes/*.STL ../../src/dog2_description/meshes/
cp meshes/collision/*.STL ../../src/dog2_description/meshes/collision/
cp urdf/dog2.urdf.xacro ../../src/dog2_description/urdf/
