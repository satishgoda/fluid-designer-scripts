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
import ENUM


class MENU_Project_Library(bpy.types.Menu):
    bl_label = "Project Library"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        prop = layout.operator("fluidlibrary.change_library",text="Project Library",icon='RENDERLAYERS')
        layout.separator()
        prop2 = layout.operator("fluidlibrary.add_library",text="Add Library",icon='ZOOMIN')
        prop2.LibraryType = 'MATERIALS'

class MENU_Project_Library_Category(bpy.types.Menu):
    bl_label = "Project Library Categories"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        layout.operator("fluidlibrary.change_library_category",text="Sample Projects",icon='FILE_FOLDER')
        layout.operator("fluidlibrary.change_library_category",text="My Templates",icon='FILE_FOLDER')

class MENU_Material_Library(bpy.types.Menu):
    bl_label = "Material Library"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        for index, MaterialLibrary in enumerate(LibrarySet.COL_MaterialLibrary):
            prop = layout.operator("fluidlibrary.change_library",text=MaterialLibrary.name,icon='MATERIAL')
            prop.LibraryIndex = index
            prop.LibraryType = 'MATERIAL'
        layout.separator()
        prop2 = layout.operator("fluidlibrary.add_library",text="Add Library",icon='ZOOMIN')
        prop2.LibraryType = 'MATERIALS'

class MENU_Material_Library_Category(bpy.types.Menu):
    bl_label = "Material Library Categories"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        MaterialLibrary = LibrarySet.COL_MaterialLibrary[LibrarySet.MaterialLibraryIndex]
        for index, Category in enumerate(MaterialLibrary.MaterialLibrary.COL_Category):
            prop = layout.operator("fluidlibrary.change_library_category",text=MaterialLibrary.MaterialLibrary.COL_Category[index].name,icon='FILE_FOLDER')
            prop.CategoryIndex = index
            prop.LibraryType = 'MATERIAL'

class MENU_Material_Library_Material(bpy.types.Menu):
    bl_label = "Material Library Material"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        MaterialLibrary = LibrarySet.COL_MaterialLibrary[LibrarySet.MaterialLibraryIndex]
        for index, Group in enumerate(MaterialLibrary.MaterialLibrary.COL_RenderingMaterial):
            prop = layout.operator("fluidlibrary.change_library_group",text=MaterialLibrary.MaterialLibrary.COL_RenderingMaterial[index].name,icon='MATERIAL')
            prop.GroupIndex = index
            prop.LibraryType = 'MATERIAL'         

class MENU_Part_Library(bpy.types.Menu):
    bl_label = "Part Library"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        for index, PartLibrary in enumerate(LibrarySet.COL_PartLibrary):
            prop = layout.operator("fluidlibrary.change_library",text=PartLibrary.name,icon='EXTERNAL_DATA')
            prop.LibraryIndex = index
            prop.LibraryType = 'PART'
        layout.separator()
        prop2 = layout.operator("fluidlibrary.add_library",text="Add Library",icon='ZOOMIN')
        prop2.LibraryType = 'PARTS'

class MENU_Part_Library_Category(bpy.types.Menu):
    bl_label = "Part Library Categories"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        PartLibrary = LibrarySet.COL_PartLibrary[LibrarySet.PartLibraryIndex]
        for index, Category in enumerate(PartLibrary.GroupLibrary.COL_Category):
            prop = layout.operator("fluidlibrary.change_library_category",text=PartLibrary.GroupLibrary.COL_Category[index].name,icon='FILE_FOLDER')
            prop.CategoryIndex = index
            prop.LibraryType = 'PART'
            
class MENU_Part_Library_Group(bpy.types.Menu):
    bl_label = "Part Library Group"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        PartLibrary = LibrarySet.COL_PartLibrary[LibrarySet.PartLibraryIndex]
        for index, Group in enumerate(PartLibrary.GroupLibrary.COL_Group):
            prop = layout.operator("fluidlibrary.change_library_group",text=PartLibrary.GroupLibrary.COL_Group[index].name,icon='MOD_MESHDEFORM')
            prop.GroupIndex = index
            prop.LibraryType = 'PART'
            
class MENU_Insert_Library(bpy.types.Menu):
    bl_label = "Insert Library"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        for index, Library in enumerate(LibrarySet.COL_InsertLibrary):
            prop = layout.operator("fluidlibrary.change_library",text=Library.name,icon='EXTERNAL_DATA')
            prop.LibraryIndex = index
            prop.LibraryType = 'INSERT'
        layout.separator()
        prop2 = layout.operator("fluidlibrary.add_library",text="Add Library",icon='ZOOMIN')
        prop2.LibraryType = 'INSERTS'


class MENU_Insert_Library_Category(bpy.types.Menu):
    bl_label = "Insert Library Categories"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        Library = LibrarySet.COL_InsertLibrary[LibrarySet.InsertLibraryIndex]
        for index, Category in enumerate(Library.GroupLibrary.COL_Category):
            prop = layout.operator("fluidlibrary.change_library_category",text=Category.name,icon='FILE_FOLDER')
            prop.CategoryIndex = index
            prop.LibraryType = 'INSERT'
            
class MENU_Insert_Library_Group(bpy.types.Menu):
    bl_label = "Insert Library Group"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        Library = LibrarySet.COL_InsertLibrary[LibrarySet.InsertLibraryIndex]
        for index, Group in enumerate(Library.GroupLibrary.COL_Group):
            prop = layout.operator("fluidlibrary.change_library_group",text=Library.GroupLibrary.COL_Group[index].name,icon='STICKY_UVS_LOC')
            prop.GroupIndex = index
            prop.LibraryType = 'INSERT'
            
class MENU_Product_Library(bpy.types.Menu):
    bl_label = "Product Library"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        for index, Library in enumerate(LibrarySet.COL_ProductLibrary):
            prop = layout.operator("fluidlibrary.change_library",text=Library.name,icon='EXTERNAL_DATA')
            prop.LibraryIndex = index
            prop.LibraryType = 'PRODUCT'
        layout.separator()
        prop2 = layout.operator("fluidlibrary.add_library",text="Add Library",icon='ZOOMIN')
        prop2.LibraryType = 'PRODUCTS'

class MENU_Product_Library_Category(bpy.types.Menu):
    bl_label = "Product Library Categories"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        Library = LibrarySet.COL_ProductLibrary[LibrarySet.ProductLibraryIndex]
        for index, Category in enumerate(Library.GroupLibrary.COL_Category):
            prop = layout.operator("fluidlibrary.change_library_category",text=Category.name,icon='FILE_FOLDER')
            prop.CategoryIndex = index
            prop.LibraryType = 'PRODUCT'
            
class MENU_Product_Library_Group(bpy.types.Menu):
    bl_label = "Product Library Group"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        Library = LibrarySet.COL_ProductLibrary[LibrarySet.ProductLibraryIndex]
        for index, Group in enumerate(Library.GroupLibrary.COL_Group):
            prop = layout.operator("fluidlibrary.change_library_group",text=Group.name,icon='MOD_MESHDEFORM')
            prop.GroupIndex = index
            prop.LibraryType = 'PRODUCT'
            
class MENU_Curve_Library(bpy.types.Menu):
    bl_label = "Curve Library"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        for index, CurveLibrary in enumerate(LibrarySet.COL_CurveLibrary):
            prop = layout.operator("fluidlibrary.change_library",text=CurveLibrary.name,icon='EXTERNAL_DATA')
            prop.LibraryIndex = index
            prop.LibraryType = 'CURVE'
        layout.separator()
        prop2 = layout.operator("fluidlibrary.add_library",text="Add Library",icon='ZOOMIN')
        prop2.LibraryType = 'CURVE'    
                

class MENU_Curve_Library_Category(bpy.types.Menu):
    bl_label = "Curve Library Categories"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        CurveLibrary = LibrarySet.COL_CurveLibrary[LibrarySet.CurveLibraryIndex]
        for index, Category in enumerate(CurveLibrary.GroupLibrary.COL_Category):
            prop = layout.operator("fluidlibrary.change_library_category",text=CurveLibrary.GroupLibrary.COL_Category[index].name,icon='FILE_FOLDER')
            prop.CategoryIndex = index
            prop.LibraryType = 'CURVE'    
            
class MENU_Object_Library(bpy.types.Menu):
    bl_label = "Object Library"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        for index, ObjectLibrary in enumerate(LibrarySet.COL_ObjectLibrary):
            prop = layout.operator("fluidlibrary.change_library",text=ObjectLibrary.name,icon='EXTERNAL_DATA')
            prop.LibraryIndex = index
            prop.LibraryType = 'OBJECT'
        layout.separator()
        prop2 = layout.operator("fluidlibrary.add_library",text="Add Library",icon='ZOOMIN')
        prop2.LibraryType = 'OBJECT'    
                

class MENU_Object_Library_Category(bpy.types.Menu):
    bl_label = "Object Library Categories"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        ObjectLibrary = LibrarySet.COL_ObjectLibrary[LibrarySet.ObjectLibraryIndex]
        for index, Category in enumerate(ObjectLibrary.GroupLibrary.COL_Category):
            prop = layout.operator("fluidlibrary.change_library_category",text=ObjectLibrary.GroupLibrary.COL_Category[index].name,icon='FILE_FOLDER')
            prop.CategoryIndex = index
            prop.LibraryType = 'OBJECT'               
                    
class MENU_Group_Library(bpy.types.Menu):
    bl_label = "Group Library"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        for index, GroupLibrary in enumerate(LibrarySet.COL_GroupLibrary):
            prop = layout.operator("fluidlibrary.change_library",text=GroupLibrary.name,icon='EXTERNAL_DATA')
            prop.LibraryIndex = index
            prop.LibraryType = 'GROUP'
        layout.separator()
        prop2 = layout.operator("fluidlibrary.add_library",text="Add Library",icon='ZOOMIN')
        prop2.LibraryType = 'GROUP'    
                

class MENU_Group_Library_Category(bpy.types.Menu):
    bl_label = "Group Library Categories"

    def draw(self, context):
        layout = self.layout
        LibrarySet = context.scene.world.mv
        GroupLibrary = LibrarySet.COL_GroupLibrary[LibrarySet.GroupLibraryIndex]
        for index, Category in enumerate(GroupLibrary.GroupLibrary.COL_Category):
            prop = layout.operator("fluidlibrary.change_library_category",text=GroupLibrary.GroupLibrary.COL_Category[index].name,icon='FILE_FOLDER')
            prop.CategoryIndex = index
            prop.LibraryType = 'GROUP'                      
                    


#------REGISTER
classes = [
           MENU_Project_Library,
           MENU_Project_Library_Category,
           MENU_Material_Library,
           MENU_Material_Library_Category,
           MENU_Material_Library_Material,
           MENU_Part_Library,
           MENU_Part_Library_Category,
           MENU_Part_Library_Group,
           MENU_Insert_Library,
           MENU_Insert_Library_Category,
           MENU_Insert_Library_Group,
           MENU_Product_Library,
           MENU_Product_Library_Category,
           MENU_Product_Library_Group,
           MENU_Curve_Library,
           MENU_Curve_Library_Category,
           MENU_Object_Library,
           MENU_Object_Library_Category,
           MENU_Group_Library,
           MENU_Group_Library_Category,
           MENU_Specgroup_Tabs
           ]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
