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
        
class MV_UL_materials(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name,icon='MATERIAL')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')

class MV_UL_vgroups(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name,icon='GROUP_VERTEX')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')

class MV_UL_prompttabs(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name)

class MV_UL_meshplane(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name,icon='MESH_PLANE')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')

class MV_UL_objectdata(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name,icon='OBJECT_DATA')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')

class MV_UL_stickyuvsloc(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name,icon='STICKY_UVS_LOC')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')

class MV_UL_modmeshdeform(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name,icon='MOD_MESHDEFORM')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')
            
class MV_UL_parts(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        Part = bpy.data.groups[item.name].mv.GetPart()
        obj_bp = bpy.data.objects[Part.Obj_BPLinkID]

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.label(bpy.data.groups[Part.Grp_LinkID].mv.PartName,icon='MOD_MESHDEFORM')
            layout.operator("fluidobject.select_object",icon='MAN_TRANS',text="").ObjectName = obj_bp.name
            layout.operator("fluidgroup.copy_fluid_group",icon='ORTHO',text="").GroupName = Part.Grp_LinkID
            
#             row.operator("mvpart.show_part_properties",text="",icon='SETTINGS').GroupName = item.name
#             row.operator("mvpart.copy_current_part",icon='ORTHO',text="").GroupName = item.name
#             row.operator("mvpart.replace_part_from_library_in_insert",icon='FILE_REFRESH',text="").GroupName = item.name
#             row.operator("mvpart.fix_normals",icon='MOD_UVPROJECT',text="").GroupName = item.name
#             row = layout.row(align=True)
            layout.operator("fluidgroup.delete_group",icon='X',text="").GroupName = Part.Grp_LinkID
            
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')

class MV_UL_products(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        Number = str(bpy.data.groups[item.name].mv.ProductNumber)
        Name = bpy.data.groups[item.name].mv.ProductName

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            #row.operator("mvproduct.select_product_bp",text="",icon='MAN_TRANS').GroupName = item.name #TODO ADD THIS OPERATOR
            row.label("#" + Number + " - " + Name,icon='OBJECT_DATA')
            row.operator("mvproduct.zoom_to_selected_product",text="",icon='VIEWZOOM').GroupName = item.name
            row.prop(item,"SoloMode",text="",icon='RESTRICT_VIEW_OFF')
            row.prop(item,"EditMode",text="",icon='GREASEPENCIL')
            row = layout.row()
            row.operator("mvproduct.delete_product",icon='X',text="",emboss=False).GroupName = item.name 
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')

class MV_UL_productmeshes(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        obj = bpy.data.objects[item.name]
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if obj.mv.ProductMeshType == 'STANDARD':
                layout.label(text=obj.mv.MeshName,icon='MESH_CUBE')
            if obj.mv.ProductMeshType == 'ITEMNUMBER':
                layout.label(text=obj.mv.MeshName,icon='FONT_DATA')
            if obj.mv.ProductMeshType == 'WALLBOOLEAN':
                layout.label(text=obj.mv.MeshName,icon='OUTLINER_OB_LATTICE')

            layout.operator("fluidobject.select_object",icon='MAN_TRANS',text="").ObjectName = item.name
            layout.operator("fluidobject.select_object",icon='X',text="",emboss=False).ObjectName = item.name
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')

class MV_UL_meshes(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        obj = bpy.data.objects[item.name]
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if obj.mv.FluidMeshType == 'STANDARD':
                layout.label(text=obj.mv.MeshName,icon='MESH_CUBE')
            if obj.mv.FluidMeshType == 'SHEETSTOCK':
                layout.label(text=obj.mv.MeshName,icon='UGLYPACKAGE')
            if obj.mv.FluidMeshType == 'EDGEBANDING':
                layout.label(text=obj.mv.MeshName,icon='MOD_SIMPLEDEFORM')
            if obj.mv.FluidMeshType == 'HARDWOOD':
                layout.label(text=obj.mv.MeshName,icon='GROUP_UVS')
            if obj.mv.FluidMeshType == 'BUYOUT':
                layout.label(text=obj.mv.MeshName,icon='MOD_SMOOTH')
            if obj.mv.FluidMeshType == 'HARDWARE':
                layout.label(text=obj.mv.MeshName,icon='MOD_SCREW')
            if obj.mv.FluidMeshType == 'MACHINING':
                layout.label(text=obj.mv.MeshName,icon='MODIFIER')
            if obj.mv.UseAsWallSubtraction:
                layout.label(text="",icon='LATTICE_DATA')

            layout.operator("fluidobject.select_object",icon='MAN_TRANS',text="").ObjectName = item.name
            layout.operator("fluidobject.delete_object",icon='X',text="",emboss=False).ObjectName = item.name
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')

class MV_UL_text(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        obj = bpy.data.objects[item.name]
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=obj.mv.TextName,icon='FONT_DATA')
            if obj.mv.UseAsItemNumber:
                layout.label(text="",icon='LINENUMBERS_ON')
            if obj.mv.UseAsObjectName:
                layout.label(text="",icon='SORTALPHA')

            layout.operator("fluidobject.select_object",icon='MAN_TRANS',text="").ObjectName = item.name
            layout.operator("fluidobject.delete_object",icon='X',text="",emboss=False).ObjectName = item.name
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')

class MV_UL_empties(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        obj = bpy.data.objects[item.name]

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if obj.mv.UseAsMeshHook:
                layout.label(text=obj.mv.EmptyName,icon='HOOK')
            else:
                layout.label(text=obj.mv.EmptyName,icon='EMPTY_DATA')
            layout.operator("fluidobject.select_object",icon='MAN_TRANS',text="").ObjectName = item.name
            layout.operator("fluidobject.delete_object",icon='X',text="",emboss=False).ObjectName = item.name
            
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')

class MV_UL_default(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')

class MV_UL_wall(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.label(text='Wall ' + str(item.Number),icon='MOD_BUILD')
            row.operator("mvwall.delete_wall",icon='X',text="",emboss=False).GroupName = item.name
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')

class MV_UL_wallcomponent(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.label(text=item.ComponentName + " " + str(item.Number),icon='OUTLINER_OB_LATTICE')
            row.operator("mvwallcomponent.delete_wall_component",icon='X',text="",emboss=False).GroupName = item.name
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')

class MV_UL_extrusion(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name,icon='CURVE_BEZCURVE')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')

class MV_UL_category(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name,icon='FILE_FOLDER')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')

class MV_UL_plane(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name,icon='MESH_PLANE')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')

class MV_UL_insert(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        grp =  bpy.data.groups[item.name]
        Insert = grp.mv.GetInsert()
        obj_bp = bpy.data.objects[Insert.Obj_BPLinkID]
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.label(text=grp.mv.InsertName,icon='STICKY_UVS_LOC')
            row.operator("fluidobject.select_object",text="",icon='MAN_TRANS').ObjectName = obj_bp.name
            row = layout.row(align=True)
            row.operator("fluidgroup.delete_group",icon='X',text="",emboss=False).GroupName = Insert.Grp_LinkID
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')

class MV_UL_pointer(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.label(text=item.name,icon='HAND')
            name = item.Value
            if name == "":
                name = "None"
            row.operator("fluidlibrary.change_category",icon='FILE_FOLDER',text="").LibraryType = data.Type
            props = row.operator("fluidlibrary.assign_pointer",icon='STYLUS_PRESSURE',text=name)
            props.PointerName = item.name
            props.LibraryType = data.Type
            props = row.operator("fluidlibrary.delete_pointer",icon='X',text="",emboss=False)
            props.PointerName = item.name
            props.LibraryType = data.Type
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name,icon='WORLD')

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

