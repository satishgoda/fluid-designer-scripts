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
import os

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       PointerProperty,
                       EnumProperty)

class OPS_create_scene(Operator):
    bl_idname = "fd_scene.create_scene"
    bl_label = "Create Scene"
    
    def execute(self, context):
        bpy.ops.scene.new(type='EMPTY')
        return {'FINISHED'}

class OPS_render_scene(Operator):
    bl_idname = "fd_scene.render_scene"
    bl_label = "Image Quality Options"
    
    def execute(self, context):
        scene = context.scene.mv
        
        for obj in context.scene.objects:
            if obj.hide or obj.mv.Type == 'CAGE':
                obj.cycles_visibility.camera = False
                obj.cycles_visibility.diffuse = False
                obj.cycles_visibility.glossy = False
                obj.cycles_visibility.transmission = False
                obj.cycles_visibility.shadow = False
            else:
                obj.cycles_visibility.camera = True
                obj.cycles_visibility.diffuse = True
                obj.cycles_visibility.glossy = True
                obj.cycles_visibility.transmission = True
                obj.cycles_visibility.shadow = True
        #render
        bpy.ops.render.render('INVOKE_DEFAULT')

        return {'FINISHED'}

class OPS_render_settings(Operator):
    bl_idname = "fd_scene.render_settings"
    bl_label = "Render Settings"
    
    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        wm = context.window_manager
        layout = self.layout
        scene = bpy.context.scene
        rd = scene.render
        space = context.space_data
        image_settings = rd.image_settings
        
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Render Size:",icon='STICKY_UVS_VERT')
        row.prop(rd, "resolution_x", text="X")
        row.prop(rd, "resolution_y", text="Y")
        row = box.row()
        row.label(text="Rendering Quality:",icon='IMAGE_COL')
        row.prop(scene.cycles,"samples",text='Passes')
        row = box.row()
        row.label(text="Image Format:",icon='IMAGE_DATA')
        row.prop(image_settings,"file_format",text="")
        row = box.row()
        row.label(text="Display Mode:",icon='RENDER_RESULT')
        row.prop(rd,"display_mode",text="")
        row = box.row()
        row.label(text="Use Transparent Film:",icon='SEQUENCE')
        row.prop(scene.cycles,"film_transparent",text='')

class OPS_render_preview(Operator):
    bl_idname = "fd_scene.render_preview"
    bl_label = "Render Preview"
    bl_options = {'UNDO'}

    def execute(self, context):
        if len(bpy.data.cameras) == 0:
            bpy.ops.object.camera_add(view_align=False)

        #else:
            #bpy.ops.object.camera_add()
            
        bpy.ops.view3d.camera_to_view()

        #set camera clipping to 9999
        bpy.data.cameras[0].clip_end = 9999

        return {'FINISHED'}         
        
class OPS_update_world_from_template(Operator):
    bl_idname = "fluidscene.update_world_from_template"
    bl_label = "Update World From Template"
    bl_options = {'UNDO'}
    
    Path = StringProperty(name="Path",default="")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.label("Under Construction")


        


class OPS_add_locrot_keyframe(Operator):
    bl_idname = "fluidscene.add_locrot_keyframe"
    bl_label = " "
    bl_options = {'UNDO'}
    
    Time = IntProperty(name="Time",subtype='TIME')
    
    def invoke(self,context,event):
        wm = context.window_manager
        obj = bpy.context.active_object
        if obj.animation_data:
            if obj.animation_data.action:
                return wm.invoke_props_dialog(self, width=400)
        else:
            bpy.ops.anim.keyframe_insert_menu(type='BUILTIN_KSI_LocRot', confirm_success=False, always_prompt=False)
            return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label("Animation Length:")
        layout.prop(self,"Time",text="Time (Seconds)")
        
    def execute(self,context):
        obj = bpy.context.active_object
        Frames = self.Time*24
        OriginalLoc = (obj.location.x,obj.location.y,obj.location.z)
        OriginalRot = (obj.rotation_euler.x,obj.rotation_euler.y,obj.rotation_euler.z)
        
        bpy.context.scene.frame_set(frame = Frames)
        
        obj.location = OriginalLoc
        obj.rotation_euler = OriginalRot
        
        bpy.ops.anim.keyframe_insert(type='BUILTIN_KSI_LocRot', confirm_success=False)
        
        return{'FINISHED'}
        
class OPS_camera_walkthrough(Operator):
    bl_idname = "fluidscene.camera_walkthrough"
    bl_label = "Camera Walkthrough"
    bl_options = {'UNDO'}

    def execute(self, context):
        bpy.context.scene.frame_set(frame=1)
        cam = 'None'

        for camera in bpy.data.objects:
            if camera.type == 'CAMERA':
                cam = bpy.context.scene.camera
                bpy.context.object.data.draw_size = 6

        else:
            bpy.ops.object.camera_add(view_align=True)
            bpy.context.object.data.draw_size = 6

            cam = bpy.context.scene.camera

        for obj in bpy.data.objects:
            if obj.type == 'EMPTY':
 
                loc = obj.location
                rot_x = (obj.rotation_euler.x) 
                rot_y = (obj.rotation_euler.y)
                rot_z = (obj.rotation_euler.z) 

                cam.location = loc
                cam.rotation_euler.x = rot_x + 3.14
                cam.rotation_euler.y = rot_y 
                cam.rotation_euler.z = rot_z

                bpy.ops.anim.keyframe_insert_menu(type='BUILTIN_KSI_LocRot', confirm_success=False, always_prompt=False)
                bpy.context.scene.frame_set(bpy.context.scene.frame_current +50)

        return {'FINISHED'} 

class OPS_add_camera_keyframe(Operator):
    bl_idname = "fluidscene.add_camera_keyframe"
    bl_label = "Add Camera Keyframe"
    bl_options = {'UNDO'}

    def execute(self, context):
        bpy.ops.object.empty_add(type='SINGLE_ARROW', view_align=True, rotation=(1.570796, 3.141593, 1.570796))
        bpy.ops.view3d.viewnumpad(type='TOP')
        bpy.context.object.empty_draw_size = 15
        return {'FINISHED'}        
    
class OPS_create_thumbnail(Operator):
    bl_idname = "fd_scene.create_thumbnail"
    bl_label = "Create Thumbnail"
    bl_options = {'UNDO'}
    
    THUMB_RENDER_RES_X = 1080
    THUMB_RENDER_RES_Y = 1080
    THUMB_RENDER_SAMPLES = 200
    THUMB_CAM_X_ROT = 1.047198
    THUMB_CAM_Y_ROT = 1.047198
    THUMB_SUN_ROT = .785398
    
    @classmethod
    def poll(cls, context):
        if bpy.data.is_saved == True:
            return True
        else:
            return False
            
    def execute(self, context):
        Scene = bpy.data.scenes["Scene"]
        SelObjs = []
        Objects = bpy.context.selected_objects
        Filepath = bpy.data.filepath
        ImageFilePath = Filepath[:-6]
        
        for obj in Objects:
            SelObjs.append(obj)  
            
        if bpy.context.scene.camera == None:
            bpy.ops.object.camera_add(view_align=False)
        bpy.ops.view3d.camera_to_view()
        bpy.data.cameras[0].clip_end = 9999
          
        Cam = bpy.data.scenes["Scene"].camera  
        Cam.rotation_euler = (self.THUMB_CAM_X_ROT, 0.0, self.THUMB_CAM_Y_ROT)   
        
        for obj in SelObjs:
            obj.select=True
        
        bpy.ops.view3d.camera_to_view_selected()  
        
        bpy.ops.object.lamp_add(type='SUN')    
        obj_Sun = bpy.context.object
        obj_Sun.select = False 
        obj_Sun.rotation_euler = (self.THUMB_SUN_ROT, self.THUMB_SUN_ROT, 0.0)  
        
        Scene.cycles.film_transparent = True
        Scene.render.resolution_x = self.THUMB_RENDER_RES_X
        Scene.render.resolution_y = self.THUMB_RENDER_RES_Y
        Scene.cycles.samples = self.THUMB_RENDER_SAMPLES
        Scene.render.display_mode = 'WINDOW'
        Scene.render.filepath = ImageFilePath
        
        bpy.ops.render.render('INVOKE_AREA', write_still=True)
            
        return {'FINISHED'}    

#------REGISTER
classes = [
           OPS_create_scene,
           OPS_render_scene,
           OPS_render_settings,
           OPS_render_preview,
           OPS_create_thumbnail
           ]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
