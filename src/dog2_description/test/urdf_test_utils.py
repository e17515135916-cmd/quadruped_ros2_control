"""Shared utilities for dog2_description property-based tests."""

import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).parent.parent.parent.parent
SOURCE_XACRO = Path(__file__).parent.parent / "urdf" / "dog2.urdf.xacro"
INSTALL_XACRO = (
    WORKSPACE_ROOT
    / "install"
    / "dog2_description"
    / "share"
    / "dog2_description"
    / "urdf"
    / "dog2.urdf.xacro"
)
SOURCE_CONTROLLERS_YAML = (
    WORKSPACE_ROOT
    / "src"
    / "dog2_description"
    / "config"
    / "ros2_controllers.yaml"
)
INSTALL_CONTROLLERS_YAML = (
    WORKSPACE_ROOT
    / "install"
    / "dog2_description"
    / "share"
    / "dog2_description"
    / "config"
    / "ros2_controllers.yaml"
)


def generate_urdf_from_xacro():
    """Generate URDF from xacro, explicitly passing controllers_yaml."""
    xacro_path = None
    if SOURCE_XACRO.exists():
        xacro_path = SOURCE_XACRO
    elif INSTALL_XACRO.exists():
        xacro_path = INSTALL_XACRO

    if xacro_path is None:
        raise RuntimeError(
            f"Could not find dog2.urdf.xacro in {SOURCE_XACRO} or {INSTALL_XACRO}"
        )

    controllers_yaml = None
    if SOURCE_CONTROLLERS_YAML.exists():
        controllers_yaml = SOURCE_CONTROLLERS_YAML
    elif INSTALL_CONTROLLERS_YAML.exists():
        controllers_yaml = INSTALL_CONTROLLERS_YAML

    cmd = ["xacro", str(xacro_path)]
    if controllers_yaml is not None:
        cmd.append(f"controllers_yaml:={controllers_yaml}")

    env = os.environ.copy()
    install_path = WORKSPACE_ROOT / "install"
    if install_path.exists():
        existing = env.get("AMENT_PREFIX_PATH", "")
        env["AMENT_PREFIX_PATH"] = (
            f"{install_path}:{existing}" if existing else str(install_path)
        )

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, env=env
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to generate URDF from xacro: {e.stderr}")


def parse_urdf(urdf_content):
    """Parse URDF XML content and return the root element."""
    return ET.fromstring(urdf_content)


def resolve_package_uri(uri, package_dir_hint=None):
    """Resolve a package:// URI to a local file path.

    Supports package://dog2_description/... by looking in source tree first,
    then install space.  Returns None if the file cannot be resolved.
    """
    if not uri.startswith("package://"):
        return None
    rest = uri[len("package://"):]
    pkg, _, rel = rest.partition("/")
    for base in [
        WORKSPACE_ROOT / "src" / pkg,
        WORKSPACE_ROOT / "install" / pkg / "share" / pkg,
    ]:
        candidate = base / rel
        if candidate.exists():
            return candidate
    if package_dir_hint is not None:
        candidate = Path(package_dir_hint) / rel
        if candidate.exists():
            return candidate
    return None
