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
from bpy.types import Menu

#This class is used to store all of the dynamic pull down menus used for Fluid Designer

from fd_datablocks import const

class MENU_active_pointer_libraries(Menu):
    '''displays context.scene.mv.dm.Libraries.col_active_pointer_libraries'''
    bl_label = "Pointer Libraries"

    def draw(self, context):
        layout = self.layout
        Libraries = context.scene.mv.dm.Libraries
        active_libraries = Libraries.col_active_pointer_library
        for index, library in enumerate(active_libraries):
            prop = layout.operator("fd_library.change_library",text=library.name,icon=Libraries.get_active_library_icon())
            prop.library_index = index
            prop.library_type = library.type
            
class MENU_active_pointer_library_categories(Menu):
    '''displays active_pointer_library.col_categories'''
    bl_label = "Library Categories"

    def draw(self, context):
        layout = self.layout
        active_library = context.scene.mv.dm.Libraries.get_active_pointer_library()
        Categories = active_library.Categories
        for index, cat in enumerate(Categories.col_category):
            prop = layout.operator("fd_library.change_library_category",text=cat.name,icon=const.icon_category)
            prop.category_index = index
            prop.library_type = active_library.type
            
class MENU_active_library_category_items(Menu):
    '''displays context.scene.mv.dm.Libraries.col_active_pointer_libraries'''
    bl_label = "Product Library Group"

    def draw(self, context):
        pass #TODO: create menu for library category items

class MENU_Specgroup_Tabs(bpy.types.Menu):
    bl_label = "Group Library Categories"

    def draw(self, context):
        layout = self.layout
        SpecGroups = context.scene.mv.dm.Specgroups
        specgroup = SpecGroups.col_specgroup[SpecGroups.index_specgroup]
        for index, tab in enumerate(specgroup.Tabs.col_tab):
            prop = layout.operator("fd_library.change_specgroup_tab",text=tab.name,icon='FILE_FOLDER').tab_index = index

#------REGISTER
classes = [
           MENU_active_pointer_libraries,
           MENU_active_pointer_library_categories,
           MENU_active_library_category_items,
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
