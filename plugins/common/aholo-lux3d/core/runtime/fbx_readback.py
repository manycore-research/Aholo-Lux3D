"""Read an FBX with Blender's importer; invoked only in Blender background mode."""

import json
import math
import pathlib
import sys

if __name__ == "__main__":
    import bpy

    source, report = sys.argv[sys.argv.index("--") + 1:]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    imported = bpy.ops.import_scene.fbx(filepath=source, use_anim=True, use_image_search=False)
    if imported != {"FINISHED"}:
        raise ValueError("FBX importer did not finish")
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH" and len(obj.data.vertices) and len(obj.data.polygons)]
    armatures = [obj for obj in bpy.data.objects if obj.type == "ARMATURE" and len(obj.data.bones)]
    skinned_meshes = 0
    for mesh in meshes:
        bound = [modifier.object for modifier in mesh.modifiers
                 if modifier.type == "ARMATURE" and modifier.object in armatures]
        if not bound:
            continue
        bones = {bone.name for armature in bound for bone in armature.data.bones if bone.use_deform}
        groups = {group.index for group in mesh.vertex_groups if group.name in bones}
        if not groups or any(
            not any(group.group in groups and math.isfinite(group.weight) and group.weight > 0
                    for group in vertex.groups) for vertex in mesh.data.vertices
        ):
            raise ValueError("FBX skinned mesh contains vertices without readable bone weights")
        skinned_meshes += 1
    bone_paths = {bone.path_from_id() for armature in armatures for bone in armature.pose.bones}
    clips = []
    for action in bpy.data.actions:
        if bpy.app.version >= (4, 4, 0):
            curves = [curve for layer in action.layers for strip in layer.strips
                      if strip.type == "KEYFRAME" for bag in strip.channelbags for curve in bag.fcurves]
        else:
            curves = list(action.fcurves)
        bone_curves = [curve for curve in curves
                       if curve.keyframe_points and any(curve.data_path.startswith(path + ".") for path in bone_paths)]
        if bone_curves:
            if any(not math.isfinite(value) for curve in bone_curves for point in curve.keyframe_points for value in point.co):
                raise ValueError("FBX animation has non-finite keyframe data")
            clips.append(action.name)
    details = {
        "reader": "Blender", "readerVersion": bpy.app.version_string,
        "meshes": len(meshes), "skins": skinned_meshes,
        "joints": sum(len(armature.data.bones) for armature in armatures),
        "rigValidated": bool(skinned_meshes), "animationClips": clips,
        "animationValidated": bool(clips),
    }
    pathlib.Path(report).write_text(json.dumps(details, ensure_ascii=False), encoding="utf-8")
