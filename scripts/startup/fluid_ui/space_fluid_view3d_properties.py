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

from bpy.types import (Header, 
                       Menu, 
                       Panel, 
                       Operator)

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       PointerProperty,
                       EnumProperty)

from fd_datablocks import enums, const

class PANEL_selection_properties(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = " "
    bl_options = {'HIDE_HEADER'}
    
    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        layout = self.layout
        layout.label("Selection Properties ",icon='MAN_TRANS')

    def draw(self, context):
        layout = self.layout
        dm = context.scene.mv.dm
        ui = context.scene.mv.ui
        obj = context.active_object
        
        grp_wall = dm.get_wall_group(obj)
        grp_product = dm.get_product_group(obj)
        grp_insert = dm.get_insert_group(obj)
        grp_part = dm.get_part_group(obj)
        
        row = layout.row(align=True)
        row.prop_enum(ui, "interface_selection_tabs", enums.enum_selection_tabs[0][0], icon=const.icon_object, text="Object") 
        
        if grp_wall:
            row.prop_enum(ui, "interface_selection_tabs", enums.enum_selection_tabs[1][0], icon=const.icon_wall, text="Wall") 
        if grp_product:
            row.prop_enum(ui, "interface_selection_tabs", enums.enum_selection_tabs[2][0], icon=const.icon_product, text="Product") 
        if grp_insert:   
            row.prop_enum(ui, "interface_selection_tabs", enums.enum_selection_tabs[3][0], icon=const.icon_insert, text="Insert")
        if grp_part:
            row.prop_enum(ui, "interface_selection_tabs", enums.enum_selection_tabs[4][0], icon=const.icon_part, text="Part")
            
        if obj and ui.interface_selection_tabs == 'OBJECT':
            obj.mv.draw_properties(layout, obj.name)
        if grp_wall and ui.interface_selection_tabs == 'WALL':
            grp_wall.mv.draw_properties(layout,advanced=False)
        if grp_product and ui.interface_selection_tabs == 'PRODUCT':
            grp_product.mv.draw_properties(layout,advanced=True)
        if grp_insert and ui.interface_selection_tabs == 'INSERT':
            grp_insert.mv.draw_properties(layout,advanced=True)
        if grp_part and ui.interface_selection_tabs == 'PART':
            grp_part.mv.draw_properties(layout,advanced=True)
            
#------REGISTER
classes = [
           PANEL_selection_properties
           ]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
