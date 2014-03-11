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
from bpy.types import Header, Menu

from fd_datablocks import const

class MENU_mesh_selection(Menu):
    bl_label = "Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("mesh.select_mode",text="Vertex Select",icon='VERTEXSEL').type='VERT'
        layout.operator("mesh.select_mode",text="Edge Select",icon='EDGESEL').type='EDGE'
        layout.operator("mesh.select_mode",text="Face Select",icon='FACESEL').type='FACE'

class MENU_delete_selection(Menu):
    bl_label = "Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("mesh.delete",text="Delete Vertices",icon='VERTEXSEL').type='VERT'
        layout.operator("mesh.delete",text="Delete Edges",icon='EDGESEL').type='EDGE'
        layout.operator("mesh.delete",text="Delete Faces",icon='FACESEL').type='FACE'
        layout.operator("mesh.delete",text="Delete Only Faces",icon='FACESEL').type='ONLY_FACE'
        
class MENU_delete_selection_curve(Menu):
    bl_label = "Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("curve.delete",text="Delete Vertices",icon='VERTEXSEL').type='VERT'
        layout.operator("curve.delete",text="Delete Edges",icon='EDGESEL').type='SEGMENT'
        
class MENU_right_click_menu_edit_mesh(Menu):
    bl_label = "Menu"

    def draw(self, context):
        obj = context.active_object
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.menu("MENU_mesh_selection",text="Selection Mode",icon='MAN_TRANS')
        layout.separator()
        layout.operator("view3d.edit_mesh_extrude_move_normal",icon='CURVE_PATH')
        layout.operator("mesh.knife_tool",icon='SCULPTMODE_HLT')
        layout.operator("mesh.subdivide",icon='OUTLINER_OB_LATTICE')
        layout.operator("mesh.loopcut_slide",icon='SNAP_EDGE')
        layout.operator("mesh.bevel",icon='MOD_BEVEL')
        layout.operator("mesh.edge_face_add",icon='SNAP_FACE')
        layout.operator("mesh.separate",icon='UV_ISLANDSEL').type = 'SELECTED'
        layout.separator()
        layout.menu("MENU_delete_selection",text="Delete",icon='X')
        layout.separator()
        layout.operator("fd_object.toggle_edit_mode",text="Exit Edit Mode",icon=const.icon_editmode).object_name = obj.name
        
class MENU_handel_type(Menu):
    bl_label = "Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("curve.handle_type_set",icon='CURVE_PATH')
        
class MENU_right_click_menu_edit_curve(Menu):
    bl_label = "Menu"

    def draw(self, context):
        obj = context.active_object
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("curve.extrude_move",icon='CURVE_PATH')
        layout.operator("curve.switch_direction",icon='SCULPTMODE_HLT')
        layout.operator("curve.subdivide",icon='OUTLINER_OB_LATTICE')
        layout.separator()
        layout.menu("MENU_delete_selection_curve",text="Delete",icon='X')
        layout.separator()
        layout.operator("fd_object.toggle_edit_mode",text="Exit Edit Mode",icon=const.icon_editmode).object_name = obj.name
        
        
#------REGISTER
classes = [
           MENU_right_click_menu_edit_mesh,
           MENU_mesh_selection,
           MENU_delete_selection,
           MENU_delete_selection_curve,
           MENU_right_click_menu_edit_curve
           ]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
