# Hip Axis Modifier Script

## Overview

This script modifies the `hip_axis` parameter in the Dog2 robot's URDF Xacro file, changing the hip joint rotation axis from z-axis (`0 0 -1`) to x-axis (`1 0 0`).

## Files

- `fix_hip_axis.py` - Main script for modifying hip_axis parameters
- `tests/test_hip_axis_modifier_unit.py` - Unit tests for the script

## Requirements

- Python 3.x
- lxml library (`pip install lxml`)
- pytest (for running tests)

## Usage

### Basic Usage

Run the script with default path:

```bash
python3 fix_hip_axis.py
```

This will modify `src/dog2_description/urdf/dog2.urdf.xacro` by default.

### Custom Path

Specify a custom xacro file path:

```bash
python3 fix_hip_axis.py /path/to/your/file.xacro
```

### What the Script Does

1. **Reads and parses** the xacro file using lxml
2. **Finds** all four leg instantiations (leg_num 1, 2, 3, 4)
3. **Modifies** the `hip_axis` parameter from `"0 0 -1"` to `"1 0 0"`
4. **Creates a backup** with timestamp (e.g., `dog2.urdf.xacro.backup_20260207_140855`)
5. **Writes** the modified content back to the original file
6. **Preserves** file permissions and formatting

## Running Tests

Run all unit tests:

```bash
python3 -m pytest tests/test_hip_axis_modifier_unit.py -v
```

Run specific test:

```bash
python3 -m pytest tests/test_hip_axis_modifier_unit.py::TestHipAxisModifier::test_file_reading -v
```

## Test Coverage

The unit tests cover:

1. File reading and parsing
2. Error handling for non-existent files
3. Finding leg instantiations
4. Parameter location
5. Parameter replacement
6. Backup creation
7. File writing
8. Permission preservation
9. Missing parameter handling
10. End-to-end workflow

## Features

- **Automatic backup**: Creates timestamped backup before modification
- **Safe operation**: Validates file exists before modification
- **Preserves formatting**: Uses lxml to maintain XML structure
- **Preserves permissions**: Restores original file permissions after writing
- **Handles missing parameters**: Adds hip_axis parameter if it doesn't exist
- **Comprehensive logging**: Prints detailed progress and results

## Example Output

```
============================================================
Hip Axis Modifier Script
============================================================
Target file: src/dog2_description/urdf/dog2.urdf.xacro

Step 1: Reading and parsing xacro file...
Successfully parsed: src/dog2_description/urdf/dog2.urdf.xacro

Step 2: Finding leg instantiations...
Found leg instantiation: leg_num=1
Found leg instantiation: leg_num=2
Found leg instantiation: leg_num=3
Found leg instantiation: leg_num=4

Step 3: Modifying hip_axis parameters...
Leg 1: Changed hip_axis from "0 0 -1" to "1 0 0"
Leg 2: Changed hip_axis from "0 0 -1" to "1 0 0"
Leg 3: Changed hip_axis from "0 0 -1" to "1 0 0"
Leg 4: Changed hip_axis from "0 0 -1" to "1 0 0"

Step 4: Writing modified file...
Backup created: src/dog2_description/urdf/dog2.urdf.xacro.backup_20260207_140855
Successfully wrote modified file: src/dog2_description/urdf/dog2.urdf.xacro

============================================================
Modification Summary:
============================================================
Leg 1: modified
  Old value: 0 0 -1
  New value: 1 0 0
Leg 2: modified
  Old value: 0 0 -1
  New value: 1 0 0
Leg 3: modified
  Old value: 0 0 -1
  New value: 1 0 0
Leg 4: modified
  Old value: 0 0 -1
  New value: 1 0 0

Hip axis modification completed successfully!
```

## Requirements Validation

This script satisfies the following requirements:

- **Requirement 5.1**: Only modifies the `hip_axis` parameter in leg macro instantiations
- **Requirement 5.2**: Changes `hip_axis` from "0 0 -1" to "1 0 0" for all four legs
- **Requirement 5.3**: Creates backup before modification
- **Requirement 5.4**: Maintains existing leg macro structure
- **Requirements 1.1-1.4**: Ensures all four hip joints (j11, j21, j31, j41) have axis "1 0 0"

## Troubleshooting

### File Not Found Error

If you see "Error: File not found", verify the path to your xacro file:

```bash
ls -la src/dog2_description/urdf/dog2.urdf.xacro
```

### Permission Denied Error

If you get a permission error, ensure you have write access to the file:

```bash
chmod u+w src/dog2_description/urdf/dog2.urdf.xacro
```

### Parsing Error

If the XML parsing fails, verify the xacro file is valid XML:

```bash
xmllint --noout src/dog2_description/urdf/dog2.urdf.xacro
```

## Rollback

To restore from backup:

```bash
# Find the backup file
ls -lt src/dog2_description/urdf/dog2.urdf.xacro.backup_*

# Restore from backup
cp src/dog2_description/urdf/dog2.urdf.xacro.backup_YYYYMMDD_HHMMSS src/dog2_description/urdf/dog2.urdf.xacro
```
