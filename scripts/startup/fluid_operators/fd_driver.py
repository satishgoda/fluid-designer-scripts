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

import bpy,os

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

import math

enum_group_drivers_tabs = [('LOC_X',"Location X","Location X"),
                           ('LOC_Y',"Location Y","Location Y"),
                           ('LOC_Z',"Location Z","Location Z"),
                           ('ROT_X',"Rotation X","Rotation X"),
                           ('ROT_Y',"Rotation Y","Rotation Y"),
                           ('ROT_Z',"Rotation Z","Rotation Z"),
                           ('DIM_X',"Dimension X","Dimension X"),
                           ('DIM_Y',"Dimension Y","Dimension Y"),
                           ('DIM_Z',"Dimension Z","Dimension Z")]

class OPS_turn_on_driver(Operator):
    bl_idname = "fd_driver.turn_on_driver"
    bl_label = "Turn On Driver"
    bl_options = {'UNDO'}

    group_name = StringProperty(name="Group Name")
    
    @classmethod
    def poll(cls, context):
        return True

    def invoke(self,context,event):
        ui = context.scene.mv.ui
        grp = bpy.data.groups[self.group_name]
        obj_bp = grp.mv.get_bp()
        obj_bp.select = True
        if ui.group_driver_tabs == 'LOC_X':
            obj_bp.driver_add('location',0)
        if ui.group_driver_tabs == 'LOC_Y':
            obj_bp.driver_add('location',1)
        if ui.group_driver_tabs == 'LOC_Z':
            obj_bp.driver_add('location',2)
        if ui.group_driver_tabs == 'ROT_X':
            obj_bp.driver_add('rotation_euler',0)
        if ui.group_driver_tabs == 'ROT_Y':
            obj_bp.driver_add('rotation_euler',1)
        if ui.group_driver_tabs == 'ROT_Z':
            obj_bp.driver_add('rotation_euler',2)
        if ui.group_driver_tabs == 'DIM_X':
            obj_x = grp.mv.get_x()
            obj_x.select = True
            obj_x.driver_add('location',0)
        if ui.group_driver_tabs == 'DIM_Y':
            obj_y = grp.mv.get_y()
            obj_y.select = True
            obj_y.driver_add('location',1)
        if ui.group_driver_tabs == 'DIM_Z':
            obj_z = grp.mv.get_z()
            obj_z.select = True
            obj_z.driver_add('location',2)
        if ui.group_driver_tabs == 'PROMPTS':
            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=400)
        return {'FINISHED'}

    def draw(self, context):
        grp = bpy.data.groups[self.group_name]
        obj_bp = grp.mv.get_bp()
        if obj_bp.parent:
            if len(obj_bp.parent.mv.PromptPage.COL_Prompt) > 0:
                layout = self.layout
                layout.template_list("FD_UL_promptitems"," ", obj_bp.mv.PromptPage, "COL_Prompt", obj_bp.mv.PromptPage, "PromptIndex",rows=len(obj_bp.mv.PromptPage.COL_Prompt))

    def execute(self, context):
        ui = context.scene.mv.ui
        grp = bpy.data.groups[self.group_name]
        obj_bp = grp.mv.get_bp()
        obj_bp.select = True
        if ui.group_driver_tabs == 'PROMPTS':
            prompt = obj_bp.mv.PromptPage.COL_Prompt[obj_bp.mv.PromptPage.PromptIndex]
            if prompt.Type == 'NUMBER':
                obj_bp.driver_add('mv.PromptPage.COL_Prompt["'+ prompt.name + '"].NumberValue')
            if prompt.Type == 'QUANTITY':
                obj_bp.driver_add('mv.PromptPage.COL_Prompt["'+ prompt.name + '"].QuantityValue')
            if prompt.Type == 'COMBOBOX':
                obj_bp.driver_add('mv.PromptPage.COL_Prompt["'+ prompt.name + '"].EnumIndex')
            if prompt.Type == 'CHECKBOX':
                obj_bp.driver_add('mv.PromptPage.COL_Prompt["'+ prompt.name + '"].CheckBoxValue')
        return {'FINISHED'}

class OPS_add_variable_to_object(Operator):
    bl_idname = "fd_driver.add_variable_to_object"
    bl_label = "Add Variable To Object"
    bl_options = {'UNDO'}
    
    object_name = StringProperty(name='Object Name')
    data_path = StringProperty(name='Data Path')
    array_index = IntProperty(name='Array Index')
    type = EnumProperty(name="Active Library Type",
                    items=[("OBJECT","Object","Object"),("SCENE","Scene","Scene")],
                    default='OBJECT')

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene
        obj_bp = bpy.data.objects[self.object_name]
        for DR in obj_bp.animation_data.drivers:
            if self.data_path in DR.data_path and DR.array_index == self.array_index:
                var = DR.driver.variables.new()
                var.targets[0].id_type = self.type
                if self.type == 'SCENE':
                    var.targets[0].id = scene    
                else:
                    var.targets[0].id = None                                         
                var.type = 'SINGLE_PROP'
                for target in var.targets:
                    target.transform_space = 'LOCAL_SPACE'
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'type')

class OPS_add_data_path_to_variable(Operator):
    bl_idname = "fd_driver.add_data_path_to_variable"
    bl_label = "Add Data Path to Variable"
    bl_options = {'UNDO'}
    
    target_data_path = StringProperty(name='Target Data Path')
    object_name = StringProperty(name='Object Name')
    variable_name = StringProperty(name='Variable Name')
    data_path = StringProperty(name='Data Path')
    array_index = IntProperty(name='Array Index')
    type = EnumProperty(name="Active Library Type",
                    items=[("OBJECT","Object","Object"),("SCENE","Scene","Scene")],
                    default='OBJECT')

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj_bp = bpy.data.objects[self.object_name]
        for DR in obj_bp.animation_data.drivers:
            if self.data_path in DR.data_path and DR.array_index == self.array_index:
                for var in DR.driver.variables:   
                    if var.name == self.variable_name:                              
                        var.type = 'SINGLE_PROP'
                        for target in var.targets:
                            target.transform_space = 'LOCAL_SPACE'
                            target.data_path = self.target_data_path
                            return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'target_data_path')

class OPS_add_variable_from_scene_prompt_to_object(Operator):
    bl_idname = "fd_driver.add_variable_from_scene_prompt_to_object"
    bl_label = "Add Variable From Scene Prompt To Object"
    bl_options = {'UNDO'}
    
    object_name = StringProperty(name='Object Name')
    data_path = StringProperty(name='Data Path')
    array_index = IntProperty(name='Array Index')
#     type = StringProperty(name='Type')

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene
        obj_bp = bpy.data.objects[self.object_name]
        PromptName = scene.mv.PromptPage.COL_Prompt[scene.mv.PromptPage.PromptIndex].name
        PromptType = scene.mv.PromptPage.COL_Prompt[scene.mv.PromptPage.PromptIndex].Type
        for DR in obj_bp.animation_data.drivers:
            if self.data_path in DR.data_path and DR.array_index == self.array_index:
                var = DR.driver.variables.new()
                var.name = PromptName.replace(" ","_")
                var.targets[0].id_type = 'SCENE'
                var.targets[0].id = scene
                if PromptType == 'NUMBER':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].NumberValue'
                if PromptType == 'QUANTITY':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].QuantityValue'
                if PromptType == 'COMBOBOX':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].EnumIndex'
                if PromptType == 'CHECKBOX':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].CheckBoxValue'
                if PromptType == 'TEXT':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].TextValue'                                                 
                var.type = 'SINGLE_PROP'
                for target in var.targets:
                    target.transform_space = 'LOCAL_SPACE'
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        layout.template_list("FD_UL_promptitems"," ", scene.mv.PromptPage, "COL_Prompt", scene.mv.PromptPage, "PromptIndex",rows=len(scene.mv.PromptPage.COL_Prompt))

class OPS_add_variable_from_group_prompt_to_object(Operator):
    bl_idname = "fd_driver.add_variable_from_group_prompt_to_object"
    bl_label = "Add Variable From Group Prompt To Object"
    bl_options = {'UNDO'}
    
    group_name = StringProperty(name='Group Name')
    object_name = StringProperty(name='Object Name')
    data_path = StringProperty(name='Data Path')
    array_index = IntProperty(name='Array Index')

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        grp = bpy.data.groups[self.group_name]
        obj_bp = grp.mv.get_bp()
        obj = bpy.data.objects[self.object_name]
        PromptName = obj_bp.mv.PromptPage.COL_Prompt[obj_bp.mv.PromptPage.PromptTempIndex].name
        PromptType = obj_bp.mv.PromptPage.COL_Prompt[obj_bp.mv.PromptPage.PromptTempIndex].Type
        for DR in obj.animation_data.drivers:
            if self.data_path in DR.data_path and DR.array_index == self.array_index:
                var = DR.driver.variables.new()
                var.name = PromptName.replace(" ","_")
                var.targets[0].id = obj_bp
                if PromptType == 'NUMBER':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].NumberValue'
                if PromptType == 'QUANTITY':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].QuantityValue'
                if PromptType == 'COMBOBOX':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].EnumIndex'
                if PromptType == 'CHECKBOX':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].CheckBoxValue'
                if PromptType == 'TEXT':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].TextValue'                                                 
                var.type = 'SINGLE_PROP'
                for target in var.targets:
                    target.transform_space = 'LOCAL_SPACE'
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        grp = bpy.data.groups[self.group_name]
        obj_bp = grp.mv.get_bp()
        layout = self.layout
        layout.template_list("FD_UL_promptitems"," ", obj_bp.mv.PromptPage, "COL_Prompt", obj_bp.mv.PromptPage, "PromptTempIndex",rows=len(obj_bp.mv.PromptPage.COL_Prompt))


class OPS_add_variable_from_group_property_to_object(Operator):
    bl_idname = "fd_driver.add_variable_from_group_property_to_object"
    bl_label = "Add Variable From Group Property To Object"
    bl_options = {'UNDO'}
    
    group_name = StringProperty(name='Group Name')
    object_name = StringProperty(name='Object Name')
    data_path = StringProperty(name='Data Path')
    array_index = IntProperty(name='Array Index')
    property = EnumProperty(name='Property',items=enum_group_drivers_tabs)
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        grp = bpy.data.groups[self.group_name]
        obj = bpy.data.objects[self.object_name]
        for DR in obj.animation_data.drivers:
            if self.data_path in DR.data_path and DR.array_index == self.array_index:
                var = DR.driver.variables.new()
                
                if self.property == 'LOC_X':
                    var.name = 'loc_x'
                    var.targets[0].id = grp.mv.get_bp()
                    var.targets[0].data_path = 'location.x'
                if self.property == 'LOC_Y':
                    var.name = 'loc_y'
                    var.targets[0].id = grp.mv.get_bp()
                    var.targets[0].data_path = 'location.y'
                if self.property == 'LOC_Z':
                    var.name = 'loc_z'
                    var.targets[0].id = grp.mv.get_bp()
                    var.targets[0].data_path = 'location.z'
                if self.property == 'ROT_X':
                    var.name = 'rot_x'
                    var.targets[0].id = grp.mv.get_bp()
                    var.targets[0].data_path = 'rotation_euler.x'
                if self.property == 'ROT_Y':
                    var.name = 'rot_y'
                    var.targets[0].id = grp.mv.get_bp()
                    var.targets[0].data_path = 'rotation_euler.y'
                if self.property == 'ROT_Z':
                    var.name = 'rot_z'
                    var.targets[0].id = grp.mv.get_bp()
                    var.targets[0].data_path = 'rotation_euler.z'
                if self.property == 'DIM_X':
                    var.name = 'dim_x'
                    var.targets[0].id = grp.mv.get_x()
                    var.targets[0].data_path = 'location.x'
                if self.property == 'DIM_Y':
                    var.name = 'dim_y'
                    var.targets[0].id = grp.mv.get_y()
                    var.targets[0].data_path = 'location.y'
                if self.property == 'DIM_Z':
                    var.name = 'dim_z'
                    var.targets[0].id = grp.mv.get_z()
                    var.targets[0].data_path = 'location.z'      

                var.type = 'SINGLE_PROP'
                for target in var.targets:
                    target.transform_space = 'LOCAL_SPACE'
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'property')
        
class OPS_add_variable_from_parent_group_prompt_to_object(Operator):
    bl_idname = "fd_driver.add_variable_from_parent_group_prompt_to_object"
    bl_label = "Add Variable From Parent Group Prompt To Object"
    bl_options = {'UNDO'}
    
    group_name = StringProperty(name='Group Name')
    object_name = StringProperty(name='Object Name')
    data_path = StringProperty(name='Data Path')
    array_index = IntProperty(name='Array Index')

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        grp = bpy.data.groups[self.group_name]
        obj_bp = grp.mv.get_bp().parent
        obj = bpy.data.objects[self.object_name]
        PromptName = obj_bp.mv.PromptPage.COL_Prompt[obj_bp.mv.PromptPage.PromptTempIndex].name
        PromptType = obj_bp.mv.PromptPage.COL_Prompt[obj_bp.mv.PromptPage.PromptTempIndex].Type
        for DR in obj.animation_data.drivers:
            if self.data_path in DR.data_path and DR.array_index == self.array_index:
                var = DR.driver.variables.new()
                var.name = PromptName.replace(" ","_")
                var.targets[0].id = obj_bp
                if PromptType == 'NUMBER':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].NumberValue'
                if PromptType == 'QUANTITY':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].QuantityValue'
                if PromptType == 'COMBOBOX':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].EnumIndex'
                if PromptType == 'CHECKBOX':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].CheckBoxValue'
                if PromptType == 'TEXT':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].TextValue'                                                 
                var.type = 'SINGLE_PROP'
                for target in var.targets:
                    target.transform_space = 'LOCAL_SPACE'
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        grp = bpy.data.groups[self.group_name]
        obj_bp = grp.mv.get_bp().parent
        layout = self.layout
        layout.template_list("FD_UL_promptitems"," ", obj_bp.mv.PromptPage, "COL_Prompt", obj_bp.mv.PromptPage, "PromptTempIndex",rows=len(obj_bp.mv.PromptPage.COL_Prompt))

class OPS_add_variable_from_product_group_prompt_to_object(Operator):
    #TODO: Consolidate with the other add prompt var operators. 
    bl_idname = "fd_driver.add_variable_from_product_group_prompt_to_object"
    bl_label = "Add Variable From Product Group Prompt To Object"
    bl_options = {'UNDO'}
    
    group_name = StringProperty(name='Group Name')
    object_name = StringProperty(name='Object Name')
    data_path = StringProperty(name='Data Path')
    array_index = IntProperty(name='Array Index')

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        grp = bpy.data.groups[self.group_name]
        obj_bp = grp.mv.get_bp().parent.parent
        obj = bpy.data.objects[self.object_name]
        PromptName = obj_bp.mv.PromptPage.COL_Prompt[obj_bp.mv.PromptPage.PromptTempIndex].name
        PromptType = obj_bp.mv.PromptPage.COL_Prompt[obj_bp.mv.PromptPage.PromptTempIndex].Type
        for DR in obj.animation_data.drivers:
            if self.data_path in DR.data_path and DR.array_index == self.array_index:
                var = DR.driver.variables.new()
                var.name = PromptName.replace(" ","_")
                var.targets[0].id = obj_bp
                if PromptType == 'NUMBER':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].NumberValue'
                if PromptType == 'QUANTITY':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].QuantityValue'
                if PromptType == 'COMBOBOX':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].EnumIndex'
                if PromptType == 'CHECKBOX':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].CheckBoxValue'
                if PromptType == 'TEXT':
                    var.targets[0].data_path = 'mv.PromptPage.COL_Prompt["' + PromptName + '"].TextValue'                                                 
                var.type = 'SINGLE_PROP'
                for target in var.targets:
                    target.transform_space = 'LOCAL_SPACE'
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        grp = bpy.data.groups[self.group_name]
        obj_bp = grp.mv.get_bp().parent.parent
        layout = self.layout
        layout.template_list("FD_UL_promptitems"," ", obj_bp.mv.PromptPage, "COL_Prompt", obj_bp.mv.PromptPage, "PromptTempIndex",rows=len(obj_bp.mv.PromptPage.COL_Prompt))

class OPS_remove_variable(Operator):
    bl_idname = "fd_driver.remove_variable"
    bl_label = "Remove Variable"
    bl_options = {'UNDO'}
    
    object_name = StringProperty(name='Object Name')
    data_path = StringProperty(name='Data Path')
    var_name = StringProperty(name='Variable Name')
    array_index = IntProperty(name='Array Index')

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = bpy.data.objects[self.object_name]
        for DR in obj.animation_data.drivers:
            if DR.data_path == self.data_path:
                if DR.array_index == self.array_index:
                    for var in DR.driver.variables:
                        if var.name == self.var_name:
                            DR.driver.variables.remove(var)
        return {'FINISHED'}

#------REGISTER
classes = [
           OPS_turn_on_driver,
           OPS_add_variable_to_object,
           OPS_add_variable_from_group_property_to_object,
           OPS_add_variable_from_scene_prompt_to_object,
           OPS_add_variable_from_group_prompt_to_object,
           OPS_add_variable_from_product_group_prompt_to_object,
           OPS_remove_variable,
           OPS_add_data_path_to_variable,
           OPS_add_variable_from_parent_group_prompt_to_object
           ]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
