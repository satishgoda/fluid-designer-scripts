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

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       BoolVectorProperty,
                       PointerProperty,
                       EnumProperty)

import fd_utils

class OPS_add_wall_to_room(Operator):
    bl_idname = "fd_wall.add_wall"
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
        dm = context.scene.mv.dm
        if context.active_object:
            grp_wall = dm.get_wall_group(context.active_object)
            if grp_wall:
                objbp = grp_wall.mv.get_bp()
                self.rotation = math.degrees(objbp.rotation_euler.z)
        return wm.invoke_props_dialog(self, width=400)
        
    def draw(self,context):
        dm = bpy.context.scene.mv.dm
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
        
        if dm.Walls.get_wall_count() > 0:
            row = col.row()
            row.prop(self,"add_to_selected",text="Add to Selected Wall")
        
    def execute(self, context):
        wm = context.window_manager
        dm = context.scene.mv.dm
        grp_wall = dm.get_wall_group(context.active_object)
        if self.add_to_selected and context.active_object:
            if grp_wall == None:
                bpy.ops.fd_general.error('INVOKE_DEFAULT',message='You must have a wall selected')
                return {'CANCELLED'}

        if self.direction == 'LEFT':
            wm.mv.wall_rotation = self.rotation + 90
        if self.direction == 'STRAIGHT':
            wm.mv.wall_rotation = self.rotation
        if self.direction == 'RIGHT':
            wm.mv.wall_rotation = self.rotation + -90

        if dm.Walls.get_wall_count() == 0:
            #HACK TO NAME GROUPS DIFFERENT FROM LIBRARY GROUP
            #LIBRARY PRODUCTS WILL ALWAYS HAVE ROOM INDEX OF 0
            #THIS WILL CHANGE IT TO 1
            #THIS IS NOT STABLE TODO: IMPLEMENT DIFFERENT NAME
            #FOR LIBRARY PRODUCTS
            if context.scene.mv.index == 0:
                context.scene.mv.index = 1 

        if dm.Walls.get_wall_count() == 0 or self.add_to_selected == False:
            size = (wm.mv.wall_length,0.1,wm.mv.wall_height)
            grp_wall = fd_utils.create_wall_group(size)
            dm.add_group_to_scene(grp_wall)
            obj_bp = grp_wall.mv.get_bp()
            
            obj_bp.rotation_euler.z = math.radians(wm.mv.wall_rotation)

        else:
            size = (wm.mv.wall_length,0.1,wm.mv.wall_height)
            grp_new_wall = fd_utils.create_wall_group(size)
            
            dm.add_group_to_scene(grp_new_wall)
            
            anchor_x = grp_wall.mv.get_x()
            obj_bp = grp_new_wall.mv.get_bp()
            
            fd_utils.connect_objects_location(anchor_x,obj_bp)
            obj_bp.rotation_euler.z = math.radians(wm.mv.wall_rotation)

            
        if len(bpy.data.groups) == 1:
            bpy.ops.view3d.view_all(center=True)
        return {'FINISHED'}

class OPS_delete_wall(Operator):
    bl_idname = "fd_delete.delete_wall"
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

#------REGISTER
classes = [
           OPS_add_wall_to_room,
           OPS_delete_wall
           ]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
