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
from bpy.types import Header, Menu, Panel

class FILEBROWSER_HT_fluidheader(Header):
    bl_space_type = 'FILE_BROWSER'

    def draw(self, context):
        layout = self.layout
        st = context.space_data
        Libraries = context.scene.mv.dm.Libraries
        if not context.scene.mv.ui.use_default_blender_interface:
            layout.template_header()
            FILE_MT_fd_menus.draw_collapsible(context, layout)
        Libraries.draw_active_pointer_library_menus(layout)

class FILEBROWSER_MT_fd_filters(Menu):
    bl_label = "View"

    def draw(self, context):
        layout = self.layout
        st = context.space_data
        params = st.params
        
        if params:
            layout.prop(params, "use_filter", text="Use Filters", icon='FILTER')
            layout.separator()
            layout.operator("fd_general.dialog_show_filters",icon='INFO')

class FILEBROWSER_MT_fd_view(Menu):
    bl_label = "View"

    def draw(self, context):
        layout = self.layout
        layout.operator("file.previous", text="Back to Previous", icon='BACK')
        layout.separator()
        layout.operator("file.parent", text="Go to Parent", icon='FILE_PARENT')
        layout.operator("file.refresh", text="Refresh", icon='FILE_REFRESH')
        layout.separator()
        layout.operator_context = "EXEC_DEFAULT"
        layout.operator("file.directory_new", icon='NEWFOLDER')

class FILEBROWSER_MT_fd_navigation(Menu):
    bl_label = "Navigation"

    def draw(self, context):
        layout = self.layout
        st = context.space_data
        params = st.params
        if params:
            layout.prop(params, "use_filter", text="Use Filters", icon='FILTER')
            layout.prop(params, "use_filter_folder", text="Show Folders")
            layout.prop(params, "use_filter_blender", text="Show Blender Files")
            layout.prop(params, "use_filter_backup", text="Show Backup Files")
            layout.prop(params, "use_filter_image", text="Show Image Files")
            layout.prop(params, "use_filter_movie", text="Show Video Files")
            layout.prop(params, "use_filter_script", text="Show Script Files")
            layout.prop(params, "use_filter_font", text="Show Font Files")
            layout.prop(params, "use_filter_text", text="Show Text Files")


#     def draw(self, context):
#         layout = self.layout
# 
#         st = context.space_data
#         if context.scene.mv.ui.use_default_blender_interface:
#             layout.template_header()
#     
#             row = layout.row()
#             row.separator()
#     
#             row = layout.row(align=True)
#             row.operator("file.previous", text="", icon='BACK')
#             row.operator("file.next", text="", icon='FORWARD')
#             row.operator("file.parent", text="", icon='FILE_PARENT')
#             row.operator("file.refresh", text="", icon='FILE_REFRESH')
#     
#             row = layout.row()
#             row.separator()
#     
#             row = layout.row(align=True)
#             layout.operator_context = "EXEC_DEFAULT"
#             row.operator("file.directory_new", icon='NEWFOLDER')
#     
#             layout.operator_context = "INVOKE_DEFAULT"
#             params = st.params
#     
#             # can be None when save/reload with a file selector open
#             if params:
#                 layout.prop(params, "display_type", expand=True, text="")
#                 layout.prop(params, "sort_method", expand=True, text="")
#     
#                 layout.prop(params, "show_hidden")
#                 layout.prop(params, "use_filter", text="", icon='FILTER')
#     
#                 row = layout.row(align=True)
#                 row.active = params.use_filter
#     
#                 row.prop(params, "use_filter_folder", text="")
#     
#                 if params.filter_glob:
#                     #if st.active_operator and hasattr(st.active_operator, "filter_glob"):
#                     #    row.prop(params, "filter_glob", text="")
#                     row.label(params.filter_glob)
#                 else:
#                     row.prop(params, "use_filter_blender", text="")
#                     row.prop(params, "use_filter_backup", text="")
#                     row.prop(params, "use_filter_image", text="")
#                     row.prop(params, "use_filter_movie", text="")
#                     row.prop(params, "use_filter_script", text="")
#                     row.prop(params, "use_filter_font", text="")
#                     row.prop(params, "use_filter_sound", text="")
#                     row.prop(params, "use_filter_text", text="")
                    
class FILE_MT_fd_menus(Menu):
    bl_space_type = 'VIEW3D_MT_editor_menus'
    bl_label = ""

    def draw(self, context):
        self.draw_menus(self.layout, context)

    @staticmethod
    def draw_menus(layout, context):
        layout.menu("FILEBROWSER_MT_fd_view",icon='VIEWZOOM',text="     View     ")
        layout.menu("FILEBROWSER_MT_fd_filters",icon='FILTER',text="     Filters     ")

class PANEL_fluid_libraries(Panel):
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "CHANNELS"
    bl_label = " "
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        layout = self.layout
        layout.label(" ",icon='EXTERNAL_DATA')

    def draw(self, context):
        layout = self.layout
        Libraries = context.scene.mv.dm.Libraries
        Libraries.draw_library_tabs(layout)



#------REGISTER
classes = [
           FILEBROWSER_HT_fluidheader,
           FILE_MT_fd_menus,
           FILEBROWSER_MT_fd_filters,
           FILEBROWSER_MT_fd_view,
           FILEBROWSER_MT_fd_navigation,
           PANEL_fluid_libraries
           ]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
