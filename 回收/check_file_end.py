#!/usr/bin/env python3
with open('src/dog2_description/urdf/dog2.urdf.xacro') as f:
    lines = f.readlines()

print(f'Total lines: {len(lines)}')
print('\nLines 330-343:')
for i, line in enumerate(lines[329:343], start=330):
    print(f'{i}: {line}', end='')
