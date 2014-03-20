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

import bpy, bgl
from bpy.types import Header, Menu, Operator
import math
import bmesh
import fd_utils

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       BoolVectorProperty,
                       PointerProperty,
                       EnumProperty)

class OPS_rename_object(Operator):
    bl_idname = "fd_object.rename_object"
    bl_label = "Rename Object"
    bl_options = {'UNDO'}
    
    object_name = StringProperty(name="Object Name")
    new_name = StringProperty(name="New Name",default="")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        dm = context.scene.mv.dm
        obj = bpy.data.objects[self.object_name]
        old_name = obj.name
        obj.mv.name_object = self.new_name
        dm.set_object_name(obj)
        if obj.parent:
            grp = None
            if obj.parent.mv.type == 'BPPRODUCT':
                grp = dm.get_product_group(obj)
            if obj.parent.mv.type == 'BPINSERT':
                grp = dm.get_insert_group(obj)
            if obj.parent.mv.type == 'BPPART':
                grp = dm.get_part_group(obj)
            if grp:
                for index, object in enumerate(grp.mv.Objects.col_mesh):
                    if old_name == object.name:
                        object.name = obj.name
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        obj = bpy.data.objects[self.object_name]
        self.new_name = obj.mv.name_object
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        obj = bpy.data.objects[self.object_name]
        layout.label("ID: " + obj.mv.name)
        layout.prop(self, "new_name")

class OPS_create_floor_plane(Operator):
    bl_idname = "fd_object.create_floor_plane"
    bl_label = "Create Floor Plane"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        largest_x = 0
        largest_y = 0
        smallest_x = 0
        smallest_y = 0
        
        for group in bpy.data.groups:
            if group.mv.type == 'WALL':
                obj_bp = group.mv.get_bp()
                obj_x = group.mv.get_x()
                start_point = (obj_bp.matrix_world[0][3],obj_bp.matrix_world[1][3],0)
                end_point = (obj_x.matrix_world[0][3],obj_x.matrix_world[1][3],0)

                if start_point[0] > largest_x:
                    largest_x = start_point[0]
                if start_point[1] > largest_y:
                    largest_y = start_point[1]
                if start_point[0] < smallest_x:
                    smallest_x = start_point[0]
                if start_point[1] < smallest_y:
                    smallest_y = start_point[1]
                if end_point[0] > largest_x:
                    largest_x = end_point[0]
                if end_point[1] > largest_y:
                    largest_y = end_point[1]
                if end_point[0] < smallest_x:
                    smallest_x = end_point[0]
                if end_point[1] < smallest_y:
                    smallest_y = end_point[1]

        loc = (smallest_x , smallest_y,0)
        width = math.fabs(smallest_y) + math.fabs(largest_y)
        length = math.fabs(largest_x) + math.fabs(smallest_x)
        if width == 0:
            width = -48
        if length == 0:
            length = -48
        obj_plane = fd_utils.create_floor_mesh('Floor',(length,width,0.0))
        obj_plane.location = loc
        return {'FINISHED'}

class OPS_move_object(Operator):
    bl_idname = "fd_object.move_object"
    bl_label = "Move Object"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        if context.active_object.mode == 'OBJECT':
            obj = context.active_object
            if obj.mv.type == 'VPDIMX' or obj.mv.type == 'VPDIMY' or obj.mv.type == 'VPDIMZ':
                bpy.ops.transform.translate('INVOKE_DEFAULT')
                return {'FINISHED'}
            if obj.parent:
                dm = context.scene.mv.dm
                grp_part = dm.get_part_group(obj)
                grp_insert = dm.get_insert_group(obj)
                grp_product = dm.get_product_group(obj)
                grp_wall = dm.get_wall_group(obj)
                if grp_part:
                    obj_bp = grp_part.mv.get_bp()
                    obj_bp.select = True
                    context.scene.objects.active = obj_bp
                    bpy.ops.transform.translate('INVOKE_DEFAULT')
                    return {'FINISHED'}
                elif grp_insert:
                    obj_bp = grp_insert.mv.get_bp()
                    obj_bp.select = True
                    context.scene.objects.active = obj_bp
                    bpy.ops.transform.translate('INVOKE_DEFAULT')
                    return {'FINISHED'}
                elif grp_product:
                    obj_bp = grp_product.mv.get_bp()
                    obj_bp.select = True
                    context.scene.objects.active = obj_bp
                    bpy.ops.transform.translate('INVOKE_DEFAULT')
                    return {'FINISHED'}
                elif grp_wall:
                    obj_bp = grp_wall.mv.get_bp()
                    obj_bp.select = True
                    context.scene.objects.active = obj_bp
                    bpy.ops.transform.translate('INVOKE_DEFAULT')
                    return {'FINISHED'}

        bpy.ops.transform.translate('INVOKE_DEFAULT')
        return {'FINISHED'}

class OPS_scale_object(Operator):
    bl_idname = "fd_object.scale_object"
    bl_label = "Scale Object"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        if context.active_object.mode == 'OBJECT':
            obj = context.active_object
            dm = context.scene.mv.dm
            grp_part = dm.get_part_group(obj)
            grp_insert = dm.get_insert_group(obj)
            grp_product = dm.get_product_group(obj)
            grp_wall = dm.get_wall_group(obj)
            if grp_part or grp_insert or grp_product or grp_wall:
                bpy.ops.fd_general.error('INVOKE_DEFAULT',message="You cannot scale this object.")
                return {'FINISHED'} 

        bpy.ops.transform.resize('INVOKE_DEFAULT')
        return {'FINISHED'}

class OPS_rotate_object(Operator):
    bl_idname = "fd_object.rotate_object"
    bl_label = "Rotate Object"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        if context.active_object.mode == 'OBJECT':
            obj = context.active_object
            if obj.parent:
                dm = context.scene.mv.dm
                grp_part = dm.get_part_group(obj)
                grp_insert = dm.get_insert_group(obj)
                grp_product = dm.get_product_group(obj)
                grp_wall = dm.get_wall_group(obj)
                if grp_part:
                    obj_bp = grp_part.mv.get_bp()
                    obj_bp.select = True
                    context.scene.objects.active = obj_bp
                    bpy.ops.transform.rotate('INVOKE_DEFAULT')
                    return {'FINISHED'}
                elif grp_insert:
                    obj_bp = grp_insert.mv.get_bp()
                    obj_bp.select = True
                    context.scene.objects.active = obj_bp
                    bpy.ops.transform.rotate('INVOKE_DEFAULT')
                    return {'FINISHED'}
                elif grp_product:
                    obj_bp = grp_product.mv.get_bp()
                    obj_bp.select = True
                    context.scene.objects.active = obj_bp
                    bpy.ops.transform.rotate('INVOKE_DEFAULT')
                    return {'FINISHED'}
                elif grp_wall:
                    obj_bp = grp_wall.mv.get_bp()
                    obj_bp.select = True
                    context.scene.objects.active = obj_bp
                    bpy.ops.transform.rotate('INVOKE_DEFAULT')
                    return {'FINISHED'}

        bpy.ops.transform.rotate('INVOKE_DEFAULT')
        return {'FINISHED'}

class OPS_delete_object_from_group(Operator):
    bl_idname = "fd_object.delete_object_from_group"
    bl_label = "Delete Object From Group"
    bl_options = {'UNDO'}

    object_name = StringProperty(name="Object Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        dm = context.scene.mv.dm
        obj = bpy.data.objects[self.object_name]
        if obj.parent:
            grp = None
            if obj.parent.mv.type == 'BPPRODUCT':
                grp = dm.get_product_group(obj)
            if obj.parent.mv.type == 'BPINSERT':
                grp = dm.get_insert_group(obj)
            if obj.parent.mv.type == 'BPPART':
                grp = dm.get_part_group(obj)
                
            if grp:
                #REMOVE OBJ FROM UI LIST
                for index, mesh in enumerate(grp.mv.Objects.col_mesh):
                    if obj.name == mesh.name:
                        grp.mv.Objects.col_mesh.remove(index)
                for index, empty in enumerate(grp.mv.Objects.col_empty):
                    if obj.name == empty.name:
                        grp.mv.Objects.col_empty.remove(index)
                for index, font in enumerate(grp.mv.Objects.col_font):
                    if obj.name == font.name:
                        grp.mv.Objects.col_font.remove(index)
                for index, curve in enumerate(grp.mv.Objects.col_curve):
                    if obj.name == curve.name:
                        grp.mv.Objects.col_curve.remove(index)
                for index, group in enumerate(grp.mv.Objects.col_group):
                    if obj.name == group.name:
                        grp.mv.Objects.col_group.remove(index)
                        
        obj_list = []
        
        #REMOVE ALL GROUPED OBJECTS IF OBJ IS BP
        if obj.mv.type == 'BPPART':
            grp_part = dm.get_part_group(obj)
            for obj1 in grp_part.objects:
                obj_list.append(obj1)
        if obj.mv.type == 'BPINSERT':
            grp_insert = dm.get_insert_group(obj)
            for obj1 in grp_insert.objects:
                obj_list.append(obj1)
        if obj.mv.type == 'BPPRODUCT':
            grp_product = dm.get_product_group(obj)
            for obj1 in grp_product.objects:
                obj_list.append(obj1)
        
        #DELETE OBJECT
        if len(obj_list) > 0:
            fd_utils.delete_obj_list(obj_list)
        else:
            bpy.ops.object.select_all(action='DESELECT')             
            context.scene.objects.active = obj
            obj.hide_select = False
            obj.select = True
            bpy.ops.object.delete()
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.label("Object Name: " + context.active_object.name)

class OPS_select_object(Operator):
    bl_idname = "fd_object.select_object"
    bl_label = "Select Object"
    bl_options = {'UNDO'}
    
    object_name = StringProperty(name="Object Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = bpy.data.objects[self.object_name]
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        context.scene.objects.active = obj
        return {'FINISHED'}

class OPS_delete_object(Operator):
    bl_idname = "fd_object.delete_object"
    bl_label = "Delete Object"
    bl_options = {'UNDO'}
    
    object_name = StringProperty(name="Object Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        dm = context.scene.mv.dm
        obj = bpy.data.objects[self.object_name]
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        context.scene.objects.active = obj
        grp = None
        
        if obj.parent:
            if obj.parent.mv.type == 'BPWALL':
                grp = dm.get_wall_group(obj.parent)
            if obj.parent.mv.type == 'BPPRODUCT':
                grp = dm.get_product_group(obj.parent)
            if obj.parent.mv.type == 'BPINSERT':
                grp = dm.get_insert_group(obj.parent)
            if obj.parent.mv.type == 'BPPART':
                grp = dm.get_part_group(obj.parent)
                
        if grp:
            grp.mv.delete_object_from_group(obj)

        return {'FINISHED'}
    
class OPS_update_object_material(Operator):
    bl_idname = "fd_object.update_object_material"
    bl_label = "Update Object Material"
    bl_options = {'UNDO'}
    
    object_name = StringProperty(name="Object Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        obj = bpy.data.objects[self.object_name]
        obj.select = True
        context.scene.objects.active = obj
        if obj.type =='MESH':
            if len(obj.data.uv_textures) == 0:
                if obj.mode == 'OBJECT':
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.fluidobject.unwrap_mesh()
                    bpy.ops.object.editmode_toggle()

#         obj.mv.AssignMaterialsFromPointers(obj.name) #TODO: IMPLEMENT POINTERS
        return {'FINISHED'}
    
class OPS_toggle_edit_mode(Operator):
    bl_idname = "fd_object.toggle_edit_mode"
    bl_label = "Toggle Edit Mode"
    bl_options = {'UNDO'}
    
    object_name = StringProperty(name="Object Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = bpy.data.objects[self.object_name]
        obj.hide = False
        obj.hide_select = False
        obj.select = True
        context.scene.objects.active = obj
        if obj.mode == 'EDIT':
            bpy.ops.object.editmode_toggle()
        else:
            bpy.ops.object.editmode_toggle()

        return {'FINISHED'}
    
class OPS_sync_material_slots(Operator):
    bl_idname = "fd_object.sync_material_slots"
    bl_label = "Toggle Edit Mode"
    bl_options = {'UNDO'}
    
    object_name = StringProperty(name="Object Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = bpy.data.objects[self.object_name]
        obj.mv.sync_material_slots(obj.name)

        return {'FINISHED'}
    
class OPS_update_object_materials(Operator):
    bl_idname = "fd_object.update_object_materials"
    bl_label = "Update object Materials"
    bl_options = {'UNDO'}
    
    object_name = StringProperty(name="Object Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = bpy.data.objects[self.object_name]
        obj.mv.assign_materials_from_pointers(obj.name)
        return {'FINISHED'}
    
class OPS_unwrap_mesh(Operator):
    bl_idname = "fd_object.unwrap_mesh"
    bl_label = "Unwrap Mesh"
    bl_options = {'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if obj.mode == 'OBJECT':
            bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66, island_margin=0, user_area_weight=0)
        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}
    
class OPS_add_wall_to_room(Operator):
    bl_idname = "fluidobject.add_wall_to_room"
    bl_label = "Draw Wall"
    bl_options = {'UNDO'}
    
    add_to_selected = BoolProperty(name="Add New Wall to Selected",default=True)
    direction = EnumProperty(name="Placement on Wall",
                             items=[('LEFT',"Left",""),
                                    ('STRAIGHT',"Straight",""),
                                    ('RIGHT',"Right","")],
                             default='STRAIGHT')
    rotation = FloatProperty(name="Rotation")
    
    @classmethod
    def poll(cls, context):
        return True
    
    def invoke(self,context,event):
        wm = context.window_manager
        if context.active_object:
            Wall = context.active_object.mv.GetWall()
            if Wall:
                objbp = bpy.data.objects[Wall.Obj_BPLinkID]
                wm.mv.wall_rotation = math.degrees(objbp.rotation_euler.z)
                self.rotation = wm.mv.wall_rotation
        return wm.invoke_props_dialog(self, width=400)
        
    def draw(self,context):
        Room = bpy.context.scene.mv
        wm = context.window_manager
        layout = self.layout
        box = layout.box()
        #box.label("Draw Wall Options",icon='SCRIPTPLUGINS')
        col = box.column(align=False)
        
        row = col.row(align=True)
        row.prop_enum(self, "direction", 'LEFT', icon='TRIA_LEFT', text="") 
        row.prop_enum(self, "direction", 'STRAIGHT', icon='TRIA_UP', text="") 
        row.prop_enum(self, "direction", 'RIGHT', icon='TRIA_RIGHT', text="")   
        
        row = col.row()
        row.label("Wall Length:")
        row.prop(wm.mv,"wall_length",text="")
        
        row = col.row()
        row.label("Wall Height:")
        row.prop(wm.mv,"wall_height",text="")
        
#         row = col.row()
#         row.label("Wall Rotation:")
#         row.prop(wm.mv,"WallRotation",text="")
        
#         row = col.row(align=True)
#         row.label("Direction:")
#         row.prop_enum(self, "Direction", 'LEFT', icon='TRIA_LEFT', text="") 
#         row.prop_enum(self, "Direction", 'STRAIGHT', icon='TRIA_UP', text="") 
#         row.prop_enum(self, "Direction", 'RIGHT', icon='TRIA_RIGHT', text="")    
        
        if len(Room.COL_Wall) > 0:
            row = col.row()
            row.prop(self,"add_to_selected",text="Add to Selected Wall")
        
    def execute(self, context):
        Room = bpy.context.scene.mv
        wm = context.window_manager
        if self.Direction == 'LEFT':
            wm.mv.wall_rotation = self.rotation + 90
        if self.Direction == 'STRAIGHT':
            wm.mv.wall_rotation = self.rotation
        if self.Direction == 'RIGHT':
            wm.mv.wall_rotation = self.rotation + -90

        if len(Room.COL_Wall) == 0 or self.add_to_selected == False:
            Room.AddWall(context.scene.cursor_location,(wm.mv.wall_length,0,wm.mv.wall_height),wm.mv.wall_rotation)
        else:
            Wall_Selected = bpy.context.object.mv.GetWall() 
            obj_wall = bpy.data.objects[Wall_Selected.Obj_BPLinkID]
            obj_length = bpy.data.objects[Wall_Selected.Obj_XDimLinkID]
            xloc = obj_wall.location.x + math.cos(obj_wall.rotation_euler.z) *obj_length.location.x
            yloc = obj_wall.location.y + math.sin(obj_wall.rotation_euler.z) *obj_length.location.x
            Wall = Room.AddWall((xloc,yloc,0),(wm.mv.WallLength,0,wm.mv.WallHeight),wm.mv.wall_rotation)
            Wall.AddWallConstraint(Wall_Selected)    
            
        Room.WallIndex = len(Room.COL_Wall) - 1
        bpy.ops.view3d.view_all(center=True)
        return {'FINISHED'}

class OPS_delete_wall(Operator):
    bl_idname = "fluidobject.delete_wall"
    bl_label = "Delete Wall"
    bl_options = {'UNDO'}
    
    GroupName = StringProperty(name="Group Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        Room = context.scene.mv
        grp_wall = bpy.data.groups[self.GroupName]
        RowToSelect = Room.WallIndex
        if Room.WallIndex == len(Room.COL_Wall) -1:
            RowToSelect = len(Room.COL_Wall) - 2
        Room.DeleteWall(grp_wall)
        Room.WallIndex = RowToSelect
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.label("Are you sure you want to delete the wall?")
    
class OPS_create_plane(Operator):
    bl_idname = "fluidobject.create_plane"
    bl_label = "Create Plane"
    bl_options = {'UNDO'}
    
    Width = FloatProperty(
                name="Width",
                default=5.0,
                )

    Length = FloatProperty(
                name="Length",
                default=10.0,
                )

    Rot = FloatVectorProperty(
                name="Rotation",
                default=(0.0,0.0,0.0),
                )

    Placement = EnumProperty(name="Type",items=[('VERTICAL',"Vertical","Vertical"),('HORIZONTAL',"Horizontal","Horizontal")],description="Select the Placement.",default='HORIZONTAL')
    
    #Properties needed for object_data_add
    location = FloatVectorProperty(
            name="Location",
            subtype='TRANSLATION',
            )

    view_align = BoolProperty(
            name="Align to View",
            default=False,
            )
            
    rotation = FloatVectorProperty(
            name="Rotation",
            subtype='EULER',
            )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.Placement == 'VERTICAL':
            partverts_loc, partfaces = FUNC.AddWall(self.Width,self.Length)
            mesh = bpy.data.meshes.new('Wall')
        else:
            partverts_loc, partfaces = FUNC.AddPlane(self.Width,self.Length)
            mesh = bpy.data.meshes.new('Plane')

        bm = bmesh.new()

        for v_co in partverts_loc:
            bm.verts.new(v_co)
        
        for f_idx in partfaces:
            bm.faces.new([bm.verts[i] for i in f_idx])
        
        bm.to_mesh(mesh)
        mesh.update()
        from bpy_extras import object_utils
        object_utils.object_data_add(context, mesh, operator=self)
        return {'FINISHED'}
    
class OPS_create_cube_mesh(Operator):
    bl_idname = "fluidobject.create_cube_mesh"
    bl_label = "Create Cube Mesh"
    bl_options = {'UNDO'}
    
    GroupName = StringProperty(name="Group Name")

    CubeSize = FloatVectorProperty(
               name="Notch Size",
               default=(4.0,3.25,.78),
               )

    CubeMirror = BoolVectorProperty(
                  name="Notch Size",
                  default=(False,False,False),
                  )

    #Properties needed for object_data_add
    location = FloatVectorProperty(
            name="Location",
            subtype='TRANSLATION',
            )

    view_align = BoolProperty(
            name="Align to View",
            default=False,
            )
            
    rotation = FloatVectorProperty(
            name="Rotation",
            subtype='EULER',
            )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        partverts_loc, partfaces = FUNC.AddPartMesh(self.CubeSize, 
                                                    self.CubeMirror)

        mesh = bpy.data.meshes.new('NEWCUBEMESH')
        
        bm = bmesh.new()

        for v_co in partverts_loc:
            bm.verts.new(v_co)
        
        for f_idx in partfaces:
            bm.faces.new([bm.verts[i] for i in f_idx])
        
        bm.to_mesh(mesh)
        mesh.update()
        from bpy_extras import object_utils
        object_utils.object_data_add(context, mesh, operator=self)
        obj_notch = context.active_object
        return {'FINISHED'}
    
class OPS_add_plane_to_room(Operator):
    bl_idname = "fluidobject.add_plane_to_room"
    bl_label = "Add Plane To Room"
    bl_options = {'UNDO'}
    
    ZLoc = FloatProperty(
                name="Z Location",
                default=0.0,
                )
    
    @classmethod
    def poll(cls, context):
        dm = bpy.context.scene.mv.dm
        return dm.Walls.get_count() > 0

    def execute(self, context):
        Room = bpy.context.scene.mv
        wm = context.window_manager
        if len(Room.COL_Wall) > 0:
            smallest, largest = Room.GetRoomBounds()
            loc = (smallest[0] , smallest[1],self.ZLoc)
            width = math.fabs(smallest[1]) + math.fabs(largest[1])
            length = math.fabs(largest[0]) + math.fabs(smallest[0])
            if width == 0:
                width = -48
            if length == 0:
                length = -48
            Plane = Room.AddPlane(loc,(length, width,0),0)
            Room.PlaneIndex = len(Room.COL_Plane) - 1
        return {'FINISHED'}
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,"ZLoc")
    
class OPS_add_material_slot(Operator):
    bl_idname = "fluidobject.add_material_slot"
    bl_label = "Add Material Slot"
    bl_options = {'UNDO'}
    
    ObjectName = StringProperty(name="Object Name")
    MaterialSlotName = StringProperty(name="Material Slot Name",default="Material Slot")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        obj = bpy.data.objects[self.ObjectName]
        context.scene.objects.active = obj
        bpy.ops.object.material_slot_add()
        Slot = obj.mv.COL_MaterialSlot.add()
        Slot.name = self.MaterialSlotName
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,"MaterialSlotName")
    
class OPS_show_object_prompts(Operator):
    bl_idname = "mvgeneral.show_object_prompts"
    bl_label = "Prompts"
    
    GroupName = StringProperty(name="GroupName")
    Index = IntProperty(name="Index")
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        grp = bpy.data.groups[self.GroupName]
        if grp.mv.Type == 'PRODUCT':
            FluidGroup = grp.mv.GetProduct()
        if grp.mv.Type == 'PRODUCT':
            FluidGroup = grp.mv.GetProduct()
        if grp.mv.Type == 'PRODUCT':
            FluidGroup = grp.mv.GetProduct()
        if FluidGroup:
            BP = bpy.data.objects[FluidGroup.Obj_BPLinkID]
            BP.mv.PromptPage.ShowPrompts(layout,BP,self.Index)      
    
class OPS_add_countertop_to_product(Operator):
    bl_idname = "fd_object.add_countertop_to_product"
    bl_label = "Add Countertop To Product"
    bl_options = {'UNDO'}
    
    ZLoc = FloatProperty(
                name="Z Location",
                default=0.0,
                )
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        dm = context.scene.mv.dm
        COUNTER_TOP_CLEARANCE = 0.1
        
        bpy.ops.object.select_all(action='DESELECT')

        list_products = fd_utils.get_product_list_from_selected(bpy.context.selected_objects)
        
        for product in list_products:
            verts = [0.0,0.0,0.0,0.0]
            obj_bp = product.mv.get_bp()
            obj_x = product.mv.get_x()
            obj_y = product.mv.get_y()
            obj_z = product.mv.get_z()
            verts[0] = obj_x.matrix_world[0][3]
            verts[1] = obj_y.obj_bp.matrix_world[1][3]
            
            #Create countertop meshes
            if product.mv.category_type == 'CORNER':
                float_LeftSideDepth = obj_bp.mv.PromptPage.COL_Prompt["Left Side Width"].NumberValue
                float_RightSideDepth = obj_bp.mv.PromptPage.COL_Prompt["Right Side Width"].NumberValue
                verts[2] = float_LeftSideDepth
                verts[3] = float_RightSideDepth
                
                obj_CounterTop = fd_utils.create_corner_countertop_mesh("countertop", verts)
            
            else:              
                obj_CounterTop = fd_utils.create_countertop_mesh("countertop", verts)
                
            bpy.context.scene.objects.active = obj_CounterTop
            obj_CounterTop.select = True
        
        #join meshes and remove doubles
        bpy.ops.object.join()
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}
    
class OPS_add_molding(Operator):
    bl_idname = "fd_object.add_molding"
    bl_label = "Add Molding"
    bl_options = {'UNDO'}
    
    ZLoc = FloatProperty(name="Z Location", default=0.0)
    Return = EnumProperty(items=(('RIGHT_RETURN',"Right Return","Right Return"),
                                 ('LEFT_RETURN',"Left Return","Left Return"),
                                 ('NO_RETURN',"No Return","No Return")),
                          name="Return",
                          default='NO_RETURN')
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        dm = context.scene.mv.dm
        obj = bpy.context.object
        grp_product = dm.get_product_group(obj)
        
        #could use GetBounds()
        obj_bp = grp_product.mv.get_bp()
        obj_x = grp_product.mv.get_x()
        obj_y = grp_product.mv.get_y()      
        
        #Add curve set handle type to vector, set origin to 1st control point, hide handles 
        bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=True)
        bpy.ops.curve.handle_type_set(type='VECTOR')
        bpy.ops.curve.select_all(action='DESELECT')
        bpy.context.active_object.data.splines[0].bezier_points[0].select_control_point = True
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.data.curves["BezierCurve"].show_handles = False
        
        Curve = bpy.context.object
        Curve.location = obj_bp.location
        
        #placement of curve based on user input
        if self.Return == 'NO_RETURN':
            Curve.location.y = obj_y.location.y
            Curve.data.splines[0].bezier_points[1].co = obj_x.location
            
        elif self.Return == 'RIGHT_RETURN':
            Curve.location.x += obj_x.location.x
            Curve.data.splines[0].bezier_points[1].co = [0.0, obj_y.location.y, 0.0] 
            bpy.ops.object.editmode_toggle()
            bpy.ops.curve.select_all(action='DESELECT')
            Curve.data.splines[0].bezier_points[1].select_control_point = True
            bpy.ops.curve.extrude_move(CURVE_OT_extrude={"mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(-(obj_x.location.x), 0.0, 0.0)})
            bpy.ops.object.editmode_toggle()

        elif self.Return == 'LEFT_RETURN':
            Curve.data.splines[0].bezier_points[1].co = [0.0, obj_y.location.y, 0.0] 
            bpy.ops.object.editmode_toggle()
            bpy.ops.curve.select_all(action='DESELECT')
            Curve.data.splines[0].bezier_points[1].select_control_point = True
            bpy.ops.curve.extrude_move(CURVE_OT_extrude={"mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(obj_x.location.x, 0.0, 0.0)})
            bpy.ops.object.editmode_toggle()
        
        return {'FINISHED'}
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,"Return") 
        layout.prop(self,"ZLoc")     
    
#------REGISTER
classes = [
           OPS_rename_object,
           OPS_move_object,
           OPS_rotate_object,
           OPS_scale_object,
           OPS_delete_object_from_group,
           OPS_select_object,
           OPS_delete_object,
           OPS_update_object_material,
           OPS_toggle_edit_mode,
           OPS_sync_material_slots,
           OPS_update_object_materials,
           OPS_add_molding,
           OPS_add_countertop_to_product,
           OPS_unwrap_mesh,
           OPS_create_floor_plane
           ]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
