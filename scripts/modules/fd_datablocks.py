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
#------IMPORTS

import os,math

from bpy.types import (Header, 
                       Menu, 
                       Panel, 
                       Operator,
                       PropertyGroup)

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       BoolVectorProperty,
                       PointerProperty,
                       CollectionProperty,
                       EnumProperty)

import fd_utils

#------PROPERTIES
class enums():
    enum_library_types = [('NONE',"   None","None"),
                          ('PROJECT',"   Project","Project"),
                          ('PRODUCT',"   Product","Product"),
                          ('INSERT',"   Insert","Insert"),
                          ('PART',"   Part","Part"),
                          ('EXTRUSION',"   Extrusion","Extrusion"),
                          ('MATERIAL',"   Material","Material"),
                          ('OBJECT',"   Object","Object"),
                          ('GROUP',"   Group","Group"),
                          ('WORLD',"   World","World")]
    
    enum_pointer_types = [('MATERIAL',"Material","Material"),
                          ('PART',"Part","Part"),
                          ('INSERT',"Insert","Insert")]
    
    enum_group_types = [('NONE',"None","Standard"),
                        ('PRODUCT',"Product","Product"),
                        ('INSERT',"Insert","Insert"),
                        ('PART',"Part","Part"),
                        ('WALL',"Wall","Wall"),
                        ('PLANE',"Plane","Plane")]
    
    enum_object_types = [('NONE',"None","None"),
                         ('CAGE',"CAGE","Cage used to represent the bounding area of the object"),
                         ('VPDIMX',"Visible Prompt X Dimension","Visible prompt control in the 3D viewport"),
                         ('VPDIMY',"Visible Prompt Y Dimension","Visible prompt control in the 3D viewport"),
                         ('VPDIMZ',"Visible Prompt Z Dimension","Visible prompt control in the 3D viewport"),
                         ('BPPRODUCT',"Product Base Point","Parent object of a product group"),
                         ('BPINSERT',"Insert Base Point","Parent object of an opening group"),
                         ('BPPART',"Part Base Point","Parent object of a part group"),
                         ('BPWALL',"Wall Base Point","Parent object of a wall group"),
                         ('BPPLANE',"Plane Base Point","Parent object of a plane")]
                         
    enum_prompt_types = [('NUMBER',"Number","Number"),
                         ('QUANTITY',"Quantity","Quantity"),
                         ('COMBOBOX',"Combo Box","Combo Box"),
                         ('CHECKBOX',"Check Box","Check Box"),
                         ('TEXT',"Text","Text"),
                         ('PRICE',"Price","Enter Price Prompt")]
    
    enum_selection_tabs = [('OBJECT',"Object","Object"),
                           ('WALL',"Wall","Wall"),
                           ('PRODUCT',"Product","Product"),
                           ('INSERT',"Insert","Insert"),
                           ('PART',"Part","Part")]
    
    enum_object_tabs = [('INFO',"","Show the Main Information"),
                        ('DISPLAY',"","Show Options for how the Object is Displayed"),
                        ('MATERIAL',"","Show the materials assign to the object"),
                        ('CONSTRAINTS',"","Show the constraints assigned to the object"),
                        ('MODIFIERS',"","Show the modifiers assigned to the object"),
                        ('MESHDATA',"","Show the Mesh Data Information"),
                        ('CURVEDATA',"","Show the Curve Data Information"),
                        ('TEXTDATA',"","Show the Text Data Information"),
                        ('EMPTYDATA',"","Show the Empty Data Information"),
                        ('LIGHTDATA',"","Show the Light Data Information"),
                        ('CAMERADATA',"","Show the Camera Data Information"),
                        ('DRIVERS',"","Show the Drivers assigned to the Object")]

    enum_group_object_tabs = [('MESH',"Mesh","Show the Mesh Objects"),
                              ('TEXT',"Text","Show the Text Objects"),
                              ('CURVE',"Curve","Show the Curve Objects"),
                              ('EMPTY',"Empty","Show the Empty Objects"),
                              ('GROUP',"Group","Show the Group Objects")]

    enum_group_tabs = [('INFO',"Main","Show the Part Info Page"),
                       ('SETTINGS',"","Show the Settings Page"),
                       ('PROMPTS',"Prompts","Show the Prompts Page"),
                       ('OBJECTS',"Objects","Show Objects"),
                       ('DRIVERS',"Drivers","Show the Driver Formulas")]

    enum_group_drivers_tabs = [('LOC_X',"Location X","Location X"),
                               ('LOC_Y',"Location Y","Location Y"),
                               ('LOC_Z',"Location Z","Location Z"),
                               ('ROT_X',"Rotation X","Rotation X"),
                               ('ROT_Y',"Rotation Y","Rotation Y"),
                               ('ROT_Z',"Rotation Z","Rotation Z"),
                               ('DIM_X',"Dimension X","Dimension X"),
                               ('DIM_Y',"Dimension Y","Dimension Y"),
                               ('DIM_Z',"Dimension Z","Dimension Z"),
                               ('PROMPTS',"Prompts","Prompts")]

    enum_object_drivers_tabs = [('LOC_X',"Location X","Location X"),
                                ('LOC_Y',"Location Y","Location Y"),
                                ('LOC_Z',"Location Z","Location Z"),
                                ('ROT_X',"Rotation X","Rotation X"),
                                ('ROT_Y',"Rotation Y","Rotation Y"),
                                ('ROT_Z',"Rotation Z","Rotation Z"),
                                ('VIS',"Visible","Visible"),
                                ('RENDER_VIS',"Render Visible","Render Visible")]

    enum_product_category_types = [('NONE',"",""),
                                   ('CORNER',"","")]

#     enum_scene_tabs = [('INFO',"",""),
#                        ('PROMPTS',"","")]
# 
#     enum_world_tabs = [('INFO',"",""),
#                        ('PROMPTS',"","")]

class events():
    def update_pointer_libraries_path(self, context):
        '''fd_pointer_library_col.path'''
        self.reload_pointer_library_collection()
    
    def update_active_library_type(self, context):
        '''fd_pointer_library_col.active_library_type'''
        self.reload_active_pointer_library_collection()
        library = self.get_active_pointer_library()
        if not library:
            self.index_active_pointer_library = 0
            self.reload_active_pointer_library_collection()
            library = self.get_active_pointer_library()
        category = library.Categories.get_active_category()
        if category:
            bpy.context.window_manager.mv.update_file_browser_parameters(category.path)
        else:
            print('NO LIBRARIES')
    
    def update_pointer_name(self, context):
        '''fd_material_slot.pointer_name'''
        dm = context.scene.mv.dm
        pointer = dm.get_pointer_by_name(self.pointer_name)
        if pointer:
            self.library_name = pointer.library_name
            self.category_name = pointer.category_name
            self.item_name = pointer.item_name
        
class const():
#ICONS

    #OBJECTS
    icon_info = 'INFO'
    icon_display = 'RESTRICT_VIEW_OFF'
    icon_mesh_data = 'MESH_DATA'
    icon_curve_data = 'CURVE_DATA'
    icon_empty_data = 'EMPTY_DATA'
    icon_font_data = 'FONT_DATA'
    icon_light = 'LAMP_SPOT'
    icon_camera = 'OUTLINER_DATA_CAMERA'
    icon_library = 'EXTERNAL_DATA'
    icon_project = 'RENDERLAYERS'
    icon_wall = 'SNAP_PEEL_OBJECT'
    icon_product = 'OBJECT_DATAMODE'
    icon_insert = 'STICKY_UVS_LOC'
    icon_part = 'MOD_MESHDEFORM'
    icon_object = 'MESH_CUBE'
    icon_group = 'GROUP'
    icon_scene = 'SCENE_DATA'
    icon_world = 'WORLD'
    icon_mesh = 'OUTLINER_OB_MESH'
    icon_font = 'OUTLINER_OB_FONT'
    icon_empty = 'OUTLINER_OB_EMPTY'
    icon_material = 'MATERIAL'
    icon_curve = 'OUTLINER_OB_CURVE'
    icon_extrusion = 'CURVE_PATH'
    icon_properties = 'INFO'
    icon_drivers = 'AUTO'
    icon_modifiers = 'MODIFIER'
    icon_constraints = 'CONSTRAINT'
    icon_category = 'FILE_FOLDER'
    icon_ghost = 'GHOST_ENABLED'
    icon_editmode = 'EDITMODE_HLT'
    icon_hook = 'HOOK'
    icon_edit_text = 'OUTLINER_DATA_FONT'
    icon_specgroup = 'SOLO_ON'
    icon_filefolder = 'FILE_FOLDER'
    icon_pointer = 'HAND'
    icon_set_pointer = 'STYLUS_PRESSURE'

    #ACTIONS
    icon_add = 'ZOOM_IN'
    icon_delete = 'ZOOM_OUT'
    icon_refresh = 'FILE_REFRESH'
    
    #TEMP NAMES
    temp_group = '_FDTEMPGROUP_'
    
    #READABLE NAMES
    folder_name_projects = 'Project Libraries'
    folder_name_extrusion = 'Extrusion Libraries'
    folder_name_group = 'Group Libraries'
    folder_name_insert = 'Insert Libraries'
    folder_name_material = 'Material Libraries'
    folder_name_object = 'Object Libraries'
    folder_name_part = 'Part Libraries'
    folder_name_product = 'Product Libraries'
    folder_name_world = 'World Libraries'
    
    filename_specgroup = 'FluidSpecificationGroups.xml'
    
    wall = 'Wall'
    product = 'Product'
    insert = 'Insert'
    part = 'Part'
    cage = 'Cage'
    xdim = 'X Dim'
    ydim = 'Y Dim'
    zdim = 'Z Dim'
    

class modifiers():
    
    def draw_object_modifiers(self,layout=None, obj=None):

        layout.operator_menu_enum("object.modifier_add", "type")

        for md in obj.modifiers:
            boxmain = layout.box()
            box = boxmain.template_modifier(md)
            if box:
                    
                # match enum type to our functions, avoids a lookup table.
                getattr(self, md.type)(self, box, obj, md)

    # the mt.type enum is (ab)used for a lookup on function names
    # ...to avoid lengthy if statements
    # so each type must have a function here.

    def ARMATURE(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.label(text="Object:")
        col.prop(md, "object", text="")
        col.prop(md, "use_deform_preserve_volume")

        col = split.column()
        col.label(text="Bind To:")
        col.prop(md, "use_vertex_groups", text="Vertex Groups")
        col.prop(md, "use_bone_envelopes", text="Bone Envelopes")

        layout.separator()

        split = layout.split()

        row = split.row(align=True)
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="")
        sub = row.row(align=True)
        sub.active = bool(md.vertex_group)
        sub.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

        split.prop(md, "use_multi_modifier")

    def ARRAY(self, layout, ob, md):
        layout.prop(md, "fit_type")

        if md.fit_type == 'FIXED_COUNT':
            layout.prop(md, "count")
        elif md.fit_type == 'FIT_LENGTH':
            layout.prop(md, "fit_length")
        elif md.fit_type == 'FIT_CURVE':
            layout.prop(md, "curve")

        layout.separator()

        split = layout.split()

        col = split.column()
        col.prop(md, "use_constant_offset")
        sub = col.column()
        sub.active = md.use_constant_offset
        sub.prop(md, "constant_offset_displace", text="")

        col.separator()

        col.prop(md, "use_merge_vertices", text="Merge")
        sub = col.column()
        sub.active = md.use_merge_vertices
        sub.prop(md, "use_merge_vertices_cap", text="First Last")
        sub.prop(md, "merge_threshold", text="Distance")

        col = split.column()
        col.prop(md, "use_relative_offset")
        sub = col.column()
        sub.active = md.use_relative_offset
        sub.prop(md, "relative_offset_displace", text="")

        col.separator()

        col.prop(md, "use_object_offset")
        sub = col.column()
        sub.active = md.use_object_offset
        sub.prop(md, "offset_object", text="")

        layout.separator()

        layout.prop(md, "start_cap")
        layout.prop(md, "end_cap")

    def BEVEL(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.prop(md, "width")
        col.prop(md, "segments")
        col.prop(md, "profile")

        col = split.column()
        col.prop(md, "use_only_vertices")
        col.prop(md, "use_clamp_overlap")

        layout.label(text="Limit Method:")
        layout.row().prop(md, "limit_method", expand=True)
        if md.limit_method == 'ANGLE':
            layout.prop(md, "angle_limit")
        elif md.limit_method == 'VGROUP':
            layout.label(text="Vertex Group:")
            layout.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

        layout.label(text="Width Method:")
        layout.row().prop(md, "offset_type", expand=True)

    def BOOLEAN(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.label(text="Operation:")
        col.prop(md, "operation", text="")

        col = split.column()
        col.label(text="Object:")
        col.prop(md, "object", text="")

    def BUILD(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.prop(md, "frame_start")
        col.prop(md, "frame_duration")
        col.prop(md, "use_reverse")

        col = split.column()
        col.prop(md, "use_random_order")
        sub = col.column()
        sub.active = md.use_random_order
        sub.prop(md, "seed")

    def MESH_CACHE(self, layout, ob, md):
        layout.prop(md, "cache_format")
        layout.prop(md, "filepath")

        layout.label(text="Evaluation:")
        layout.prop(md, "factor", slider=True)
        layout.prop(md, "deform_mode")
        layout.prop(md, "interpolation")

        layout.label(text="Time Mapping:")

        row = layout.row()
        row.prop(md, "time_mode", expand=True)
        row = layout.row()
        row.prop(md, "play_mode", expand=True)
        if md.play_mode == 'SCENE':
            layout.prop(md, "frame_start")
            layout.prop(md, "frame_scale")
        else:
            time_mode = md.time_mode
            if time_mode == 'FRAME':
                layout.prop(md, "eval_frame")
            elif time_mode == 'TIME':
                layout.prop(md, "eval_time")
            elif time_mode == 'FACTOR':
                layout.prop(md, "eval_factor")

        layout.label(text="Axis Mapping:")
        split = layout.split(percentage=0.5, align=True)
        split.alert = (md.forward_axis[-1] == md.up_axis[-1])
        split.label("Forward/Up Axis:")
        split.prop(md, "forward_axis", text="")
        split.prop(md, "up_axis", text="")
        split = layout.split(percentage=0.5)
        split.label(text="Flip Axis:")
        row = split.row()
        row.prop(md, "flip_axis")

    def CAST(self, layout, ob, md):
        split = layout.split(percentage=0.25)

        split.label(text="Cast Type:")
        split.prop(md, "cast_type", text="")

        split = layout.split(percentage=0.25)

        col = split.column()
        col.prop(md, "use_x")
        col.prop(md, "use_y")
        col.prop(md, "use_z")

        col = split.column()
        col.prop(md, "factor")
        col.prop(md, "radius")
        col.prop(md, "size")
        col.prop(md, "use_radius_as_size")

        split = layout.split()

        col = split.column()
        col.label(text="Vertex Group:")
        col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")
        col = split.column()
        col.label(text="Control Object:")
        col.prop(md, "object", text="")
        if md.object:
            col.prop(md, "use_transform")

    def CLOTH(self, layout, ob, md):
        layout.label(text="Settings can be found inside the Physics context")

    def COLLISION(self, layout, ob, md):
        layout.label(text="Settings can be found inside the Physics context")

    def CURVE(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.label(text="Object:")
        col.prop(md, "object", text="")
        col = split.column()
        col.label(text="Vertex Group:")
        col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")
        layout.label(text="Deformation Axis:")
        layout.row().prop(md, "deform_axis", expand=True)

    def DECIMATE(self, layout, ob, md):
        decimate_type = md.decimate_type

        row = layout.row()
        row.prop(md, "decimate_type", expand=True)

        if decimate_type == 'COLLAPSE':
            layout.prop(md, "ratio")

            split = layout.split()
            row = split.row(align=True)
            row.prop_search(md, "vertex_group", ob, "vertex_groups", text="")
            row.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

            split.prop(md, "use_collapse_triangulate")
        elif decimate_type == 'UNSUBDIV':
            layout.prop(md, "iterations")
        else:  # decimate_type == 'DISSOLVE':
            layout.prop(md, "angle_limit")
            layout.prop(md, "use_dissolve_boundaries")
            layout.label("Delimit:")
            row = layout.row()
            row.prop(md, "delimit")

        layout.label(text=iface_("Face Count: %d") % md.face_count, translate=False)

    def DISPLACE(self, layout, ob, md):
        has_texture = (md.texture is not None)

        split = layout.split()

        col = split.column()
        col.label(text="Texture:")
        col.template_ID(md, "texture", new="texture.new")
        col.label(text="Vertex Group:")
        col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

        col = split.column()
        col.label(text="Direction:")
        col.prop(md, "direction", text="")
        colsub = col.column()
        colsub.active = has_texture
        colsub.label(text="Texture Coordinates:")
        colsub.prop(md, "texture_coords", text="")
        if md.texture_coords == 'OBJECT':
            row = layout.row()
            row.active = has_texture
            row.prop(md, "texture_coords_object", text="Object")
        elif md.texture_coords == 'UV' and ob.type == 'MESH':
            row = layout.row()
            row.active = has_texture
            row.prop_search(md, "uv_layer", ob.data, "uv_textures")

        layout.separator()

        row = layout.row()
        row.prop(md, "mid_level")
        row.prop(md, "strength")

    def DYNAMIC_PAINT(self, layout, ob, md):
        layout.label(text="Settings can be found inside the Physics context")

    def EDGE_SPLIT(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.prop(md, "use_edge_angle", text="Edge Angle")
        sub = col.column()
        sub.active = md.use_edge_angle
        sub.prop(md, "split_angle")

        split.prop(md, "use_edge_sharp", text="Sharp Edges")

    def EXPLODE(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.label(text="Vertex group:")
        col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")
        sub = col.column()
        sub.active = bool(md.vertex_group)
        sub.prop(md, "protect")
        col.label(text="Particle UV")
        col.prop_search(md, "particle_uv", ob.data, "uv_textures", text="")

        col = split.column()
        col.prop(md, "use_edge_cut")
        col.prop(md, "show_unborn")
        col.prop(md, "show_alive")
        col.prop(md, "show_dead")
        col.prop(md, "use_size")

        layout.operator("object.explode_refresh", text="Refresh")

    def FLUID_SIMULATION(self, layout, ob, md):
        layout.label(text="Settings can be found inside the Physics context")

    def HOOK(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.label(text="Object:")
        col.prop(md, "object", text="")
        if md.object and md.object.type == 'ARMATURE':
            col.label(text="Bone:")
            col.prop_search(md, "subtarget", md.object.data, "bones", text="")
        col = split.column()
        col.label(text="Vertex Group:")
        col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

        layout.separator()

        split = layout.split()

        col = split.column()
        col.prop(md, "falloff")
        col.prop(md, "force", slider=True)

        col = split.column()
        col.operator("object.hook_reset", text="Reset")
        col.operator("object.hook_recenter", text="Recenter")

        if ob.mode == 'EDIT':
            layout.separator()
            row = layout.row()
            row.operator("object.hook_select", text="Select")
            row.operator("object.hook_assign", text="Assign")

    def LAPLACIANDEFORM(self, layout, ob, md):
        is_bind = md.is_bind

        layout.prop(md, "iterations")

        row = layout.row()
        row.active = not is_bind
        row.label(text="Anchors Vertex Group:")

        row = layout.row()
        row.enabled = not is_bind
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

        layout.separator()

        row = layout.row()
        row.enabled = bool(md.vertex_group)
        row.operator("object.laplaciandeform_bind", text="Unbind" if is_bind else "Bind")

    def LAPLACIANSMOOTH(self, layout, ob, md):
        layout.prop(md, "iterations")

        split = layout.split(percentage=0.25)

        col = split.column()
        col.label(text="Axis:")
        col.prop(md, "use_x")
        col.prop(md, "use_y")
        col.prop(md, "use_z")

        col = split.column()
        col.label(text="Lambda:")
        col.prop(md, "lambda_factor", text="Factor")
        col.prop(md, "lambda_border", text="Border")

        col.separator()
        col.prop(md, "use_volume_preserve")
        col.prop(md, "use_normalized")

        layout.label(text="Vertex Group:")
        layout.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

    def LATTICE(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.label(text="Object:")
        col.prop(md, "object", text="")

        col = split.column()
        col.label(text="Vertex Group:")
        col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

        layout.separator()
        layout.prop(md, "strength", slider=True)

    def MASK(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.label(text="Mode:")
        col.prop(md, "mode", text="")

        col = split.column()
        if md.mode == 'ARMATURE':
            col.label(text="Armature:")
            col.prop(md, "armature", text="")
        elif md.mode == 'VERTEX_GROUP':
            col.label(text="Vertex Group:")
            row = col.row(align=True)
            row.prop_search(md, "vertex_group", ob, "vertex_groups", text="")
            sub = row.row(align=True)
            sub.active = bool(md.vertex_group)
            sub.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

    def MESH_DEFORM(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.active = not md.is_bound
        col.label(text="Object:")
        col.prop(md, "object", text="")

        col = split.column()
        col.label(text="Vertex Group:")

        row = col.row(align=True)
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="")
        sub = row.row(align=True)
        sub.active = bool(md.vertex_group)
        sub.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

        layout.separator()

        if md.is_bound:
            layout.operator("object.meshdeform_bind", text="Unbind")
        else:
            layout.operator("object.meshdeform_bind", text="Bind")

            row = layout.row()
            row.prop(md, "precision")
            row.prop(md, "use_dynamic_bind")

    def MIRROR(self, layout, ob, md):
        split = layout.split(percentage=0.25)

        col = split.column()
        col.label(text="Axis:")
        col.prop(md, "use_x")
        col.prop(md, "use_y")
        col.prop(md, "use_z")

        col = split.column()
        col.label(text="Options:")
        col.prop(md, "use_mirror_merge", text="Merge")
        col.prop(md, "use_clip", text="Clipping")
        col.prop(md, "use_mirror_vertex_groups", text="Vertex Groups")

        col = split.column()
        col.label(text="Textures:")
        col.prop(md, "use_mirror_u", text="U")
        col.prop(md, "use_mirror_v", text="V")

        col = layout.column()

        if md.use_mirror_merge is True:
            col.prop(md, "merge_threshold")
        col.label(text="Mirror Object:")
        col.prop(md, "mirror_object", text="")

    def MULTIRES(self, layout, ob, md):
        layout.row().prop(md, "subdivision_type", expand=True)

        split = layout.split()
        col = split.column()
        col.prop(md, "levels", text="Preview")
        col.prop(md, "sculpt_levels", text="Sculpt")
        col.prop(md, "render_levels", text="Render")

        col = split.column()

        col.enabled = ob.mode != 'EDIT'
        col.operator("object.multires_subdivide", text="Subdivide")
        col.operator("object.multires_higher_levels_delete", text="Delete Higher")
        col.operator("object.multires_reshape", text="Reshape")
        col.operator("object.multires_base_apply", text="Apply Base")
        col.prop(md, "use_subsurf_uv")
        col.prop(md, "show_only_control_edges")

        layout.separator()

        col = layout.column()
        row = col.row()
        if md.is_external:
            row.operator("object.multires_external_pack", text="Pack External")
            row.label()
            row = col.row()
            row.prop(md, "filepath", text="")
        else:
            row.operator("object.multires_external_save", text="Save External...")
            row.label()

    def OCEAN(self, layout, ob, md):
        if not bpy.app.build_options.mod_oceansim:
            layout.label("Built without OceanSim modifier")
            return

        layout.prop(md, "geometry_mode")

        if md.geometry_mode == 'GENERATE':
            row = layout.row()
            row.prop(md, "repeat_x")
            row.prop(md, "repeat_y")

        layout.separator()

        split = layout.split()

        col = split.column()
        col.prop(md, "time")
        col.prop(md, "depth")
        col.prop(md, "random_seed")

        col = split.column()
        col.prop(md, "resolution")
        col.prop(md, "size")
        col.prop(md, "spatial_size")

        layout.label("Waves:")

        split = layout.split()

        col = split.column()
        col.prop(md, "choppiness")
        col.prop(md, "wave_scale", text="Scale")
        col.prop(md, "wave_scale_min")
        col.prop(md, "wind_velocity")

        col = split.column()
        col.prop(md, "wave_alignment", text="Alignment")
        sub = col.column()
        sub.active = (md.wave_alignment > 0.0)
        sub.prop(md, "wave_direction", text="Direction")
        sub.prop(md, "damping")

        layout.separator()

        layout.prop(md, "use_normals")

        split = layout.split()

        col = split.column()
        col.prop(md, "use_foam")
        sub = col.row()
        sub.active = md.use_foam
        sub.prop(md, "foam_coverage", text="Coverage")

        col = split.column()
        col.active = md.use_foam
        col.label("Foam Data Layer Name:")
        col.prop(md, "foam_layer_name", text="")

        layout.separator()

        if md.is_cached:
            layout.operator("object.ocean_bake", text="Free Bake").free = True
        else:
            layout.operator("object.ocean_bake").free = False

        split = layout.split()
        split.enabled = not md.is_cached

        col = split.column(align=True)
        col.prop(md, "frame_start", text="Start")
        col.prop(md, "frame_end", text="End")

        col = split.column(align=True)
        col.label(text="Cache path:")
        col.prop(md, "filepath", text="")

        split = layout.split()
        split.enabled = not md.is_cached

        col = split.column()
        col.active = md.use_foam
        col.prop(md, "bake_foam_fade")

        col = split.column()

    def PARTICLE_INSTANCE(self, layout, ob, md):
        layout.prop(md, "object")
        layout.prop(md, "particle_system_index", text="Particle System")

        split = layout.split()
        col = split.column()
        col.label(text="Create From:")
        col.prop(md, "use_normal")
        col.prop(md, "use_children")
        col.prop(md, "use_size")

        col = split.column()
        col.label(text="Show Particles When:")
        col.prop(md, "show_alive")
        col.prop(md, "show_unborn")
        col.prop(md, "show_dead")

        layout.separator()

        layout.prop(md, "use_path", text="Create Along Paths")

        split = layout.split()
        split.active = md.use_path
        col = split.column()
        col.row().prop(md, "axis", expand=True)
        col.prop(md, "use_preserve_shape")

        col = split.column()
        col.prop(md, "position", slider=True)
        col.prop(md, "random_position", text="Random", slider=True)

    def PARTICLE_SYSTEM(self, layout, ob, md):
        layout.label(text="Settings can be found inside the Particle context")

    def SCREW(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.prop(md, "axis")
        col.prop(md, "object", text="AxisOb")
        col.prop(md, "angle")
        col.prop(md, "steps")
        col.prop(md, "render_steps")
        col.prop(md, "use_smooth_shade")

        col = split.column()
        row = col.row()
        row.active = (md.object is None or md.use_object_screw_offset is False)
        row.prop(md, "screw_offset")
        row = col.row()
        row.active = (md.object is not None)
        row.prop(md, "use_object_screw_offset")
        col.prop(md, "use_normal_calculate")
        col.prop(md, "use_normal_flip")
        col.prop(md, "iterations")
        col.prop(md, "use_stretch_u")
        col.prop(md, "use_stretch_v")

    def SHRINKWRAP(self, layout, ob, md):
        split = layout.split()
        col = split.column()
        col.label(text="Target:")
        col.prop(md, "target", text="")
        col = split.column()
        col.label(text="Vertex Group:")
        col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

        split = layout.split()

        col = split.column()
        col.prop(md, "offset")

        col = split.column()
        col.label(text="Mode:")
        col.prop(md, "wrap_method", text="")

        if md.wrap_method == 'PROJECT':
            split = layout.split()
            col = split.column()
            col.prop(md, "subsurf_levels")
            col = split.column()

            col.prop(md, "project_limit", text="Limit")
            split = layout.split(percentage=0.25)

            col = split.column()
            col.label(text="Axis:")
            col.prop(md, "use_project_x")
            col.prop(md, "use_project_y")
            col.prop(md, "use_project_z")

            col = split.column()
            col.label(text="Direction:")
            col.prop(md, "use_negative_direction")
            col.prop(md, "use_positive_direction")

            col = split.column()
            col.label(text="Cull Faces:")
            col.prop(md, "cull_face", expand=True)

            layout.prop(md, "auxiliary_target")

        elif md.wrap_method == 'NEAREST_SURFACEPOINT':
            layout.prop(md, "use_keep_above_surface")

    def SIMPLE_DEFORM(self, layout, ob, md):

        layout.row().prop(md, "deform_method", expand=True)

        split = layout.split()

        col = split.column()
        col.label(text="Vertex Group:")
        col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

        split = layout.split()

        col = split.column()
        col.label(text="Origin:")
        col.prop(md, "origin", text="")

        if md.deform_method in {'TAPER', 'STRETCH', 'TWIST'}:
            col.label(text="Lock:")
            col.prop(md, "lock_x")
            col.prop(md, "lock_y")

        col = split.column()
        col.label(text="Deform:")
        if md.deform_method in {'TAPER', 'STRETCH'}:
            col.prop(md, "factor")
        else:
            col.prop(md, "angle")
        col.prop(md, "limits", slider=True)

    def SMOKE(self, layout, ob, md):
        layout.label(text="Settings can be found inside the Physics context")

    def SMOOTH(self, layout, ob, md):
        split = layout.split(percentage=0.25)

        col = split.column()
        col.label(text="Axis:")
        col.prop(md, "use_x")
        col.prop(md, "use_y")
        col.prop(md, "use_z")

        col = split.column()
        col.prop(md, "factor")
        col.prop(md, "iterations")
        col.label(text="Vertex Group:")
        col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

    def SOFT_BODY(self, layout, ob, md):
        layout.label(text="Settings can be found inside the Physics context")

    def SOLIDIFY(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.prop(md, "thickness")
        col.prop(md, "thickness_clamp")

        col.separator()

        row = col.row(align=True)
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="")
        sub = row.row(align=True)
        sub.active = bool(md.vertex_group)
        sub.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')

        sub = col.row()
        sub.active = bool(md.vertex_group)
        sub.prop(md, "thickness_vertex_group", text="Factor")

        col.label(text="Crease:")
        col.prop(md, "edge_crease_inner", text="Inner")
        col.prop(md, "edge_crease_outer", text="Outer")
        col.prop(md, "edge_crease_rim", text="Rim")

        col = split.column()

        col.prop(md, "offset")
        col.prop(md, "use_flip_normals")

        col.prop(md, "use_even_offset")
        col.prop(md, "use_quality_normals")
        col.prop(md, "use_rim")

        col.separator()

        col.label(text="Material Index Offset:")

        sub = col.column()
        row = sub.split(align=True, percentage=0.4)
        row.prop(md, "material_offset", text="")
        row = row.row(align=True)
        row.active = md.use_rim
        row.prop(md, "material_offset_rim", text="Rim")

    def SUBSURF(self, layout, ob, md):
        layout.row().prop(md, "subdivision_type", expand=True)

        split = layout.split()
        col = split.column()
        col.label(text="Subdivisions:")
        col.prop(md, "levels", text="View")
        col.prop(md, "render_levels", text="Render")

        col = split.column()
        col.label(text="Options:")
        col.prop(md, "use_subsurf_uv")
        col.prop(md, "show_only_control_edges")

    def SURFACE(self, layout, ob, md):
        layout.label(text="Settings can be found inside the Physics context")

    def UV_PROJECT(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.label(text="Image:")
        col.prop(md, "image", text="")

        col = split.column()
        col.label(text="UV Map:")
        col.prop_search(md, "uv_layer", ob.data, "uv_textures", text="")

        split = layout.split()
        col = split.column()
        col.prop(md, "use_image_override")
        col.prop(md, "projector_count", text="Projectors")
        for proj in md.projectors:
            col.prop(proj, "object", text="")

        col = split.column()
        sub = col.column(align=True)
        sub.prop(md, "aspect_x", text="Aspect X")
        sub.prop(md, "aspect_y", text="Aspect Y")

        sub = col.column(align=True)
        sub.prop(md, "scale_x", text="Scale X")
        sub.prop(md, "scale_y", text="Scale Y")

    def WARP(self, layout, ob, md):
        use_falloff = (md.falloff_type != 'NONE')
        split = layout.split()

        col = split.column()
        col.label(text="From:")
        col.prop(md, "object_from", text="")

        col.prop(md, "use_volume_preserve")

        col = split.column()
        col.label(text="To:")
        col.prop(md, "object_to", text="")
        col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

        col = layout.column()

        row = col.row(align=True)
        row.prop(md, "strength")
        if use_falloff:
            row.prop(md, "falloff_radius")

        col.prop(md, "falloff_type")
        if use_falloff:
            if md.falloff_type == 'CURVE':
                col.template_curve_mapping(md, "falloff_curve")

        # 2 new columns
        split = layout.split()
        col = split.column()
        col.label(text="Texture:")
        col.template_ID(md, "texture", new="texture.new")

        col = split.column()
        col.label(text="Texture Coordinates:")
        col.prop(md, "texture_coords", text="")

        if md.texture_coords == 'OBJECT':
            layout.prop(md, "texture_coords_object", text="Object")
        elif md.texture_coords == 'UV' and ob.type == 'MESH':
            layout.prop_search(md, "uv_layer", ob.data, "uv_textures")

    def WAVE(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.label(text="Motion:")
        col.prop(md, "use_x")
        col.prop(md, "use_y")
        col.prop(md, "use_cyclic")

        col = split.column()
        col.prop(md, "use_normal")
        sub = col.column()
        sub.active = md.use_normal
        sub.prop(md, "use_normal_x", text="X")
        sub.prop(md, "use_normal_y", text="Y")
        sub.prop(md, "use_normal_z", text="Z")

        split = layout.split()

        col = split.column()
        col.label(text="Time:")
        sub = col.column(align=True)
        sub.prop(md, "time_offset", text="Offset")
        sub.prop(md, "lifetime", text="Life")
        col.prop(md, "damping_time", text="Damping")

        col = split.column()
        col.label(text="Position:")
        sub = col.column(align=True)
        sub.prop(md, "start_position_x", text="X")
        sub.prop(md, "start_position_y", text="Y")
        col.prop(md, "falloff_radius", text="Falloff")

        layout.separator()

        layout.prop(md, "start_position_object")
        layout.prop_search(md, "vertex_group", ob, "vertex_groups")
        split = layout.split(percentage=0.33)
        col = split.column()
        col.label(text="Texture")
        col = split.column()
        col.template_ID(md, "texture", new="texture.new")
        layout.prop(md, "texture_coords")
        if md.texture_coords == 'MAP_UV' and ob.type == 'MESH':
            layout.prop_search(md, "uv_layer", ob.data, "uv_textures")
        elif md.texture_coords == 'OBJECT':
            layout.prop(md, "texture_coords_object")

        layout.separator()

        split = layout.split()

        col = split.column()
        col.prop(md, "speed", slider=True)
        col.prop(md, "height", slider=True)

        col = split.column()
        col.prop(md, "width", slider=True)
        col.prop(md, "narrowness", slider=True)

    def REMESH(self, layout, ob, md):
        layout.prop(md, "mode")

        row = layout.row()
        row.prop(md, "octree_depth")
        row.prop(md, "scale")

        if md.mode == 'SHARP':
            layout.prop(md, "sharpness")

        layout.prop(md, "use_smooth_shade")
        layout.prop(md, "use_remove_disconnected")
        row = layout.row()
        row.active = md.use_remove_disconnected
        row.prop(md, "threshold")

    @staticmethod
    def vertex_weight_mask(layout, ob, md):
        layout.label(text="Influence/Mask Options:")

        split = layout.split(percentage=0.4)
        split.label(text="Global Influence:")
        split.prop(md, "mask_constant", text="")

        if not md.mask_texture:
            split = layout.split(percentage=0.4)
            split.label(text="Vertex Group Mask:")
            split.prop_search(md, "mask_vertex_group", ob, "vertex_groups", text="")

        if not md.mask_vertex_group:
            split = layout.split(percentage=0.4)
            split.label(text="Texture Mask:")
            split.template_ID(md, "mask_texture", new="texture.new")
            if md.mask_texture:
                split = layout.split()

                col = split.column()
                col.label(text="Texture Coordinates:")
                col.prop(md, "mask_tex_mapping", text="")

                col = split.column()
                col.label(text="Use Channel:")
                col.prop(md, "mask_tex_use_channel", text="")

                if md.mask_tex_mapping == 'OBJECT':
                    layout.prop(md, "mask_tex_map_object", text="Object")
                elif md.mask_tex_mapping == 'UV' and ob.type == 'MESH':
                    layout.prop_search(md, "mask_tex_uv_layer", ob.data, "uv_textures")

    def VERTEX_WEIGHT_EDIT(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.label(text="Vertex Group:")
        col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

        col.label(text="Default Weight:")
        col.prop(md, "default_weight", text="")

        col = split.column()
        col.prop(md, "use_add")
        sub = col.column()
        sub.active = md.use_add
        sub.prop(md, "add_threshold")

        col = col.column()
        col.prop(md, "use_remove")
        sub = col.column()
        sub.active = md.use_remove
        sub.prop(md, "remove_threshold")

        layout.separator()

        layout.prop(md, "falloff_type")
        if md.falloff_type == 'CURVE':
            layout.template_curve_mapping(md, "map_curve")

        # Common mask options
        layout.separator()
        self.vertex_weight_mask(layout, ob, md)

    def VERTEX_WEIGHT_MIX(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.label(text="Vertex Group A:")
        col.prop_search(md, "vertex_group_a", ob, "vertex_groups", text="")
        col.label(text="Default Weight A:")
        col.prop(md, "default_weight_a", text="")

        col.label(text="Mix Mode:")
        col.prop(md, "mix_mode", text="")

        col = split.column()
        col.label(text="Vertex Group B:")
        col.prop_search(md, "vertex_group_b", ob, "vertex_groups", text="")
        col.label(text="Default Weight B:")
        col.prop(md, "default_weight_b", text="")

        col.label(text="Mix Set:")
        col.prop(md, "mix_set", text="")

        # Common mask options
        layout.separator()
        self.vertex_weight_mask(layout, ob, md)

    def VERTEX_WEIGHT_PROXIMITY(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        col.label(text="Vertex Group:")
        col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

        col = split.column()
        col.label(text="Target Object:")
        col.prop(md, "target", text="")

        split = layout.split()

        col = split.column()
        col.label(text="Distance:")
        col.prop(md, "proximity_mode", text="")
        if md.proximity_mode == 'GEOMETRY':
            col.row().prop(md, "proximity_geometry")

        col = split.column()
        col.label()
        col.prop(md, "min_dist")
        col.prop(md, "max_dist")

        layout.separator()
        layout.prop(md, "falloff_type")

        # Common mask options
        layout.separator()
        self.vertex_weight_mask(layout, ob, md)

    def SKIN(self, layout, ob, md):
        layout.operator("object.skin_armature_create", text="Create Armature")

        layout.separator()

        col = layout.column(align=True)
        col.prop(md, "branch_smoothing")
        col.prop(md, "use_smooth_shade")

        split = layout.split()

        col = split.column()
        col.label(text="Selected Vertices:")
        sub = col.column(align=True)
        sub.operator("object.skin_loose_mark_clear", text="Mark Loose").action = 'MARK'
        sub.operator("object.skin_loose_mark_clear", text="Clear Loose").action = 'CLEAR'

        sub = col.column()
        sub.operator("object.skin_root_mark", text="Mark Root")
        sub.operator("object.skin_radii_equalize", text="Equalize Radii")

        col = split.column()
        col.label(text="Symmetry Axes:")
        col.prop(md, "use_x_symmetry")
        col.prop(md, "use_y_symmetry")
        col.prop(md, "use_z_symmetry")

    def TRIANGULATE(self, layout, ob, md):
        row = layout.row()

        col = row.column()
        col.label(text="Quad Method:")
        col.prop(md, "quad_method", text="")
        col = row.column()
        col.label(text="Ngon Method:")
        col.prop(md, "ngon_method", text="")

    def UV_WARP(self, layout, ob, md):
        split = layout.split()
        col = split.column()
        col.prop(md, "center")

        col = split.column()
        col.label(text="UV Axis:")
        col.prop(md, "axis_u", text="")
        col.prop(md, "axis_v", text="")

        split = layout.split()
        col = split.column()
        col.label(text="From:")
        col.prop(md, "object_from", text="")

        col = split.column()
        col.label(text="To:")
        col.prop(md, "object_to", text="")

        split = layout.split()
        col = split.column()
        obj = md.object_from
        if obj and obj.type == 'ARMATURE':
            col.label(text="Bone:")
            col.prop_search(md, "bone_from", obj.data, "bones", text="")

        col = split.column()
        obj = md.object_to
        if obj and obj.type == 'ARMATURE':
            col.label(text="Bone:")
            col.prop_search(md, "bone_to", obj.data, "bones", text="")

        split = layout.split()

        col = split.column()
        col.label(text="Vertex Group:")
        col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

        col = split.column()
        col.label(text="UV Map:")
        col.prop_search(md, "uv_layer", ob.data, "uv_textures", text="")

    def WIREFRAME(self, layout, ob, md):
        has_vgroup = bool(md.vertex_group)

        split = layout.split()

        col = split.column()
        col.prop(md, "thickness", text="Thickness")

        row = col.row(align=True)
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="")
        sub = row.row(align=True)
        sub.active = has_vgroup
        sub.prop(md, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
        row = col.row(align=True)
        row.active = has_vgroup
        row.prop(md, "thickness_vertex_group", text="Factor")

        col.prop(md, "use_crease", text="Crease Edges")
        col.prop(md, "crease_weight", text="Crease Weight")

        col = split.column()

        col.prop(md, "offset")
        col.prop(md, "use_even_offset", text="Even Thickness")
        col.prop(md, "use_relative_offset", text="Relative Thickness")
        col.prop(md, "use_boundary", text="Boundary")
        col.prop(md, "use_replace", text="Replace Original")

        col.prop(md, "material_offset", text="Material Offset")

        
class constraints():

    def draw_object_constraints(self, layout, obj):

        if obj:
            layout.operator_menu_enum("object.constraint_add", "type")

            for con in obj.constraints:
                box = layout.box()
                self.draw_constraint(self, box, con)
        else:
            layout.label("Select an Object to View Constraints",icon='ERROR')

    def draw_constraint(self, layout, con):

        box = layout.template_constraint(con)

        if box:
            # match enum type to our functions, avoids a lookup table.
            getattr(self, con.type)(self, None, box, con)

            if con.type not in {'RIGID_BODY_JOINT', 'NULL'}:
                box.prop(con, "influence")

    def space_template(self, layout, con, target=True, owner=True):
        if target or owner:

            split = layout.split(percentage=0.2)

            split.label(text="Space:")
            row = split.row()

            if target:
                row.prop(con, "target_space", text="")

            if target and owner:
                row.label(icon='ARROW_LEFTRIGHT')

            if owner:
                row.prop(con, "owner_space", text="")

    def target_template(self, layout, con, subtargets=True):
        layout.prop(con, "target")  # XXX limiting settings for only 'curves' or some type of object

        if con.target and subtargets:
            if con.target.type == 'ARMATURE':
                layout.prop_search(con, "subtarget", con.target.data, "bones", text="Bone")

                if hasattr(con, "head_tail"):
                    row = layout.row()
                    row.label(text="Head/Tail:")
                    row.prop(con, "head_tail", text="")
            elif con.target.type in {'MESH', 'LATTICE'}:
                layout.prop_search(con, "subtarget", con.target, "vertex_groups", text="Vertex Group")

    def ik_template(self, layout, con):
        # only used for iTaSC
        layout.prop(con, "pole_target")

        if con.pole_target and con.pole_target.type == 'ARMATURE':
            layout.prop_search(con, "pole_subtarget", con.pole_target.data, "bones", text="Bone")

        if con.pole_target:
            row = layout.row()
            row.label()
            row.prop(con, "pole_angle")

        split = layout.split(percentage=0.33)
        col = split.column()
        col.prop(con, "use_tail")
        col.prop(con, "use_stretch")

        col = split.column()
        col.prop(con, "chain_count")

    def CHILD_OF(self, context, layout, con):
        self.target_template(self, layout, con)

        split = layout.split()

        col = split.column()
        col.label(text="Location:")
        col.prop(con, "use_location_x", text="X")
        col.prop(con, "use_location_y", text="Y")
        col.prop(con, "use_location_z", text="Z")

        col = split.column()
        col.label(text="Rotation:")
        col.prop(con, "use_rotation_x", text="X")
        col.prop(con, "use_rotation_y", text="Y")
        col.prop(con, "use_rotation_z", text="Z")

        col = split.column()
        col.label(text="Scale:")
        col.prop(con, "use_scale_x", text="X")
        col.prop(con, "use_scale_y", text="Y")
        col.prop(con, "use_scale_z", text="Z")

        row = layout.row()
        row.operator("constraint.childof_set_inverse")
        row.operator("constraint.childof_clear_inverse")

    def TRACK_TO(self, context, layout, con):
        self.target_template(self, layout, con)

        row = layout.row()
        row.label(text="To:")
        row.prop(con, "track_axis", expand=True)

        row = layout.row()
        row.prop(con, "up_axis", text="Up")
        row.prop(con, "use_target_z")

        self.space_template(layout, con)

    def IK(self, context, layout, con):
        if context.object.pose.ik_solver == 'ITASC':
            layout.prop(con, "ik_type")
            getattr(self, 'IK_' + con.ik_type)(context, layout, con)
        else:
            # Standard IK constraint
            self.target_template(self, layout, con)
            layout.prop(con, "pole_target")

            if con.pole_target and con.pole_target.type == 'ARMATURE':
                layout.prop_search(con, "pole_subtarget", con.pole_target.data, "bones", text="Bone")

            if con.pole_target:
                row = layout.row()
                row.prop(con, "pole_angle")
                row.label()

            split = layout.split()
            col = split.column()
            col.prop(con, "iterations")
            col.prop(con, "chain_count")

            col = split.column()
            col.prop(con, "use_tail")
            col.prop(con, "use_stretch")

            layout.label(text="Weight:")

            split = layout.split()
            col = split.column()
            row = col.row(align=True)
            row.prop(con, "use_location", text="")
            sub = row.row()
            sub.active = con.use_location
            sub.prop(con, "weight", text="Position", slider=True)

            col = split.column()
            row = col.row(align=True)
            row.prop(con, "use_rotation", text="")
            sub = row.row()
            sub.active = con.use_rotation
            sub.prop(con, "orient_weight", text="Rotation", slider=True)

    def IK_COPY_POSE(self, context, layout, con):
        self.target_template(self, layout, con)
        self.ik_template(self, layout, con)

        row = layout.row()
        row.label(text="Axis Ref:")
        row.prop(con, "reference_axis", expand=True)
        split = layout.split(percentage=0.33)
        split.row().prop(con, "use_location")
        row = split.row()
        row.prop(con, "weight", text="Weight", slider=True)
        row.active = con.use_location
        split = layout.split(percentage=0.33)
        row = split.row()
        row.label(text="Lock:")
        row = split.row()
        row.prop(con, "lock_location_x", text="X")
        row.prop(con, "lock_location_y", text="Y")
        row.prop(con, "lock_location_z", text="Z")
        split.active = con.use_location

        split = layout.split(percentage=0.33)
        split.row().prop(con, "use_rotation")
        row = split.row()
        row.prop(con, "orient_weight", text="Weight", slider=True)
        row.active = con.use_rotation
        split = layout.split(percentage=0.33)
        row = split.row()
        row.label(text="Lock:")
        row = split.row()
        row.prop(con, "lock_rotation_x", text="X")
        row.prop(con, "lock_rotation_y", text="Y")
        row.prop(con, "lock_rotation_z", text="Z")
        split.active = con.use_rotation

    def IK_DISTANCE(self, context, layout, con):
        self.target_template(self,layout, con)
        self.ik_template(self,layout, con)

        layout.prop(con, "limit_mode")

        row = layout.row()
        row.prop(con, "weight", text="Weight", slider=True)
        row.prop(con, "distance", text="Distance", slider=True)

    def FOLLOW_PATH(self, context, layout, con):
        self.target_template(self,layout, con)
        layout.operator("constraint.followpath_path_animate", text="Animate Path", icon='ANIM_DATA')

        split = layout.split()

        col = split.column()
        col.prop(con, "use_curve_follow")
        col.prop(con, "use_curve_radius")

        col = split.column()
        col.prop(con, "use_fixed_location")
        if con.use_fixed_location:
            col.prop(con, "offset_factor", text="Offset")
        else:
            col.prop(con, "offset")

        row = layout.row()
        row.label(text="Forward:")
        row.prop(con, "forward_axis", expand=True)

        row = layout.row()
        row.prop(con, "up_axis", text="Up")
        row.label()

    def LIMIT_ROTATION(self, context, layout, con):
        split = layout.split()

        col = split.column(align=True)
        col.prop(con, "use_limit_x")
        sub = col.column()
        sub.active = con.use_limit_x
        sub.prop(con, "min_x", text="Min")
        sub.prop(con, "max_x", text="Max")

        col = split.column(align=True)
        col.prop(con, "use_limit_y")
        sub = col.column()
        sub.active = con.use_limit_y
        sub.prop(con, "min_y", text="Min")
        sub.prop(con, "max_y", text="Max")

        col = split.column(align=True)
        col.prop(con, "use_limit_z")
        sub = col.column()
        sub.active = con.use_limit_z
        sub.prop(con, "min_z", text="Min")
        sub.prop(con, "max_z", text="Max")

        layout.prop(con, "use_transform_limit")

        row = layout.row()
        row.label(text="Convert:")
        row.prop(con, "owner_space", text="")

    def LIMIT_LOCATION(self, context, layout, con):
        split = layout.split()

        col = split.column()
        col.prop(con, "use_min_x")
        sub = col.column()
        sub.active = con.use_min_x
        sub.prop(con, "min_x", text="")
        col.prop(con, "use_max_x")
        sub = col.column()
        sub.active = con.use_max_x
        sub.prop(con, "max_x", text="")

        col = split.column()
        col.prop(con, "use_min_y")
        sub = col.column()
        sub.active = con.use_min_y
        sub.prop(con, "min_y", text="")
        col.prop(con, "use_max_y")
        sub = col.column()
        sub.active = con.use_max_y
        sub.prop(con, "max_y", text="")

        col = split.column()
        col.prop(con, "use_min_z")
        sub = col.column()
        sub.active = con.use_min_z
        sub.prop(con, "min_z", text="")
        col.prop(con, "use_max_z")
        sub = col.column()
        sub.active = con.use_max_z
        sub.prop(con, "max_z", text="")

        row = layout.row()
        row.prop(con, "use_transform_limit")
        row.label()

        row = layout.row()
        row.label(text="Convert:")
        row.prop(con, "owner_space", text="")

    def LIMIT_SCALE(self, context, layout, con):
        split = layout.split()

        col = split.column()
        col.prop(con, "use_min_x")
        sub = col.column()
        sub.active = con.use_min_x
        sub.prop(con, "min_x", text="")
        col.prop(con, "use_max_x")
        sub = col.column()
        sub.active = con.use_max_x
        sub.prop(con, "max_x", text="")

        col = split.column()
        col.prop(con, "use_min_y")
        sub = col.column()
        sub.active = con.use_min_y
        sub.prop(con, "min_y", text="")
        col.prop(con, "use_max_y")
        sub = col.column()
        sub.active = con.use_max_y
        sub.prop(con, "max_y", text="")

        col = split.column()
        col.prop(con, "use_min_z")
        sub = col.column()
        sub.active = con.use_min_z
        sub.prop(con, "min_z", text="")
        col.prop(con, "use_max_z")
        sub = col.column()
        sub.active = con.use_max_z
        sub.prop(con, "max_z", text="")

        row = layout.row()
        row.prop(con, "use_transform_limit")
        row.label()

        row = layout.row()
        row.label(text="Convert:")
        row.prop(con, "owner_space", text="")

    def COPY_ROTATION(self, context, layout, con):
        self.target_template(self,layout, con)

        split = layout.split()

        col = split.column()
        col.prop(con, "use_x", text="X")
        sub = col.column()
        sub.active = con.use_x
        sub.prop(con, "invert_x", text="Invert")

        col = split.column()
        col.prop(con, "use_y", text="Y")
        sub = col.column()
        sub.active = con.use_y
        sub.prop(con, "invert_y", text="Invert")

        col = split.column()
        col.prop(con, "use_z", text="Z")
        sub = col.column()
        sub.active = con.use_z
        sub.prop(con, "invert_z", text="Invert")

        layout.prop(con, "use_offset")

        self.space_template(layout, con)

    def COPY_LOCATION(self, context, layout, con):
        self.target_template(self,layout, con)

        split = layout.split()

        col = split.column()
        col.prop(con, "use_x", text="X")
        sub = col.column()
        sub.active = con.use_x
        sub.prop(con, "invert_x", text="Invert")

        col = split.column()
        col.prop(con, "use_y", text="Y")
        sub = col.column()
        sub.active = con.use_y
        sub.prop(con, "invert_y", text="Invert")

        col = split.column()
        col.prop(con, "use_z", text="Z")
        sub = col.column()
        sub.active = con.use_z
        sub.prop(con, "invert_z", text="Invert")

        layout.prop(con, "use_offset")

        self.space_template(layout, con)

    def COPY_SCALE(self, context, layout, con):
        self.target_template(self,layout, con)

        row = layout.row(align=True)
        row.prop(con, "use_x", text="X")
        row.prop(con, "use_y", text="Y")
        row.prop(con, "use_z", text="Z")

        layout.prop(con, "use_offset")

        self.space_template(layout, con)

    def MAINTAIN_VOLUME(self, context, layout, con):

        row = layout.row()
        row.label(text="Free:")
        row.prop(con, "free_axis", expand=True)

        layout.prop(con, "volume")

        row = layout.row()
        row.label(text="Convert:")
        row.prop(con, "owner_space", text="")

    def COPY_TRANSFORMS(self, context, layout, con):
        self.target_template(self,layout, con)

        self.space_template(self,layout, con)

    #def SCRIPT(self, context, layout, con):

    def ACTION(self, context, layout, con):
        self.target_template(self,layout, con)

        split = layout.split()

        col = split.column()
        col.label(text="From Target:")
        col.prop(con, "transform_channel", text="")
        col.prop(con, "target_space", text="")

        col = split.column()
        col.label(text="To Action:")
        col.prop(con, "action", text="")
        col.prop(con, "use_bone_object_action")

        split = layout.split()

        col = split.column(align=True)
        col.label(text="Target Range:")
        col.prop(con, "min", text="Min")
        col.prop(con, "max", text="Max")

        col = split.column(align=True)
        col.label(text="Action Range:")
        col.prop(con, "frame_start", text="Start")
        col.prop(con, "frame_end", text="End")

    def LOCKED_TRACK(self, context, layout, con):
        self.target_template(self,layout, con)

        row = layout.row()
        row.label(text="To:")
        row.prop(con, "track_axis", expand=True)

        row = layout.row()
        row.label(text="Lock:")
        row.prop(con, "lock_axis", expand=True)

    def LIMIT_DISTANCE(self, context, layout, con):
        self.target_template(self,layout, con)

        col = layout.column(align=True)
        col.prop(con, "distance")
        col.operator("constraint.limitdistance_reset")

        row = layout.row()
        row.label(text="Clamp Region:")
        row.prop(con, "limit_mode", text="")

        row = layout.row()
        row.prop(con, "use_transform_limit")
        row.label()

        self.space_template(layout, con)

    def STRETCH_TO(self, context, layout, con):
        self.target_template(self,layout, con)

        row = layout.row()
        row.prop(con, "rest_length", text="Rest Length")
        row.operator("constraint.stretchto_reset", text="Reset")

        layout.prop(con, "bulge", text="Volume Variation")

        row = layout.row()
        row.label(text="Volume:")
        row.prop(con, "volume", expand=True)

        row.label(text="Plane:")
        row.prop(con, "keep_axis", expand=True)

    def FLOOR(self, context, layout, con):
        self.target_template(self,layout, con)

        row = layout.row()
        row.prop(con, "use_sticky")
        row.prop(con, "use_rotation")

        layout.prop(con, "offset")

        row = layout.row()
        row.label(text="Min/Max:")
        row.prop(con, "floor_location", expand=True)

        self.space_template(self,layout, con)

    def RIGID_BODY_JOINT(self, context, layout, con):
        self.target_template(self,layout, con, subtargets=False)

        layout.prop(con, "pivot_type")
        layout.prop(con, "child")

        row = layout.row()
        row.prop(con, "use_linked_collision", text="Linked Collision")
        row.prop(con, "show_pivot", text="Display Pivot")

        split = layout.split()

        col = split.column(align=True)
        col.label(text="Pivot:")
        col.prop(con, "pivot_x", text="X")
        col.prop(con, "pivot_y", text="Y")
        col.prop(con, "pivot_z", text="Z")

        col = split.column(align=True)
        col.label(text="Axis:")
        col.prop(con, "axis_x", text="X")
        col.prop(con, "axis_y", text="Y")
        col.prop(con, "axis_z", text="Z")

        if con.pivot_type == 'CONE_TWIST':
            layout.label(text="Limits:")
            split = layout.split()

            col = split.column()
            col.prop(con, "use_angular_limit_x", text="Angle X")
            sub = col.column()
            sub.active = con.use_angular_limit_x
            sub.prop(con, "limit_angle_max_x", text="")

            col = split.column()
            col.prop(con, "use_angular_limit_y", text="Angle Y")
            sub = col.column()
            sub.active = con.use_angular_limit_y
            sub.prop(con, "limit_angle_max_y", text="")

            col = split.column()
            col.prop(con, "use_angular_limit_z", text="Angle Z")
            sub = col.column()
            sub.active = con.use_angular_limit_z
            sub.prop(con, "limit_angle_max_z", text="")

        elif con.pivot_type == 'GENERIC_6_DOF':
            layout.label(text="Limits:")
            split = layout.split()

            col = split.column(align=True)
            col.prop(con, "use_limit_x", text="X")
            sub = col.column()
            sub.active = con.use_limit_x
            sub.prop(con, "limit_min_x", text="Min")
            sub.prop(con, "limit_max_x", text="Max")

            col = split.column(align=True)
            col.prop(con, "use_limit_y", text="Y")
            sub = col.column()
            sub.active = con.use_limit_y
            sub.prop(con, "limit_min_y", text="Min")
            sub.prop(con, "limit_max_y", text="Max")

            col = split.column(align=True)
            col.prop(con, "use_limit_z", text="Z")
            sub = col.column()
            sub.active = con.use_limit_z
            sub.prop(con, "limit_min_z", text="Min")
            sub.prop(con, "limit_max_z", text="Max")

            split = layout.split()

            col = split.column(align=True)
            col.prop(con, "use_angular_limit_x", text="Angle X")
            sub = col.column()
            sub.active = con.use_angular_limit_x
            sub.prop(con, "limit_angle_min_x", text="Min")
            sub.prop(con, "limit_angle_max_x", text="Max")

            col = split.column(align=True)
            col.prop(con, "use_angular_limit_y", text="Angle Y")
            sub = col.column()
            sub.active = con.use_angular_limit_y
            sub.prop(con, "limit_angle_min_y", text="Min")
            sub.prop(con, "limit_angle_max_y", text="Max")

            col = split.column(align=True)
            col.prop(con, "use_angular_limit_z", text="Angle Z")
            sub = col.column()
            sub.active = con.use_angular_limit_z
            sub.prop(con, "limit_angle_min_z", text="Min")
            sub.prop(con, "limit_angle_max_z", text="Max")

        elif con.pivot_type == 'HINGE':
            layout.label(text="Limits:")
            split = layout.split()

            row = split.row(align=True)
            col = row.column()
            col.prop(con, "use_angular_limit_x", text="Angle X")

            col = row.column()
            col.active = con.use_angular_limit_x
            col.prop(con, "limit_angle_min_x", text="Min")
            col = row.column()
            col.active = con.use_angular_limit_x
            col.prop(con, "limit_angle_max_x", text="Max")

    def CLAMP_TO(self, context, layout, con):
        self.target_template(self,layout, con)

        row = layout.row()
        row.label(text="Main Axis:")
        row.prop(con, "main_axis", expand=True)

        layout.prop(con, "use_cyclic")

    def TRANSFORM(self, context, layout, con):
        self.target_template(self,layout, con)

        layout.prop(con, "use_motion_extrapolate", text="Extrapolate")

        col = layout.column()
        col.row().label(text="Source:")
        col.row().prop(con, "map_from", expand=True)

        split = layout.split()

        sub = split.column(align=True)
        sub.label(text="X:")
        sub.prop(con, "from_min_x", text="Min")
        sub.prop(con, "from_max_x", text="Max")

        sub = split.column(align=True)
        sub.label(text="Y:")
        sub.prop(con, "from_min_y", text="Min")
        sub.prop(con, "from_max_y", text="Max")

        sub = split.column(align=True)
        sub.label(text="Z:")
        sub.prop(con, "from_min_z", text="Min")
        sub.prop(con, "from_max_z", text="Max")

        col = layout.column()
        row = col.row()
        row.label(text="Source to Destination Mapping:")

        # note: chr(187) is the ASCII arrow ( >> ). Blender Text Editor can't
        # open it. Thus we are using the hard-coded value instead.
        row = col.row()
        row.prop(con, "map_to_x_from", expand=False, text="")
        row.label(text=" %s    X" % chr(187))

        row = col.row()
        row.prop(con, "map_to_y_from", expand=False, text="")
        row.label(text=" %s    Y" % chr(187))

        row = col.row()
        row.prop(con, "map_to_z_from", expand=False, text="")
        row.label(text=" %s    Z" % chr(187))

        split = layout.split()

        col = split.column()
        col.label(text="Destination:")
        col.row().prop(con, "map_to", expand=True)

        split = layout.split()

        col = split.column()
        col.label(text="X:")

        sub = col.column(align=True)
        sub.prop(con, "to_min_x", text="Min")
        sub.prop(con, "to_max_x", text="Max")

        col = split.column()
        col.label(text="Y:")

        sub = col.column(align=True)
        sub.prop(con, "to_min_y", text="Min")
        sub.prop(con, "to_max_y", text="Max")

        col = split.column()
        col.label(text="Z:")

        sub = col.column(align=True)
        sub.prop(con, "to_min_z", text="Min")
        sub.prop(con, "to_max_z", text="Max")

        self.space_template(self,layout, con)

    def SHRINKWRAP(self, context, layout, con):
        self.target_template(self,layout, con, False)

        layout.prop(con, "distance")
        layout.prop(con, "shrinkwrap_type")

        if con.shrinkwrap_type == 'PROJECT':
            row = layout.row(align=True)
            row.prop(con, "use_x")
            row.prop(con, "use_y")
            row.prop(con, "use_z")

    def DAMPED_TRACK(self, context, layout, con):
        self.target_template(self,layout, con)

        row = layout.row()
        row.label(text="To:")
        row.prop(con, "track_axis", expand=True)

    def SPLINE_IK(self, context, layout, con):
        self.target_template(self,layout, con)

        col = layout.column()
        col.label(text="Spline Fitting:")
        col.prop(con, "chain_count")
        col.prop(con, "use_even_divisions")
        col.prop(con, "use_chain_offset")

        col = layout.column()
        col.label(text="Chain Scaling:")
        col.prop(con, "use_y_stretch")
        col.prop(con, "xz_scale_mode")
        col.prop(con, "use_curve_radius")

    def PIVOT(self, context, layout, con):
        self.target_template(self,layout, con)

        if con.target:
            col = layout.column()
            col.prop(con, "offset", text="Pivot Offset")
        else:
            col = layout.column()
            col.prop(con, "use_relative_location")
            if con.use_relative_location:
                col.prop(con, "offset", text="Relative Pivot Point")
            else:
                col.prop(con, "offset", text="Absolute Pivot Point")

        col = layout.column()
        col.prop(con, "rotation_range", text="Pivot When")

    @staticmethod
    def _getConstraintClip(context, con):
        if not con.use_active_clip:
            return con.clip
        else:
            return context.scene.active_clip

    def FOLLOW_TRACK(self, context, layout, con):
        clip = self._getConstraintClip(self,context, con)

        row = layout.row()
        row.prop(con, "use_active_clip")
        row.prop(con, "use_3d_position")

        col = layout.column()

        if not con.use_active_clip:
            col.prop(con, "clip")

        row = col.row()
        row.prop(con, "frame_method", expand=True)

        if clip:
            tracking = clip.tracking

            col.prop_search(con, "object", tracking, "objects", icon='OBJECT_DATA')

            tracking_object = tracking.objects.get(con.object, tracking.objects[0])

            col.prop_search(con, "track", tracking_object, "tracks", icon='ANIM_DATA')

        col.prop(con, "camera")

        row = col.row()
        row.active = not con.use_3d_position
        row.prop(con, "depth_object")

        layout.operator("clip.constraint_to_fcurve")

    def CAMERA_SOLVER(self, context, layout, con):
        layout.prop(con, "use_active_clip")

        if not con.use_active_clip:
            layout.prop(con, "clip")

        layout.operator("clip.constraint_to_fcurve")

    def OBJECT_SOLVER(self, context, layout, con):
        clip = self._getConstraintClip(self,context, con)

        layout.prop(con, "use_active_clip")

        if not con.use_active_clip:
            layout.prop(con, "clip")

        if clip:
            layout.prop_search(con, "object", clip.tracking, "objects", icon='OBJECT_DATA')

        layout.prop(con, "camera")

        row = layout.row()
        row.operator("constraint.objectsolver_set_inverse")
        row.operator("constraint.objectsolver_clear_inverse")

        layout.operator("clip.constraint_to_fcurve")

    def SCRIPT(self, context, layout, con):
        layout.label("Blender 2.6 doesn't support python constraints yet.")


#------DATABLOCK EXTENSIONS

class fd_tab(bpy.types.PropertyGroup):
    type = StringProperty(name="Type")
    index = IntProperty(name="Index")

bpy.utils.register_class(fd_tab)
    
class fd_tab_col(bpy.types.PropertyGroup):
    col_tab = CollectionProperty(name="Collection Tab",type=fd_tab)
    index_tab = IntProperty(name="Index Tab",min=-1)

    def add_tab(self, name):
        tab = self.col_tab.add()
        tab.name = name
        tab.index = len(self.col_tab)
        return tab
    
    def delete_tab(self, index):
        for index, tab in enumerate(self.col_tab):
            if tab.index == index:
                self.col_tab.remove(index)

    def draw_tabs(self,layout):
        layout.template_list("FD_UL_specgroups", " ", self, "col_tab", self, "index_tab", rows=3)

bpy.utils.register_class(fd_tab_col)

#TODO: implement the standard collections or remove this and add to RNA Structure
class mvPrompt(bpy.types.PropertyGroup):
    Obj_LinkID = StringProperty(name="Obj_LinkID")
    Type = EnumProperty(name="Type",items=enums.enum_prompt_types)
    Value = StringProperty(name="Value")
    TabIndex = IntProperty(name="Tab Index",default = 0)
    parent_link_name = StringProperty(name="Parent Link Name")
    lock_value = BoolProperty(name="lock value")
    
    COL_EnumItem = bpy.props.CollectionProperty(name="COL_Enum Items",type=fd_tab)
    EnumIndex = IntProperty(name="EnumIndex")
    
    CheckBoxValue = BoolProperty(name="Check Box Values")
    
    QuantityValue = IntProperty(name="Quantity Value")
    
    TextValue = StringProperty(name="Text Value")
    
    NumberValue = FloatProperty(name="Number Value",precision=4,step=10)
    
    def draw_prompt(self,layout,data,allow_edit=True):
        data_type = 'OBJECT' #SETS DEFAULT
        
        if data is bpy.types.Scene:
            data_type = 'SCENE'
        elif data is bpy.types.Material:
            data_type = 'MATERIAL'
        elif data is bpy.types.World:
            data_type = 'WORLD'
        
        row = layout.row()
        row.label(self.name)
        if self.Type == 'NUMBER':
            if self.lock_value:
                row.label(str(self.NumberValue))
            else:
                row.prop(self,"NumberValue",text="")
            
        if self.Type == 'QUANTITY':
            if self.lock_value:
                row.label(str(self.QuantityValue))
            else:
                row.prop(self,"QuantityValue",text="")
            
        if self.Type == 'COMBOBOX':
            if self.lock_value:
                row.label(self.COL_EnumItem[self.EnumIndex].name)
            else:
                if allow_edit:
                    prop = row.operator("fd_prompts.add_combo_box_option",icon='ZOOMIN',text="")
                    prop.prompt_name = self.name
                    prop.data_name = self.Obj_LinkID
                col = layout.column()
                col.template_list("FD_UL_prompttabs"," ", self, "COL_EnumItem", self, "EnumIndex",rows=len(self.COL_EnumItem),type='DEFAULT')
        
        if self.Type == 'CHECKBOX':
            if self.lock_value:
                row.label(str(self.CheckBoxValue))
            else:
                row.prop(self,"CheckBoxValue",text="")
            
        if self.Type == 'SLIDER':
            row.prop(self,"NumberValue",text="",slider=True)
            
        if self.Type == 'TEXT':
            row.prop(self,"TextValue",text="")
            
        if allow_edit:
            props = row.operator("fd_prompts.show_prompt_properties",text="",icon='INFO')
            props.prompt_name = self.name
            props.data_type = data_type
            props.data_name = data.name
            
            props = row.operator("fd_prompts.delete_prompt",icon='X',text="")
            props.prompt_name = self.name
            props.data_type = data_type
            props.data_name = data.name
        
    def add_enum_item(self,Name):
        Item = self.COL_EnumItem.add()
        Item.name = Name
        
    def Update(self):
        self.NumberValue = self.NumberValue
        self.TextValue = self.TextValue
        self.QuantityValue = self.QuantityValue
        self.CheckBoxValue = self.CheckBoxValue
        self.EnumIndex = self.EnumIndex
        
    def draw_prompt_properties(self,layout):
        layout.prop(self,"name")
        layout.prop(self,"Type")
        layout.prop(self,"lock_value")
        row = layout.row()
        row.label('Tab Index:')
        row.prop(self,"TabIndex",expand=True)
        
    def show_prompt_tabs(self,layout):  
        layout.template_list("FD_UL_prompttabs"," ", self, "COL_MainTab", self, "MainTabIndex",rows=len(self.COL_MainTab),type='DEFAULT')
        
bpy.utils.register_class(mvPrompt)

#TODO: implement the standard collections or remove this and add to RNA Structure
class mvPromptPage(bpy.types.PropertyGroup):
    COL_MainTab = CollectionProperty(name="COL_Enum Items",type=fd_tab)
    MainTabIndex = IntProperty(name="Main Tab Index")
    COL_Prompt = CollectionProperty(name="COL_Prompt",type=mvPrompt)
    PromptIndex = IntProperty(name="Prompt Index")
    PromptTempIndex = IntProperty(name="Prompt Temp Index")
    Obj_LinkID = StringProperty(name="Obj Link ID")
    
    def add_tab(self,Name):
        Tab = self.COL_MainTab.add()
        Tab.name = Name
    
    def add_prompt(self,name,type,data_name):
        self.Obj_LinkID = data_name
        Prompt = self.COL_Prompt.add()
        Prompt.name = name
        Prompt.Type = type
        return Prompt

    def delete_prompt(self,Name):
        for index, Prompt in enumerate(self.COL_Prompt):
            if Prompt.name == Name:
                self.COL_Prompt.remove(index)

    def delete_selected_tab(self):
        self.COL_MainTab.remove(self.MainTabIndex)

    def rename_selected_tab(self,Name):
        self.COL_MainTab[self.MainTabIndex].name = Name

    #TODO: MAYBE DELETE THIS
    def Update(self):
        for Prompt in self.COL_Prompt:
            Prompt.Update()

    def draw_prompts_list(self,layout):
        Rows = len(self.COL_Prompt)
        if Rows > 8:
            Rows = 10
        layout.template_list("MV_UL_default"," ", self, "COL_Prompt", self, "PromptIndex",rows=Rows)
        Prompt = self.COL_Prompt[self.PromptIndex]
        Prompt.DrawPrompt(layout,obj=None,AllowEdit=False)

    def draw_prompt_page(self,layout,data,allow_edit=True):
        datatype = 'OBJECT'
        if type(data) is bpy.types.Scene:
            datatype = 'SCENE'
        elif type(data) is bpy.types.Material:
            datatype = 'MATERIAL'
        elif type(data) is bpy.types.World:
            datatype = 'WORLD'
        layout.label('Custom Prompts',icon='SETTINGS')
        row = layout.row(align=True)
        if allow_edit:
            props = row.operator("fd_prompts.add_main_tab",text="Add Tab",icon='SPLITSCREEN')
            props.data_type = datatype
            props.data_name = data.name
        if len(self.COL_MainTab) > 0:
            if allow_edit:
                props1 = row.operator("fd_prompts.rename_main_tab",text="Rename Tab",icon='GREASEPENCIL')
                props1.data_type = datatype
                props1.data_name = data.name
                props2 = row.operator("fd_prompts.delete_main_tab",text="Delete Tab",icon='X')
                props2.data_type = datatype
                props2.data_name = data.name
                
            layout.template_list("FD_UL_prompttabs"," ", self, "COL_MainTab", self, "MainTabIndex",rows=len(self.COL_MainTab),type='DEFAULT')
            box = layout.box()
            props3 = box.operator("fd_prompts.add_prompt",text="Add Prompt",icon='UI')
            props3.data_type = datatype
            props3.data_name = data.name
            for prompt in self.COL_Prompt:
                prompt.Obj_LinkID = self.Obj_LinkID
                if prompt.TabIndex == self.MainTabIndex:
                    prompt.draw_prompt(box,data,allow_edit)

    def show_prompts(self,layout,obj,index):
            for Prompt in self.COL_Prompt:
                if Prompt.TabIndex == index:
                    Prompt.draw_prompt(layout,obj,allow_edit=False)
                    
bpy.utils.register_class(mvPromptPage)

#TODO: this can possibly be removed and replaced with custom properties
class fd_material(bpy.types.PropertyGroup):
    PromptPage = bpy.props.PointerProperty(name="Prompt Page",type=mvPromptPage)
    library_name = StringProperty(name="Library Name")
    category_name = StringProperty(name="Category Name")
    
    def draw_properties(self,layout,material):
        layout.prop(material,"name")
        if "Finish Color" in material.node_tree.nodes:
            node_finish_color = material.node_tree.nodes["Finish Color"]
            row = layout.row()
            row.label("Finish Color:")
            row.prop(node_finish_color.inputs[0],"default_value",text="")
            
        if "Finish Color Mix Shader" in material.node_tree.nodes:
            node_color_influence = material.node_tree.nodes["Finish Color Mix Shader"]
            row = layout.row()
            row.label("Finish Color Influence:")
            row.prop(node_color_influence.inputs[0],"default_value",slider=True,text="")
            
        if "Mapping" in material.node_tree.nodes:
            node_mapping = material.node_tree.nodes["Mapping"]
            layout.label(text="Texture Mapping:")
            col = layout.column(align=True)
            row=col.row(align=True)
            row.prop(node_mapping,"translation",index=0,text="Location X")
            row.prop(node_mapping,"translation",index=1,text="Location Y")
            row=col.row(align=True)
            row.prop(node_mapping,"scale",index=0,text="Scale X")
            row.prop(node_mapping,"scale",index=1,text="Scale Y")
            row=col.row(align=True)
            row.prop(node_mapping,"rotation",index=2,text="Texture Rotation")

bpy.utils.register_class(fd_material)

class fd_material_slot(bpy.types.PropertyGroup):
    index = IntProperty(name="Index")
    library_name = StringProperty(name="Library Name")
    category_name = StringProperty(name="Category Name")
    pointer_name = StringProperty(name="Pointer Name",update=events.update_pointer_name)
    item_name = StringProperty(name="Item Name")

bpy.utils.register_class(fd_material_slot)

class fd_object(PropertyGroup):
    index = IntProperty(name="Index")
    Type = EnumProperty(name="type",items=enums.enum_object_types,description="Select the Object Type.",default='NONE') #TODO: REMOVE This is only here for backwards compatibility
    type = EnumProperty(name="type",items=enums.enum_object_types,description="Select the Object Type.",default='NONE')
    
    #These are the group names this object is assign to 
    id_wall = StringProperty(name="LinkID Wall")
    id_plane = StringProperty(name="LinkID Plane")
    id_product = StringProperty(name="LinkID Product")
    id_insert = StringProperty(name="LinkID Insert")
    id_part = StringProperty(name="LinkID Part")
    
    #This is the human readable name of the object
    name_object = StringProperty(name="Object Name")
    
    #This is the human readable name of the group this object belongs to
    #NOTE: These properties are only assigned to the bp object of the smart group
    #      It is needed when dynamically creating groups when appending products or inserts.
#     name_product = StringProperty(name="Name Product")
#     name_insert = StringProperty(name="Name Insert")
#     name_part = StringProperty(name="Name Part")
    
    #Object Options - MUST BE STORED HERE TO PERSIST
    use_as_wall_subtraction = BoolProperty(name="Use As Wall Subtraction",description="Use this object to cut a hole in the wall its added to. Only For Meshes.",default=False)
    use_as_item_number = BoolProperty(name="Use As Item Number",description="Use this object to display the product item number. Only For TEXTPRODUCT.",default=False)
    use_as_mesh_hook = BoolProperty(name="Use As Mesh Hook",description="Use this object to hook to deform a mesh. Only for Empties",default=False)
    
    #TODO: Implement Pointers for Objects and Groups
    library_name = StringProperty(name="Library Name")
    pointer_name = StringProperty(name="Pointer Name")
    
    #TODO: implement the standard collections or remove this and add to RNA Structure
    PromptPage = bpy.props.PointerProperty(name="Prompt Page",type=mvPromptPage)
    
    #MOVE TO SOURCE
    material_slot_col = bpy.props.CollectionProperty(name="Material Slot Collection",type= fd_material_slot)
    
    def draw_properties(self,layout,name):
        ui = bpy.context.scene.mv.ui
        col = layout.column(align=True)
        box = col.box()
        self.draw_object_header(box,name)
        box = col.box()
        split = box.split(percentage=.12)
        col = split.column(align=True)
        self.draw_object_tabs(col,name)
        col = split.column()
        if ui.interface_object_tabs == 'INFO':
            self.draw_object_info(col,name)
        if ui.interface_object_tabs == 'DISPLAY':
            self.draw_object_display(col,name)
        if ui.interface_object_tabs == 'MATERIAL':
            self.draw_object_materials(col,name)
        if ui.interface_object_tabs == 'CONSTRAINTS':
            self.draw_object_constraints(col,name)
        if ui.interface_object_tabs == 'MODIFIERS':
            self.draw_object_modifiers(col,name)
        if ui.interface_object_tabs == 'MESHDATA':
            self.draw_object_data(col,name)
        if ui.interface_object_tabs == 'CURVEDATA':
            self.draw_object_data(col,name)
        if ui.interface_object_tabs == 'TEXTDATA':
            self.draw_object_data(col,name)
        if ui.interface_object_tabs == 'EMPTYDATA':
            self.draw_object_data(col,name)
        if ui.interface_object_tabs == 'LIGHTDATA':
            self.draw_object_data(col,name)
        if ui.interface_object_tabs == 'CAMERADATA':
            self.draw_object_data(col,name)
        if ui.interface_object_tabs == 'DRIVERS':
            self.draw_object_drivers(col,name)

    def draw_object_header(self,layout,name):
        obj = bpy.data.objects[name]
        if obj.mv.name_object == "":
            object_name = "Click to Set Name"
        else:
            object_name = obj.mv.name_object
        if obj.type == 'MESH':
            row = layout.row()
            props = row.operator("fd_object.rename_object",text=object_name,icon=const.icon_mesh)
            props.object_name = obj.name
        if obj.type == 'CURVE':
            row = layout.row()
            props = row.operator("fd_object.rename_object",text=object_name,icon=const.icon_curve)
            props.object_name = obj.name
        if obj.type == 'FONT':
            row = layout.row()
            props = row.operator("fd_object.rename_object",text=object_name,icon=const.icon_font)
            props.object_name = obj.name
        if obj.type == 'EMPTY':
            row = layout.row()
            props = row.operator("fd_object.rename_object",text=object_name,icon=const.icon_empty)
            props.object_name = obj.name
        if obj.type == 'LIGHT':
            row = layout.row()
            props = row.operator("fd_object.rename_object",text=object_name,icon=const.icon_light)
            props.object_name = obj.name
        if obj.type == 'CAMERA':
            row = layout.row()
            props = row.operator("fd_object.rename_object",text=object_name,icon=const.icon_camera)
            props.object_name = obj.name
            
    def draw_object_tabs(self,layout,name):
        ui = bpy.context.scene.mv.ui
        obj = bpy.data.objects[name]
        if obj.type == 'MESH':
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[0][0], icon=const.icon_info, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[1][0], icon=const.icon_display, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[2][0], icon=const.icon_material, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[3][0], icon=const.icon_constraints, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[4][0], icon=const.icon_modifiers, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[5][0], icon=const.icon_mesh_data, text="")  
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[11][0], icon=const.icon_drivers, text="")   
        if obj.type == 'CURVE':
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[0][0], icon=const.icon_info, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[1][0], icon=const.icon_display, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[2][0], icon=const.icon_material, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[3][0], icon=const.icon_constraints, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[4][0], icon=const.icon_modifiers, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[6][0], icon=const.icon_curve_data, text="")  
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[11][0], icon=const.icon_drivers, text="")  
        if obj.type == 'FONT':
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[0][0], icon=const.icon_info, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[1][0], icon=const.icon_display, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[2][0], icon=const.icon_material, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[3][0], icon=const.icon_constraints, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[4][0], icon=const.icon_modifiers, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[7][0], icon=const.icon_font_data, text="")  
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[11][0], icon=const.icon_drivers, text="")  
        if obj.type == 'EMPTY':
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[0][0], icon=const.icon_info, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[1][0], icon=const.icon_display, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[3][0], icon=const.icon_constraints, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[8][0], icon=const.icon_empty_data, text="")  
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[11][0], icon=const.icon_drivers, text="")  
        if obj.type == 'LIGHT':
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[0][0], icon=const.icon_info, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[1][0], icon=const.icon_display, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[3][0], icon=const.icon_constraints, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[9][0], icon=const.icon_light_data, text="")  
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[11][0], icon=const.icon_drivers, text="")  
        if obj.type == 'CAMERA':
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[0][0], icon=const.icon_info, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[3][0], icon=const.icon_constraints, text="") 
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[10][0], icon=const.icon_camera_data, text="")  
            layout.prop_enum(ui, "interface_object_tabs", enums.enum_object_tabs[11][0], icon=const.icon_drivers, text="")  

    def draw_object_info(self,layout,name):
        obj = bpy.data.objects[name]
        box = layout.box()
        box.label('Dimensions:')
        box.prop(obj,"dimensions",text="")
        col1 = box.row()
        
        if obj:
            col2 = col1.split()
            col = col2.column(align=True)
            col.label('Location:')
            
            if obj.lock_location[0]:
                row = col.row(align=True)
                row.prop(obj,"lock_location",index=0,text="")
                row.label(str(obj.location.x))
            else:
                row = col.row(align=True)
                row.prop(obj,"lock_location",index=0,text="")
                row.prop(obj,"location",index=0,text="X")
                
            if obj.lock_location[1]:
                row = col.row(align=True)
                row.prop(obj,"lock_location",index=1,text="")
                row.label(str(obj.location.y))
            else:
                row = col.row(align=True)
                row.prop(obj,"lock_location",index=1,text="")
                row.prop(obj,"location",index=1,text="Y")
                
            if obj.lock_location[2]:
                row = col.row(align=True)
                row.prop(obj,"lock_location",index=2,text="")
                row.label(str(obj.location.z))
            else:
                row = col.row(align=True)
                row.prop(obj,"lock_location",index=2,text="")
                row.prop(obj,"location",index=2,text="Z")
                
            col2 = col1.split()
            col = col2.column(align=True)
            col.label('Rotation:')
            
            if obj.lock_rotation[0]:
                row = col.row(align=True)
                row.prop(obj,"lock_rotation",index=0,text="")
                row.label(str(obj.rotation_euler.x))
            else:
                row = col.row(align=True)
                row.prop(obj,"lock_rotation",index=0,text="")
                row.prop(obj,"rotation_euler",index=0,text="X")
                
            if obj.lock_rotation[1]:
                row = col.row(align=True)
                row.prop(obj,"lock_rotation",index=1,text="")
                row.label(str(obj.rotation_euler.y))
            else:
                row = col.row(align=True)
                row.prop(obj,"lock_rotation",index=1,text="")
                row.prop(obj,"rotation_euler",index=1,text="Y")
                
            if obj.lock_rotation[2]:
                row = col.row(align=True)
                row.prop(obj,"lock_rotation",index=2,text="")
                row.label(str(obj.rotation_euler.z))
            else:
                row = col.row(align=True)
                row.prop(obj,"lock_rotation",index=2,text="")
                row.prop(obj,"rotation_euler",index=2,text="Z")
                
    def draw_object_display(self,layout,name):
        obj = bpy.data.objects[name]
        box = layout.box()
        row = box.row()
        row.prop(obj,'draw_type',expand=True)#TODO: Add Icons for Each
        box.prop(obj,'hide_select',expand=True)
        box.prop(obj,'hide')
        box.prop(obj,'hide_render')
        box.prop(obj,'show_x_ray',icon=const.icon_ghost,text='Show X-Ray')
        box.prop(obj.cycles_visibility,'camera',icon='CAMERA_DATA',text='Show in Viewport Render')

    def draw_object_materials(self,layout,name):
        mat = None
        obj = bpy.data.objects[name]
        slot = None
        
        if obj:
            row = layout.row()
            row.template_list("FD_UL_materials", "", obj, "material_slots", obj, "active_material_index", rows=1)

            col = row.column(align=True)
            col.operator("fd_material.add_material_slot", icon='ZOOMIN', text="").object_name = obj.name
            col.operator("object.material_slot_remove", icon='ZOOMOUT', text="")
            col.operator("fd_object.update_object_materials", icon='FILE_REFRESH', text="").object_name = obj.name
            
            col.menu("MATERIAL_MT_specials", icon='DOWNARROW_HLT', text="")
            
            if obj.mode == 'EDIT':
                row = layout.row(align=True)
                row.operator("object.material_slot_assign", text="Assign")
                row.operator("object.material_slot_select", text="Select")
                row.operator("object.material_slot_deselect", text="Deselect")

        if len(obj.material_slots) > 0:
            slot = obj.material_slots[obj.active_material_index]
            mat = slot.material

        row = layout.column()

        if obj:
            row.template_ID(obj, "active_material", new="material.new")
            
        if slot:
            if len(obj.mv.material_slot_col) < len(obj.material_slots):
                layout.operator("fd_object.sync_material_slots", icon='ZOOMIN', text="Sync").object_name = obj.name
            else:
                Pointers = bpy.context.scene.mv.dm.Specgroups.get_active().Pointers
                mvslot = obj.mv.material_slot_col[obj.active_material_index]
                box = layout.box()
                box.prop(mvslot,"name")
                box.prop_search(mvslot,"pointer_name",Pointers,"col_pointer",icon=const.icon_pointer)
                box.label("Library Name: " + mvslot.library_name)
                box.label("Category Name: " + mvslot.category_name)
                box.label("Material Name: " + mvslot.item_name)

    def draw_object_modifiers(self,layout,name):
        obj = bpy.data.objects[name]
        modifiers.draw_object_modifiers(modifiers,layout=layout, obj=obj)

    def draw_object_constraints(self,layout,name):
        obj = bpy.data.objects[name]
        constraints.draw_object_constraints(constraints,layout,obj)

    def draw_object_data(self,layout,name):
        obj = bpy.data.objects[name]
        box = layout.box()
        if obj.type == 'MESH':
            grp = None
            if obj.parent:
                dm = bpy.context.scene.mv.dm
                if obj.parent.mv.type == 'BPWALL':
                    grp = dm.get_wall_group(obj.parent)
                elif obj.parent.mv.type == 'BPPRODUCT':
                    grp = dm.get_product_group(obj.parent)
                elif obj.parent.mv.type == 'BPINSERT':
                    grp = dm.get_insert_group(obj.parent)
                elif obj.parent.mv.type == 'BPPART':
                    grp = dm.get_part_group(obj.parent)
            row = box.row()
            row.prop(obj.mv,"use_as_wall_subtraction")
            box = layout.box()
            row = box.row()
            row.label("Vertex Groups:")
            if len(obj.vertex_groups) > 0:
                if grp:
                    if obj.mode == 'EDIT':
                        row.operator("fd_object.toggle_edit_mode",text="Exit Edit Mode",icon=const.icon_editmode).object_name = obj.name
                    else:
                        row.operator("fd_object.toggle_edit_mode",text="Enter Edit Mode",icon=const.icon_editmode).object_name = obj.name
                box.template_list("FD_UL_vgroups", "", obj, "vertex_groups", obj.vertex_groups, "active_index", rows=3)
                
                if obj.mode == 'EDIT':
                    row = box.row()
                    sub = row.row(align=True)
                    sub.operator("object.vertex_group_assign", text="Assign")
                    sub.operator("object.vertex_group_remove_from", text="Remove")
        
                    sub = row.row(align=True)
                    sub.operator("object.vertex_group_select", text="Select")
                    sub.operator("object.vertex_group_deselect", text="Deselect")
                else:
                    row = box.row()
                    row.operator("fd_group.connect_group_meshes_to_hooks",text="Connect Hooks",icon=const.icon_hook).group_name = grp.name
            else:
                if obj.mode == 'EDIT':
                    row.operator("fd_object.toggle_edit_mode",text="Exit Edit Mode",icon=const.icon_editmode).object_name = obj.name
                else:
                    row.operator("fd_object.toggle_edit_mode",text="Enter Edit Mode",icon=const.icon_editmode).object_name = obj.name
                    
        if obj.type == 'EMPTY':
            box = layout.box()
            box.label("Empty Data",icon=const.icon_font_data)
            box.prop(obj,'empty_draw_type',text='Draw Type')
            box.prop(obj,'empty_draw_size')
            
        if obj.type == 'CURVE':
            box = layout.box()
            box.label("Curve Data",icon=const.icon_curve_data)
            curve = obj.data
            box.prop(curve,"dimensions")
            box.prop(curve,"use_cyclic_u")
            box.prop(curve,"bevel_object")
            box.prop(curve,"bevel_depth")
            box.prop(curve,"extrude")
        
        if obj.type == 'FONT':
            text = obj.data
            box = layout.box()
            row = box.row()
            row.prop(obj.mv,"use_as_item_number")
            box = layout.box()
            row = box.row()
            row.label("Font Data:")
            if obj.mode == 'OBJECT':
                row.operator("fd_object.toggle_edit_mode",text="Edit Text",icon=const.icon_edit_text).object_name = obj.name
            else:
                row.operator("fd_object.toggle_edit_mode",text="Exit Edit Mode",icon=const.icon_edit_text).object_name = obj.name
            row = box.row()
            row.template_ID(text, "font", open="font.open", unlink="font.unlink")
            row = box.row()
            row.label("Text Size:")
            row.prop(text,"size",text="")
            row = box.row()
            row.prop(text,"align")
            
            box = layout.box()
            row = box.row()
            row.label("3D Font:")
            row = box.row()
            row.prop(text,"extrude")
            row = box.row()
            row.prop(text,"bevel_depth")
            
        if obj.type == 'LAMP':
            lamp = obj.data
            clamp = lamp.cycles
            cscene = bpy.context.scene.cycles  
                      
            row = box.row()
            row.label("Lamp: "+obj.name,icon='OUTLINER_OB_LAMP')      
            
            row = box.row()
            row.label(text="Lamp Type:")  
            row = box.row()
            row.prop(lamp, "type", expand=True)
    
            split = box.split()
            col = split.column(align=True)
    
            if lamp.type in {'POINT', 'SUN', 'SPOT'}:
                col.prop(lamp, "shadow_soft_size", text="Size")
            elif lamp.type == 'AREA':
                col.prop(lamp, "shape", text="")
                sub = col.column(align=True)
    
                if lamp.shape == 'SQUARE':
                    sub.prop(lamp, "size")
                elif lamp.shape == 'RECTANGLE':
                    sub.prop(lamp, "size", text="Size X")
                    sub.prop(lamp, "size_y", text="Size Y")
    
            if cscene.progressive == 'BRANCHED_PATH':
                col.prop(clamp, "samples")
    
            col = split.column()
            col.prop(clamp, "cast_shadow")
    
            box.prop(clamp, "use_multiple_importance_sampling")
    
            if lamp.type == 'HEMI':
                box.label(text="Not supported, interpreted as sun lamp")   
                   
        if obj.type == 'CAMERA':
            cam = obj.data
            ccam = cam.cycles
            row = box.row()
            row.label("",icon='SCENE')
            row.prop(cam,"name",text="")
            row = box.row()
            row.operator("view3d.viewnumpad", text="View Through Active Camera",icon='RESTRICT_VIEW_OFF').type = 'CAMERA'
            
            box.label("Transform:")   
            
            box1 = box.box()
            row = box1.row()
            split = box1.split()
            col = split.column()
            row = col.row(align=True)            
            row.prop(obj,"location",index=0,text="Location X")
            row.prop(obj,"lock_location",index=0,text="")
            row = col.row(align=True)
            row.prop(obj,"location",index=1,text="Location Y")
            row.prop(obj,"lock_location",index=1,text="")
            row = col.row(align=True)
            row.prop(obj,"location",index=2,text="Location Z")
            row.prop(obj,"lock_location",index=2,text="")
            
            col = split.column()
            row = col.row(align=True)
            row.prop(obj,"rotation_euler",index=0,text="Rotation X")
            row.prop(obj,"lock_rotation",index=0,text="")
            row = col.row(align=True)
            row.prop(obj,"rotation_euler",index=1,text="Rotation Y")
            row.prop(obj,"lock_rotation",index=1,text="")
            row = col.row(align=True)
            row.prop(obj,"rotation_euler",index=2,text="Rotation Z")
            row.prop(obj,"lock_rotation",index=2,text="")
            
            box.label("Camera Options:")
            
            box2 = box.box()
            row = box2.row()
            split = row.split()
            col = split.column()
            col.prop(bpy.context.space_data,"lock_camera",text="Lock Camera to View")
            col.prop(bpy.context.scene.cycles,"film_transparent",text="Transparent Film")       
            col = row.column()
            col.prop(cam, "clip_start", text="Clipping Start")
            col.prop(cam, "clip_end", text="Clipping End")            
            row = box2.row()
            row.menu("CAMERA_MT_presets", text=bpy.types.CAMERA_MT_presets.bl_label)         
            row.prop_menu_enum(cam, "show_guide")          
            row = box2.row(align=True)
            if cam.lens_unit == 'MILLIMETERS':
                row.prop(cam, "lens")
            elif cam.lens_unit == 'FOV':
                row.prop(cam, "angle")
            row.prop(cam, "lens_unit", text="")

            box.label(text="Depth of Field:")
            
            box3 = box.box()
            row = box3.row()
            row.label("Focus:")
            row = box3.row(align=True)
            row.prop(cam, "dof_object", text="")
            col = row.column()
            sub = col.row()
            sub.active = cam.dof_object is None
            sub.prop(cam, "dof_distance", text="Distance")

    def draw_object_drivers(self,layout,name):
        obj = bpy.data.objects[name]
        if obj:
            if not obj.animation_data:
                layout.label("There are no drivers assigned to the object",icon='ERROR')
            else:
                if len(obj.animation_data.drivers) == 0:
                    layout.label("There are no drivers assigned to the object",icon='ERROR')
                for DR in obj.animation_data.drivers:
                    box = layout.box()
                    row = box.row()
                    DriverName = DR.data_path
                    if DriverName == "location" or DriverName == "rotation_euler" or DriverName == "dimensions":
                        if DR.array_index == 0:
                            DriverName = DriverName + " X"
                        if DR.array_index == 1:
                            DriverName = DriverName + " Y"
                        if DR.array_index == 2:
                            DriverName = DriverName + " Z"                     
                    value = eval('bpy.data.objects["' + obj.name + '"].' + DR.data_path)
                    if isinstance(value,type(obj.location)):
                        value = value[DR.array_index]
                        
                    row.label(DriverName + " = " + str(value),icon='AUTO')
                    props = row.operator("fd_driver.add_variable_to_object",text="",icon='ZOOMIN')
                    props.object_name = obj.name
                    props.data_path = DR.data_path
                    props.array_index = DR.array_index
                    fd_utils.draw_driver_expression(box,DR)
                    fd_utils.draw_driver_variables(box,DR,obj.name)

    def assign_material_to_object(self,name,Material,index_list=None):
        if Material:
            if name in bpy.data.objects:
                obj = bpy.data.objects[name]
                if len(obj.material_slots) == 0:
                    bpy.ops.fd_material.add_material_slot(object_name=obj.name)
                for index, slot in enumerate(obj.material_slots):
                    if index_list:
                        if index in index_list:
                            slot.material = Material
                            obj.mv.material_slot_col[index].library_name = Material.mv.library_name
                            obj.mv.material_slot_col[index].category_name = Material.mv.category_name
                            obj.mv.material_slot_col[index].item_name = Material.name
                    else:
                        slot.material = Material
                        obj.mv.material_slot_col[index].library_name = Material.mv.library_name
                        obj.mv.material_slot_col[index].category_name = Material.mv.category_name
                        obj.mv.material_slot_col[index].item_name = Material.name
                        
    def assign_materials_from_pointers(self,name):
        dm = bpy.context.scene.mv.dm
        obj = bpy.data.objects[name]
        if len(obj.mv.material_slot_col) < len(obj.material_slots):
            obj.mv.sync_material_slots(obj.name)
            
        for index, mat_slot in enumerate(obj.material_slots):
            mv_slot = obj.mv.material_slot_col[index]
            mv_slot.pointer_name = mv_slot.pointer_name # FORCE POINTER REFRESH
            mat = dm.retrieve_material_for_mat_slot(mv_slot.pointer_name,
                                                    mv_slot.library_name,
                                                    mv_slot.category_name,
                                                    mv_slot.item_name)
            if mat:
                mat_slot.material = mat

    def sync_material_slots(self,name):
        obj = bpy.data.objects[name]
        for slot in obj.mv.material_slot_col:
            obj.mv.material_slot_col.remove(0)
        
        for index, mat_slot in enumerate(obj.material_slots):
            slot = obj.mv.material_slot_col.add()
            slot.index = index
            
bpy.utils.register_class(fd_object)

class fd_object_col(PropertyGroup):
    col_mesh = CollectionProperty(name="Collection Mesh",type=fd_object)
    index_mesh = IntProperty(name="Index Mesh",min=-1)
    counter_mesh = IntProperty(name="Current Mesh Counter",default = 1)
    
    col_empty = CollectionProperty(name="Collection Empty",type=fd_object)
    index_empty = IntProperty(name="Index Empty",min=-1)
    counter_empty = IntProperty(name="Current Empty Counter",default = 1)
    
    col_curve = CollectionProperty(name="Collection Curve",type=fd_object)
    index_curve = IntProperty(name="Index Curve",min=-1)
    counter_curve = IntProperty(name="Current Curve Counter",default = 1)
    
    col_font = CollectionProperty(name="Collection Font",type=fd_object)
    index_font = IntProperty(name="Index Font",min=-1)
    counter_font = IntProperty(name="Current Font Counter",default = 1)

    col_group = CollectionProperty(name="Collection Group",type=fd_object)
    index_group = IntProperty(name="Index Group",min=-1)
    counter_group = IntProperty(name="Current Group Counter",default = 1)

    def ReloadCollections(self, obj_bp, grp):
        self.clear_collections()
        for obj in obj_bp.children:
            if obj.mv.Type == 'MESHPRODUCT' or obj.mv.Type == 'MESHINSERT' or obj.mv.Type == 'MESHPART':
                self.AddMesh(obj, grp)
            if obj.mv.Type == 'EMPTYPRODUCT' or obj.mv.Type == 'EMPTYINSERT' or obj.mv.Type == 'EMPTYPART':
                self.AddEmpty(obj, grp)
            if obj.mv.Type == 'TEXTPRODUCT' or obj.mv.Type == 'TEXTINSERT' or obj.mv.Type == 'TEXTPART':
                self.AddText(obj, grp)
            if obj.mv.Type == 'CURVEPRODUCT' or obj.mv.Type == 'CURVEINSERT' or obj.mv.Type == 'CURVEPART':
                self.AddCurve(obj, grp)

    def clear_collections(self):
        self.counter_mesh = 1
        self.counter_empty = 1
        self.counter_curve = 1
        self.counter_font = 1
        self.counter_group = 1
        for part in self.col_mesh:
           self.col_mesh.remove(0)
        for empty in self.col_empty:
           self.col_empty.remove(0)
        for curve in self.col_curve:
           self.col_curve.remove(0)
        for text in self.col_font:
           self.col_font.remove(0)
        for group in self.col_group:
           self.col_group.remove(0)
            
    def draw_mesh_collection(self,layout,grp):
        layout.operator("fd_group.add_mesh_to_group",text="Add Mesh",icon='ZOOMIN').group_name = grp.name
        layout.template_list("FD_UL_objects", " ", self, "col_mesh", self, "index_mesh", rows=3)

    def draw_active_mesh_properties(self,layout):
        if len(self.col_mesh) > 0:
            obj = bpy.data.objects[self.col_mesh[self.index_mesh].name]
            obj.mv.draw_properties(layout)

    def draw_text_collection(self,layout,grp):
        layout.operator("fluidgroup.add_text_to_group",text="Add Text",icon='ZOOMIN').GroupName = grp.name
        layout.template_list("MV_UL_text", " ", self, "COL_Text", self, "TextIndex", rows=3)
        if len(self.COL_Text) > 0:
            Text = bpy.data.objects[self.COL_Text[self.TextIndex].name]
            Text.mv.DrawProperties(Text.name,layout)
    
    def draw_curve_collection(self,layout,grp):
        layout.operator("fluidgroup.add_curve_to_group",text="Add Curve",icon='ZOOMIN').GroupName = grp.name
        layout.template_list("MV_UL_partmeshes", " ", self, "COL_Curve", self, "CurveIndex", rows=3)
        if len(self.COL_Mesh) > 0:
            Mesh = bpy.data.objects[self.COL_Mesh[self.MeshIndex].name]
            Mesh.mv.DrawProperties(Mesh.name,layout)
    
    def draw_empty_collection(self,layout,grp):
        layout.operator("fluidgroup.add_empty_to_group",text="Add Empty",icon='ZOOMIN').GroupName = grp.name
        layout.template_list("MV_UL_empties", " ", self, "COL_Empty", self, "EmptyIndex", rows=3)
        if len(self.COL_Empty) > 0:
            Empty = bpy.data.objects[self.COL_Empty[self.EmptyIndex].name]
            Empty.mv.DrawProperties(Empty.name,layout)
            
bpy.utils.register_class(fd_object_col)

class fd_group(PropertyGroup):
    Type = EnumProperty(name="Type",items=enums.enum_group_types,description="Select the Group Type.",default='NONE')
    type = EnumProperty(name="Type",items=enums.enum_group_types,description="Select the Group Type.",default='NONE')
    category_type = EnumProperty(name="Category Type",items=enums.enum_product_category_types,description="Select the Group Type.",default='NONE')
    
    tabs = EnumProperty(name="tabs",items=enums.enum_group_tabs,description="Group Tabs",default='INFO')
    
    #This is the human readable name for the group
    name_group = StringProperty(name="Product Name")#TODO: make sure the bpy.data.group gets renames too
    
    #LinkID's to Main group objects Used for Products, Inserts, and Parts
    bp_id = StringProperty(name="BP LinkID")
    x_id = StringProperty(name="X Obj LinkID")
    y_id = StringProperty(name="Y Obj LinkID")
    z_id = StringProperty(name="Z Obj LinkID")
    cage_id = StringProperty(name="Cage LinkID")
    
    #These are the group id names of the self and parent groups
    id_wall = StringProperty(name="Wall LinkID")
    id_product = StringProperty(name="Product LinkID")
    id_insert = StringProperty(name="Insert LinkID")
    id_part = StringProperty(name="Part LinkID")
    
    #Index System that contributes to the group id to correctly index the group
    room_index = IntProperty(name="Room Index")
    wall_index = IntProperty(name="Wall Index")
    product_index = IntProperty(name="Product Index")
    insert_index = IntProperty(name="Insert Index")
    part_index = IntProperty(name="Part Index")
    
    #Collection that holds all group objects
    Objects = bpy.props.PointerProperty(name="Objects",type=fd_object_col)

    current_mesh_count = IntProperty(name="Current Mesh Count",default = 1)
    current_empty_count = IntProperty(name="Current Empty Count",default = 1)
    current_curve_count = IntProperty(name="Current Curve Count",default = 1)
    current_text_count = IntProperty(name="Current Text Count",default = 1)
    current_group_count = IntProperty(name="Current Text Count",default = 1)

    def add_object_to_group_collection(self,obj):
        """ NOTE: Every Object that is a direct child of the
                  groups base point will be passed through this function
                  this is needed to build the UI lists for objects
        """
        dm = bpy.context.scene.mv.dm
        obj_bp = self.get_bp()
        if obj.mv.type == 'NONE' and obj.type == 'MESH':
            obj.parent = obj_bp
            self.index_object(obj)
            dm.set_object_name(obj)
            item = self.Objects.col_mesh.add()
            item.name = obj.name
        if obj.mv.type == 'NONE' and obj.type == 'EMPTY':
            obj_bp.parent = obj
            self.index_object(obj)
            dm.set_object_name(obj)
            item = self.Objects.col_empty.add()
            item.name = obj.name
        if obj.mv.type == 'NONE' and obj.type == 'CURVE':
            obj_bp.parent = obj
            self.index_object(obj)
            dm.set_object_name(obj)
            item = self.Objects.col_curve.add()
            item.name = obj.name
        if obj.mv.type == 'NONE' and obj.type == 'FONT':
            obj_bp.parent = obj
            self.index_object(obj)
            dm.set_object_name(obj)
            item = self.Objects.col_font.add()
            item.name = obj.name
        if obj.mv.type in {'BPRODUCT','BPINSERT','BPPART'}:
            self.index_object(obj)
            dm.set_object_name(obj)
            item = self.Objects.col_group.add()
            item.name = obj.name
            if self.type == 'PRODUCT' and obj.mv.type == 'BPPRODUCT':
                self.bp_id = obj.name
            if self.type == 'INSERT' and obj.mv.type == 'BPINSERT':
                self.bp_id = obj.name
            if self.type == 'PART' and obj.mv.type == 'BPPART':
                self.bp_id = obj.name
        
    def index_object(self,obj):
        if obj.mv.type == 'NONE' and obj.type == 'MESH':
            obj.mv.index = self.current_mesh_count
            self.current_mesh_count += 1
        if obj.mv.type == 'NONE' and obj.type == 'EMPTY':
            obj.mv.index = self.current_empty_count
            self.current_empty_count += 1
        if obj.mv.type == 'NONE' and obj.type == 'CURVE':
            obj.mv.index = self.current_curve_count
            self.current_curve_count += 1
        if obj.mv.type == 'NONE' and obj.type == 'FONT':
            obj.mv.index = self.current_text_count
            self.current_text_count += 1
        if obj.mv.type in {'BPPRODUCT','BPINSERT','BPPART'}:
            obj.mv.index = self.current_group_count
            self.current_group_count += 1
            
    def delete_object_from_group(self,obj):
        pass
    
    def get_bp(self):
        if self.bp_id in bpy.data.objects:
            return bpy.data.objects[self.bp_id]
    
    def get_x(self):
        if self.x_id in bpy.data.objects:
            return bpy.data.objects[self.x_id]

    def get_y(self):
        if self.y_id in bpy.data.objects:
            return bpy.data.objects[self.y_id]
    
    def get_z(self):
        if self.z_id in bpy.data.objects:
            return bpy.data.objects[self.z_id]
    
    def get_wall_bool(self):
        for obj in self.Objects.col_mesh:
            obj1 = bpy.data.objects[obj.name]
            if obj1.mv.use_as_wall_subtraction:
                return obj1
    
    def get_cage(self):
        if self.cage_id in bpy.data.objects:
            return bpy.data.objects[self.cage_id]

    def add_bool(self,obj):
        obj_bp = self.get_bp()
        for child in obj_bp.children:
            if child.type == 'MESH' and child.mv.type != 'BPPRODUCT':
                bpy.context.scene.objects.active = child
                bpy.ops.object.modifier_add(type='BOOLEAN')
                modname = 'BOOL ' + obj.name
                child.modifiers["Boolean"].name = modname
                child.modifiers[modname].operation = 'UNION'
                child.modifiers[modname].object = obj
                obj.hide = True

    def get_active_object(self):
        """ NOTE: This is uesd to get the object
                  that is selected in the UILists.
        """
        ui = bpy.context.scene.mv.ui
        if ui.interface_group_object_tabs == 'MESH':
            if len(self.Objects.col_mesh) > 0:
                objname = self.Objects.col_mesh[self.Objects.index_mesh].name
                if objname in bpy.data.objects:
                    return bpy.data.objects[objname]
                
        if ui.interface_group_object_tabs == 'TEXT':
            if len(self.Objects.col_font) > 0:
                objname = self.Objects.col_font[self.Objects.index_font].name
                if objname in bpy.data.objects:
                    return bpy.data.objects[objname]
                
        if ui.interface_group_object_tabs == 'CURVE':
            if len(self.Objects.col_curve) > 0:
                objname = self.Objects.col_curve[self.Objects.index_curve].name
                if objname in bpy.data.objects:
                    return bpy.data.objects[objname]
                
        if ui.interface_group_object_tabs == 'EMPTY':
            if len(self.Objects.col_empty) > 0:
                objname = self.Objects.col_empty[self.Objects.index_empty].name
                if objname in bpy.data.objects:
                    return bpy.data.objects[objname]

        if ui.interface_group_object_tabs == 'GROUP':
            if len(self.Objects.col_group) > 0:
                objname = self.Objects.col_group[self.Objects.index_group].name
                if objname in bpy.data.objects:
                    return bpy.data.objects[objname]
                
    def get_connected_wall(self,direction):#TODO: FINISH THIS FUNCTION
        dm = bpy.context.scene.mv.dm
        grp = bpy.data.groups[self.name]
        grp_wall = dm.get_wall_group(grp)
        
        if direction == 'LEFT':
            obj_wall_bp = grp_wall.mv.get_bp()
            for con in obj_wall_bp.constraints:
                if con.type == 'COPY_LOCATION':
                    if con.target:
                        return dm.get_wall_group(con.target)
                    
        if direction == 'RIGHT':
            obj_wall_x = grp_wall.mv.get_x()
            for group in bpy.data.groups:
                if group.mv.type == 'WALL':
                    obj_nextwall_bp = group.mv.get_bp()
                    for con in obj_nextwall_bp.constraints:
                        if con.type == 'COPY_LOCATION':
                            if con.target == obj_wall_x:
                                return group

    def draw_properties(self,layout,advanced=False):
        if advanced:
            col = layout.column(align=True)
            box = col.box()
            self.draw_group_header(box)
            if self.tabs == 'INFO':
                box = col.box()
                self.draw_group_transform(box)
            if self.tabs == 'SETTINGS':
                box = col.box()
                self.draw_options_page(box)
            if self.tabs == 'PROMPTS':
                box = col.box()
                self.draw_prompts_page(box)
            if self.tabs == 'OBJECTS':
                box = col.box()
                self.draw_objects(box)
            if self.tabs == 'DRIVERS':
                box = col.box()
                self.draw_group_drivers(box)
        else:
            col = layout.column(align=True)
            box = col.box()
            self.draw_group_transform(box)
            obj_bp = self.get_bp()
            for index, tab in enumerate(obj_bp.mv.PromptPage.COL_MainTab):
                props = layout.operator("fd_general.show_object_prompts",text="Show " + tab.name)
                props.group_name = self.name
                props.index = index
 
    def draw_group_name(self,layout):
        grp = bpy.data.groups[self.name]
        
        if grp.mv.type == 'WALL':
            layout.label(grp.mv.name_group,icon=const.icon_wall)

        elif grp.mv.type == 'PRODUCT':
            props = layout.operator("fd_group.rename_group",text=grp.mv.name_group,icon=const.icon_product)
            props.group_name = grp.name

        elif grp.mv.type == 'INSERT':
            props = layout.operator("fd_group.rename_group",text=grp.mv.name_group,icon=const.icon_insert)
            props.group_name = grp.name

        elif grp.mv.type == 'PART':
            props = layout.operator("fd_group.rename_group",text=grp.mv.name_group,icon=const.icon_part)
            props.group_name = grp.name


    def draw_group_header(self,layout):
        row = layout.row(align=True)
#         self.draw_group_name(row)
#         row.separator()
        row.prop_enum(self, "tabs", enums.enum_group_tabs[0][0], icon='INFO', text="") 
        row.prop_enum(self, "tabs", enums.enum_group_tabs[2][0], icon='SETTINGS', text="")    
        row.prop_enum(self, "tabs", enums.enum_group_tabs[3][0], icon='GROUP', text="")
        row.prop_enum(self, "tabs", enums.enum_group_tabs[4][0], icon='AUTO', text="")

    def draw_group_transform(self,layout):
        obj_bp = self.get_bp()
        obj_x = self.get_x()
        obj_y = self.get_y()
        obj_z = self.get_z()
        
        row = layout.row(align=True)
        self.draw_group_name(row)
        row = layout.row(align=True)
        row.label('Dimension X:')
        row.prop(obj_x,"lock_location",index=0,text='')
        if obj_x.lock_location[0]:
            row.label(str(obj_x.location.x))
        else:
            row.prop(obj_x,"location",index=0,text="")
        
        row = layout.row(align=True)
        row.label('Dimension Y:')
        row.prop(obj_y,"lock_location",index=1,text='')
        if obj_y.lock_location[1]:
            row.label(str(obj_y.location.y))
        else:
            row.prop(obj_y,"location",index=1,text="")
        
        row = layout.row(align=True)
        row.label('Dimension Z:')
        row.prop(obj_z,"lock_location",index=2,text='')
        if obj_z.lock_location[2]:
            row.label(str(obj_z.location.z))
        else:
            row.prop(obj_z,"location",index=2,text="")
        
        col1 = layout.row()
        if obj_bp:
            col2 = col1.split()
            col = col2.column(align=True)
            col.label('Location:')
            
            if obj_bp.lock_location[0]:
                row = col.row(align=True)
                row.prop(obj_bp,"lock_location",index=0,text="")
                row.label(str(obj_bp.location.x))
            else:
                row = col.row(align=True)
                row.prop(obj_bp,"lock_location",index=0,text="")
                row.prop(obj_bp,"location",index=0,text="X")
                
            if obj_bp.lock_location[1]:
                row = col.row(align=True)
                row.prop(obj_bp,"lock_location",index=1,text="")
                row.label(str(obj_bp.location.y))
            else:
                row = col.row(align=True)
                row.prop(obj_bp,"lock_location",index=1,text="")
                row.prop(obj_bp,"location",index=1,text="Y")
                
            if obj_bp.lock_location[2]:
                row = col.row(align=True)
                row.prop(obj_bp,"lock_location",index=2,text="")
                row.label(str(obj_bp.location.z))
            else:
                row = col.row(align=True)
                row.prop(obj_bp,"lock_location",index=2,text="")
                row.prop(obj_bp,"location",index=2,text="Z")
                
            col2 = col1.split()
            col = col2.column(align=True)
            col.label('Rotation:')
            
            if obj_bp.lock_rotation[0]:
                row = col.row(align=True)
                row.prop(obj_bp,"lock_rotation",index=0,text="")
                row.label(str(obj_bp.rotation_euler.x))
            else:
                row = col.row(align=True)
                row.prop(obj_bp,"lock_rotation",index=0,text="")
                row.prop(obj_bp,"rotation_euler",index=0,text="X")
                
            if obj_bp.lock_rotation[1]:
                row = col.row(align=True)
                row.prop(obj_bp,"lock_rotation",index=1,text="")
                row.label(str(obj_bp.rotation_euler.y))
            else:
                row = col.row(align=True)
                row.prop(obj_bp,"lock_rotation",index=1,text="")
                row.prop(obj_bp,"rotation_euler",index=1,text="Y")
                
            if obj_bp.lock_rotation[2]:
                row = col.row(align=True)
                row.prop(obj_bp,"lock_rotation",index=2,text="")
                row.label(str(obj_bp.rotation_euler.z))
            else:
                row = col.row(align=True)
                row.prop(obj_bp,"lock_rotation",index=2,text="")
                row.prop(obj_bp,"rotation_euler",index=2,text="Z")

    def draw_options_page(self, layout):
        obj_bp = bpy.data.objects[self.bp_id]
        layout.label('TODO: Toggle Cage')
        layout.label('TODO: Show Visible Prompts')

    def draw_objects(self,layout):
        grp = bpy.data.groups[self.name]
        ui = bpy.context.scene.mv.ui
        row = layout.row(align=True)
        row.prop_enum(ui, "interface_group_object_tabs", enums.enum_group_object_tabs[0][0], icon=const.icon_mesh, text="") 
        row.prop_enum(ui, "interface_group_object_tabs", enums.enum_group_object_tabs[1][0], icon=const.icon_font, text="") 
        row.prop_enum(ui, "interface_group_object_tabs", enums.enum_group_object_tabs[2][0], icon=const.icon_curve, text="")    
        row.prop_enum(ui, "interface_group_object_tabs", enums.enum_group_object_tabs[3][0], icon=const.icon_empty, text="")
        if grp.mv.type != 'PART':
            row.prop_enum(ui, "interface_group_object_tabs", enums.enum_group_object_tabs[4][0], icon=const.icon_group, text="")
            
        col = layout.column(align=True)
        if ui.interface_group_object_tabs == 'MESH':
            col.operator("fd_group.add_mesh_to_group",text="Add Mesh",icon='ZOOMIN').group_name = grp.name
            col.template_list("FD_UL_objects", " ", self.Objects, "col_mesh", self.Objects, "index_mesh", rows=3)
        if ui.interface_group_object_tabs == 'TEXT':
            col.operator("fd_group.add_text_to_group",text="Add Font",icon='ZOOMIN').group_name = grp.name
            col.template_list("FD_UL_objects", " ", self.Objects, "col_font", self.Objects, "index_font", rows=3)
        if ui.interface_group_object_tabs == 'CURVE':
            col.operator("fd_group.add_curve_to_group",text="Add Curve",icon='ZOOMIN').group_name = grp.name
            col.template_list("FD_UL_objects", " ", self.Objects, "col_curve", self.Objects, "index_curve", rows=3)
        if ui.interface_group_object_tabs == 'EMPTY':
            col.operator("fd_group.add_empty_to_group",text="Add Empty",icon='ZOOMIN').group_name = grp.name
            col.template_list("FD_UL_objects", " ", self.Objects, "col_empty", self.Objects, "index_empty", rows=3)
        if ui.interface_group_object_tabs == 'GROUP':
            col.template_list("FD_UL_objects", " ", self.Objects, "col_group", self.Objects, "index_group", rows=3)
            
        obj = self.get_active_object()
        
        if obj:
            
            if obj.mv.type == 'BPPART':
                grp_part = bpy.context.scene.mv.dm.get_part_group(obj)
                if grp_part:
                    grp_part.mv.draw_properties(col,False)
                else:
                    prop = col.operator("fd_group.create_group",text='Create Group',icon=const.icon_group)
                    prop.object_name = obj.name
                    prop.parent_group = grp.name

            elif obj.mv.type == 'BPINSERT':
                grp_insert = bpy.context.scene.mv.dm.get_insert_group(obj)
                if grp_insert:
                    grp_insert.mv.draw_properties(col,False)
                else:
                    prop = col.operator("fd_group.create_group",text='Create Group',icon=const.icon_group)
                    prop.object_name = obj.name
                    prop.parent_group = grp.name
                    
            else:
                obj.mv.draw_properties(col,obj.name)

    def draw_prompts_page(self, layout):
        obj_bp = bpy.data.objects[self.bp_id]
        obj_bp.mv.PromptPage.draw_prompt_page(layout,obj_bp,allow_edit=True)
    
    def draw_add_variable_operators(self,layout,object_name,data_path,array_index):
        #GLOBAL PROMPT
        box = layout.box()
        box.label("Quick Variables")
        row = box.row()
        row.label('Scene',icon=const.icon_scene)
        props = row.operator("fd_driver.add_variable_from_scene_prompt_to_object",text="Prompt")
        props.object_name = object_name
        props.data_path = data_path
        props.array_index = array_index
        #SELF PROMPT
        row = box.row()
        row.label('Self',icon=const.icon_group)
        props = row.operator("fd_driver.add_variable_from_group_property_to_object",text="Property")
        props.group_name = self.name
        props.object_name = object_name
        props.data_path = data_path
        props.array_index = array_index
        props = row.operator("fd_driver.add_variable_from_group_prompt_to_object",text="Prompt")
        props.group_name = self.name
        props.object_name = object_name
        props.data_path = data_path
        props.array_index = array_index
        #PARENT PROMPT
        obj_bp = self.get_bp()
        if obj_bp.parent:
            dm = bpy.context.scene.mv.dm
            grp_parent = None
            if obj_bp.parent.mv.type == 'BPWALL':
                grp_parent = dm.get_wall_group(obj_bp.parent)
            if obj_bp.parent.mv.type == 'BPPRODUCT':
                grp_parent = dm.get_product_group(obj_bp.parent)
            if obj_bp.parent.mv.type == 'BPINSERT':
                grp_parent = dm.get_insert_group(obj_bp.parent)

            if grp_parent:
                row = box.row()
                row.label('Parent',icon=const.icon_group)
                props = row.operator("fd_driver.add_variable_from_group_property_to_object",text="Property")
                props.group_name = grp_parent.name
                props.object_name = object_name
                props.data_path = data_path
                props.array_index = array_index
                props = row.operator("fd_driver.add_variable_from_parent_group_prompt_to_object",text="Prompt")
                props.group_name = self.name
                props.object_name = object_name
                props.data_path = data_path
                props.array_index = array_index
                
            if obj_bp.parent.parent:
                grp_grandparent = None
                if obj_bp.parent.parent.mv.type == 'BPPRODUCT':
                    grp_grandparent = dm.get_product_group(obj_bp.parent.parent)
                if grp_grandparent:
                    row = box.row()
                    row.label('Product',icon=const.icon_group)
                    props = row.operator("fd_driver.add_variable_from_group_property_to_object",text="Property")
                    props.group_name = grp_grandparent.name
                    props.object_name = object_name
                    props.data_path = data_path
                    props.array_index = array_index
                    props = row.operator("fd_driver.add_variable_from_product_group_prompt_to_object",text="Prompt")
                    props.group_name = self.name
                    props.object_name = object_name
                    props.data_path = data_path
                    props.array_index = array_index
            
    def draw_group_drivers(self,layout):
        ui = bpy.context.scene.mv.ui
        obj_bp = self.get_bp()
        obj_x = self.get_x()
        obj_y = self.get_y()
        obj_z = self.get_z()
        row = layout.row(align=True)
        row.operator("fd_driver.turn_on_driver",text="",icon='QUIT').group_name = self.name
        row.prop(ui,'group_driver_tabs',text='')
        box = layout.box()
        
        if ui.group_driver_tabs == 'LOC_X':
            box.prop(obj_bp,'location',index=0,text="Location X")
            driver = fd_utils.get_driver(obj_bp,'location',0)
            if driver:
                fd_utils.draw_driver_expression(box,driver)
                self.draw_add_variable_operators(layout,obj_bp.name,'location',0)
                fd_utils.draw_driver_variables(layout,driver,obj_bp.name)

        if ui.group_driver_tabs == 'LOC_Y':
            box.prop(obj_bp,'location',index=1,text="Location Y")
            driver = fd_utils.get_driver(obj_bp,'location',1)
            if driver:
                fd_utils.draw_driver_expression(box,driver)
                self.draw_add_variable_operators(layout,obj_bp.name,'location',1)
                fd_utils.draw_driver_variables(layout,driver,obj_bp.name)
                
        if ui.group_driver_tabs == 'LOC_Z':
            box.prop(obj_bp,'location',index=2,text="Location Z")
            driver = fd_utils.get_driver(obj_bp,'location',2)
            if driver:
                fd_utils.draw_driver_expression(box,driver)
                self.draw_add_variable_operators(layout,obj_bp.name,'location',2)
                fd_utils.draw_driver_variables(layout,driver,obj_bp.name)
                
        if ui.group_driver_tabs == 'ROT_X':
            box.prop(obj_bp,'rotation_euler',index=0,text="Rotation X")
            driver = fd_utils.get_driver(obj_bp,'rotation_euler',0)
            if driver:
                fd_utils.draw_driver_expression(box,driver)
                self.draw_add_variable_operators(layout,obj_bp.name,'rotation_euler',0)
                fd_utils.draw_driver_variables(layout,driver,obj_bp.name)
                
        if ui.group_driver_tabs == 'ROT_Y':
            box.prop(obj_bp,'rotation_euler',index=1,text="Rotation Y")
            driver = fd_utils.get_driver(obj_bp,'rotation_euler',1)
            if driver:
                fd_utils.draw_driver_expression(box,driver)
                self.draw_add_variable_operators(layout,obj_bp.name,'rotation_euler',1)
                fd_utils.draw_driver_variables(layout,driver,obj_bp.name)

        if ui.group_driver_tabs == 'ROT_Z':
            box.prop(obj_bp,'rotation_euler',index=2,text="Rotation Z")
            driver = fd_utils.get_driver(obj_bp,'rotation_euler',2)
            if driver:
                fd_utils.draw_driver_expression(box,driver)
                self.draw_add_variable_operators(layout,obj_bp.name,'rotation_euler',2)
                fd_utils.draw_driver_variables(layout,driver,obj_bp.name)

        if ui.group_driver_tabs == 'DIM_X':
            box.prop(obj_x,'location',index=0,text="Dimension X")
            driver = fd_utils.get_driver(obj_x,'location',0)
            if driver:
                fd_utils.draw_driver_expression(box,driver)
                self.draw_add_variable_operators(layout,obj_x.name,'location',0)
                fd_utils.draw_driver_variables(layout,driver,obj_x.name)

        if ui.group_driver_tabs == 'DIM_Y':
            box.prop(obj_y,'location',index=1,text="Dimension Y")
            driver = fd_utils.get_driver(obj_y,'location',1)
            if driver:
                fd_utils.draw_driver_expression(box,driver)
                self.draw_add_variable_operators(layout,obj_y.name,'location',1)
                fd_utils.draw_driver_variables(layout,driver,obj_y.name)
                        
        if ui.group_driver_tabs == 'DIM_Z':
            box.prop(obj_z,'location',index=2,text="Dimension Z")
            driver = fd_utils.get_driver(obj_z,'location',2)
            if driver:
                fd_utils.draw_driver_expression(box,driver)
                self.draw_add_variable_operators(layout,obj_z.name,'location',2)
                fd_utils.draw_driver_variables(layout,driver,obj_z.name)
                
        if ui.group_driver_tabs == 'PROMPTS':
            box.template_list("FD_UL_promptitems"," ", obj_bp.mv.PromptPage, "COL_Prompt", obj_bp.mv.PromptPage, "PromptIndex",rows=len(obj_bp.mv.PromptPage.COL_Prompt),type='DEFAULT')
            prompt = obj_bp.mv.PromptPage.COL_Prompt[obj_bp.mv.PromptPage.PromptIndex]
            
            if prompt.Type == 'NUMBER':
                driver = fd_utils.get_driver(obj_bp,'mv.PromptPage.COL_Prompt["' + prompt.name + '"].NumberValue',0)
                if driver:
                    fd_utils.draw_driver_expression(box,driver)
                    self.draw_add_variable_operators(layout,obj_bp.name,'mv.PromptPage.COL_Prompt["' + prompt.name + '"].NumberValue',0)
                    fd_utils.draw_driver_variables(layout,driver,obj_bp.name)
                    
            if prompt.Type == 'QUANTITY':
                driver = fd_utils.get_driver(obj_bp,'mv.PromptPage.COL_Prompt["' + prompt.name + '"].QuantityValue',0)
                if driver:
                    fd_utils.draw_driver_expression(box,driver)
                    self.draw_add_variable_operators(layout,obj_bp.name,'mv.PromptPage.COL_Prompt["' + prompt.name + '"].QuantityValue',0)
                    fd_utils.draw_driver_variables(layout,driver,obj_bp.name)

            if prompt.Type == 'COMBOBOX':
                driver = fd_utils.get_driver(obj_bp,'mv.PromptPage.COL_Prompt["' + prompt.name + '"].EnumIndex',0)
                if driver:
                    fd_utils.draw_driver_expression(box,driver)
                    self.draw_add_variable_operators(layout,obj_bp.name,'mv.PromptPage.COL_Prompt["' + prompt.name + '"].EnumIndex',0)
                    fd_utils.draw_driver_variables(layout,driver,obj_bp.name)

            if prompt.Type == 'CHECKBOX':
                driver = fd_utils.get_driver(obj_bp,'mv.PromptPage.COL_Prompt["' + prompt.name + '"].CheckBoxValue',0)
                if driver:
                    fd_utils.draw_driver_expression(box,driver)
                    self.draw_add_variable_operators(layout,obj_bp.name,'mv.PromptPage.COL_Prompt["' + prompt.name + '"].CheckBoxValue',0)
                    fd_utils.draw_driver_variables(layout,driver,obj_bp.name)

    def build_cage(self):
        obj_bp = self.get_bp()
        obj_x = self.get_x()
        obj_y = self.get_y()
        obj_z = self.get_z()
        
        if obj_bp and obj_x and obj_y and obj_z:
            size = (obj_x.location.x, obj_y.location.y, obj_z.location.z)
            obj_cage = fd_utils.create_cube_mesh(self.name_group,size)
            obj_cage.mv.name_object = self.name_group
            obj_cage.parent = obj_bp
            obj_cage.location = obj_bp.location
            obj_cage.mv.type = 'CAGE'
            
            bpy.context.scene.objects.active = obj_cage
            bpy.ops.object.group_link(group=self.name)
    
            fd_utils.create_vertex_group_for_hooks(obj_cage,[2,3,6,7],'X Dimension')
            fd_utils.create_vertex_group_for_hooks(obj_cage,[1,2,5,6],'Y Dimension')
            fd_utils.create_vertex_group_for_hooks(obj_cage,[4,5,6,7],'Z Dimension')
            fd_utils.hook_vertex_group_to_object(obj_cage,'X Dimension',obj_x)
            fd_utils.hook_vertex_group_to_object(obj_cage,'Y Dimension',obj_y)
            fd_utils.hook_vertex_group_to_object(obj_cage,'Z Dimension',obj_z)
            
            obj_cage.draw_type = 'WIRE'
            obj_cage.hide_select = True
            obj_cage.lock_location = (True,True,True)
            obj_cage.lock_rotation = (True,True,True)
            obj_cage.cycles_visibility.camera = False
            obj_cage.cycles_visibility.diffuse = False
            obj_cage.cycles_visibility.glossy = False
            obj_cage.cycles_visibility.transmission = False
            obj_cage.cycles_visibility.shadow = False
    
    def update_vector_groups(self):
        obj_bp = self.get_bp()
        vgroupslist = []
        vgroupslist.append('X Dimension') #THIS IS USED FOR ALL MESHES
        vgroupslist.append('Y Dimension') #THIS IS USED FOR ALL MESHES
        vgroupslist.append('Z Dimension') #THIS IS USED FOR ALL MESHES
        objlist = []
        
        for child in obj_bp.children:
            if child.type == 'EMPTY' and child.mv.use_as_mesh_hook:
                vgroupslist.append(child.mv.name_object)
            if child.type == 'MESH' and child.mv.type != 'BPPART' and child.mv.type != 'BPINSERT' and child.mv.type != 'BPPRODUCT' and child.mv.type != 'BPWALL':
                objlist.append(child)
        
        for obj in objlist:
            for vgroup in vgroupslist:
                if vgroup not in obj.vertex_groups:
                    obj.vertex_groups.new(name=vgroup)
    
    def connect_meshes_to_hooks(self):
        obj_bp = self.get_bp()
        obj_x = self.get_x()
        obj_y = self.get_y()
        obj_z = self.get_z()
        hooklist = []
        meshlist = []
        
        for child in obj_bp.children:
            if child.type == 'EMPTY'  and child.mv.use_as_mesh_hook:
                hooklist.append(child)
            if child.type == 'MESH' and child.mv.type != 'BPPART' and child.mv.type != 'BPINSERT' and child.mv.type != 'BPPRODUCT' and child.mv.type != 'BPWALL' and child.mv.type != 'CAGE':
                meshlist.append(child)
                
        for mesh in meshlist:
            fd_utils.apply_hook_modifiers(mesh)
            for vgroup in mesh.vertex_groups:
                if vgroup.name == 'X Dimension':
                    fd_utils.hook_vertex_group_to_object(mesh,vgroup.name,obj_x)
                elif vgroup.name == 'Y Dimension':
                    fd_utils.hook_vertex_group_to_object(mesh,vgroup.name,obj_y)
                elif vgroup.name == 'Z Dimension':
                    fd_utils.hook_vertex_group_to_object(mesh,vgroup.name,obj_z)
                else:
                    for hook in hooklist:
                        if hook.mv.name_object == vgroup.name:
                            fd_utils.hook_vertex_group_to_object(mesh,vgroup.name,hook)
                
    def get_available_space(self,direction):
        dm = bpy.context.scene.mv.dm
        if self.type == 'PRODUCT':
            
            obj_self_bp = self.get_bp()
            grp_self = dm.get_product_group(obj_self_bp)
            grp_wall = dm.get_wall_group(obj_self_bp)
            if grp_wall:
                list_obj_bp = dm.get_product_list_from_wall_grp(grp_wall)
                wall_length = grp_wall.mv.get_x().location.x
                
                if len(list_obj_bp) > 0:
                    for index, obj_bp in enumerate(list_obj_bp):
                        if obj_bp.name == obj_self_bp.name:
                            if direction == 'LEFT':
                                if index > 0:
                                    
                                    obj_left_bp = list_obj_bp[index-1]
                                    grp_left_product = dm.get_product_group(obj_left_bp)
                                    
                                    if fd_utils.check_for_group_collision(grp_self,grp_left_product):
                                        left_product_width = grp_left_product.mv.get_x().location.x
                                        if obj_self_bp.rotation_euler.z < 0:
                                            return (obj_self_bp.location.x - math.fabs(grp_self.mv.get_y().location.y)) - (obj_left_bp.location.x + left_product_width)
                                        else:
                                            return obj_self_bp.location.x - (obj_left_bp.location.x + left_product_width)
                                        
                                else:
                                    
                                    return obj_self_bp.location.x

                            if direction == 'RIGHT':
                                if len(list_obj_bp) > index + 1:
                                    obj_right_bp = list_obj_bp[index+1]
                                    grp_right_product = dm.get_product_group(obj_right_bp)
                                    if fd_utils.check_for_group_collision(grp_self,grp_right_product):
                                        if obj_right_bp.rotation_euler.z < 0: #CORNER CABINET
                                            return (obj_right_bp.location.x - math.fabs(grp_right_product.mv.get_y().location.y)) - (obj_self_bp.location.x + self.get_x().location.x)
                                        else:
                                            return obj_right_bp.location.x - (obj_self_bp.location.x + self.get_x().location.x)
                                else:
                                    if obj_self_bp.rotation_euler.z < 0:
                                        return wall_length - obj_self_bp.location.x
                                    else:
                                        return grp_wall.mv.get_x().location.x - (obj_self_bp.location.x +self.get_x().location.x)

bpy.utils.register_class(fd_group)

class fd_group_col(PropertyGroup):
    col_part = CollectionProperty(name="Collection Part",type=fd_group)
    index_part = IntProperty(name="Index Part",min=-1)
    col_insert = CollectionProperty(name="Collection Insert",type=fd_group)
    index_insert = IntProperty(name="Index Insert",min=-1)
    col_product = CollectionProperty(name="Collection Product",type=fd_group)
    index_product = IntProperty(name="Index Product",min=-1)
    col_wall = CollectionProperty(name="Collection Wall",type=fd_group)
    index_wall = IntProperty(name="Index Wall",min=-1)
    
    def add_part(self, grp):
        part = self.col_part.add()
        part.name = grp.name
        return part
 
    def delete_part(self, grp):
        for index, part in enumerate(self.col_part):
            if part.name == grp.name:
                self.col_part.remove(index)
 
    def get_part_count(self):
        return len(self.col_part)

    def add_insert(self, grp):
        insert = self.col_insert.add()
        insert.name = grp.name
        return insert

    def delete_insert(self, grp):
        for index, insert in enumerate(self.col_insert):
            if insert.name == grp.name:
                self.col_insert.remove(index)

    def get_insert_count(self):
        return len(self.col_insert)

    def add_product(self, grp):
        product = self.col_product.add()
        product.name = grp.mv.name
        return product
 
    def delete_product(self, grp):
        for index, product in enumerate(self.col_product):
            if product.name == grp.name:
                self.col_product.remove(index)
 
    def get_product_count(self):
        return len(self.col_product)

    def add_wall(self, grp):
        wall = self.col_wall.add()
        wall.name = grp.name
        return wall
 
    def delete_wall(self, grp):
        for index, wall in enumerate(self.col_wall):
            if wall.name == grp.name:
                self.col_wall.remove(index)

    def get_wall_count(self):
        return len(self.col_wall)
    
bpy.utils.register_class(fd_group_col)

class fd_item(PropertyGroup):
    path = StringProperty(name="Path")

bpy.utils.register_class(fd_item)

class fd_item_col(PropertyGroup):
    col_item = CollectionProperty(name="Collection Library Item",type=fd_item)
    index_item = IntProperty(name="Index Library Item",min=-1)
    
    def add_library_item(self, name,path):
        item = self.col_item.add()
        item.path = path
        item.name = name

    def delete_library_item(self, name):
        for index, Pointer in enumerate(self.col_item):
            if Pointer.name == name:
                self.COL_Pointer.remove(index)
                
    def reload_item_col(self,path,update_file_browser=True): #TODO: Build collection from file
        for item in self.col_item:
            self.col_item.remove(0)
            
        if os.path.exists(path):
            folders = os.listdir(path)
            for fullname in folders:
                filename, fileext = os.path.splitext(fullname)
                if fileext.upper() == '.PNG' or fileext.upper() == '.JPG' or fileext.upper() == '.JPEG' or fileext.upper() == '.WMF':
                    self.add_library_item(filename,os.path.join(path,filename))

bpy.utils.register_class(fd_item_col)


class fd_category(PropertyGroup):
    path = StringProperty(name="Path")
    corner_category = BoolProperty(name="Category Type")
    Items = PointerProperty(name="Library Item Collection Pointer",type=fd_item_col)
    
    def init(self):
        if 'Corner' in self.name: #TODO: implement file to store category prefs
            self.corner_category = True

    def load_items(self):
        self.Items.reload_item_col(self.path)
        
bpy.utils.register_class(fd_category)

class fd_category_col(PropertyGroup):
    col_category = CollectionProperty(name="Collection Category",type=fd_category)
    index_category = IntProperty(name="Index Category",min=-1)
    
    def add_category(self, name, path):
        cat = self.col_category.add()
        cat.name = name
        cat.path = path
        return cat

    def delete_category(self, Name):
        for index, Pointer in enumerate(self.COL_Pointer):
            if Pointer.name == Name:
                self.COL_Pointer.remove(index)
                
    def get_active_category(self):
        if len(self.col_category) > 0:
            return self.col_category[self.index_category]
    
    def reload_category_col(self,path): #TODO: Build collection from file
        for category in self.col_category:
            self.col_category.remove(0)
            
        if os.path.exists(path):
            if os.path.isdir(path):
                folders = os.listdir(path)
                for folder in folders:
                    if self.is_valid_category(os.path.join(path,folder)):
                        category = self.add_category(folder, os.path.join(path,folder))
                        category.load_items()

    def is_valid_category(self,path):
        #TODO: Implement category file settings
        if os.path.exists(path):
            if os.path.isdir(path):
                files = os.listdir(path)
                for file in files:
                    filename, file_ext = os.path.splitext(file)
                    if file_ext == '.blend':
                        return True
        return False

bpy.utils.register_class(fd_category_col)

class fd_pointer(PropertyGroup):
    index = IntProperty(name="Index")
    type = EnumProperty(name="Type",items=enums.enum_library_types)
    library_name = StringProperty(name="Library Name")
    category_name = StringProperty(name="Category Name")
    item_name = StringProperty(name="Item Name")
    
bpy.utils.register_class(fd_pointer)

class fd_pointer_col(PropertyGroup):
    col_pointer = CollectionProperty(name="Collection Pointer",type=fd_pointer)
    index_pointer = IntProperty(name="Index Pointer",min=-1)
    
    def add_pointer(self, name):
        pointer = self.col_pointer.add()
        pointer.name = name
        pointer.index = len(self.col_pointer)
        return pointer
    
    def delete_pointer(self, index):
        for index, pointer in enumerate(self.col_pointer):
            if pointer.index == index:
                self.col_pointer.remove(index)

    def draw_pointers(self,layout):
        layout.template_list("FD_UL_pointers", " ", self, "col_pointer", self, "index_pointer", rows=3)

    def get_active(self):
        return self.col_pointer[self.index_pointer]
    
bpy.utils.register_class(fd_pointer_col)

class fd_pointer_library(PropertyGroup):
    path = StringProperty(name="Path")
    type = EnumProperty(name="Type",items=enums.enum_library_types,default='NONE')
    Categories = PointerProperty(name="Category Collection Pointer",type=fd_category_col)

    def load_categories(self):
        self.Categories.reload_category_col(self.path)

bpy.utils.register_class(fd_pointer_library)

class fd_pointer_library_col(PropertyGroup):
    path = StringProperty(name="Path To Libraries",default="",subtype='DIR_PATH',update=events.update_pointer_libraries_path)
    active_library_type = EnumProperty(name="Active Library Type",items=enums.enum_library_types,default='PROJECT',update=events.update_active_library_type)
    
    col_pointer_library = CollectionProperty(name="Collection Pointer Library",type=fd_pointer_library)
    index_pointer_library = IntProperty(name="Index Pointer Library",min=-1)
    
    col_active_pointer_library = CollectionProperty(name="Collection Active Pointer Library",type=fd_pointer_library)
    index_active_pointer_library = IntProperty(name="Index Active Pointer Library",min=-1,update=events.update_active_library_type)
    
    def add_pointer_library(self, library_type, name, path):
        pointer_library = self.col_pointer_library.add()
        pointer_library.type = library_type
        pointer_library.name = name
        pointer_library.path = path
        return pointer_library

    def delete_pointer_library(self, Name, Path):
        for index, pointer_library in enumerate(self.COL_Pointer):
            if pointer_library.name == Name and pointer_library.path == Path:
                self.col_pointer_library.remove(index)
                
    def clear_pointer_library_col(self):
        '''Note: This should only be called by the reload functions'''
        for pointer_library in self.col_pointer_library:
            self.col_pointer_library.remove(0)
    
    def clear_active_pointer_library_col(self):
        '''Note: This should only be called by the reload functions'''
        for pointer_library in self.col_active_pointer_library:
            self.col_active_pointer_library.remove(0)
    
    def get_active_library_icon(self):
        if self.active_library_type == 'PRODUCT':
            return const.icon_product
        if self.active_library_type == 'INSERT':
            return const.icon_insert
        if self.active_library_type == 'PART':
            return const.icon_part
        if self.active_library_type == 'EXTRUSION':
            return const.icon_extrusion
        if self.active_library_type == 'MATERIAL':
            return const.icon_material
        if self.active_library_type == 'OBJECT':
            return const.icon_object
        if self.active_library_type == 'GROUP':
            return const.icon_group
        if self.active_library_type == 'WORLD':
            return const.icon_world
        if self.active_library_type == 'PROJECT':
            return const.icon_project
    
    def get_active_pointer_library(self):
        if len(self.col_active_pointer_library) > self.index_active_pointer_library:
            return self.col_active_pointer_library[self.index_active_pointer_library]
    
    def reload_pointer_library_collection(self): #TODO: Build collection from file
        '''EVENT: update_pointer_libraries_path'''
        self.clear_pointer_library_col()
        if os.path.exists(self.path):
            folders = os.listdir(self.path)
            
            for folder in folders:
                if folder == const.folder_name_projects:
                    library_folders = os.listdir(os.path.join(self.path,folder))
                    for library_folder in library_folders:
                        library = self.add_pointer_library('PROJECT', library_folder, os.path.join(self.path,folder,library_folder))
                        library.load_categories()
                        
                if folder == const.folder_name_extrusion:
                    library_folders = os.listdir(os.path.join(self.path,folder))
                    for library_folder in library_folders:
                        library = self.add_pointer_library('EXTRUSION', library_folder,  os.path.join(self.path,folder,library_folder))
                        library.load_categories()
                        
                if folder == const.folder_name_group:
                    library_folders = os.listdir(os.path.join(self.path,folder))
                    for library_folder in library_folders:
                        library = self.add_pointer_library('GROUP', library_folder, os.path.join(self.path,folder,library_folder))
                        library.load_categories()
                        
                if folder == const.folder_name_insert:
                    library_folders = os.listdir(os.path.join(self.path,folder))
                    for library_folder in library_folders:
                        library = self.add_pointer_library('INSERT', library_folder, os.path.join(self.path,folder,library_folder))
                        library.load_categories()
                        
                if folder == const.folder_name_material:
                    library_folders = os.listdir(os.path.join(self.path,folder))
                    for library_folder in library_folders:
                        library = self.add_pointer_library('MATERIAL', library_folder, os.path.join(self.path,folder,library_folder))
                        library.load_categories()
                        
                if folder == const.folder_name_object:
                    library_folders = os.listdir(os.path.join(self.path,folder))
                    for library_folder in library_folders:
                        library = self.add_pointer_library('OBJECT', library_folder, os.path.join(self.path,folder,library_folder))
                        library.load_categories()
                        
                if folder == const.folder_name_part:
                    library_folders = os.listdir(os.path.join(self.path,folder))
                    for library_folder in library_folders:
                        library = self.add_pointer_library('PART', library_folder,  os.path.join(self.path,folder,library_folder))
                        library.load_categories()
                        
                if folder == const.folder_name_product:
                    library_folders = os.listdir(os.path.join(self.path,folder))
                    for library_folder in library_folders:
                        library = self.add_pointer_library('PRODUCT', library_folder, os.path.join(self.path,folder,library_folder))
                        library.load_categories()
                        
                if folder == const.folder_name_world:
                    library_folders = os.listdir(os.path.join(self.path,folder))
                    for library_folder in library_folders:
                        self.add_pointer_library('WORLD', library_folder, os.path.join(self.path,folder,library_folder))
        else:
            print("fd_datablocks.py","fd_pointer_library_col.reload_col","Path: " + self.path + " not valid.") #TODO: CREATE BETTER WARRING SYSTEM
        
    def reload_active_pointer_library_collection(self):
        '''EVENT: update_active_library_type'''
        '''Note: This should only be called by the user changing self.active_library_type'''
        self.clear_active_pointer_library_col()
        for pointer_library in self.col_pointer_library:
            if pointer_library.type == self.active_library_type:
                active_pointer_library = self.col_active_pointer_library.add()
                active_pointer_library.name = pointer_library.name
                active_pointer_library.type = pointer_library.type
                active_pointer_library.path = pointer_library.path
                active_pointer_library.load_categories()
        
    def draw_active_pointer_library_menus(self,layout):
        row = layout.row(align=True)
        if len(self.col_active_pointer_library) > 0:
            library = self.get_active_pointer_library()
            row.menu("MENU_active_pointer_libraries",icon=self.get_active_library_icon(),text=" " + library.name + "       ")
            category = library.Categories.get_active_category()
            if category:
                row.menu("MENU_active_pointer_library_categories",icon=const.icon_category,text=" " + category.name + "       ")
            else:
                row.label("No Categories",icon='ERROR')
        else:
            layout.label("No Active Pointer Libraries. Check Library Path.",icon='ERROR')

    def draw_library_tabs(self, layout):
#         box = layout.box()
        row = layout.column(align=True)
        row.prop_enum(self, "active_library_type", enums.enum_library_types[1][0], icon=const.icon_project, text="") 
        row.separator()
        row.prop_enum(self, "active_library_type", enums.enum_library_types[2][0], icon=const.icon_product, text="")
        row.prop_enum(self, "active_library_type", enums.enum_library_types[3][0], icon=const.icon_insert, text="")
        row.prop_enum(self, "active_library_type", enums.enum_library_types[4][0], icon=const.icon_part, text="")
        row.prop_enum(self, "active_library_type", enums.enum_library_types[5][0], icon=const.icon_extrusion, text="")
        row.separator() 
        row.prop_enum(self, "active_library_type", enums.enum_library_types[6][0], icon=const.icon_material, text="") 
        row.prop_enum(self, "active_library_type", enums.enum_library_types[7][0], icon=const.icon_object, text="")
        row.prop_enum(self, "active_library_type", enums.enum_library_types[8][0], icon=const.icon_group, text="")
        row.prop_enum(self, "active_library_type", enums.enum_library_types[9][0], icon=const.icon_world, text="")
    
    def get_category_type_from_filepath(self,filepath):
        #TODO: Implement how category settings will be stored
        #      The Category Type should be retrieved a better way
        foldername = os.path.basename(filepath)
        if 'Corner' in foldername:
            return 'CORNER'
        else:
            return 'NONE'

    def get_library_name_from_path(self,filepath):
        for library in self.col_pointer_library:
            if library.path in filepath:
                return library.name
    
    def get_category_name_from_path(self,filepath):
        for library in self.col_pointer_library:
            if library.path in filepath:
                for category in library.Categories.col_category:
                    if category.path in filepath:
                        return category.name

    def get_library_type_from_filepath(self,filepath):
        for library in self.col_pointer_library:
            if library.path in filepath:
                return library.type
    
    def get_blend_file_path_from_thumbnail_path(self,filepath):
        library_type = self.get_library_type_from_filepath(filepath)
        if library_type in {'PRODUCT','INSERT','PART','GROUP'}: #Note: This data must have separate blend files.
            filename = os.path.basename(filepath)
            thumbnail_name, ext = os.path.splitext(filename)
            path = os.path.dirname(filepath)
            files = os.listdir(path)
            for file in files:
                if file == thumbnail_name + ".blend":
                    return os.path.join(path,file)
        
        if library_type in {'EXTRUSION','OBJECT'}: #Note: This data can have multiples stored in one blend file.
            filename = os.path.basename(filepath)
            materialname, worldext = os.path.splitext(filename)
            path = os.path.dirname(filepath)
            files = os.listdir(path)
            for file in files:
                filename2, file_ext2 = os.path.splitext(file)
                if file_ext2 == '.blend':
                    blendpath = os.path.join(path,file)
                    with bpy.data.libraries.load(blendpath, False, True) as (data_from, data_to):
                        if materialname in data_from.objects:
                            return blendpath
                        
        if library_type == 'MATERIAL': #Note: This data can have multiples stored in one blend file.
            filename = os.path.basename(filepath)
            materialname, worldext = os.path.splitext(filename)
            path = os.path.dirname(filepath)
            files = os.listdir(path)
            for file in files:
                filename2, file_ext2 = os.path.splitext(file)
                if file_ext2 == '.blend':
                    blendpath = os.path.join(path,file)
                    with bpy.data.libraries.load(blendpath, False, True) as (data_from, data_to):
                        if materialname in data_from.materials:
                            return blendpath
                        
        if library_type == 'WORLD': #Note: This data can have multiples stored in one blend file.
            filename = os.path.basename(filepath)
            worldname, worldext = os.path.splitext(filename)
            path = os.path.dirname(filepath)
            files = os.listdir(path)
            for file in files:
                filename2, file_ext2 = os.path.splitext(file)
                if file_ext2 == '.blend':
                    blendpath = os.path.join(path,file)
                    with bpy.data.libraries.load(blendpath, False, True) as (data_from, data_to):
                        if worldname in data_from.worlds:
                            return blendpath
                        
        return ""

bpy.utils.register_class(fd_pointer_library_col)

class fd_specgroup(PropertyGroup):
    #Collection of Pointers
    Pointers = PointerProperty(name="Collection Pointers",type=fd_pointer_col)
    Tabs = PointerProperty(name="Collection Tabs",type=fd_tab_col)
    
bpy.utils.register_class(fd_specgroup)
    
class fd_specgroup_col(PropertyGroup):
    #Collection of Pointers
    col_specgroup = CollectionProperty(name="Spec Group Collection",type=fd_specgroup)
    index_specgroup = IntProperty(name="Index Pointer",min=-1)
    type = EnumProperty(name="Type",items=enums.enum_pointer_types,default='MATERIAL')
    
    def add_specgroup(self, name):
        specgroup = self.col_specgroup.add()
        specgroup.name = name
        specgroup.index = len(self.col_specgroup)
        return specgroup
    
    def delete_specgroup(self, index):
        for index, specgroup in enumerate(self.col_specgroup):
            if specgroup.index == index:
                self.col_specgroup.remove(index)

    def rebuild_specgroups_from_xml(self):
        for specgroup in self.col_specgroup:
            self.col_specgroup.remove(0)
            
        import xml.etree.ElementTree as ET
        dm = bpy.context.scene.mv.dm
        path = os.path.join(dm.Libraries.path,const.filename_specgroup)
        tree = ET.parse(path)
        specgroups = tree.getroot()
        
        for specgroup in specgroups:
            mvspecgroup = self.add_specgroup(specgroup.attrib['Name'])
            tabs = specgroup.find('Tabs')
            pointers = specgroup.find('Pointers')
            
            for index, tab in enumerate(tabs):
                mvtab = mvspecgroup.Tabs.add_tab(tab.attrib['Name'])
                mvtab.type = tab.find('Type').text
                
            for index, pointer in enumerate(pointers):
                mvpointer = mvspecgroup.Pointers.add_pointer(pointer.attrib['Name'])
                mvpointer.type = pointer.find('Type').text
                mvpointer.library_name = pointer.find('LibraryName').text
                mvpointer.category_name = pointer.find('CategoryName').text
                mvpointer.item_name = pointer.find('Value').text

    def get_active(self):
        return self.col_specgroup[self.index_specgroup]

    def draw_spec_groups(self,layout):
        layout.template_list("FD_UL_specgroups", " ", self, "col_specgroup", self, "index_specgroup", rows=len(self.col_specgroup))
        specgroup = self.col_specgroup[self.index_specgroup]   
#         tab = specgroup.Tabs.col_tab[specgroup.Tabs.index_tab]
#         layout.menu("MENU_Specgroup_Tabs",icon=const.icon_filefolder,text=" " + tab.name + " ")
        specgroup.Pointers.draw_pointers(layout)
        pointer = specgroup.Pointers.col_pointer[specgroup.Pointers.index_pointer]
        box = layout.box()
        box.label("Pointer Name: " + pointer.name,icon=const.icon_pointer)
        box.label("Pointer Library: " + pointer.library_name,icon=const.icon_library)
        box.label("Pointer Category: " + pointer.category_name,icon=const.icon_category)
        if pointer.type == 'MATERIAL':
            box.label("Pointer Item Name: " + pointer.item_name,icon=const.icon_material)
        elif pointer.type == 'PART':
            box.label("Pointer Item Name: " + pointer.item_name,icon=const.icon_part)
        elif pointer.type == 'INSERT':
            box.label("Pointer Item Name: " + pointer.item_name,icon=const.icon_insert)

bpy.utils.register_class(fd_specgroup_col)

class fd_datamanager(PropertyGroup):
    path = StringProperty(name="Path To Libraries",default="C:\\Program Files\\Microvellum Fluid Beta\\Library Data\\Projects")
    
    #Collection of Pointer Libraries
    Libraries = PointerProperty(name="Collection Libraries",type=fd_pointer_library_col)
    
    Specgroups  = PointerProperty(name="Collection Specs",type=fd_specgroup_col)
    
    #Collection that holds all group objects in the scene
    Walls = PointerProperty(name="Collection Wall",type=fd_group_col)
    Parts = PointerProperty(name="Collection Part",type=fd_group_col)
    Inserts = PointerProperty(name="Collection Insert",type=fd_group_col)
    Products = PointerProperty(name="Collection Product",type=fd_group_col)
    
    def retrieve_data_from_library(self,filepath):
        dataname = ""
        type = self.Libraries.get_library_type_from_filepath(filepath)
        blendfilepath = self.Libraries.get_blend_file_path_from_thumbnail_path(filepath) 
        if type == 'PRODUCT' or type == 'INSERT' or type == 'PART' or type == 'GROUP':
            with bpy.data.libraries.load(blendfilepath, False, True) as (data_from, data_to):
                for grp in data_from.groups:     #NOTE: data_from is just a ([string]).
                    if type + "." in grp:        #      Because of this names of the data 
                        data_to.groups = [grp]   #      must begin with '<type>.'
                        dataname = grp
                        break
            return bpy.data.groups[dataname]

        if type == 'EXTRUSION' or type == 'OBJECT':
            filename = os.path.basename(filepath)
            objectname, worldext = os.path.splitext(filename)
            with bpy.data.libraries.load(blendfilepath, False, True) as (data_from, data_to):
                for object in data_from.objects:    
                    if objectname == object:               
                        data_to.objects = [object]         
                        dataname = object          
                        break
            return bpy.data.objects[dataname]

        if type == 'MATERIAL':
            filename = os.path.basename(filepath)
            materialname, worldext = os.path.splitext(filename)
            with bpy.data.libraries.load(blendfilepath, False, True) as (data_from, data_to):
                for material in data_from.materials:   
                    if materialname == material:                
                        data_to.materials = [material]          
                        dataname = material          
                        break
            material =  bpy.data.materials[dataname]
            material.mv.library_name = self.Libraries.get_library_name_from_path(filepath)
            material.mv.category_name = self.Libraries.get_category_name_from_path(filepath)
            return material
            
        if type == 'WORLD':
            filename = os.path.basename(filepath)
            worldname, worldext = os.path.splitext(filename)
            with bpy.data.libraries.load(blendfilepath, False, True) as (data_from, data_to):
                for world in data_from.worlds:    
                    if worldname == world:                 
                        data_to.worlds = [world]           
                        dataname = world          
                        break
            return bpy.data.worlds[dataname]
    
    def retrieve_material_for_mat_slot(self,pointer_name="",library_name="",category_name="",material_name=""):
        if material_name in bpy.data.materials:
            return bpy.data.materials[material_name]
        
        if pointer_name in self.Specgroups.col_specgroup:
            pass #TODO: SET UP POINTER MATERIAL GETTER
            
        for library in self.Libraries.col_pointer_library:
            if library.type == 'MATERIAL':
                if library.name == library_name:
                    for category in library.Categories.col_category:
                        if category.name == category_name:
                            for item in category.Items.col_item:
                                if item.name == material_name:
                                    return self.retrieve_data_from_library(item.path)
                                
    def retrieve_material_from_library_by_name(self,material_name,library_name="",category_name="",):
        if material_name in bpy.data.materials:
            return bpy.data.materials[material_name]
        
        for library in self.Libraries.col_pointer_library:
            if library.type == 'MATERIAL':
                if library.name == library_name:
                    library.load_categories(False)
                    for cat in library.Categories.col_category:
                        if cat.name == category_name:
                            pass
    
    def add_group_to_scene(self,grp):
        """ Used to add smart groups to the scene.
            Used to Set Group Name
            Used to Add group to Collection        
        """
        
        #HACK THIS IS USED TO FIX A NAMESPACE CHANGE
        if grp.mv.type == 'NONE':
            grp.mv.type = grp.mv.Type
        
        scene = bpy.context.scene
        self.index_group(grp)
        
        obj_bp = None
        obj_x = None
        obj_y = None
        obj_z = None
        obj_cages = []
        
        # HACK: BLENDER BUG?
        # It is not reliable to loop through a groups objects
        # Sometimes blender will exit the loop before it reaches
        # the end of the collection. It seems like it is related to 
        # renaming data while looping. Maybe blender is storing these as strings.
        # Sometimes blender likes to try and trick you. :)
        # TODO: find out why this is happening
        objects = []
        for object in grp.objects:
            objects.append(object)
        # END HACK
        
        for obj in objects:
            obj.mv.id_wall = grp.mv.id_wall
            obj.mv.id_product = grp.mv.id_product
            obj.mv.id_insert = grp.mv.id_insert
            obj.mv.id_part = grp.mv.id_part

            #NAMESPACE FIX
            if obj.mv.Type == 'BPWALL' or obj.mv.Type == 'BPPRODUCT' or obj.mv.Type == 'BPINSERT' or obj.mv.Type == 'BPPART' or obj.mv.Type == 'VPDIMX' or obj.mv.Type == 'VPDIMY' or obj.mv.Type == 'VPDIMZ' or obj.mv.Type == 'CAGE':
                obj.mv.type = obj.mv.Type
            
#             if obj.mv.type == 'BPWALL' or obj.mv.type == 'BPPRODUCT' or obj.mv.type == 'BPINSERT' or obj.mv.type == 'BPPART':
#                 if not obj.parent:
            if grp.mv.type == 'WALL' and obj.mv.type == 'BPWALL':
                obj_bp = obj
                obj_bp.mv.name_object = grp.mv.name_group
            if grp.mv.type == 'PRODUCT' and obj.mv.type == 'BPPRODUCT':
                obj_bp = obj
                obj_bp.mv.name_object = grp.mv.name_group
            if grp.mv.type == 'INSERT' and obj.mv.type == 'BPINSERT':
                obj_bp = obj
                obj_bp.mv.name_object = grp.mv.name_group
            if grp.mv.type == 'PART' and obj.mv.type == 'BPPART':
                obj_bp = obj
                obj_bp.mv.name_object = grp.mv.name_group
                    
            if obj.mv.type == 'VPDIMX':
                if grp.mv.type == 'WALL':
                    if obj.parent.mv.type == 'BPWALL':
                        obj_x = obj
                        obj_x.mv.name_object = const.wall + " " + const.xdim
                if grp.mv.type == 'PRODUCT':
                    if obj.parent.mv.type == 'BPPRODUCT':
                        obj_x = obj
                        obj_x.mv.name_object = const.product + " " + const.xdim
                if grp.mv.type == 'INSERT':
                    if obj.parent.mv.type == 'BPINSERT':
                        obj_x = obj
                        obj_x.mv.name_object = const.insert + " " + const.xdim
                if grp.mv.type == 'PART':
                    if obj.parent.mv.type == 'BPPART':
                        obj_x = obj
                        obj_x.mv.name_object = const.part + " " + const.xdim
                    
            if obj.mv.type == 'VPDIMY':
                if grp.mv.type == 'WALL':
                    if obj.parent.mv.type == 'BPWALL':
                        obj_y = obj
                        obj_y.mv.name_object = const.wall + " " + const.ydim
                if grp.mv.type == 'PRODUCT':
                    if obj.parent.mv.type == 'BPPRODUCT':
                        obj_y = obj
                        obj_y.mv.name_object = const.product + " " + const.ydim
                if grp.mv.type == 'INSERT':
                    if obj.parent.mv.type == 'BPINSERT':
                        obj_y = obj
                        obj_y.mv.name_object = const.insert + " " + const.ydim
                if grp.mv.type == 'PART':
                    if obj.parent.mv.type == 'BPPART':
                        obj_y = obj
                        obj_y.mv.name_object = const.part + " " + const.ydim
                    
            if obj.mv.type == 'VPDIMZ':
                
                if grp.mv.type == 'WALL':
                    if obj.parent.mv.type == 'BPWALL':
                        obj_z = obj
                        obj_z.mv.name_object = const.wall + " " + const.zdim
                if grp.mv.type == 'PRODUCT':
                    if obj.parent.mv.type == 'BPPRODUCT':
                        obj_z = obj
                        obj_z.mv.name_object = const.product + " " + const.zdim
                if grp.mv.type == 'INSERT':
                    if obj.parent.mv.type == 'BPINSERT':
                        obj_z = obj
                        obj_z.mv.name_object = const.insert + " " + const.zdim
                if grp.mv.type == 'PART':
                    if obj.parent.mv.type == 'BPPART':
                        obj_z = obj
                        obj_z.mv.name_object = const.part + " " + const.zdim
                    
            if obj.mv.type == 'CAGE':
                obj_cages.append(obj)

            obj.hide_select = False
            obj.hide = False
            
            self.force_obj_update(obj) #TODO: Figure out if there is a better way to update object data
            
            if obj.name not in scene.objects:
                scene.objects.link(obj)
                
            self.link_object_with_groups(obj)
            self.set_object_name(obj)
            if obj.type == 'EMPTY':
                obj.hide = True
            if obj.type == 'MESH':
                obj.mv.assign_materials_from_pointers(obj.name)
            
        if obj_bp:
            grp.mv.bp_id = obj_bp.name
        if obj_x:
            grp.mv.x_id = obj_x.name
        if obj_y:
            grp.mv.y_id = obj_y.name
        if obj_z:
            grp.mv.z_id = obj_z.name
        
        self.rebuild_group_collections(grp)

        if len(obj_cages) > 0:
            fd_utils.delete_obj_list(obj_cages)
            
        return grp

    def add_obj_to_grp(self,obj,grp):
        scene = bpy.context.scene
        if obj.name not in scene.objects:
            scene.objects.link(obj)
        obj.mv.id_wall = grp.mv.id_wall
        obj.mv.id_product = grp.mv.id_product
        obj.mv.id_insert = grp.mv.id_insert
        obj.mv.id_part = grp.mv.id_part
        grp.mv.add_object_to_group_collection(obj)
        self.link_object_with_groups(obj)
        grp.mv.update_vector_groups()

    def add_product_to_wall(self,grp,grp_wall):
        #SYNC_GROUPS
        grp.mv.room_index = grp_wall.mv.room_index
        grp.mv.wall_index = grp_wall.mv.wall_index
        grp.mv.id_wall = grp_wall.name
        
        #ADD TO SCENE SETUP GROUP
        self.add_group_to_scene(grp)
        
        obj_bool = grp.mv.get_wall_bool()
        
        if obj_bool:
            grp_wall.mv.add_bool(obj_bool)
        
        #SET HIERARCHY
        obj_wallbp = grp_wall.mv.get_bp()
        obj_productbp = grp.mv.get_bp()
        obj_productbp.parent = obj_wallbp
        
    def add_grp_to_product(self,grp,product_grp):
        #SYNC_GROUPS
        grp.mv.room_index = product_grp.mv.room_index
        
        grp.mv.wall_index = product_grp.mv.wall_index
        grp.mv.product_index = product_grp.mv.product_index
        grp.mv.id_wall = product_grp.mv.id_wall
        grp.mv.id_product = product_grp.name
        
        #ADD TO SCENE SETUP GROUP
        self.add_group_to_scene(grp)
        
        #SET HIERARCHY
        obj_productbp = product_grp.mv.get_bp()
        obj_bp = grp.mv.get_bp()
        obj_bp.parent = obj_productbp
        
        obj_new_bp = grp.mv.get_bp()
        product_grp.mv.add_object_to_group_collection(obj_new_bp)
        grp.mv.bp_id = obj_new_bp.name
        
    def add_part_to_insert(self,grp,insert_grp):
        #SYNC_GROUPS
        grp.mv.room_index = insert_grp.mv.room_index
        
        grp.mv.wall_index = insert_grp.mv.wall_index
        grp.mv.product_index = insert_grp.mv.product_index
        grp.mv.insert_index = insert_grp.mv.insert_index
        grp.mv.id_wall = insert_grp.mv.id_wall
        grp.mv.id_product = insert_grp.mv.id_product
        grp.mv.id_insert = insert_grp.name
        
        #ADD TO SCENE SETUP GROUP
        self.add_group_to_scene(grp)
        
        #SET HIERARCHY
        obj_insertbp = insert_grp.mv.get_bp()
        obj_bp = grp.mv.get_bp()
        obj_bp.parent = obj_insertbp
        insert_grp.mv.add_object_to_group_collection(obj_bp)
        grp.mv.bp_id = obj_bp.name
        
    def index_group(self,grp):
        scene = bpy.context.scene #MUST BE IN CORRECT SCENE TO CALL REGISERT GROUP
        
        if grp.mv.type == 'NONE':     #HACK TO FIX NAMESPACE CHANGE...WILL DELETE
            grp.mv.type = grp.mv.Type #HACK TO FIX NAMESPACE CHANGE...WILL DELETE
            
        grp.mv.room_index = scene.mv.index
        
        if grp.mv.type == 'PRODUCT':
            grp.mv.product_index = self.Products.get_product_count() + 1
            self.set_group_name(grp)
            self.Products.add_product(grp)
            
        if grp.mv.type == 'INSERT':
            grp.mv.insert_index = self.Inserts.get_insert_count() + 1
            self.set_group_name(grp)
            self.Inserts.add_insert(grp)

        if grp.mv.type == 'PART':
            grp.mv.part_index = self.Parts.get_part_count() + 1
            self.set_group_name(grp)
            self.Parts.add_part(grp)
                
        if grp.mv.type == 'WALL':
            grp.mv.wall_index = self.Walls.get_wall_count() + 1
            self.set_group_name(grp)
            self.Walls.add_wall(grp)
        
    def set_group_name(self,grp):
        # GROUPTYPE.RN.WN.PN.IN.TN.GRPINDEX.GRPNAME
        index = str(grp.mv.room_index) + '.'
        index += str(grp.mv.wall_index) + '.'
        index += str(grp.mv.product_index) + '.'
        index += str(grp.mv.insert_index) + '.'
        index += str(grp.mv.part_index) + '.'
        
        grpname = grp.mv.type + '.'
        grpname += index
        grpname += grp.mv.name_group
        grp.name = grpname #BLENDER GRP NAME
        grp.mv.name = grpname #FLUID DESIGNER GRP NAME
        
        if grp.mv.type == 'WALL':
            grp.mv.id_wall = grpname
        elif grp.mv.type == 'PRODUCT':
            grp.mv.id_product = grpname
        elif grp.mv.type == 'INSERT':
            grp.mv.id_insert = grpname
        elif grp.mv.type == 'PART':
            grp.mv.id_part = grpname
            
        #TODO: SET IF I CAN SET THE BASEOINT OBJECT NAME HERE

    def set_object_name(self,obj):
        # OBJECTTYPE.RN.WN.PN.IN.TN.OBJINDEX.OBJNAME
        room_index = 0
        wall_index = 0
        product_index = 0
        insert_index = 0
        part_index = 0
        
        for grp in obj.users_group:
            if grp.mv.type == 'NONE':     #HACK: This is used to fix namespace changes
                grp.mv.type = grp.mv.Type #      remove this at some point
                
            room_index = grp.mv.room_index
            if grp.mv.type == 'WALL':
                wall_index = grp.mv.wall_index
            if grp.mv.type == 'PRODUCT':
                product_index = grp.mv.product_index
            if grp.mv.type == 'INSERT':
                insert_index = grp.mv.insert_index
            if grp.mv.type == 'PART':
                part_index = grp.mv.part_index
                
        index = str(room_index) + '.'
        index += str(wall_index) + '.'
        index += str(product_index) + '.'
        index += str(insert_index) + '.'
        index += str(part_index) + '.'
        index += str(obj.mv.index) + '.'
        if obj.mv.type == 'NONE':
            objname = obj.type + '.' 
            objname += index 
            objname += obj.mv.name_object
            obj.name = objname #BLENDER OBJ NAME
            obj.mv.name = objname #FLUID DESINGER OBJ NAME
        else:
            objname = obj.mv.type + '.' 
            objname += index 
            objname += obj.mv.name_object
            obj.name = objname #BLENDER OBJ NAME
            obj.mv.name = objname #FLUID DESINGER OBJ NAME

    def get_product_list_from_wall_grp(self,grp_wall):
        obj_bp_wall = grp_wall.mv.get_bp()
        list_obj_bp = []
        
        for child in obj_bp_wall.children:
            if child.mv.type == 'BPPRODUCT':
                list_obj_bp.append(child)

        list_obj_bp.sort(key=lambda obj: obj.location.x, reverse=False)
        return list_obj_bp

    def get_wall_group(self,data):
        if type(data) is bpy.types.Object:
            for grp in data.users_group:
                if grp.mv.type == 'WALL':
                    return grp
        elif type(data) is bpy.types.Group:
            return bpy.data.groups[data.mv.id_wall]
        else:
            return None
            
    def get_plane_group(self,data):
        if type(data) is bpy.types.Object:
            for grp in data.users_group:
                if grp.mv.type == 'PLANE':
                    return grp
        elif type(data) is bpy.types.Group:
            return self.Planes.get_plane(data.mv.id_wall)
        else:
            return None
            
    def get_product_group(self,data):
        if type(data) is bpy.types.Object:
            for grp in data.users_group:
                if grp.mv.type == 'PRODUCT':
                    return grp
        elif type(data) is bpy.types.Group:
            return self.Products.get_product(data.mv.id_product)
        else:
            return None
            
    def get_insert_group(self,data):
        if type(data) is bpy.types.Object:
            for grp in data.users_group:
                if grp.mv.type == 'INSERT':
                    return grp
        elif type(data) is bpy.types.Group:
            return self.Inserts.get_insert(data.mv.id_insert)
        else:
            return None
            
    def get_part_group(self,data):
        if type(data) is bpy.types.Object:
            for grp in data.users_group:
                if grp.mv.type == 'PART':
                    return grp
        elif type(data) is bpy.types.Group:
            return self.Parts.get_part(data.mv.id_part)
        else:
            return None
            
    def get_pointer_by_name(self,name):
        for spec in self.Specgroups.col_specgroup:
            for pointer in spec.Pointers.col_pointer:
                if pointer.name == name:
                    return pointer
            
    def force_obj_update(self, obj):
        """ This manually recalcs blender/python logic
            There has got to be a better way to do this
        """
        if obj is None:
            return
        #Needed to maintain modifier logic
#         if len(obj.modifiers) > 0:
#             if obj.modifiers[0].type == 'HOOK' or obj.modifiers[0].type == 'BOOLEAN':
#                 obj.modifiers[0].object = obj.modifiers[0].object
        #Needed to maintain driver logic
        if obj.animation_data is not None:
            if len(obj.animation_data.drivers) > 0:
                for driver in obj.animation_data.drivers:
                    driver.driver.expression = driver.driver.expression
        #Needed to maintain parent relationship
        if obj.parent is not None:
            obj.parent = obj.parent
            
    def rebuild_group_collections(self,grp):
        """ This rebuilds the group.Objects collection
            This is used to display lists and name objects
        """
        grp.mv.Objects.clear_collections()
        obj_bp = grp.mv.get_bp()
        if obj_bp:
            for child in obj_bp.children:
                grp.mv.add_object_to_group_collection(child)
                
    def link_object_with_groups(self,obj):
        obj.hide = False
        obj.select = True
        bpy.context.scene.objects.active = obj
        if obj.mv.id_wall in bpy.data.groups:
            bpy.ops.object.group_link(group=obj.mv.id_wall)
        if obj.mv.id_product in bpy.data.groups:
            bpy.ops.object.group_link(group=obj.mv.id_product)
        if obj.mv.id_insert in bpy.data.groups:
            bpy.ops.object.group_link(group=obj.mv.id_insert)
        if obj.mv.id_part in bpy.data.groups:
            bpy.ops.object.group_link(group=obj.mv.id_part)
    
bpy.utils.register_class(fd_datamanager)

class fd_interface(PropertyGroup):
    show_debug_tools = BoolProperty(name="Show Debug Tools",default = True,description="Show Debug Tools")
    use_default_blender_interface = BoolProperty(name="Use Default Blender Interface",default = False,description="Show Default Blender interface")
    
    interface_object_tabs = EnumProperty(name="Interface Object Tabs",items=enums.enum_object_tabs,default = 'INFO')
    interface_group_object_tabs = EnumProperty(name="Interface Group Object Tabs",items=enums.enum_group_object_tabs,default = 'MESH')
    interface_group_tabs = EnumProperty(name="Interface Group Tabs",items=enums.enum_group_tabs,default = 'INFO')
    interface_selection_tabs = EnumProperty(name="Interface Selection Tabs",items=enums.enum_selection_tabs,default = 'OBJECT')
    
    group_driver_tabs = EnumProperty(name="Group Driver Tabs",items=enums.enum_group_drivers_tabs,default = 'LOC_X')
    object_driver_tabs = EnumProperty(name="Object Driver Tabs",items=enums.enum_object_drivers_tabs,default = 'LOC_X')
    
bpy.utils.register_class(fd_interface)

class fd_scene(PropertyGroup):
    index = IntProperty(name="Index Scene",min=-1,default = 0)
    dm = PointerProperty(name="Data Manager",type= fd_datamanager)
    ui = PointerProperty(name="Interface",type= fd_interface)
    
    active_material_index = IntProperty(name="Index Scene",min=-1,default = 0)
    
    #TODO: implement the standard collections or remove this and add to RNA Structure
    PromptPage = bpy.props.PointerProperty(name="Prompt Page",type=mvPromptPage)

bpy.utils.register_class(fd_scene)

class fd_world(PropertyGroup):
    #TODO: implement the standard collections or remove this and add to RNA Structure
    PromptPage = bpy.props.PointerProperty(name="Prompt Page",type=mvPromptPage)

bpy.utils.register_class(fd_world)


class fd_window_manager(PropertyGroup):
    placement_on_wall = EnumProperty(name="Placement on Wall",items=[('LEFT',"Left",""),
                                                                     ('CENTER',"Center",""),
                                                                     ('RIGHT',"Right",""),
                                                                     ('FILL_WALL',"Fill Wall","")],default = 'LEFT')
    
    placement_on_product = EnumProperty(name="Placement on Product",items=[('LEFT',"Left","left"),
                                                                           ('RIGHT',"Right","Right"),
                                                                           ('CENTER',"Center",""),
                                                                           ('FILL_RIGHT',"Fill Right","Fill Right"),
                                                                           ('FILL_LEFT',"Fill Left","Fill Left")],default = 'LEFT')  
    
    wall_length = FloatProperty(name="Wall Length",default=120.0,unit='LENGTH')
    
    wall_height = FloatProperty(name="Wall Height",default=108.0,unit='LENGTH')
    
    wall_rotation = FloatProperty(name="Wall Rotation",default=0,unit='ROTATION')
    
    def update_file_browser_parameters(self,path):
        """ This function will update the file_browser space with the correct settings
            Called by fd_category_col.reload_category_col
            Called by bpy.ops.fd_library.change_library_category
        """
        library_type = bpy.context.scene.mv.dm.Libraries.get_library_type_from_filepath(path)
        if bpy.context.screen:
            for area in bpy.context.screen.areas:
                if area.type == 'FILE_BROWSER': #TODO: Make sure this is right
                    for space in area.spaces:
                        if space.type == 'FILE_BROWSER': #???: why is the type stored in areas and spaces.
                            params = space.params
                            params.directory = path
                            params.use_filter = True
                            params.display_type = 'FILE_IMGDISPLAY'
                            params.use_filter_movie = False
                            params.use_filter_script = False
                            params.use_filter_sound = False
                            params.use_filter_text = False
                            params.use_filter_font = False
                            params.use_filter_folder = False
                            if library_type == 'PROJECT':
                                params.use_filter_blender = True
                                params.use_filter_image = False
                            else:
                                params.use_filter_blender = False
                                params.use_filter_image = True
                            #Blender removed the operator bpy.ops.file.directory()
                            #This used to update the current directory. but somewhere between
                            #2.69.2 and 2.69.10 it was remove. I cannot find any reason or anything
                            #in the change log that explains why this was done. UGH...
                            #bpy.ops.file.next() seems to update the directory, but i hope
                            #this doesn't present any other problems.
                            bpy.ops.file.next()

bpy.utils.register_class(fd_window_manager)

class extend_blender_data():
    bpy.types.Material.mv = PointerProperty(type = fd_material)
    bpy.types.Object.mv = PointerProperty(type = fd_object)
    bpy.types.Group.mv = PointerProperty(type = fd_group)
    bpy.types.Scene.mv = PointerProperty(type = fd_scene)
    bpy.types.World.mv = PointerProperty(type = fd_world)
    bpy.types.WindowManager.mv = PointerProperty(type = fd_window_manager)
