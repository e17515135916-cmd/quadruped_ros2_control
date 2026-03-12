#!/usr/bin/env python3
with open('src/dog2_description/urdf/dog2.urdf.xacro') as f:
    lines = f.readlines()

for i in [173, 206, 239]:  # Lines 174, 207, 240 (0-indexed: 173, 206, 239)
    print(f"\n--- Line {i+1} ---")
    # Print context (5 lines before and after)
    for j in range(max(0, i-5), min(len(lines), i+6)):
        marker = ">>>" if j == i else "   "
        print(f"{marker} {j+1}: {lines[j]}", end='')
