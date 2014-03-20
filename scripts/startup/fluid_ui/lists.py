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
from bpy.types import Panel, Menu, Header, UIList

from fd_datablocks import const

class FD_UL_pointers(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item.item_name == "":
            layout.label(text=item.name,icon=const.icon_pointer)
        else:
            layout.label(text=item.name + ' = ' + item.item_name,icon=const.icon_set_pointer)

class FD_UL_specgroups(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name,icon=const.icon_specgroup)

class FD_UL_materials(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name,icon='MATERIAL')

class FD_UL_vgroups(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name,icon='GROUP_VERTEX')

class FD_UL_prompttabs(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name)

class FD_UL_promptitems(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name)
        if item.Type == 'NUMBER':
            layout.prop(item,'NumberValue',text="")
        if item.Type == 'CHECKBOX':
            layout.prop(item,'CheckBoxValue',text="")
        if item.Type == 'QUANTITY':
            layout.prop(item,'QuantityValue',text="")
        if item.Type == 'COMBOBOX':
            layout.prop(item,'EnumIndex',text="")
            
class FD_UL_objects(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        obj = bpy.data.objects[item.name]
        
        if obj.type == 'MESH':
            if obj.mv.type == 'BPPRODUCT':
                if obj.mv.name_object == "":
                    layout.label(text=obj.mv.name,icon=const.icon_product)
                else:
                    layout.label(text=obj.mv.name_object,icon=const.icon_product)
            elif obj.mv.type == 'BPINSERT':
                if obj.mv.name_object == "":
                    layout.label(text=obj.mv.name,icon=const.icon_insert)
                else:
                    layout.label(text=obj.mv.name_object,icon=const.icon_insert)
            elif obj.mv.type == 'BPPART':
                if obj.mv.name_object == "":
                    layout.label(text=obj.mv.name,icon=const.icon_part)
                else:
                    layout.label(text=obj.mv.name_object,icon=const.icon_part)
            else:
                if obj.mv.name_object == "":
                    layout.label(text=obj.mv.name,icon=const.icon_mesh)
                else:
                    layout.label(text=obj.mv.name_object,icon=const.icon_mesh)
                if obj.mv.use_as_wall_subtraction:
                    layout.label(text="",icon='LATTICE_DATA')
                    
        if obj.type == 'EMPTY':
            if obj.mv.name_object == "":
                layout.label(text=obj.mv.name,icon=const.icon_empty)
            else:
                layout.label(text=obj.mv.name_object,icon=const.icon_empty)
                
            if obj.mv.use_as_mesh_hook:
                layout.label(text="",icon='HOOK')
                
        if obj.type == 'CURVE':
            if obj.mv.name_object == "":
                layout.label(text=obj.mv.name,icon=const.icon_curve)
            else:
                layout.label(text=obj.mv.name_object,icon=const.icon_curve)
            
        if obj.type == 'FONT':
            if obj.mv.name_object == "":
                layout.label(text=obj.mv.name,icon=const.icon_font)
            else:
                layout.label(text=obj.mv.name_object,icon=const.icon_font)
            if obj.mv.use_as_item_number:
                layout.label(text="",icon='LINENUMBERS_ON')
                
        layout.operator("fd_object.select_object",icon='MAN_TRANS',text="").object_name = item.name
        layout.operator("fd_object.delete_object_from_group",icon='X',text="",emboss=False).object_name = obj.name

classes = [
           FD_UL_pointers,
           FD_UL_specgroups,
           FD_UL_materials,
           FD_UL_vgroups,
           FD_UL_prompttabs,
           FD_UL_objects,
           FD_UL_promptitems
           ]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

