#!/usr/bin/env python3
"""
Run with Blender:
  blender --background --python src/dog2_description/scripts/batch_rebase_mesh_and_zero_origins.py -- \
    --workspace /home/dell/aperfect/carbot_ws \
    --shift 0.9780 -0.87203 0.2649 \
    --backup-dir /home/dell/aperfect/carbot_ws/src/dog2_description/meshes_backup_rebase \
    --apply-xacro

What it does:
  1) Parse dog2.urdf.xacro and collect all mesh files referenced as:
       package://dog2_description/meshes/*.stl
       package://dog2_description/meshes/collision/*.stl
  2) Backup those STL files
  3) Rebase every referenced STL by translating all vertices by --shift
  4) (optional) Set all <visual>/<collision> origins in xacro to 0 0 0
"""

import argparse
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET


def _parse_args():
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1 :]
    else:
        argv = []
    p = argparse.ArgumentParser()
    p.add_argument("--workspace", required=True)
    p.add_argument("--shift", nargs=3, type=float, required=True, metavar=("X", "Y", "Z"))
    p.add_argument("--backup-dir", required=True)
    p.add_argument("--xacro", default="src/dog2_description/urdf/dog2.urdf.xacro")
    p.add_argument("--apply-xacro", action="store_true")
    return p.parse_args(argv)


def _collect_mesh_paths(xacro_path, workspace):
    # Xacro contains templated paths such as l${leg_num}.STL.
    # For full-batch rebasing, scan the actual meshes directory instead.
    meshes_root = os.path.join(workspace, "src/dog2_description/meshes")
    abs_paths = []
    for root, _, files in os.walk(meshes_root):
        for name in files:
            if name.lower().endswith(".stl"):
                abs_paths.append(os.path.join(root, name))
    abs_paths.sort()
    print(f"[INFO] Found {len(abs_paths)} STL files under meshes/")
    return abs_paths


def _backup_files(files, workspace, backup_dir):
    os.makedirs(backup_dir, exist_ok=True)
    for src in files:
        rel = os.path.relpath(src, workspace)
        dst = os.path.join(backup_dir, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    print(f"[INFO] Backed up {len(files)} mesh files to: {backup_dir}")


def _rebase_stl_with_blender(file_path, shift):
    import bpy  # type: ignore

    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Blender STL operators vary by version:
    # - 3.x commonly uses import_mesh.stl / export_mesh.stl
    # - newer versions may expose wm.stl_import / wm.stl_export
    imported = False
    try:
        bpy.ops.wm.stl_import(filepath=file_path)
        imported = True
    except Exception:
        pass
    if not imported:
        bpy.ops.import_mesh.stl(filepath=file_path)

    mesh_objs = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not mesh_objs:
        print(f"[WARN] No mesh object imported: {file_path}")
        return

    sx, sy, sz = shift
    for obj in mesh_objs:
        mesh = obj.data
        for v in mesh.vertices:
            v.co.x += sx
            v.co.y += sy
            v.co.z += sz
        mesh.update()

    bpy.ops.object.select_all(action="DESELECT")
    for obj in mesh_objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_objs[0]
    exported = False
    try:
        bpy.ops.wm.stl_export(
            filepath=file_path,
            export_selected_objects=True,
            ascii_format=False,
        )
        exported = True
    except Exception:
        pass
    if not exported:
        bpy.ops.export_mesh.stl(
            filepath=file_path,
            use_selection=True,
            ascii=False,
        )
    print(f"[OK] Rebased: {file_path}")


def _zero_visual_collision_origins(xacro_path):
    tree = ET.parse(xacro_path)
    root = tree.getroot()

    # xacro files may contain xacro namespace tags, but visual/collision/origin
    # are plain URDF tags in this file.
    changed = 0
    for link in root.findall("link"):
        for tag in ("visual", "collision"):
            node = link.find(tag)
            if node is None:
                continue
            origin = node.find("origin")
            if origin is None:
                origin = ET.SubElement(node, "origin")
            old_xyz = origin.attrib.get("xyz")
            old_rpy = origin.attrib.get("rpy")
            if old_xyz != "0 0 0" or old_rpy != "0 0 0":
                origin.set("xyz", "0 0 0")
                origin.set("rpy", "0 0 0")
                changed += 1

    tree.write(xacro_path, encoding="utf-8", xml_declaration=True)
    print(f"[INFO] Updated visual/collision origins: {changed}")


def main():
    args = _parse_args()
    workspace = os.path.abspath(args.workspace)
    xacro_path = os.path.join(workspace, args.xacro)
    backup_dir = os.path.abspath(args.backup_dir)
    shift = tuple(args.shift)

    if not os.path.exists(xacro_path):
        raise FileNotFoundError(f"xacro not found: {xacro_path}")

    mesh_files = _collect_mesh_paths(xacro_path, workspace)
    if not mesh_files:
        raise RuntimeError("No mesh files found from xacro references.")

    _backup_files(mesh_files, workspace, backup_dir)

    for p in mesh_files:
        _rebase_stl_with_blender(p, shift)

    if args.apply_xacro:
        _zero_visual_collision_origins(xacro_path)

    print("[DONE] Batch rebase finished.")


if __name__ == "__main__":
    main()
