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

from fd_datablocks import enums

class OPS_add_prompt(Operator):
    bl_idname = "fd_prompts.add_prompt"
    bl_label = "Add Prompt"
    bl_options = {'UNDO'}
    
    prompt_name = StringProperty(name="Prompt Name",default = "New Prompt")
    prompt_type = EnumProperty(name="Prompt Type",items=enums.enum_prompt_types)
    data_name = StringProperty(name="Data Name")
    data_type = StringProperty(name="Data Type",default = 'OBJECT')
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.data_type == 'OBJECT':
            obj = bpy.data.objects[self.data_name]
            if self.prompt_name not in obj.mv.PromptPage.COL_Prompt:
                prompt = obj.mv.PromptPage.add_prompt(self.prompt_name,self.prompt_type,obj.name)
                prompt.TabIndex = obj.mv.PromptPage.MainTabIndex
        elif self.data_type == 'SCENE':
            obj = bpy.data.scenes[self.data_name]
            if self.prompt_name not in obj.mv.PromptPage.COL_Prompt:
                prompt = obj.mv.PromptPage.add_prompt(self.prompt_name,self.prompt_type,obj.name)
                prompt.TabIndex = obj.mv.PromptPage.MainTabIndex
        elif self.data_type == 'MATERIAL':
            obj = bpy.data.materials[self.data_name]
            if self.prompt_name not in obj.mv.PromptPage.COL_Prompt:
                prompt = obj.mv.PromptPage.add_prompt(self.prompt_name,self.prompt_type,obj.name)
                prompt.TabIndex = obj.mv.PromptPage.MainTabIndex
        elif self.data_type == 'WORLD':
            obj = bpy.data.worlds[self.data_name]
            if self.prompt_name not in obj.mv.PromptPage.COL_Prompt:
                prompt = obj.mv.PromptPage.add_prompt(self.prompt_name,self.prompt_type,obj.name)
                prompt.TabIndex = obj.mv.PromptPage.MainTabIndex
        return {'FINISHED'}

    def invoke(self,context,event):
        if self.data_type == 'OBJECT':
            data = bpy.data.objects[self.data_name]
            Counter = 1
            while self.prompt_name + " " + str(Counter) in data.mv.PromptPage.COL_Prompt:
                Counter += 1
            self.prompt_name = self.prompt_name + " " + str(Counter)        

        elif self.data_type == 'SCENE':
            data = bpy.data.scenes[self.data_name]
            Counter = 1
            while self.prompt_name + " " + str(Counter) in data.mv.PromptPage.COL_Prompt:
                Counter += 1
            self.prompt_name = self.prompt_name + " " + str(Counter)    
            
        elif self.data_type == 'MATERIAL':
            data = bpy.data.materials[self.data_name]
            Counter = 1
            while self.prompt_name + " " + str(Counter) in data.mv.PromptPage.COL_Prompt:
                Counter += 1
            self.prompt_name = self.prompt_name + " " + str(Counter)    
            
        elif self.data_type == 'WORLD':
            data = bpy.data.worlds[self.data_name]
            Counter = 1
            while self.prompt_name + " " + str(Counter) in data.mv.PromptPage.COL_Prompt:
                Counter += 1
            self.prompt_name = self.prompt_name + " " + str(Counter)    
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=380)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self,"prompt_name")
        layout.prop(self,"prompt_type")

class OPS_delete_prompt(Operator):
    bl_idname = "fd_prompts.delete_prompt"
    bl_label = "Delete Prompt"
    bl_options = {'UNDO'}
    
    prompt_name = StringProperty(name="Prompt Name",default = "New Prompt")
    data_name = StringProperty(name="Data Name")
    data_type = StringProperty(name="Data Type",default = 'OBJECT')
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.data_type == 'OBJECT':
            obj = bpy.data.objects[self.data_name]
            obj.mv.PromptPage.delete_prompt(self.prompt_name)
        elif self.data_type == 'SCENE':
            obj = bpy.data.scenes[self.data_name]
            obj.mv.PromptPage.delete_prompt(self.prompt_name)
        elif self.data_type == 'MATERIAL':
            obj = bpy.data.materials[self.data_name]
            obj.mv.PromptPage.delete_prompt(self.prompt_name)
        elif self.data_type == 'WORLD':
            obj = bpy.data.worlds[self.data_name]
            obj.mv.PromptPage.delete_prompt(self.prompt_name)
        return {'FINISHED'}

    def invoke(self,context,event):    
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        layout.label("Are you sure you want to delete the prompt?")

class OPS_delete_main_tab(Operator):
    bl_idname = "fd_prompts.delete_main_tab"
    bl_label = "Delete Main Tab"
    bl_options = {'UNDO'}

    data_name = StringProperty(name="Object Name")
    data_type = StringProperty(name="Data Type",default = 'OBJECT')
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.data_type == 'OBJECT':
            data = bpy.data.objects[self.data_name]
            data.mv.PromptPage.delete_selected_tab()
        elif self.data_type == 'SCENE':
            data = bpy.data.scenes[self.data_name]
            data.mv.PromptPage.delete_selected_tab()
        elif self.data_type == 'MATERIAL':
            data = bpy.data.materials[self.data_name]
            data.mv.PromptPage.delete_selected_tab()
        elif self.data_type == 'WORLD':
            data = bpy.data.worlds[self.data_name]
            data.mv.PromptPage.delete_selected_tab()
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        layout.label("Are you sure you want to delete the selected tab?")

class OPS_rename_main_tab(Operator):
    bl_idname = "fd_prompts.rename_main_tab"
    bl_label = "Rename Main Tab"

    data_name = StringProperty(name="Data Name")
    new_name = StringProperty(name="New Name",default="Enter New Name")
    data_type = StringProperty(name="Data Type",default = 'OBJECT')
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.data_type == 'OBJECT':
            data = bpy.data.objects[self.data_name]
            data.mv.PromptPage.rename_selected_tab(self.new_name)
        elif self.data_type == 'SCENE':
            data = bpy.data.scenes[self.data_name]
            data.mv.PromptPage.rename_selected_tab(self.new_name)
        elif self.data_type == 'MATERIAL':
            data = bpy.data.materials[self.data_name]
            data.mv.PromptPage.rename_selected_tab(self.new_name)
        elif self.data_type == 'WORLD':
            data = bpy.data.worlds[self.data_name]
            data.mv.PromptPage.rename_selected_tab(self.new_name)
        return {'FINISHED'}

    def invoke(self,context,event):    
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,"new_name")

class OPS_show_prompt_properties(Operator):
    bl_idname = "fd_prompts.show_prompt_properties"
    bl_label = "Show Prompt Properties"
    
    prompt_name = StringProperty(name="Prompt Name",default = "New Prompt")
    prompt_type = EnumProperty(name="Prompt Type",items=enums.enum_prompt_types)
    data_name = StringProperty(name="Data Name")
    data_type = StringProperty(name="Data Type",default = 'OBJECT')
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        if self.data_type == 'OBJECT':
            data = bpy.data.objects[self.data_name]
            data.mv.PromptPage.COL_Prompt[self.prompt_name].draw_prompt_properties(layout)
        elif self.data_type == 'SCENE':
            data = bpy.data.scenes[self.data_name]
            data.mv.PromptPage.COL_Prompt[self.prompt_name].draw_prompt_properties(layout)
        elif self.data_type == 'MATERIAL':
            data = bpy.data.materials[self.data_name]
            data.mv.PromptPage.COL_Prompt[self.prompt_name].draw_prompt_properties(layout)
        elif self.data_type == 'WORLD':
            data = bpy.data.worlds[self.data_name]
            data.mv.PromptPage.COL_Prompt[self.prompt_name].draw_prompt_properties(layout)
            
class OPS_add_main_tab(Operator):
    bl_idname = "fd_prompts.add_main_tab"
    bl_label = "Add Main Tab"
    bl_options = {'UNDO'}
    
    tab_name = StringProperty(name="Tab Name",default="New Tab")
    data_name = StringProperty(name="Data Name")
    data_type = StringProperty(name="Data Type",default = 'OBJECT')

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.data_type == 'OBJECT':
            data = bpy.data.objects[self.data_name]
            data.mv.PromptPage.add_tab(self.tab_name)
        elif self.data_type == 'SCENE':
            data = bpy.data.scenes[self.data_name]
            data.mv.PromptPage.add_tab(self.tab_name)
        elif self.data_type == 'MATERIAL':
            data = bpy.data.materials[self.data_name]
            data.mv.PromptPage.add_tab(self.tab_name)
        elif self.data_type == 'WORLD':
            data = bpy.data.worlds[self.data_name]
            data.mv.PromptPage.add_tab(self.tab_name)
        return {'FINISHED'}

    def invoke(self,context,event):
        if self.data_type == 'OBJECT':
            data = bpy.data.objects[self.data_name]
            Counter = 1
            while self.tab_name + " " + str(Counter) in data.mv.PromptPage.COL_MainTab:
                Counter += 1
            self.tab_name = self.tab_name + " " + str(Counter)
            
        elif self.data_type == 'SCENE':
            data = bpy.data.scenes[self.data_name]
            Counter = 1
            while self.tab_name + " " + str(Counter) in data.mv.PromptPage.COL_MainTab:
                Counter += 1
            self.tab_name = self.tab_name + " " + str(Counter)
            
        elif self.data_type == 'MATERIAL':
            data = bpy.data.materials[self.data_name]
            Counter = 1
            while self.tab_name + " " + str(Counter) in data.mv.PromptPage.COL_MainTab:
                Counter += 1
            self.tab_name = self.tab_name + " " + str(Counter)
            
        elif self.data_type == 'WORLD':
            data = bpy.data.worlds[self.data_name]
            Counter = 1
            while self.tab_name + " " + str(Counter) in data.mv.PromptPage.COL_MainTab:
                Counter += 1
            self.tab_name = self.tab_name + " " + str(Counter)
            
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,"tab_name")
        
class OPS_add_combo_box_option(Operator):
    bl_idname = "fd_prompts.add_combo_box_option"
    bl_label = "Add Combo Box Option"
    bl_options = {'UNDO'}
    
    data_name = StringProperty(name="Data Name")
    data_type = StringProperty(name="Data Type",default = 'OBJECT')
    prompt_name = StringProperty(name="Prompt Name")
    combo_box_value = StringProperty(name="Combo Box Value",default = "Option")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.data_type == 'OBJECT':
            data = bpy.data.objects[self.data_name]
            data.mv.PromptPage.COL_Prompt[self.prompt_name].add_enum_item(self.combo_box_value)
        elif self.data_type == 'SCENE':
            data = bpy.data.scenes[self.data_name]
            data.mv.PromptPage.COL_Prompt[self.prompt_name].add_enum_item(self.combo_box_value)
        elif self.data_type == 'MATERIAL':
            data = bpy.data.materials[self.data_name]
            data.mv.PromptPage.COL_Prompt[self.prompt_name].add_enum_item(self.combo_box_value)
        elif self.data_type == 'WORLD':
            data = bpy.data.worlds[self.data_name]
            data.mv.PromptPage.COL_Prompt[self.prompt_name].add_enum_item(self.combo_box_value)
        return {'FINISHED'}

    def invoke(self,context,event):
        if self.data_type == 'OBJECT':
            data = bpy.data.objects[self.data_name]
            Counter = 1
            while self.combo_box_value + " " + str(Counter) in data.mv.PromptPage.COL_Prompt[self.prompt_name].COL_EnumItem:
                Counter += 1
            self.combo_box_value = self.combo_box_value + " " + str(Counter)   
            
        elif self.data_type == 'SCENE':
            data = bpy.data.scenes[self.data_name]
            Counter = 1
            while self.combo_box_value + " " + str(Counter) in data.mv.PromptPage.COL_Prompt[self.prompt_name].COL_EnumItem:
                Counter += 1
            self.combo_box_value = self.combo_box_value + " " + str(Counter)   
            
        elif self.data_type == 'MATERIAL':
            data = bpy.data.materials[self.data_name]
            Counter = 1
            while self.combo_box_value + " " + str(Counter) in data.mv.PromptPage.COL_Prompt[self.prompt_name].COL_EnumItem:
                Counter += 1
            self.combo_box_value = self.combo_box_value + " " + str(Counter)   
            
        elif self.data_type == 'WORLD':
            data = bpy.data.worlds[self.data_name]
            Counter = 1
            while self.combo_box_value + " " + str(Counter) in data.mv.PromptPage.COL_Prompt[self.prompt_name].COL_EnumItem:
                Counter += 1
            self.combo_box_value = self.combo_box_value + " " + str(Counter)   
            
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,"combo_box_value")


#------REGISTER
classes = [
           OPS_add_prompt,
           OPS_delete_prompt,
           OPS_delete_main_tab,
           OPS_rename_main_tab,
           OPS_show_prompt_properties,
           OPS_add_main_tab,
           OPS_add_combo_box_option
           ]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
