#!/usr/bin/env python3
with open('src/dog2_description/urdf/dog2.urdf.xacro') as f:
    lines = f.readlines()

# Find macro definition
for i, line in enumerate(lines):
    if '<xacro:macro name="leg"' in line:
        print(f"Found macro at line {i+1}")
        # Print next 15 lines
        for j in range(15):
            if i+j < len(lines):
                print(f"{i+j+1}: {lines[i+j]}", end='')
        break
