#!/usr/bin/env python3
"""
URDF Joint Limits Validation Script

Validates that the Dog2 robot URDF has correct joint limits:
- No continuous joints (all should be revolute or prismatic)
- Hip joints: ±2.618 rad (±150°)
- Knee joints: ±2.8 rad (±160°)
- All 8 hip/knee joints present and consistent
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple


class URDFValidator:
    """Validates URDF joint limits for Dog2 robot."""
    
    # Expected limits
    HIP_LOWER = -2.618
    HIP_UPPER = 2.618
    KNEE_LOWER = -2.8
    KNEE_UPPER = 2.8
    TOLERANCE = 0.001  # Tolerance for floating point comparison
    
    # Expected joint names
    HIP_JOINTS = ['j11', 'j21', 'j31', 'j41']
    KNEE_JOINTS = ['j111', 'j211', 'j311', 'j411']
    
    def __init__(self, urdf_path: str):
        self.urdf_path = Path(urdf_path)
        self.tree = None
        self.root = None
        self.errors = []
        self.warnings = []
        
    def load_urdf(self) -> bool:
        """Load and parse URDF file."""
        if not self.urdf_path.exists():
            self.errors.append(f"URDF file not found: {self.urdf_path}")
            return False
            
        try:
            self.tree = ET.parse(self.urdf_path)
            self.root = self.tree.getroot()
            return True
        except ET.ParseError as e:
            self.errors.append(f"Failed to parse URDF: {e}")
            return False
    
    def check_continuous_joints(self) -> bool:
        """Check that no continuous joints exist."""
        continuous_joints = []
        
        for joint in self.root.findall('.//joint'):
            joint_type = joint.get('type')
            joint_name = joint.get('name')
            
            if joint_type == 'continuous':
                continuous_joints.append(joint_name)
        
        if continuous_joints:
            self.errors.append(
                f"Found {len(continuous_joints)} continuous joint(s): {', '.join(continuous_joints)}"
            )
            self.errors.append("All hip and knee joints should be 'revolute' type")
            return False
        
        return True
    
    def get_joint_limits(self, joint_name: str) -> Tuple[float, float]:
        """Get lower and upper limits for a joint."""
        for joint in self.root.findall('.//joint'):
            if joint.get('name') == joint_name:
                limit = joint.find('limit')
                if limit is not None:
                    lower = float(limit.get('lower', 0))
                    upper = float(limit.get('upper', 0))
                    return lower, upper
        return None, None
    
    def check_joint_limits(self, joint_names: List[str], 
                          expected_lower: float, 
                          expected_upper: float,
                          joint_type: str) -> bool:
        """Check that joints have consistent limits."""
        all_ok = True
        
        for joint_name in joint_names:
            lower, upper = self.get_joint_limits(joint_name)
            
            if lower is None or upper is None:
                self.errors.append(f"{joint_type} joint '{joint_name}' not found or has no limits")
                all_ok = False
                continue
            
            # Check lower limit
            if abs(lower - expected_lower) > self.TOLERANCE:
                self.errors.append(
                    f"{joint_type} joint '{joint_name}' has incorrect lower limit: "
                    f"{lower:.4f} (expected {expected_lower:.4f})"
                )
                all_ok = False
            
            # Check upper limit
            if abs(upper - expected_upper) > self.TOLERANCE:
                self.errors.append(
                    f"{joint_type} joint '{joint_name}' has incorrect upper limit: "
                    f"{upper:.4f} (expected {expected_upper:.4f})"
                )
                all_ok = False
        
        return all_ok
    
    def check_joint_types(self) -> bool:
        """Check that hip and knee joints are revolute type."""
        all_ok = True
        
        for joint_name in self.HIP_JOINTS + self.KNEE_JOINTS:
            for joint in self.root.findall('.//joint'):
                if joint.get('name') == joint_name:
                    joint_type = joint.get('type')
                    if joint_type != 'revolute':
                        self.errors.append(
                            f"Joint '{joint_name}' has type '{joint_type}' (expected 'revolute')"
                        )
                        all_ok = False
                    break
        
        return all_ok
    
    def check_zero_in_range(self) -> bool:
        """Check that 0° is within knee joint range (critical for morphing)."""
        all_ok = True
        
        for joint_name in self.KNEE_JOINTS:
            lower, upper = self.get_joint_limits(joint_name)
            
            if lower is not None and upper is not None:
                if not (lower < 0 < upper):
                    self.errors.append(
                        f"Knee joint '{joint_name}' range [{lower:.4f}, {upper:.4f}] "
                        f"does not include 0° (singularity point)"
                    )
                    all_ok = False
        
        return all_ok
    
    def validate(self) -> bool:
        """Run all validation checks."""
        print(f"Validating URDF: {self.urdf_path}")
        print("=" * 60)
        
        if not self.load_urdf():
            return False
        
        # Run all checks
        checks = [
            ("Checking for continuous joints", self.check_continuous_joints),
            ("Checking joint types", self.check_joint_types),
            ("Checking hip joint limits", 
             lambda: self.check_joint_limits(self.HIP_JOINTS, self.HIP_LOWER, self.HIP_UPPER, "Hip")),
            ("Checking knee joint limits",
             lambda: self.check_joint_limits(self.KNEE_JOINTS, self.KNEE_LOWER, self.KNEE_UPPER, "Knee")),
            ("Checking knee range includes 0°", self.check_zero_in_range),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            print(f"\n{check_name}...")
            if check_func():
                print(f"  ✓ PASS")
            else:
                print(f"  ✗ FAIL")
                all_passed = False
        
        # Print summary
        print("\n" + "=" * 60)
        if all_passed:
            print("✓ ALL CHECKS PASSED")
            print(f"\nValidated joints:")
            print(f"  - Hip joints (4): {', '.join(self.HIP_JOINTS)}")
            print(f"    Limits: [{self.HIP_LOWER}, {self.HIP_UPPER}] rad (±150°)")
            print(f"  - Knee joints (4): {', '.join(self.KNEE_JOINTS)}")
            print(f"    Limits: [{self.KNEE_LOWER}, {self.KNEE_UPPER}] rad (±160°)")
        else:
            print("✗ VALIDATION FAILED")
            print(f"\nErrors found: {len(self.errors)}")
            for error in self.errors:
                print(f"  - {error}")
        
        return all_passed


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 validate_urdf_limits.py <path_to_urdf>")
        print("Example: python3 scripts/validate_urdf_limits.py src/dog2_description/urdf/dog2.urdf")
        sys.exit(1)
    
    urdf_path = sys.argv[1]
    validator = URDFValidator(urdf_path)
    
    if validator.validate():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
