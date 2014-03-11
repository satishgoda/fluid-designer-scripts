# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.types import Header, Menu, Operator

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       BoolVectorProperty,
                       PointerProperty,
                       EnumProperty)

class OPS_clear_all_materials_from_file(Operator):
    bl_idname = "fd_material.clear_all_materials_from_file"
    bl_label = "Clear All Materials From File"
    bl_options = {'UNDO'}
    
    def execute(self,context):
        for obj in bpy.data.objects:
            for slot in obj.material_slots:
                slot.material = None
        
        for mat in bpy.data.materials:
            mat.user_clear()
            bpy.data.materials.remove(mat)
            
        for image in bpy.data.images:
            image.user_clear()
            bpy.data.images.remove(image)
        return{'FINISHED'}

class OPS_clear_unused_materials_from_file(Operator):
    bl_idname = "fd_material.clear_unused_materials_from_file"
    bl_label = "Clear Unused Materials From File"
    bl_options = {'UNDO'}
    
    def execute(self,context):
        for mat in bpy.data.materials:
            if mat.users == 0:
                bpy.data.materials.remove(mat)
        return{'FINISHED'}

class OPS_apply_materials_from_pointers(Operator):
    bl_idname = "fd_material.apply_materials_from_pointers"
    bl_label = "Apply Materials From Pointers"
    bl_options = {'UNDO'}
    
    def execute(self,context):
        for obj in bpy.data.objects:
            obj.mv.assign_materials_from_pointers(obj.name)
        return{'FINISHED'}

class OPS_add_material_slot(Operator):
    bl_idname = "fd_material.add_material_slot"
    bl_label = "Add Material Slot"
    bl_options = {'UNDO'}
    
    object_name = StringProperty(name="Object Name")
    
    def execute(self,context):
        obj = bpy.data.objects[self.object_name]
        obj.mv.material_slot_col.add()
        override = {'active_object':obj,'object':obj}
        bpy.ops.object.material_slot_add(override)
        for obj in bpy.data.objects:
            obj.mv.assign_materials_from_pointers(obj.name)
        return{'FINISHED'}

class OPS_fix_texture_paths(Operator):
    bl_idname = "fluidmaterial.fix_texture_paths"
    bl_label = "Fix Texture Paths"
    bl_options = {'UNDO'}
    
    def execute(self,context):
        for image in bpy.data.images:
            image.filepath = "C:\\fluidtextures\\" + image.name
        return{'FINISHED'}


#------REGISTER
classes = [
           OPS_clear_all_materials_from_file,
           OPS_clear_unused_materials_from_file,
           OPS_apply_materials_from_pointers,
           OPS_add_material_slot,
           OPS_fix_texture_paths
           ]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()