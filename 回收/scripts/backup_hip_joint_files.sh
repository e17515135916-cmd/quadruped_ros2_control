#!/bin/bash
# Backup script for hip joint axis change
# This script backs up all files that will be modified during the hip joint axis change
# Date: $(date +%Y-%m-%d)

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Timestamp for backup directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/hip_joint_axis_change_${TIMESTAMP}"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Hip Joint Axis Change - Backup Script${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo "Backup directory: ${BACKUP_DIR}"
echo ""

# Create backup directory
echo -e "${YELLOW}Creating backup directory...${NC}"
mkdir -p "${BACKUP_DIR}/urdf"
mkdir -p "${BACKUP_DIR}/meshes/visual"
mkdir -p "${BACKUP_DIR}/meshes/collision"
mkdir -p "${BACKUP_DIR}/kinematics"
echo -e "${GREEN}✓ Backup directory created${NC}"
echo ""

# Backup URDF file
echo -e "${YELLOW}Backing up URDF file...${NC}"
if [ -f "src/dog2_description/urdf/dog2.urdf.xacro" ]; then
    cp "src/dog2_description/urdf/dog2.urdf.xacro" "${BACKUP_DIR}/urdf/dog2.urdf.xacro"
    echo -e "${GREEN}✓ URDF backed up: dog2.urdf.xacro${NC}"
else
    echo -e "${RED}✗ URDF file not found!${NC}"
    exit 1
fi
echo ""

# Backup hip link visual mesh files (l11.STL, l21.STL, l31.STL, l41.STL)
echo -e "${YELLOW}Backing up hip link visual meshes...${NC}"
VISUAL_MESHES=("l11.STL" "l21.STL" "l31.STL" "l41.STL")
for mesh in "${VISUAL_MESHES[@]}"; do
    if [ -f "src/dog2_description/meshes/${mesh}" ]; then
        cp "src/dog2_description/meshes/${mesh}" "${BACKUP_DIR}/meshes/visual/${mesh}"
        echo -e "${GREEN}✓ Visual mesh backed up: ${mesh}${NC}"
    else
        echo -e "${RED}✗ Visual mesh not found: ${mesh}${NC}"
        exit 1
    fi
done
echo ""

# Backup hip link collision mesh files
echo -e "${YELLOW}Backing up hip link collision meshes...${NC}"
COLLISION_MESHES=("l11_collision.STL" "l21_collision.STL" "l31_collision.STL" "l41_collision.STL")
for mesh in "${COLLISION_MESHES[@]}"; do
    if [ -f "src/dog2_description/meshes/collision/${mesh}" ]; then
        cp "src/dog2_description/meshes/collision/${mesh}" "${BACKUP_DIR}/meshes/collision/${mesh}"
        echo -e "${GREEN}✓ Collision mesh backed up: ${mesh}${NC}"
    else
        echo -e "${RED}✗ Collision mesh not found: ${mesh}${NC}"
        exit 1
    fi
done
echo ""

# Backup kinematics solver files
echo -e "${YELLOW}Backing up kinematics solver files...${NC}"
KINEMATICS_FILES=(
    "src/dog2_kinematics/dog2_kinematics/leg_ik_4dof.py"
    "src/dog2_kinematics/src/leg_ik_4dof.cpp"
    "src/dog2_kinematics/include/dog2_kinematics/leg_ik_4dof.hpp"
)
for file in "${KINEMATICS_FILES[@]}"; do
    if [ -f "${file}" ]; then
        # Preserve directory structure
        file_dir=$(dirname "${file}")
        file_name=$(basename "${file}")
        mkdir -p "${BACKUP_DIR}/kinematics/$(basename ${file_dir})"
        cp "${file}" "${BACKUP_DIR}/kinematics/$(basename ${file_dir})/${file_name}"
        echo -e "${GREEN}✓ Kinematics file backed up: ${file}${NC}"
    else
        echo -e "${YELLOW}⚠ Kinematics file not found (may not exist yet): ${file}${NC}"
    fi
done
echo ""

# Create backup manifest
echo -e "${YELLOW}Creating backup manifest...${NC}"
cat > "${BACKUP_DIR}/BACKUP_MANIFEST.txt" << EOF
Hip Joint Axis Change - Backup Manifest
========================================
Backup Date: $(date)
Backup Directory: ${BACKUP_DIR}

Files Backed Up:
----------------

URDF:
- dog2.urdf.xacro

Visual Meshes:
- l11.STL
- l21.STL
- l31.STL
- l41.STL

Collision Meshes:
- l11_collision.STL
- l21_collision.STL
- l31_collision.STL
- l41_collision.STL

Kinematics Solvers:
- leg_ik_4dof.py
- leg_ik_4dof.cpp
- leg_ik_4dof.hpp

Purpose:
--------
This backup was created before changing the hip joint rotation axes
(j11, j21, j31, j41) from z-axis to x-axis rotation.

Restoration:
------------
To restore from this backup, run:
  ./scripts/restore_hip_joint_files.sh ${BACKUP_DIR}

Or manually copy files back from the backup directory.
EOF
echo -e "${GREEN}✓ Backup manifest created${NC}"
echo ""

# Verify all backups
echo -e "${YELLOW}Verifying backups...${NC}"
BACKUP_COUNT=$(find "${BACKUP_DIR}" -type f -name "*.STL" -o -name "*.xacro" -o -name "*.py" -o -name "*.cpp" -o -name "*.hpp" | wc -l)
echo "Total files backed up: ${BACKUP_COUNT}"

if [ ${BACKUP_COUNT} -ge 9 ]; then
    echo -e "${GREEN}✓ All critical files backed up successfully${NC}"
else
    echo -e "${RED}✗ Warning: Expected at least 9 files, found ${BACKUP_COUNT}${NC}"
    exit 1
fi
echo ""

# Create symlink to latest backup
echo -e "${YELLOW}Creating symlink to latest backup...${NC}"
rm -f "backups/hip_joint_axis_change_latest"
ln -s "$(basename ${BACKUP_DIR})" "backups/hip_joint_axis_change_latest"
echo -e "${GREEN}✓ Symlink created: backups/hip_joint_axis_change_latest${NC}"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Backup completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Backup location: ${BACKUP_DIR}"
echo "Manifest: ${BACKUP_DIR}/BACKUP_MANIFEST.txt"
echo ""
echo "To restore from this backup, run:"
echo "  ./scripts/restore_hip_joint_files.sh ${BACKUP_DIR}"
echo ""
