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
import os
import math

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       BoolVectorProperty,
                       PointerProperty,
                       EnumProperty)

from mathutils import Vector
from fd_datablocks import const

import fd_utils

class OPS_drag_and_drop(bpy.types.Operator):
    """SPECIAL OPERATOR: This is called when you drop an image to the 3dview space"""
    bl_idname = "fd_dragdrop.drag_and_drop"
    bl_label = "Drag and Drop"
    bl_options = {'UNDO'}

    #READONLY
    filepath = StringProperty(name="Filepath")
    objectname = StringProperty(name="Object Name")
    
    library_type = StringProperty(name="Object Name")

    material_header_text = ('Left Click = Assign Material to Object',
                            'Enter/Return = Assign to Scene', 
                            'Key R = Recursive Assignment', 
                            'Key P = Pointer Assignment', 
                            'Right Click/Esc = Exit Command')
    
    product_header_text = ('Left Click = Assign Product to Wall/Product',
                           'Enter/Return = Add to Cursor Location', 
                           'Key R = Replace Product', 
                           'Right Click/Esc = Exit Command')
    
    part_header_text = ('Left Click = Assign Part to Insert/Product',
                        'Enter/Return = Add to Cursor Location', 
                        'Key R = Replace Part', 
                        'Right Click/Esc = Exit Command')
    
    insert_header_text = ('Left Click = Assign Insert to Product',
                          'Enter/Return = Add to Cursor Location', 
                          'Key R = Replace Insert', 
                          'Right Click/Esc = Exit Command')
    
    object_header_text = ('Left Click = Assign Object to Insert/Product',
                          'Enter/Return = Add to Cursor Location', 
                          'Right Click/Esc = Exit Command')
    
    extrusion_header_text = ('Left Click = Assign Extrusion to Group',
                             'Enter/Return = Add to Cursor Location', 
                             'Right Click/Esc = Exit Command')

    def __del__(self): #RESET HEADER TEXT AFTER OP HAS FINISHED
        bpy.context.area.header_text_set()
        bpy.context.area.tag_redraw()

    def invoke(self, context, event):
        ls = context.scene.mv.dm.Libraries
        self.library_type = ls.get_library_type_from_filepath(self.filepath)
        if context.space_data.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)
            
            if self.library_type == 'MATERIAL':
                text = "Material Assignment Mode: "
                for index, command in enumerate(self.material_header_text):
                    text += command
                    if index + 1 != len(self.material_header_text):
                        text += " | "
                context.area.header_text_set(text)
                
            if self.library_type == 'PRODUCT':
                text = "Product Assignment Mode: "
                for index, command in enumerate(self.product_header_text):
                    text += command
                    if index + 1 != len(self.product_header_text):
                        text += " | "
                context.area.header_text_set(text)
                
            if self.library_type == 'INSERT':
                text = "Insert Assignment Mode: "
                for index, command in enumerate(self.insert_header_text):
                    text += command
                    if index + 1 != len(self.insert_header_text):
                        text += " | "
                context.area.header_text_set(text)
                
            if self.library_type == 'PART':
                text = "Part Assignment Mode: "
                for index, command in enumerate(self.part_header_text):
                    text += command
                    if index + 1 != len(self.part_header_text):
                        text += " | "
                context.area.header_text_set(text)
                
            if self.library_type == 'EXTRUSION':
                text = "Extrusion Assignment Mode: "
                for index, command in enumerate(self.extrusion_header_text):
                    text += command
                    if index + 1 != len(self.extrusion_header_text):
                        text += " | "
                context.area.header_text_set(text)
                
            if self.library_type == 'OBJECT':
                text = "Object Assignment Mode: "
                for index, command in enumerate(self.object_header_text):
                    text += command
                    if index + 1 != len(self.object_header_text):
                        text += " | "
                context.area.header_text_set(text)
                
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}

    def modal(self, context, event):
        fd_utils.select_cursor_object(context, event)
        
        # allow navigation
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        # exit operator
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'FINISHED'}
        
        if self.library_type == 'PROJECT':
            return {'CANCELLED'} #TODO: Implement add background image & add image as plane

        elif self.library_type == 'MATERIAL': 
            if event.type == 'LEFTMOUSE' or event.type == 'R': #Assign Materialrr
                if context.active_object:
                    dm = bpy.context.scene.mv.dm
                    if len(context.active_object.mv.material_slot_col) > 1:
                        bpy.ops.fd_dragdrop.place_material('INVOKE_DEFAULT',filepath=self.filepath,object_name=context.active_object.name)
                    else:
                        material = dm.retrieve_data_from_library(self.filepath)
                        context.active_object.mv.assign_material_to_object(context.active_object.name,material)
                    if context.active_object.type =='MESH':
                        if len(context.active_object.data.uv_textures) == 0:
                            if context.active_object.mode == 'OBJECT':
                                bpy.ops.fd_object.unwrap_mesh() #THIS WORKS ON ACTIVE OBJECT
                    
                    if event.type == 'LEFTMOUSE':
                        return {'FINISHED'}

            if event.type == 'P':
                dm = bpy.context.scene.mv.dm
                filename, ext = os.path.splitext(os.path.basename(self.filepath))
                pointer = dm.Specgroups.get_active().Pointers.get_active()
                pointer.library_name = dm.Libraries.get_library_name_from_path(self.filepath)
                pointer.category_name = dm.Libraries.get_category_name_from_path(self.filepath)
                pointer.item_name = filename
                return {'FINISHED'}

            if event.type == 'RET' or event.type == 'NUMPAD_ENTER': #AddMaterialToFile
                dm = bpy.context.scene.mv.dm
                dm.retrieve_data_from_library(self.filepath)
                return {'FINISHED'}

        elif self.library_type == 'EXTRUSION':
            if event.type == 'LEFTMOUSE': #Assign to Product or Wall
                dm = bpy.context.scene.mv.dm
                product = dm.get_product_group(context.active_object)
                wall = dm.get_wall_group(context.active_object)
                if product or wall:
                    bpy.ops.fd_dragdrop.place_extrusion('INVOKE_DEFAULT',filepath = self.filepath)
                    return {'FINISHED'}
                    
            if event.type == 'RET' or event.type == 'NUMPAD_ENTER': #AddMaterialToFile
                filename, ext = os.path.splitext(os.path.basename(self.filepath))
                dm = bpy.context.scene.mv.dm
                obj = dm.retrieve_data_from_library(self.filepath)
                obj.mv.name_object = filename
                bpy.context.scene.objects.link(obj)
                return {'FINISHED'}
                
            if event.type == 'R': #Replace selected Product
                dm = bpy.context.scene.mv.dm
                product = dm.get_product_group(context.active_object)
                wall = dm.get_wall_group(context.active_object)
                if product or wall:
                    bpy.ops.fd_dragdrop.place_extrusion('INVOKE_DEFAULT',filepath = self.filepath)
            
        elif self.library_type == 'PRODUCT':
            if event.type == 'LEFTMOUSE': #Assign to Product or Wall
                dm = bpy.context.scene.mv.dm
                product = dm.get_product_group(context.active_object)
                wall = dm.get_wall_group(context.active_object)
                if product or wall:
                    bpy.ops.fd_dragdrop.place_product('INVOKE_DEFAULT',filepath = self.filepath,
                                                    active_obj_id = context.active_object.name)
                    return {'FINISHED'}
                    
            if event.type == 'RET' or event.type == 'NUMPAD_ENTER': #AddMaterialToFile
                bpy.ops.fd_dragdrop.place_product('INVOKE_DEFAULT',filepath = self.filepath,
                                active_obj_id = "")
                return {'FINISHED'}
                
            if event.type == 'R': #Replace selected Product
                pass #TODO: IMPLEMENT REPLACE
            
        elif self.library_type == 'INSERT':
            if event.type == 'LEFTMOUSE' or event.type == 'R': #Add to Product or Wall
                if context.active_object:
                    dm = bpy.context.scene.mv.dm
                    grp_product = dm.get_product_group(context.active_object)
                    filename, ext = os.path.splitext(os.path.basename(self.filepath))
                    grp = dm.retrieve_data_from_library(self.filepath)
                    grp.mv.name_group = filename
                    if grp_product:
                        dm.add_grp_to_product(grp,grp_product)
                        return {'FINISHED'}
                    else:
                        dm.add_group_to_scene(grp)
                        return {'FINISHED'}
                
            if event.type == 'RET' or event.type == 'NUMPAD_ENTER': #Add to Room
                dm = bpy.context.scene.mv.dm
                filename, ext = os.path.splitext(os.path.basename(self.filepath))
                grp = dm.retrieve_data_from_library(self.filepath)
                grp.mv.name_group = filename
                dm.add_group_to_scene(grp)
                return {'FINISHED'}

        elif self.library_type == 'PART':
            if event.type == 'LEFTMOUSE': #Add to Product or Wall
                if context.active_object:
                    dm = bpy.context.scene.mv.dm
                    grp_product = dm.get_product_group(context.active_object)
                    grp_insert = dm.get_insert_group(context.active_object)
                    filename, ext = os.path.splitext(os.path.basename(self.filepath))
                    if grp_product:
                        grp = dm.retrieve_data_from_library(self.filepath)
                        grp.mv.name_group = filename
                        dm.add_grp_to_product(grp,grp_product)
                        return {'FINISHED'}
                    elif grp_insert:
                        grp = dm.retrieve_data_from_library(self.filepath)
                        grp.mv.name_group = filename
                        dm.add_part_to_insert(grp,grp_insert)
                        return {'FINISHED'}

            if event.type == 'RET' or event.type == 'NUMPAD_ENTER': #Add to Room
                dm = bpy.context.scene.mv.dm
                filename, ext = os.path.splitext(os.path.basename(self.filepath))
                grp = dm.retrieve_data_from_library(self.filepath)
                grp.mv.name_group = filename
                dm.add_group_to_scene(grp)
                return {'FINISHED'}

        elif self.library_type == 'WORLD':
            dm = context.scene.mv.dm
            world = dm.retrieve_data_from_library(self.filepath)
            context.scene.world = world
            return {'FINISHED'}
            
        elif self.library_type =='OBJECT':
            if event.type == 'LEFTMOUSE': #Add to Product or Wall
                if context.active_object:
                    dm = bpy.context.scene.mv.dm
                    grp_product = dm.get_product_group(context.active_object)
                    grp_insert = dm.get_insert_group(context.active_object)
                    grp_part = dm.get_part_group(context.active_object)
                    filename, ext = os.path.splitext(os.path.basename(self.filepath))
                    if grp_product:
                        obj = dm.retrieve_data_from_library(self.filepath)
                        obj.mv.name_object = filename
                        dm.add_obj_to_grp(obj,grp_product)
                        return {'FINISHED'}
                    elif grp_insert:
                        obj = dm.retrieve_data_from_library(self.filepath)
                        obj.mv.name_object = filename
                        dm.add_obj_to_grp(obj,grp_product)
                        return {'FINISHED'}
                    elif grp_part:
                        obj = dm.retrieve_data_from_library(self.filepath)
                        obj.mv.name_object = filename
                        dm.add_obj_to_grp(obj,grp_part)
                        return {'FINISHED'}
                    else:
                        return {'RUNNING_MODAL'}
                else:
                    return {'RUNNING_MODAL'}
                
            if event.type == 'RET' or event.type == 'NUMPAD_ENTER': #Add to Room
                filename, ext = os.path.splitext(os.path.basename(self.filepath))
                dm = bpy.context.scene.mv.dm
                obj = dm.retrieve_data_from_library(self.filepath)
                obj.mv.name_object = filename
                bpy.context.scene.objects.link(obj)
                obj.mv.assign_materials_from_pointers(obj.name)
                dm.set_object_name(obj)
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.scene.objects.active = obj
                obj.hide = False
                obj.select = True
                return {'FINISHED'}

        elif self.library_type =='GROUP':
            dm = bpy.context.scene.mv.dm
            grp = dm.retrieve_data_from_library(self.filepath)
            for obj in grp.objects:
                context.scene.objects.link(obj)
            return {'FINISHED'}

        else:
            print("FILE: module/fd_dragdrop.py","CLASS: OPS_drag_and_drop.modal","Missing Library Type:",self.library_type)
            return {'CANCELLED'}
        
        return {'RUNNING_MODAL'}
        
class OPS_place_product(Operator):
    bl_idname = "fd_dragdrop.place_product"
    bl_label = "Draw Product:"

    filepath = StringProperty(name="Filepath")
    active_obj_id = StringProperty(name="Active Object ID")

    quantity = IntProperty(name="Quantity",default = 1)
    
    left_offset = FloatProperty(name="Left Offset", default=0)
    right_offset = FloatProperty(name="Right Offset", default=0)
    
    def __init__(self):
        """ Several of the functions need information about the group
            so here it is added and set with a specific name.
        """
        dm = bpy.context.scene.mv.dm
        grp = dm.retrieve_data_from_library(self.filepath)
        grp.name = const.temp_group
        
    def __del__(self):
        """ Make sure the temp group is delete if the user canceled
            the command.
        """
        if const.temp_group in bpy.data.groups:
            grp = bpy.data.groups[const.temp_group]
            obj_list = []
            for obj in grp.objects:
                obj_list.append(obj)
            fd_utils.delete_obj_list(obj_list)
            bpy.data.groups.remove(grp)
            
    def invoke(self,context,event):
        if self.active_obj_id in bpy.data.objects:
            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=500)
        else:
            dm = context.scene.mv.dm
            grp = bpy.data.groups[const.temp_group]
            grp.mv.name_group = self.get_group_name()
            dm.add_group_to_scene(grp)
            obj_product_bp = grp.mv.get_bp()
            bpy.ops.object.select_all(action='DESELECT')
            obj_product_bp.select = True
            bpy.context.scene.objects.active = obj_product_bp
            return{'FINISHED'}

    def execute(self,context):
        wm = bpy.context.window_manager
        dm = context.scene.mv.dm
        obj = bpy.data.objects[self.active_obj_id]
        grp_wall = self.get_placement_wall(obj)
        grp_sel_product = dm.get_product_group(obj)
        grp_product = self.get_temp_group()
        wall_length = grp_wall.mv.get_x().location.x
        
        start_x = 0
        end_x = 0
        quantity = self.quantity
        
        place_as_return = False
        
        if grp_sel_product:
            placement = wm.mv.placement_on_product
            if placement == 'FILL_LEFT':
                start_x = grp_sel_product.mv.get_bp().location.x - grp_sel_product.mv.get_available_space('LEFT')
                end_x = grp_sel_product.mv.get_bp().location.x
            
            if placement == 'LEFT':
                if grp_sel_product.mv.category_type == 'CORNER':
                    if grp_sel_product.mv.left_x_distance_from_wall() > 1:
                        place_as_return = True
                        start_x = grp_sel_product.mv.get_bp().location.x - math.fabs(grp_sel_product.mv.get_y().location.y) - (grp_product.mv.get_x().location.x * quantity)
                        end_x = grp_sel_product.mv.get_bp().location.x - math.fabs(grp_sel_product.mv.get_y().location.y)
                    else:
                        start_x = grp_wall.mv.get_x().location.x - math.fabs(grp_sel_product.mv.get_y().location.y) - (grp_product.mv.get_x().location.x * quantity)
                        end_x = grp_wall.mv.get_x().location.x - math.fabs(grp_sel_product.mv.get_y().location.y)
                else:
                    if grp_sel_product.mv.get_bp().rotation_euler.z > 0:
                        place_as_return = True
                    start_x = grp_sel_product.mv.get_bp().location.x - (grp_product.mv.get_x().location.x * quantity)
                    end_x = grp_sel_product.mv.get_bp().location.x
                
            if placement == 'FILL_RIGHT':
                start_x = grp_sel_product.mv.get_bp().location.x + grp_sel_product.mv.get_x().location.x
                end_x = start_x + grp_sel_product.mv.get_available_space('RIGHT')
            
            if placement == 'RIGHT':
                if grp_sel_product.mv.category_type == 'CORNER' and grp_sel_product.mv.get_bp().rotation_euler.z < 0:
                    if grp_sel_product.mv.right_x_distance_from_wall() > 1:
                        place_as_return = True
                        start_x = grp_sel_product.mv.get_x().location.x
                        end_x = start_x + (grp_product.mv.get_x().location.x * quantity)
                    else:
                        start_x = grp_sel_product.mv.get_x().location.x
                        end_x = start_x + (grp_product.mv.get_x().location.x * quantity)
                else:
                    if grp_sel_product.mv.get_bp().rotation_euler.z < 0:
                        place_as_return = True
                    start_x = grp_sel_product.mv.get_bp().location.x + grp_sel_product.mv.get_x().location.x
                    end_x = start_x + (grp_product.mv.get_x().location.x * quantity)
            
            if placement == 'CENTER':
                space = grp_product.mv.get_x().location.x * quantity
                start_x = grp_sel_product.mv.get_bp().location.x + (grp_sel_product.mv.get_x().location.x / 2) - (space / 2)
                end_x = grp_sel_product.mv.get_bp().location.x + (grp_sel_product.mv.get_x().location.x / 2) + (space / 2)
            
        else:
            
            placement = wm.mv.placement_on_wall
            if placement == 'FILL_WALL':
                start_x = self.left_offset
                end_x = wall_length - self.right_offset
            
            if placement == 'LEFT':
                start_x = self.left_offset
                end_x = (grp_product.mv.get_x().location.x * quantity) + self.left_offset

            if placement == 'CENTER':
                start_x = (wall_length / 2) - ((grp_product.mv.get_x().location.x * quantity) / 2)
                end_x = (wall_length / 2) - ((grp_product.mv.get_x().location.x * quantity) / 2) + (grp_product.mv.get_x().location.x * quantity)

            if placement == 'RIGHT':
                start_x = wall_length - (grp_product.mv.get_x().location.x * quantity) - self.right_offset
                end_x = wall_length - self.right_offset
                
        if grp_product.mv.category_type == 'CORNER':
            if placement == 'RIGHT':
                self.place_corner_product(grp_product,grp_wall,end_x,math.radians(-90))
            else:
                self.place_corner_product(grp_product,grp_wall,start_x,0)
        else:
            if place_as_return:
                self.place_product_return(grp_wall, grp_sel_product, grp_product, placement)
            else:
                self.place_products(self.filepath, quantity, grp_wall, start_x, end_x)
        
        return{'FINISHED'}
    
    def place_product_return(self,grp_wall,grp_sel_product,grp_product,placement):
        dm = bpy.context.scene.mv.dm
        grp_product.mv.name_group = self.get_group_name()
        dm.add_product_to_wall(grp_product,grp_wall)
        obj_bp = grp_product.mv.get_bp()
        obj_bp.location.x = grp_sel_product.mv.get_bp().location.x
        
        if placement == 'LEFT':
            if grp_sel_product.mv.category_type == 'CORNER':
                obj_bp.location.y = (grp_product.mv.get_x().location.x + math.fabs(grp_sel_product.mv.get_y().location.y))*-1
            else:
                obj_bp.location.y = grp_sel_product.mv.get_bp().location.y - grp_product.mv.get_x().location.x
            obj_bp.rotation_euler.z = math.radians(90)

        if placement == 'RIGHT':
            if grp_sel_product.mv.category_type == 'CORNER':
                obj_bp.location.y = (math.fabs(grp_sel_product.mv.get_x().location.x))*-1
            else:
                obj_bp.location.y = grp_sel_product.mv.get_bp().location.y - grp_sel_product.mv.get_x().location.x
            obj_bp.rotation_euler.z = math.radians(-90)

    def place_corner_product(self,grp_product,grp_wall,x_loc,z_rot):
        dm = bpy.context.scene.mv.dm
        grp = dm.retrieve_data_from_library(self.filepath)
        grp.mv.name_group = self.get_group_name()
        dm.add_product_to_wall(grp,grp_wall)
        grp.mv.get_bp().location.x = x_loc
        grp.mv.get_bp().rotation_euler.z = z_rot
        grp.mv.category_type = dm.Libraries.get_category_type_from_filepath(self.filepath)
    
    def place_products(self,filepath,qty,grp_wall,start_x,end_x):
        dm = bpy.context.scene.mv.dm
        product_width = (end_x - start_x) / qty
        for index in range(qty):
            grp = dm.retrieve_data_from_library(self.filepath)
            grp.name = self.get_group_name()
            dm.add_product_to_wall(grp,grp_wall)
            grp.mv.get_bp().location.x = start_x + (product_width * index)
            grp.mv.get_x().location.x = product_width
            
    def get_placement_wall(self,obj):
        dm = bpy.context.scene.mv.dm
        wm = bpy.context.window_manager
        grp_wall = dm.get_wall_group(obj)
        if grp_wall:
            grp_product = dm.get_product_group(obj)
            if grp_product:
                if grp_product.mv.category_type == 'CORNER': #PLACE ON NEXT OR PREV WALL IF CORNER CAB
                    obj_bp = grp_product.mv.get_bp()
                    if wm.mv.placement_on_product == 'FILL_LEFT' or wm.mv.placement_on_product == 'LEFT':
                        if obj_bp.location.x < 1: #1 INCH THRESHHOLD TO PLACE ON NEXT WALL
                            grp_wall = grp_product.mv.get_connected_wall('LEFT') #PLACE CABINET ON WALL TO LEFT
                    if wm.mv.placement_on_product == 'FILL_RIGHT' or wm.mv.placement_on_product == 'RIGHT':
                        grp_wall_temp = grp_product.mv.get_connected_wall('RIGHT')
                        if grp_wall_temp:
                            wall_length = grp_wall.mv.get_x().location.x
                            if obj_bp.location.x > wall_length - 1:    #1 INCH THRESHHOLD TO PLACE ON NEXT WALL
                                grp_wall = grp_wall_temp               #PLACE CABINET ON WALL TO RIGHT
            return grp_wall

    def get_temp_group(self):
        dm = bpy.context.scene.mv.dm
        grp = bpy.data.groups[const.temp_group]
        grp.mv.name_group = self.get_group_name()
        category_type = dm.Libraries.get_category_type_from_filepath(self.filepath)
        grp.mv.category_type = category_type
        return grp
        
    def get_group_name(self):
        filename, ext = os.path.splitext(os.path.basename(self.filepath))
        return filename
        
    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        dm = context.scene.mv.dm
        obj = bpy.data.objects[self.active_obj_id]
        grp_product = dm.get_product_group(obj)
        grp_wall = dm.get_wall_group(obj)
        grp_new = bpy.data.groups[const.temp_group]
        category_type = dm.Libraries.get_category_type_from_filepath(self.filepath) #TODO: IMPLEMENT CATEGORY TYPE
        
        dict = {}
        
        for obj in grp_new.objects:
            obj_parent = obj.parent
            if obj_parent is None:
                dict['BP'] = obj
            if obj.mv.type == 'VPDIMX':
                if obj_parent.parent is None:
                    dict['X'] = obj
            if obj.mv.type == 'VPDIMY':
                if obj_parent.parent is None:
                    dict['Y'] = obj
            if obj.mv.type == 'VPDIMZ':
                if obj_parent.parent is None:
                    dict['Z'] = obj
                
            if len(dict) == 4:
                break
        
        box = layout.box()
        row = box.row()
        
        if grp_product:
            #TODO: hide prop enums that don't apply to current placement
            row.label("Placement: Next to Product",icon='OBJECT_DATA')
            row = box.row(align=True)
            if grp_product.mv.category_type != 'CORNER':
                row.prop_enum(wm.mv, "placement_on_product", 'FILL_LEFT', icon='PREV_KEYFRAME', text="")
            row.prop_enum(wm.mv, "placement_on_product", 'LEFT', icon='TRIA_LEFT', text="") 
            if grp_product.mv.category_type != 'CORNER':
                row.prop_enum(wm.mv, "placement_on_product", 'CENTER', icon='CURSOR', text="")
            row.prop_enum(wm.mv, "placement_on_product", 'RIGHT', icon='TRIA_RIGHT', text="")    
            if grp_product.mv.category_type != 'CORNER':
                row.prop_enum(wm.mv, "placement_on_product", 'FILL_RIGHT', icon='NEXT_KEYFRAME', text="")
            
        else:
            #TODO: hide prop enums that don't apply to current placement
            row.label("Placement: On Wall",icon='MESH_PLANE')
            row = box.row(align=True)
            row.prop_enum(wm.mv, "placement_on_wall", 'LEFT', icon='TRIA_LEFT', text="") 
            row.prop_enum(wm.mv, "placement_on_wall", 'CENTER', icon='CURSOR', text="")
            row.prop_enum(wm.mv, "placement_on_wall", 'RIGHT', icon='TRIA_RIGHT', text="")    
            if category_type != 'CORNER':
                row.separator()
                row.prop_enum(wm.mv, "placement_on_wall", 'FILL_WALL', icon='ARROW_LEFTRIGHT', text="") 
        
        box = layout.box()
        row = box.row()
        row.label("Product: " + grp_new.mv.name_group,icon='OBJECT_DATA')
        if category_type != 'CORNER':
            row.prop(self,"quantity",text="Quantity")
            
        split = box.split(percentage=0.5)
        col = split.column(align=True)
        col.label("Dimensions:")
        
        col.prop(dict['X'],"location",index=0,text="X Dimension")
        col.prop(dict['Y'],"location",index=1,text="Y Dimension")
        col.prop(dict['Z'],"location",index=2,text="Z Dimension")
        
        col = split.column(align=True)
        col.label("Offset:")
        col.prop(self,"left_offset",text="Left")
        col.prop(self,"right_offset",text="Right")
        col.prop(dict['BP'],"location",index=2,text="Z Location")
        
class OPS_place_extrusion(Operator):
    bl_idname = "fd_dragdrop.place_extrusion"
    bl_label = "Add Molding"

    filepath = StringProperty(name="Filepath")

    Type = EnumProperty(items=(('BASE',"Base Molding","Base Molding"),
                                 ('CROWN',"Crown Molding","Crown Molding")),
                          name="Return",
                          default='BASE')
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        dm = context.scene.mv.dm
        obj = bpy.context.object
        grp_product = dm.get_product_group(obj)
        grp_wall = dm.get_wall_group(obj)
        
        if grp_product:
            obj_bp = grp_product.mv.get_bp()
            obj_x = grp_product.mv.get_x()
            obj_z = grp_product.mv.get_z()    
        else:
            obj_bp = grp_wall.mv.get_bp()
            obj_x = grp_wall.mv.get_x()
            obj_z = grp_wall.mv.get_z()
            
        filename, ext = os.path.splitext(os.path.basename(self.filepath))
        dm = bpy.context.scene.mv.dm
        profile = dm.retrieve_data_from_library(self.filepath)
        profile.mv.name_object = filename
        if profile.name not in context.scene.objects:
            context.scene.objects.link(profile)
        
        #Add curve set handle type to vector, set origin to 1st control point, hide handles 
        bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=False)
        obj_curve = context.active_object
        obj_curve.data.show_handles = False
        obj_curve.data.bevel_object = profile
        
        obj_curve.data.splines[0].bezier_points[0].co = (0,0,0)
#         obj_curve.data.splines[0].bezier_points[0].handle_left_type = 'VECTOR'
        obj_curve.data.splines[0].bezier_points[1].co = (obj_x.location.x,0,0)
#         obj_curve.data.splines[0].bezier_points[1].handle_left_type = 'VECTOR'
        
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.handle_type_set(type='VECTOR')
        bpy.ops.object.editmode_toggle()
        
        obj_curve.data.dimensions = '2D'
        obj_curve.parent = obj_bp
        if self.Type == 'CROWN':
            if obj_z.location.z > 0: #UPPER CABINETS HAVE MIRRORED Z DIMS
                obj_curve.location.z = obj_z.location.z
        return {'FINISHED'}
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,"Type") 

class OPS_place_insert(Operator):
    bl_idname = "fd_dragdrop.place_insert"
    bl_label = "Draw Insert:"

    filepath = StringProperty(name="Filepath")
    active_obj_id = StringProperty(name="Active Object ID")

    def __init__(self):
        """ Several of the functions need information about the group
            so here it is added and set with a specific name.
        """
        dm = bpy.context.scene.mv.dm
        grp = dm.retrieve_data_from_library(self.filepath)
        grp.name = const.temp_group
        
    def __del__(self):
        """ Make sure the temp group is delete if the user canceled
            the command.
        """
        if const.temp_group in bpy.data.groups:
            grp = bpy.data.groups[const.temp_group]

    def invoke(self,context,event):
        if self.active_obj_id in bpy.data.objects:
            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=500)
        else:
            dm = context.scene.mv.dm
            grp = bpy.data.groups[const.temp_group]
            filename, ext = os.path.splitext(os.path.basename(self.filepath))
            grp.mv.name_group = filename
            dm.add_group_to_scene(grp)
            return{'FINISHED'}
            
    def execute(self,context):
        dm = context.scene.mv.dm
        filename, ext = os.path.splitext(os.path.basename(self.filepath))
        obj = bpy.data.objects[self.active_obj_id]
        grp_product = dm.get_product_group(obj)
        grp_insert = bpy.data.groups[const.temp_group]
        grp_insert.mv.name_group = filename
        if grp_product:
            dm.add_group_to_product(grp_insert,grp_product)
        return{'FINISHED'}

class OPS_place_material(Operator):
    bl_idname = "fd_dragdrop.place_material"
    bl_label = "Place Material:"

    object_name = StringProperty(name="Object Name")
    filepath = StringProperty(name="Filepath")
    add_to_slot = BoolVectorProperty(name="Add To Slot",size=20)
    
    def invoke(self,context,event):
        obj = bpy.data.objects[self.object_name]
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=250)
            
    def execute(self,context):
        dm = context.scene.mv.dm
        filename, ext = os.path.splitext(os.path.basename(self.filepath))
        obj = bpy.data.objects[self.object_name]
        material = dm.retrieve_data_from_library(self.filepath)
        list_slot = []
        for index, slot in enumerate(obj.mv.material_slot_col):
            if self.add_to_slot[index]:
                list_slot.append(index)
                
        if len(list_slot) > 0:
            obj.mv.assign_material_to_object(obj.name,material,list_slot)
        return{'FINISHED'}

    def draw(self, context):
        layout = self.layout
        obj = bpy.data.objects[self.object_name]
        for index, slot in enumerate(obj.mv.material_slot_col):
            layout.prop(self,"add_to_slot",index=index,text=slot.name)

#------REGISTER
classes = [
           OPS_drag_and_drop,
           OPS_place_product,
           OPS_place_extrusion,
           OPS_place_material
           ]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
