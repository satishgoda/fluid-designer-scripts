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

import bpy, bgl, blf
from bpy.types import Header, Menu, Operator

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       BoolVectorProperty,
                       PointerProperty,
                       EnumProperty)

import fd_utils
from fd_datablocks import const

class OPS_right_click(Operator):
    bl_idname = "fd_general.right_click"
    bl_label = "Right Click Options"

    GroupName = StringProperty(name="GroupName")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        dm = context.scene.mv.dm
        obj = context.active_object
        if obj:
            if obj.type == 'LAMP':
                obj.mv.draw_object_data(layout,obj.name)
            elif obj.type == 'CAMERA':
                obj.mv.draw_object_data(layout,obj.name)
            else:
                grp_wall = dm.get_wall_group(obj)
                grp_product = dm.get_product_group(obj)
                grp_insert = dm.get_insert_group(obj)
                grp_part = dm.get_part_group(obj)
                if grp_product:
                    grp_product.mv.draw_properties(layout,advanced=False)
                elif grp_wall:
                    grp_wall.mv.draw_properties(layout,advanced=False)
                elif grp_insert:
                    grp_insert.mv.draw_properties(layout,advanced=False)
                elif grp_part:
                    grp_part.mv.draw_properties(layout,advanced=False)
                else:
                    obj.mv.draw_properties(layout,obj.name)

class OPS_delete(Operator):
    bl_idname = "fd_general.delete"
    bl_label = "Delete"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object

    def get_product(self,obj):
        dm = bpy.context.scene.mv.dm
        return dm.get_product_group(obj)

    def execute(self, context):
        grp_product = self.get_product(context.active_object)
        if grp_product:
            bpy.ops.object.select_all(action='DESELECT')
            obj_list = []
            for obj in grp_product.objects:
                obj_list.append(obj)
            fd_utils.delete_obj_list(obj_list)
            return {'FINISHED'}
            
        bpy.ops.object.delete()
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        grp_product = self.get_product(context.active_object)
        if grp_product:
            layout.label("Product Name: " + grp_product.mv.name_group,icon=const.icon_product)
        else:
            layout.label("Object Name: " + context.active_object.name)
        
class OPS_change_shademode(Operator):
    bl_idname = "fd_general.change_shademode"
    bl_label = "Change Shademode"

    shade_mode = bpy.props.EnumProperty(
            name="Shade Mode",
            items=(('WIREFRAME', "Wire Frame", "WIREFRAME",'WIRE',1),
                   ('SOLID', "Solid", "SOLID",'SOLID',2),
                   ('MATERIAL', "Material","MATERIAL",'MATERIAL',3),
                   ('RENDERED', "Rendered", "RENDERED",'SMOOTH',4)
                   ),
            )

    def execute(self, context):
        context.scene.render.engine = 'CYCLES'
        context.space_data.viewport_shade = self.shade_mode
        return {'FINISHED'}
        
class OPS_dialog_show_filters(Operator):
    bl_idname = "fd_general.dialog_show_filters"
    bl_label = "Show Filters"
    bl_options = {'UNDO'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        st = context.space_data
        params = st.params
        if params:
            row = layout.row()
            row.label('File Display Mode:')
            row.prop(params, "display_type", expand=False,text="")
            layout.prop(params, "use_filter", text="Use Filters", icon='FILTER')
            layout.prop(params, "use_filter_folder", text="Show Folders")
            layout.prop(params, "use_filter_blender", text="Show Blender Files")
            layout.prop(params, "use_filter_backup", text="Show Backup Files")
            layout.prop(params, "use_filter_image", text="Show Image Files")
            layout.prop(params, "use_filter_movie", text="Show Video Files")
            layout.prop(params, "use_filter_script", text="Show Script Files")
            layout.prop(params, "use_filter_font", text="Show Font Files")
            layout.prop(params, "use_filter_text", text="Show Text Files")
        
class OPS_error(Operator):
    bl_idname = "fd_general.error"
    bl_label = "Fluid Designer"

    message = StringProperty(name="Message",default="Error")

    def execute(self, context):
        return {'FINISHED'} 

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        layout.label(self.message)
    
class OPS_set_cursor_location(Operator):
    bl_idname = "fd_general.set_cursor_location"
    bl_label = "Cursor Location"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(context.scene,"cursor_location",text="")
    
class OPS_show_object_prompts(Operator):
    bl_idname = "fd_general.show_object_prompts"
    bl_label = "Prompts"
    
    group_name = StringProperty(name="GroupName")
    index = IntProperty(name="Index")
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        grp = bpy.data.groups[self.group_name]
        if grp:
            obj_bp = grp.mv.get_bp()
            obj_bp.mv.PromptPage.show_prompts(layout,obj_bp,self.index)
    
class OPS_show_properties(Operator):
    bl_idname = "fluidgeneral.show_properties"
    bl_label = "Show Properties"

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout
        Part = context.active_object.mv.GetPart()
        Insert = context.active_object.mv.GetInsert()
        Product = context.active_object.mv.GetProduct()
        Wall = context.active_object.mv.GetWall()
        Plane = context.active_object.mv.GetPlane()
        
        if Part and Product is None:
            Part.DrawRightClickProperties(layout)
        elif Insert and Product is None:
            Insert.DrawRightClickProperties(layout)
        elif Product:
            Product.DrawRightClickProperties(layout)
        elif Wall:
            Wall.DrawMainWallProperties(layout)
        elif Plane:
            Plane.DrawMainPlaneProperties(layout)
        else:
            context.active_object.mv.DrawProperties(context.active_object.name,layout)
    
class OPS_toggle_editmode(Operator):
    bl_idname = "fluidgeneral.toggle_editmode"
    bl_label = "Toggle Editmode"

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        Part = context.active_object.mv.GetPart()
        Insert = context.active_object.mv.GetInsert()
        Product = context.active_object.mv.GetProduct()
        Wall = context.active_object.mv.GetWall()
        Plane = context.active_object.mv.GetPlane()

        if context.active_object.mode == 'OBJECT':

            if Part:
                bpy.ops.fluidgroup.prepare_for_library(GroupName=Part.Grp_LinkID)
            elif Insert:
                bpy.ops.fluidgroup.prepare_for_library(GroupName=Insert.Grp_LinkID)
            elif Product:
                bpy.ops.fluidgroup.prepare_for_library(GroupName=Product.Grp_LinkID)
#             elif Wall:
#                 bpy.ops.fluidgroup.prepare_for_library(GroupName=Wall.Grp_LinkID)
#             elif Plane:
#                 bpy.ops.fluidgroup.prepare_for_library(GroupName=Plane.Grp_LinkID)
            else:
                pass
                
            bpy.ops.object.editmode_toggle()
        else:
            bpy.ops.object.editmode_toggle()
        
        return {'FINISHED'}
    
class OPS_start_debug(Operator):
    bl_idname = "fluidgeneral.start_debug"
    bl_label = "Start Debug"
    bl_description = "Start Debug with Eclipse"

    def execute(self, context):
        import pydevd
        pydevd.settrace()
        return {'FINISHED'}
    
# class OPS_bevel(Operator):
#     bl_idname = "fd_general.bevel"
#     bl_label = "Bevel"
#     bl_options = {'UNDO'}
#     
#     offset = FloatProperty(name="Offset",default=1)
#     segments = IntProperty(name="")
#     @classmethod
#     def poll(cls, context):
#         return True
# 
#     def execute(self, context):
#         return {'FINISHED'}
# 
#     def invoke(self,context,event):
#         wm = context.window_manager
#         return wm.invoke_props_dialog(self, width=400)
# 
#     def draw(self, context):
#         layout = self.layout

#------REGISTER
classes = [
           OPS_right_click,
           OPS_delete,
           OPS_dialog_show_filters,
           OPS_toggle_editmode,
           OPS_change_shademode,
           OPS_show_object_prompts,
           OPS_error,
           OPS_start_debug,
           OPS_set_cursor_location
           ]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
