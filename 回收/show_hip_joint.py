#!/usr/bin/env python3
with open('src/dog2_description/urdf/dog2.urdf.xacro') as f:
    lines = f.readlines()

# Find hip joint definition
for i, line in enumerate(lines):
    if 'Hip joint (j${leg_num}1)' in line:
        print(f"Found at line {i+1}")
        print("".join(lines[i:i+10]))
        break
