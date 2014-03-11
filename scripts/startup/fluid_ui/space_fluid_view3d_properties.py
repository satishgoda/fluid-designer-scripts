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

from fd_datablocks import enums, const

class PANEL_selection_properties(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = " "
    bl_options = {'HIDE_HEADER'}
    
    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        layout = self.layout
        layout.label("Selection Properties ",icon='MAN_TRANS')

    def draw(self, context):
        layout = self.layout
        dm = context.scene.mv.dm
        ui = context.scene.mv.ui
        obj = context.active_object
        
        grp_wall = dm.get_wall_group(obj)
        grp_product = dm.get_product_group(obj)
        grp_insert = dm.get_insert_group(obj)
        grp_part = dm.get_part_group(obj)
        
        row = layout.row(align=True)
        row.prop_enum(ui, "interface_selection_tabs", enums.enum_selection_tabs[0][0], icon=const.icon_object, text="Object") 
        
        if grp_wall:
            row.prop_enum(ui, "interface_selection_tabs", enums.enum_selection_tabs[1][0], icon=const.icon_wall, text="Wall") 
        if grp_product:
            row.prop_enum(ui, "interface_selection_tabs", enums.enum_selection_tabs[2][0], icon=const.icon_product, text="Product") 
        if grp_insert:   
            row.prop_enum(ui, "interface_selection_tabs", enums.enum_selection_tabs[3][0], icon=const.icon_insert, text="Insert")
        if grp_part:
            row.prop_enum(ui, "interface_selection_tabs", enums.enum_selection_tabs[4][0], icon=const.icon_part, text="Part")
            
        if obj and ui.interface_selection_tabs == 'OBJECT':
            obj.mv.draw_properties(layout, obj.name)
        if grp_wall and ui.interface_selection_tabs == 'WALL':
            grp_wall.mv.draw_properties(layout,advanced=False)
        if grp_product and ui.interface_selection_tabs == 'PRODUCT':
            grp_product.mv.draw_properties(layout,advanced=True)
        if grp_insert and ui.interface_selection_tabs == 'INSERT':
            grp_insert.mv.draw_properties(layout,advanced=True)
        if grp_part and ui.interface_selection_tabs == 'PART':
            grp_part.mv.draw_properties(layout,advanced=True)
            
class PANEL_drivers(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = " "
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return False

    def draw_header(self, context):
        layout = self.layout
        layout.label("Drivers ",icon='AUTO')

    def draw(self, context):
        layout = self.layout
        mv = context.window_manager.mv
        obj = context.active_object
        if obj:
            if obj.animation_data:
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
                    row.label(DriverName,icon='AUTO')
                    value = eval('bpy.data.objects["' + obj.name + '"].' + DR.data_path)
                    if isinstance(value,type(obj.location)):
                        value = value[DR.array_index]
#                     if type(value) == "class 'Vector'":
#                         value = value[DR.array_index]
                    row.label(str(value))
                    row = box.row()
                    if DR.driver.is_valid:
                        if DR.driver.show_debug_info:
                            row.prop(DR.driver,"show_debug_info",icon='TRIA_DOWN',text="",emboss=False)
                        else:
                            row.prop(DR.driver,"show_debug_info",icon='TRIA_RIGHT',text="",emboss=False)
                        row.prop(DR.driver,"expression",icon='FILE_TICK',text="")
                        row.prop(DR,"mute",icon='SPEAKER',text="")
                    else:
                        if DR.driver.show_debug_info:
                            row.prop(DR.driver,"show_debug_info",icon='TRIA_DOWN',text="",emboss=False)
                        else:
                            row.prop(DR.driver,"show_debug_info",icon='TRIA_RIGHT',text="",emboss=False)                        
                        row.prop(DR.driver,"expression",icon='ERROR',text="")
                    if DR.driver.show_debug_info:
                        col = box.column()
                        varbox = col.box()
                        row = varbox.row()
                        row.label("Product Variables:",icon='OBJECT_DATA')
                        props = row.operator("fluiddriver.add_variable_from_product_property",text="Property Variable",icon='INFO')
                        props.object_name = obj.name
                        props.data_path = DR.data_path
                        props.array_index = DR.array_index
                        
                        props = row.operator("fluiddriver.add_variable_from_prompt",text="Prompt Variable",icon='SETTINGS')
                        props.object_name = obj.name
                        props.data_path = DR.data_path
                        props.array_index = DR.array_index
                        props.type = 'PRODUCT'
                        
                        row = varbox.row()
                        row.label("Insert Variables:",icon='STICKY_UVS_LOC')
                        props = row.operator("fluiddriver.add_variable_from_insert_property",text="Property Variable",icon='INFO')
                        props.object_name = obj.name
                        props.data_path = DR.data_path
                        props.array_index = DR.array_index
                        
                        props = row.operator("fluiddriver.add_variable_from_prompt",text="Prompt Variable",icon='SETTINGS')
                        props.object_name = obj.name
                        props.data_path = DR.data_path
                        props.array_index = DR.array_index
                        props.type = 'INSERT'
                        
                        row = varbox.row()
                        row.label("Part Variables:",icon='MOD_MESHDEFORM')
                        props = row.operator("fluiddriver.add_variable_from_part_property",text="Property Variable",icon='INFO')
                        props.object_name = obj.name
                        props.data_path = DR.data_path
                        props.array_index = DR.array_index
                        
                        props = row.operator("fluiddriver.add_variable_from_prompt",text="Prompt Variable",icon='SETTINGS')
                        props.object_name = obj.name
                        props.data_path = DR.data_path
                        props.array_index = DR.array_index
                        props.type = 'PART'
                        
                        for var in DR.driver.variables:
                            col = box.column()
                            boxvar = col.box()
                            row = boxvar.row()
                            row.prop(var,"name")
                            props = row.operator("fluiddriver.remove_variable",text="",icon='X')
                            props.object_name = obj.name
                            props.data_path = DR.data_path
                            props.array_index = DR.array_index
                            props.var_name = var.name
                            row = boxvar.row()
                            row.prop(var,"type")
                            for target in var.targets:
                                row = boxvar.row()
                                row.prop(target,"id")
                                row = boxvar.row()
                                row.prop(target,"data_path")
                                if target.id:
                                    row = boxvar.row()
                                    value = eval('bpy.data.objects["' + target.id.name + '"].' + target.data_path)
                                    col = boxvar.column()
                                    boxval = col.box()
                                    row = boxval.row(align=True)
                                    row.label("     ")
                                    row.label("Value: " + str(value))
                                    row.label("     ")
        else:
            layout.label("Select an Object to View Drivers",icon='ERROR')

class PANEL_materials(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = " "
    bl_options = {'HIDE_HEADER'}
    
    @classmethod
    def poll(cls, context):
        return False

    def draw_header(self, context):
        layout = self.layout
        layout.label("Materials ",icon='MATERIAL')

    def draw(self, context):
        layout = self.layout

        mat = None
        obj = context.object
        slot = None
        space = context.space_data

        if obj:
            row = layout.row()

            row.template_list("MATERIAL_UL_matslots", "", obj, "material_slots", obj, "active_material_index", rows=1)

            col = row.column(align=True)
            col.operator("object.material_slot_add", icon='ZOOMIN', text="")
            col.operator("object.material_slot_remove", icon='ZOOMOUT', text="")

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

            if mat:
                mat.mv.PromptPage.draw_prompt_page(layout,mat,allow_edit=True)
            
#             if mat:
#                 row.prop(mat, "use_nodes", icon='NODETREE', text="")
# 
#             if slot:
#                 row.prop(slot, "link", text="")
#             else:
#                 row.label()
#         elif mat:
#             split.template_ID(space, "pin_id")
#             split.separator()
# 
#         if mat:
#             layout.prop(mat, "type", expand=True)
#             if mat.use_nodes:
#                 row = layout.row()
#                 row.label(text="", icon='NODETREE')
#                 if mat.active_node_material:
#                     row.prop(mat.active_node_material, "name", text="")
#                 else:
#                     row.label(text="No material node selected")

        
#         layout = self.layout
#         obj = context.object
#         space = context.space_data
#         box = layout.box()
#         if obj:
#             row = box.row()
#             row.label("Material Slots:")
#             row.operator("fd_object.update_object_material").object_name = obj.name
#             row = box.row()
#             row.template_list("MATERIAL_UL_matslots", "", obj, "material_slots", obj, "active_material_index", rows=1)
# 
#             col = row.column(align=True)
#             col.operator("fluidobject.add_material_slot", icon='ZOOMIN', text="").ObjectName = obj.name
#             col.operator("object.material_slot_remove", icon='ZOOMOUT', text="")
# 
#             if obj.mode == 'EDIT':
#                 row = box.row(align=True)
#                 row.operator("object.material_slot_assign", text="Assign")
#                 row.operator("object.material_slot_select", text="Select")
#                 row.operator("object.material_slot_deselect", text="Deselect")
# 
#         if obj:
#             if obj.active_material_index + 1 > len(obj.mv.COL_MaterialSlot):
#                 box.label("ENABLE POINTERS")
#             else:
#                 Slot = obj.mv.COL_MaterialSlot[obj.active_material_index]
#                 row = box.row(align=True)
#                 row.prop(Slot,"UsePointer",icon='HAND',text="")
#                 row.prop(Slot,"name",text="")
#                 if Slot.UsePointer:
#                     row = box.row(align=True)
#                     row.prop_search(Slot,"LibraryName",context.scene.world.mv,"COL_MaterialLibrary",text="",icon='EXTERNAL_DATA')
#                     if Slot.LibraryName in context.scene.world.mv.COL_MaterialLibrary:
#                         row = box.row(align=True)
#                         Library = context.scene.world.mv.COL_MaterialLibrary[Slot.LibraryName]
#                         row.prop_search(Slot,"PointerName",Library,"COL_Pointer",text="",icon='STYLUS_PRESSURE')
#                 else:
#                     box.template_ID(obj, "active_material", new="material.new")
#             
            
            
#             if slot:
#                 row.prop(slot, "link", text="")
#             else:
#                 row.label()
#         elif mat:
#             split.template_ID(space, "pin_id")
#             split.separator()

class PANEL_modifiers(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = " "
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return False

    def draw_header(self, context):
        layout = self.layout
        layout.label("Modifiers ",icon='MODIFIER')

    def draw(self, context):
        Room = context.scene.mv
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label("Object Modifiers:")
        row.prop(Room,"ShowHookModifiers",text="",icon='HOOK')

        ob = context.object
        if ob:
            box.operator_menu_enum("object.modifier_add", "type")
            col = box.column()
    
            for md in ob.modifiers:
                if md.type == 'HOOK':
                    if Room.ShowHookModifiers:
                        box = col.template_modifier(md)
                        if box:
                            # match enum type to our functions, avoids a lookup table.
                            getattr(self, md.type)(box, ob, md)
                else:
                    box = col.template_modifier(md)
                    if box:
                        # match enum type to our functions, avoids a lookup table.
                        getattr(self, md.type)(box, ob, md)
        else:
            layout.label("Select an Object to View Modifiers",icon='ERROR')

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

        row = layout.row()
        row.prop_search(md, "vertex_group", ob, "vertex_groups", text="")
        sub = row.row()
        sub.active = bool(md.vertex_group)
        sub.prop(md, "invert_vertex_group")

        layout.prop(md, "use_multi_modifier")

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

        split.prop(md, "width")
        split.prop(md, "use_only_vertices")

        # -- new modifier only, this may be reverted in favor of 2.62 mod.
        '''
        split = layout.split()
        split.prop(md, "use_even_offset")
        split.prop(md, "use_distance_offset")
        '''
        # -- end

        layout.label(text="Limit Method:")
        layout.row().prop(md, "limit_method", expand=True)
        if md.limit_method == 'ANGLE':
            layout.prop(md, "angle_limit")
        elif md.limit_method == 'WEIGHT':
            layout.row().prop(md, "edge_weight_method", expand=True)

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
        row = layout.row()
        row.prop(md, "decimate_type", expand=True)
        decimate_type = md.decimate_type

        if decimate_type == 'COLLAPSE':
            layout.prop(md, "ratio")
            row = layout.row()
            row.prop_search(md, "vertex_group", ob, "vertex_groups", text="")
            row.prop(md, "invert_vertex_group")
            layout.prop(md, "use_collapse_triangulate")
        elif decimate_type == 'UNSUBDIV':
            layout.prop(md, "iterations")
        else:  # decimate_type == 'DISSOLVE':
            layout.prop(md, "angle_limit")
            layout.prop(md, "use_dissolve_boundaries")

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
            col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

        sub = col.column()
        sub.active = bool(md.vertex_group)
        sub.prop(md, "invert_vertex_group")

    def MESH_DEFORM(self, layout, ob, md):
        split = layout.split()

        col = split.column()
        sub = col.column()
        sub.label(text="Object:")
        sub.prop(md, "object", text="")
        sub.active = not md.is_bound
        col = split.column()
        col.label(text="Vertex Group:")
        col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

        sub = col.column()
        sub.active = bool(md.vertex_group)
        sub.prop(md, "invert_vertex_group")

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
        if not md.is_build_enabled:
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
        sub.active = md.wave_alignment > 0
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
        col.prop(md, "subsurf_levels")

        col = split.column()
        col.label(text="Mode:")
        col.prop(md, "wrap_method", text="")

        if md.wrap_method == 'PROJECT':
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
        sub = col.column()
        sub.active = (md.origin is not None)
        sub.prop(md, "use_relative")

        col = split.column()
        col.label(text="Deform:")
        col.prop(md, "factor")
        col.prop(md, "limits", slider=True)
        if md.deform_method in {'TAPER', 'STRETCH', 'TWIST'}:
            col.prop(md, "lock_x")
            col.prop(md, "lock_y")

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
        col.prop_search(md, "vertex_group", ob, "vertex_groups", text="")

        col.label(text="Crease:")
        col.prop(md, "edge_crease_inner", text="Inner")
        col.prop(md, "edge_crease_outer", text="Outer")
        col.prop(md, "edge_crease_rim", text="Rim")
        col.label(text="Material Index Offset:")

        col = split.column()

        col.prop(md, "offset")
        sub = col.column()
        sub.active = bool(md.vertex_group)
        sub.prop(md, "invert_vertex_group", text="Invert")
        sub.prop(md, "thickness_vertex_group", text="Factor")

        col.prop(md, "use_even_offset")
        col.prop(md, "use_quality_normals")
        col.prop(md, "use_rim")

        sub = col.column()
        row = sub.split(align=True, percentage=0.4)
        row.prop(md, "material_offset", text="")
        row = row.row()
        row.active = md.use_rim
        row.prop(md, "material_offset_rim", text="Rim")
        sub.prop(md, "use_flip_normals")

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
        layout.prop(md, "remove_disconnected_pieces")
        row = layout.row()
        row.active = md.remove_disconnected_pieces
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

        col = split.column()
        col.label(text="Default Weight:")
        col.prop(md, "default_weight", text="")

        layout.prop(md, "falloff_type")
        if md.falloff_type == 'CURVE':
            col = layout.column()
            col.template_curve_mapping(md, "map_curve")

        split = layout.split(percentage=0.4)
        split.prop(md, "use_add")
        row = split.row()
        row.active = md.use_add
        row.prop(md, "add_threshold")

        split = layout.split(percentage=0.4)
        split.prop(md, "use_remove")
        row = split.row()
        row.active = md.use_remove
        row.prop(md, "remove_threshold")

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

        layout.row().prop(md, "proximity_mode", expand=True)
        if md.proximity_mode == 'GEOMETRY':
            layout.row().prop(md, "proximity_geometry", expand=True)

        row = layout.row()
        row.prop(md, "min_dist")
        row.prop(md, "max_dist")

        layout.prop(md, "falloff_type")

        # Common mask options
        layout.separator()
        self.vertex_weight_mask(layout, ob, md)

    def SKIN(self, layout, ob, md):
        layout.operator("object.skin_armature_create", text="Create Armature")

        layout.separator()
        layout.prop(md, "branch_smoothing")
        layout.prop(md, "use_smooth_shade")

        layout.label(text="Selected Vertices:")
        split = layout.split()

        col = split.column(align=True)
        col.operator("object.skin_loose_mark_clear", text="Mark Loose").action = 'MARK'
        col.operator("object.skin_loose_mark_clear", text="Clear Loose").action = 'CLEAR'

        col = split.column()
        col.operator("object.skin_root_mark", text="Mark Root")
        col.operator("object.skin_radii_equalize", text="Equalize Radii")

        layout.label(text="Symmetry Axes:")
        col = layout.column()
        col.prop(md, "use_x_symmetry")
        col.prop(md, "use_y_symmetry")
        col.prop(md, "use_z_symmetry")

    def TRIANGULATE(self, layout, ob, md):
        layout.prop(md, "use_beauty")

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
        
class PANEL_constraints(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = " "
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return False

    def draw_header(self, context):
        layout = self.layout
        layout.label("Constraints ",icon='CONSTRAINT')

    def draw(self, context):
        layout = self.layout

        ob = context.object

        if ob:
            layout.operator_menu_enum("object.constraint_add", "type")

            for con in ob.constraints:
                self.draw_constraint(context, con)
        else:
            layout.label("Select an Object to View Constraints",icon='ERROR')

    def draw_constraint(self, context, con):
        layout = self.layout

        box = layout.template_constraint(con)

        if box:
            # match enum type to our functions, avoids a lookup table.
            getattr(self, con.type)(context, box, con)

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
        self.target_template(layout, con)

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
        self.target_template(layout, con)

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
            self.target_template(layout, con)
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
        self.target_template(layout, con)
        self.ik_template(layout, con)

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
        self.target_template(layout, con)
        self.ik_template(layout, con)

        layout.prop(con, "limit_mode")

        row = layout.row()
        row.prop(con, "weight", text="Weight", slider=True)
        row.prop(con, "distance", text="Distance", slider=True)

    def FOLLOW_PATH(self, context, layout, con):
        self.target_template(layout, con)
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
        self.target_template(layout, con)

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
        self.target_template(layout, con)

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
        self.target_template(layout, con)

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
        self.target_template(layout, con)

        self.space_template(layout, con)

    #def SCRIPT(self, context, layout, con):

    def ACTION(self, context, layout, con):
        self.target_template(layout, con)

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
        self.target_template(layout, con)

        row = layout.row()
        row.label(text="To:")
        row.prop(con, "track_axis", expand=True)

        row = layout.row()
        row.label(text="Lock:")
        row.prop(con, "lock_axis", expand=True)

    def LIMIT_DISTANCE(self, context, layout, con):
        self.target_template(layout, con)

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
        self.target_template(layout, con)

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
        self.target_template(layout, con)

        row = layout.row()
        row.prop(con, "use_sticky")
        row.prop(con, "use_rotation")

        layout.prop(con, "offset")

        row = layout.row()
        row.label(text="Min/Max:")
        row.prop(con, "floor_location", expand=True)

        self.space_template(layout, con)

    def RIGID_BODY_JOINT(self, context, layout, con):
        self.target_template(layout, con, subtargets=False)

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
        self.target_template(layout, con)

        row = layout.row()
        row.label(text="Main Axis:")
        row.prop(con, "main_axis", expand=True)

        layout.prop(con, "use_cyclic")

    def TRANSFORM(self, context, layout, con):
        self.target_template(layout, con)

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

        self.space_template(layout, con)

    def SHRINKWRAP(self, context, layout, con):
        self.target_template(layout, con, False)

        layout.prop(con, "distance")
        layout.prop(con, "shrinkwrap_type")

        if con.shrinkwrap_type == 'PROJECT':
            row = layout.row(align=True)
            row.prop(con, "use_x")
            row.prop(con, "use_y")
            row.prop(con, "use_z")

    def DAMPED_TRACK(self, context, layout, con):
        self.target_template(layout, con)

        row = layout.row()
        row.label(text="To:")
        row.prop(con, "track_axis", expand=True)

    def SPLINE_IK(self, context, layout, con):
        self.target_template(layout, con)

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
        self.target_template(layout, con)

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
        clip = self._getConstraintClip(context, con)

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
        clip = self._getConstraintClip(context, con)

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

class PANEL_degub_panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = " "

    @classmethod
    def poll(cls, context):
        return False

    def draw_header(self, context):
        layout = self.layout
        layout.label("Debug Panel ",icon='MOD_FLUIDSIM')

    def draw(self, context):
        obj = context.active_object
        layout = self.layout
        if obj:
            layout.prop(obj.mv,"Type")
        
            for grp in obj.users_group:
                layout.prop(grp.mv,"Type")


#------REGISTER
classes = [
           PANEL_selection_properties,
           PANEL_materials,
           PANEL_drivers,
           PANEL_modifiers,
           PANEL_constraints,
           PANEL_degub_panel
           ]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
