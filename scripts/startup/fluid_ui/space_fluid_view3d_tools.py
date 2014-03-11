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
from bpy.types import Header, Menu, Panel, PropertyGroup

from fd_datablocks import enums, const

import os

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       BoolVectorProperty,
                       PointerProperty,
                       CollectionProperty,
                       EnumProperty)

def find_node(material, nodetype):
    if material and material.node_tree:
        ntree = material.node_tree

        for node in ntree.nodes:
            if getattr(node, "type", None) == nodetype:
                return node

    return None

def find_node_input(node, name):
    for input in node.inputs:
        if input.name == name:
            return input

    return None

def panel_node_draw(layout, id_data, output_type, input_name):
    if not id_data.use_nodes:
        layout.operator("cycles.use_shading_nodes", icon='NODETREE')
        return False

    ntree = id_data.node_tree

    node = find_node(id_data, output_type)
    if not node:
        layout.label(text="No output node")
    else:
        input = find_node_input(node, input_name)
        layout.template_node_view(ntree, node, input)

    return True

class PANEL_scenes(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Scenes"
    bl_context = "objectmode"
    bl_label = " "
    bl_options = {'HIDE_HEADER'}
    #bl_idname = "mvProject.part_properties"

    def draw_header(self,context):
        layout = self.layout
        row = layout.row(align=True)
        row.label("Scenes:        ",icon='SCENE_DATA')

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        unit = context.scene.unit_settings
        scene = context.scene
        layout = self.layout
        space = context.space_data

        col = layout.column(align=True)
        box = col.box()
        row = box.row(align=True)
        row.template_ID(context.screen, "scene", new="fd_scene.create_scene", unlink="scene.delete")
        box = col.box()
        row = box.row()
        row.prop(scene, "camera",text="Active Camera")
        row = box.row()
        row.label("Main Units:")
        row.row().prop(unit, "system", expand=True)
        row = box.row()
        row.label("Angle Units:")
        row.row().prop(unit, "system_rotation", expand=True)
        if space.type == 'VIEW_3D' and scene.unit_settings.system == 'NONE':
            row = box.row()
            row.label("Grid Spacing:")
            row.row().prop(space, "grid_scale", expand=True)
        box = col.box()
        scene.mv.PromptPage.draw_prompt_page(box,scene)

class PANEL_worlds(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Worlds"
    bl_context = "objectmode"
    bl_label = " "
    bl_options = {'HIDE_HEADER'}
    #bl_idname = "mvProject.part_properties"

    def draw_header(self,context):
        layout = self.layout
        row = layout.row(align=True)
        row.label("World Management:        ",icon=const.icon_world)

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        scene = context.scene
        world = context.scene.world
        layout = self.layout
        col = layout.column(align=True)
        box = col.box()
        row = box.row(align=True)
        row.template_ID(context.scene, "world", new="world.new")
        box = col.box()
        if not panel_node_draw(box, world, 'OUTPUT_WORLD', 'Surface'):
            box.prop(world, "horizon_color", text="Color")
        box = col.box()
        world.mv.PromptPage.draw_prompt_page(box,world)
 
class PANEL_materials(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Materials"
    bl_context = "objectmode"
    bl_label = " "
    bl_options = {'HIDE_HEADER'}

    def draw_header(self,context):
        layout = self.layout
        row = layout.row(align=True)
        row.label("Material Management:        ",icon=const.icon_material)

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.operator("fd_material.apply_materials_from_pointers",text="Assign Materials",icon=const.icon_material)
        row.operator("fd_material.clear_unused_materials_from_file",text="Clear Unused",icon='ZOOMOUT')
        row.operator("fd_material.clear_all_materials_from_file",text="Clear All",icon='PANEL_CLOSE')
        box.template_list("MATERIAL_UL_matslots", "", bpy.data, "materials", context.scene.mv, "active_material_index", rows=5)
        if len(bpy.data.materials) > 0:
            box = layout.box()
            material = bpy.data.materials[context.scene.mv.active_material_index]
            material.mv.draw_properties(box,material)
            
class PANEL_libraries(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Libraries"
    bl_context = "objectmode"
    bl_label = " "
    bl_options = {'HIDE_HEADER'}

    def draw_header(self,context):
        layout = self.layout
        row = layout.row(align=True)
        row.label("Library Management:        ",icon=const.icon_library)

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        dm = context.scene.mv.dm
        layout = self.layout
        col = layout.column(align=True)
        box = col.box()
        if os.path.exists(dm.Libraries.path):
            Libraries = context.scene.mv.dm.Libraries
            row = box.row(align=True)
            row.prop(dm.Libraries,"path",text="",icon='FILE_TICK')
#             box = col.box()
#             row = box.row(align=True)
#             Libraries.draw_active_pointer_library_menus(row)
        else:
            row = box.row(align=True)
            row.prop(dm.Libraries,"path",text="",icon='ERROR')
        dm.Specgroups.draw_spec_groups(box)
       
#------REGISTER
classes = [
           PANEL_scenes,
           PANEL_worlds,
           PANEL_materials,
           PANEL_libraries
           ]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
