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

class VIEW3D_HT_fluidheader(Header):
    bl_space_type = 'VIEW_3D'

    def draw(self, context):
        layout = self.layout

        if not context.scene.mv.ui.use_default_blender_interface:
            view = context.space_data
            mode_string = context.mode
            edit_object = context.edit_object
            obj = context.active_object
            toolsettings = context.tool_settings
    
            row = layout.row(align=True)
            row.template_header()
            
            VIEW3D_MT_fd_menus.draw_collapsible(context, layout)
            
            if context.space_data.viewport_shade == 'WIREFRAME':
                layout.operator_menu_enum("fd_general.change_shademode","shade_mode",text="Wire Frame",icon='WIRE')
            if context.space_data.viewport_shade == 'SOLID':
                layout.operator_menu_enum("fd_general.change_shademode","shade_mode",text="Solid        ",icon='SOLID')
            if context.space_data.viewport_shade == 'MATERIAL':
                layout.operator_menu_enum("fd_general.change_shademode","shade_mode",text="Material     ",icon='MATERIAL')
            if context.space_data.viewport_shade == 'RENDERED':
                layout.operator_menu_enum("fd_general.change_shademode","shade_mode",text="Rendered    ",icon='SMOOTH')
            
            row = layout.row(align=True)
            row.prop(context.space_data,"show_manipulator",text="")
            row.prop(context.space_data,"transform_manipulators",text="")
            row.prop(context.space_data,"transform_orientation",text="")
        
            if not obj or obj.mode not in {'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT', 'TEXTURE_PAINT'}:
                snap_element = toolsettings.snap_element
                row = layout.row(align=True)
                row.prop(toolsettings, "use_snap", text="")
                row.prop(toolsettings, "snap_element", text="", icon_only=True)
                if snap_element != 'INCREMENT':
                    row.prop(toolsettings, "snap_target", text="")
                    if obj:
                        if obj.mode in {'OBJECT', 'POSE'} and snap_element != 'VOLUME':
                            row.prop(toolsettings, "use_snap_align_rotation", text="")
                        elif obj.mode == 'EDIT':
                            row.prop(toolsettings, "use_snap_self", text="")
    
                if snap_element == 'VOLUME':
                    row.prop(toolsettings, "use_snap_peel_object", text="")
                elif snap_element == 'FACE':
                    row.prop(toolsettings, "use_snap_project", text="")

            row = layout.row(align=True)
            row.operator("view3d.ruler",text="",icon='CURVE_NCURVE')

class VIEW3D_MT_fd_menus(Menu):
    bl_space_type = 'VIEW3D_MT_editor_menus'
    bl_label = ""

    def draw(self, context):
        self.draw_menus(self.layout, context)

    @staticmethod
    def draw_menus(layout, context):
        layout.menu("VIEW3D_MT_fluidview",icon='VIEWZOOM',text="   View   ")
        layout.menu("INFO_MT_fluidaddobject",icon='GREASEPENCIL',text="   Add   ")
        layout.menu("VIEW3D_MT_fluidtools",icon='MODIFIER',text="   Tools   ")
        layout.menu("MENU_cursor_tools",icon='CURSOR',text="   Cursor   ")

class VIEW3D_MT_fluidview(Menu):
    bl_label = "View"

    def draw(self, context):
        layout = self.layout

        layout.operator("view3d.view_all",icon='VIEWZOOM')
        layout.operator("fd_group.zoom_to_group",text="Zoom To Selected",icon='ZOOM_SELECTED')

        layout.separator()

        layout.operator("view3d.viewnumpad", text="Camera",icon='CAMERA_DATA').type = 'CAMERA'
        layout.operator("view3d.viewnumpad", text="Top",icon='TRIA_DOWN').type = 'TOP'
        layout.operator("view3d.viewnumpad", text="Front",icon='TRIA_UP').type = 'FRONT'
        layout.operator("view3d.viewnumpad", text="Left",icon='TRIA_LEFT').type = 'LEFT'
        layout.operator("view3d.viewnumpad", text="Right",icon='TRIA_RIGHT').type = 'RIGHT'

        layout.separator()

        layout.operator("view3d.view_persportho",icon='SCENE')

        layout.operator_context = 'INVOKE_REGION_WIN'

        layout.separator()

        layout.operator("screen.area_dupli",icon='GHOST')
        layout.operator("screen.region_quadview",icon='VIEW3D_VEC')
        layout.operator("screen.screen_full_area",icon='FULLSCREEN_ENTER')
        
        layout.separator()
        
        layout.menu("MENU_viewport_settings",icon='SCRIPTPLUGINS',text="Viewport Settings")

class INFO_MT_fluidaddobject(Menu):
    bl_label = "Add Object"

    def draw(self, context):
        layout = self.layout

        # note, don't use 'EXEC_SCREEN' or operators wont get the 'v3d' context.

        # Note: was EXEC_AREA, but this context does not have the 'rv3d', which prevents
        #       "align_view" to work on first call (see [#32719]).
        layout.operator_context = 'INVOKE_REGION_WIN'
        
        layout.operator("fd_wall.add_wall",icon='SNAP_PEEL_OBJECT')
        layout.operator("fd_object.create_floor_plane", icon='MESH_GRID')
        layout.separator()
        layout.menu("MENU_add_smart_groups",icon='MOD_FLUIDSIM')
        layout.operator_context = 'EXEC_REGION_WIN'
        layout.separator()
        layout.menu("INFO_MT_mesh_add", icon='OUTLINER_OB_MESH')

        #layout.operator_menu_enum("object.curve_add", "type", text="Curve", icon='OUTLINER_OB_CURVE')
        layout.menu("INFO_MT_curve_add", icon='OUTLINER_OB_CURVE')
        #layout.operator_menu_enum("object.surface_add", "type", text="Surface", icon='OUTLINER_OB_SURFACE')
        layout.operator_context = 'EXEC_REGION_WIN'
        layout.operator("object.text_add", text="Text", icon='OUTLINER_OB_FONT')
        layout.separator()

        layout.operator_menu_enum("object.empty_add", "type", text="Empty", icon='OUTLINER_OB_EMPTY')
        layout.separator()
        layout.operator("fd_scene.render_preview",text="Camera",icon='OUTLINER_OB_CAMERA')
        layout.operator_menu_enum("object.lamp_add", "type", text="Lamp", icon='OUTLINER_OB_LAMP')
        layout.separator()

        if len(bpy.data.groups) > 10:
            layout.operator_context = 'INVOKE_REGION_WIN'
            layout.operator("object.group_instance_add", text="Group Instance...", icon='OUTLINER_OB_EMPTY')
        else:
            layout.operator_menu_enum("object.group_instance_add", "group", text="Group Instance", icon='OUTLINER_OB_EMPTY')

class VIEW3D_MT_fluidtools(Menu):
    bl_context = "objectmode"
    bl_label = "Object"

    def draw(self, context):
        layout = self.layout
        layout.menu("VIEW3D_MT_selectiontools",icon='RESTRICT_SELECT_OFF')
        layout.menu("VIEW3D_MT_objecttools",icon='MESH_CUBE')
        layout.menu("VIEW3D_MT_producttools",icon='OBJECT_DATA')

class VIEW3D_MT_transformtools(Menu):
    bl_context = "objectmode"
    bl_label = "Transforms"

    def draw(self, context):
        layout = self.layout
        layout.operator("fd_object.move_object",text='Grab',icon='MAN_TRANS')
        layout.operator("fd_object.rotate_object",icon='MAN_ROT')
        layout.operator("fd_object.scale_object",icon='MAN_SCALE')

class VIEW3D_MT_selectiontools(Menu):
    bl_context = "objectmode"
    bl_label = "Selection Tools"

    def draw(self, context):
        layout = self.layout
        if context.active_object:
            if context.active_object.mode == 'OBJECT':
                layout.operator("object.select_all",text='Toggle De/Select',icon='MAN_TRANS')
            else:
                layout.operator("mesh.select_all",text='Toggle De/Select',icon='MAN_TRANS')
        else:
            layout.operator("object.select_all",text='Toggle De/Select',icon='MAN_TRANS')
        layout.operator("view3d.select_border",icon='BORDER_RECT')
        layout.operator("view3d.select_circle",icon='BORDER_LASSO')

class VIEW3D_MT_origintools(Menu):
    bl_context = "objectmode"
    bl_label = "Origin Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.origin_set",text="Origin to Cursor",icon='CURSOR').type = 'ORIGIN_CURSOR'
        layout.operator("object.origin_set",text="Origin to Geometry",icon='CLIPUV_HLT').type = 'ORIGIN_GEOMETRY'

class VIEW3D_MT_shadetools(Menu):
    bl_context = "objectmode"
    bl_label = "Object Shading"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.shade_smooth",icon='SOLID')
        layout.operator("object.shade_flat",icon='SNAP_FACE')

class VIEW3D_MT_objecttools(Menu):
    bl_context = "objectmode"
    bl_label = "Object Tools"

    def draw(self, context):
        layout = self.layout
        layout.menu("VIEW3D_MT_transformtools",icon='MAN_TRANS')
        layout.separator()
        layout.operator("object.duplicate_move",icon='PASTEDOWN')
        layout.operator("object.convert", text="Convert to Mesh",icon='MOD_REMESH').target = 'MESH'
        layout.operator("object.join",icon='ROTATECENTER')
        layout.separator()
        layout.menu("VIEW3D_MT_origintools",icon='SPACE2')
        layout.separator()
        layout.menu("VIEW3D_MT_shadetools",icon='MOD_MULTIRES')
        layout.separator()
        layout.operator("fd_general.delete",icon='X')

class VIEW3D_MT_producttools(Menu):
    bl_context = "objectmode"
    bl_label = "Product Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("fd_group.bump_product_group_left",icon='TRIA_LEFT')
        layout.operator("fd_group.bump_product_group_right",icon='TRIA_RIGHT')
        layout.operator("fd_group.stretch_product_group_left",icon='REW')
        layout.operator("fd_group.stretch_product_group_right",icon='FF')
        layout.separator()
        layout.operator("fd_object.add_countertop_to_product",icon='SNAP_PEEL_OBJECT')
        layout.separator()
        layout.separator("fd_general.delete",icon='X')

class MENU_cursor_tools(Menu):
    bl_label = "Cursor Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("fd_general.set_cursor_location",icon='CURSOR',text="Set Cursor Location")
        layout.separator()
        layout.operator("view3d.snap_cursor_to_selected",icon='CURSOR')
        layout.operator("view3d.snap_cursor_to_center",icon='VIEW3D_VEC')
        layout.operator("view3d.snap_selected_to_cursor",icon='SPACE2')
        layout.separator()
        layout.prop(context.space_data,"pivot_point",text="")

class MENU_add_smart_groups(Menu):
    bl_label = "Smart Groups"

    def draw(self, context):
        layout = self.layout
        layout.operator("fd_group.add_empty_product",icon='OBJECT_DATA')
        layout.operator("fd_group.add_empty_insert",icon='STICKY_UVS_LOC')
        layout.operator("fd_group.add_empty_part",icon='MOD_MESHDEFORM')

class MENU_viewport_settings(Menu):
    bl_label = "Viewport Settings"

    def draw(self, context):

        layout = self.layout
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        view3dspace = space
                        layout.prop(view3dspace,"show_floor",text="Show Grid Floor")
                        layout.prop(view3dspace,"show_axis_x",text="Show X Axis")
                        layout.prop(view3dspace,"show_axis_y",text="Show Y Axis")
                        layout.prop(view3dspace,"show_axis_z",text="Show Z Axis")
                        layout.prop(view3dspace,"show_only_render",text="Only Render")
                        layout.prop(view3dspace,"grid_lines",text="Grid Lines")
                        layout.prop(view3dspace,"lock_camera",text="Lock Camera to View")
                        break

#------REGISTER
classes = [
           VIEW3D_HT_fluidheader,
           VIEW3D_MT_fd_menus,
           VIEW3D_MT_fluidview,
           VIEW3D_MT_fluidtools,
           VIEW3D_MT_producttools,
           MENU_viewport_settings,
           INFO_MT_fluidaddobject,
           MENU_add_smart_groups,
           MENU_cursor_tools,
           VIEW3D_MT_origintools,
           VIEW3D_MT_shadetools,
           VIEW3D_MT_objecttools,
           VIEW3D_MT_transformtools,
           VIEW3D_MT_selectiontools
           ]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
