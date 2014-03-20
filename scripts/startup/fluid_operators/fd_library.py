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
                       PointerProperty,
                       EnumProperty)

from fd_datablocks import enums

import os

class OPS_change_library(Operator):
    bl_idname = "fd_library.change_library"
    bl_label = "Change Library"

    library_index = IntProperty(name="Library Index")
    library_type = EnumProperty(name="Group Name",items=enums.enum_library_types)

    def execute(self, context):
        Libraries = context.scene.mv.dm.Libraries
        Libraries.index_active_pointer_library = self.library_index
        Library = Libraries.get_active_pointer_library()
        Library.load_categories()
        return {'FINISHED'}

class OPS_change_library_category(Operator):
    bl_idname = "fd_library.change_library_category"
    bl_label = "Change Library Category"

    category_index = IntProperty(name="Category Index")
    library_type = EnumProperty(name="Group Name",items=enums.enum_library_types)

    def execute(self, context):
        Libraries = context.scene.mv.dm.Libraries
        library = Libraries.get_active_pointer_library()
        library.Categories.index_category = self.category_index
        category = library.Categories.get_active_category()
        bpy.context.window_manager.mv.update_file_browser_parameters(category.path)
        return {'FINISHED'}
    
class OPS_change_library_group(Operator):
    bl_idname = "fd_library.change_library_group"
    bl_label = "Change Library Group"

    GroupIndex = IntProperty(name="Group Index")
    LibraryType = EnumProperty(name="Group Name",items=enums.enum_library_types)

    def execute(self, context):
        LibrarySet = context.scene.world.mv
        
        if self.LibraryType == 'MATERIAL':
            Library = LibrarySet.COL_MaterialLibrary[LibrarySet.MaterialLibraryIndex]
            Library.MaterialLibrary.RenderingMaterialIndex = self.GroupIndex

        if self.LibraryType == 'PRODUCT':
            Library = LibrarySet.COL_ProductLibrary[LibrarySet.ProductLibraryIndex]
            Library.GroupLibrary.GroupIndex = self.GroupIndex

        if self.LibraryType == 'INSERT':
            Library = LibrarySet.COL_InsertLibrary[LibrarySet.InsertLibraryIndex]
            Library.GroupLibrary.GroupIndex = self.GroupIndex
            
        if self.LibraryType == 'PART':
            Library = LibrarySet.COL_PartLibrary[LibrarySet.PartLibraryIndex]
            Library.GroupLibrary.GroupIndex = self.GroupIndex
            
        return {'FINISHED'}

class OPS_change_specgroup_tab(Operator):
    bl_idname = "fd_library.change_specgroup_tab"
    bl_label = "Change Spec Group Tab"

    tab_index = IntProperty(name="Tab String")

    def execute(self, context):
        SpecGroups = context.scene.mv.dm.Specgroups
        specgroup = SpecGroups.col_specgroup[SpecGroups.index_specgroup]
        specgroup.Tabs.index_tab = self.tab_index
        return {'FINISHED'}

class OPS_add_pointer(Operator):
    bl_idname = "fd_library.add_pointer"
    bl_label = "Add Pointer"
    bl_options = {'UNDO'}
    
    LibraryType = EnumProperty(name="LibraryType",items=enums.enum_library_types)
    PointerName = StringProperty(name="PointerName",default="New Pointer")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        #TODO: Implement Add Pointer
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.label("Enter the name of the pointer")
        layout.prop(self,"PointerName")

class OPS_delete_pointer(Operator):
    bl_idname = "fd_library.delete_pointer"
    bl_label = "Delete Pointer"
    bl_options = {'UNDO'}
    
    PointerName = StringProperty(name="PointerName")
    LibraryType = EnumProperty(name="LibraryType",items=enums.enum_library_types)
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        #TODO: Implement Delete Pointer
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label("Are you sure you want to delete the pointer?")

class OPS_add_library(Operator):
    bl_idname = "fd_library.add_library"
    bl_label = "Add Library"
    
    LibraryType = EnumProperty(name="LibraryType",items=enums.enum_library_types)
    LibraryName = StringProperty(name="Library Name")
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        #TODO: Implement Add Category
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def draw(self, context):
        pass

class OPS_add_category(Operator):
    bl_idname = "fd_library.add_category"
    bl_label = "Add Category"

    category_name = StringProperty(name="Category Name")
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        dm = context.scene.mv.dm
        library = dm.Libraries.get_active_pointer_library()
        if not os.path.exists(os.path.join(library.path,self.category_name)):
            os.makedirs(os.path.join(library.path,self.category_name))
        dm.Libraries.path = dm.Libraries.path
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'category_name')
    
class OPS_open_active_library_path(Operator):
    bl_idname = "fd_library.open_active_library_path"
    bl_label = "Open Active Library Path"
    
    category_name = StringProperty(name="Category Name")
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        dm = context.scene.mv.dm
        library = dm.Libraries.get_active_pointer_library()
        category = library.Categories.get_active_category()
        import subprocess
        subprocess.Popen(r'explorer /select,' + category.path)
        return {'FINISHED'}

class OPS_refresh_library(Operator):
    bl_idname = "fd_library.refresh_library"
    bl_label = "Refresh_library"
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        dm = context.scene.mv.dm
        dm.Libraries.path = dm.Libraries.path
        return {'FINISHED'}
    
#------REGISTER
classes = [
           OPS_change_library,
           OPS_change_library_category,
           OPS_change_library_group,
           OPS_change_specgroup_tab,
           OPS_add_category,
           OPS_open_active_library_path,
           OPS_refresh_library
           ]

def register():
    pass
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
