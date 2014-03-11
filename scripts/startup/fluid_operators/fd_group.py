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
                       BoolVectorProperty,
                       PointerProperty,
                       EnumProperty)

import math

import fd_utils

class OPS_rename_group(Operator):
    bl_idname = "fd_group.rename_group"
    bl_label = "Rename Group"
    bl_options = {'UNDO'}
    
    group_name = StringProperty(name="Group Name")
    new_name = StringProperty(name="New Name",default="")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        dm = context.scene.mv.dm
        grp = bpy.data.groups[self.group_name]
        obj_bp = grp.mv.get_bp()
        obj_bp.mv.name_group = self.new_name
        obj_bp.mv.name_object = self.new_name
        grp.mv.name_group = self.new_name
        dm.set_group_name(grp)
        
        for grp_bp in grp.mv.Objects.col_group:
            if grp_bp.name == obj_bp.name:
                dm.set_object_name(obj_bp)
                grp_bp.name = obj_bp.name
                grp.mv.bp_id = obj_bp.name
                
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        grp = bpy.data.groups[self.group_name]
        self.new_name = grp.mv.name_group
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        grp = bpy.data.groups[self.group_name]
        layout.label("ID: " + grp.mv.name)
        layout.prop(self, "new_name")

class OPS_delete_fluid_group(Operator):# IMPLEMENT ALL DELETE FUNCTIONS 
    bl_idname = "fd_group.delete_group"
    bl_label = "Delete Group"
    bl_options = {'UNDO'}
    
    group_name = StringProperty(name="Group Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        dm = context.scene.mv.dm
        grp = bpy.data.groups[self.group_name]
        obj_list = []
        obj_bp = None
        for obj in grp.objects:
            if grp.mv.type == 'INSERT':
                if obj.mv.type == 'BPINSERT':
                    obj_bp = obj
            elif grp.mv.type == 'PART':
                if obj.mv.type == 'BPPART':
                    obj_bp = obj
            obj_list.append(obj)
            
        fd_utils.delete_obj_list(obj_list)
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        grp = bpy.data.groups[self.GroupName]
        layout = self.layout
        layout.label("Group Name: " + grp.mv.name_group)

class OPS_add_empty_product(Operator):
    bl_idname = "fd_group.add_empty_product"
    bl_label = "Empty Product"
    bl_description = "This operator add a new empty product to the scene."
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        wm = context.window_manager
        dm = context.scene.mv.dm
        grp = fd_utils.create_group('PRODUCT',(18,-23,34))
        dm.add_group_to_scene(grp)
        grp.mv.build_cage()
        obj_bp = grp.mv.get_bp()
        obj_bp.select = True
        context.scene.objects.active = obj_bp
        return {'FINISHED'}

class OPS_add_empty_insert(Operator):
    bl_idname = "fd_group.add_empty_insert"
    bl_label = "Empty Insert"
    bl_description = "This operator add a new empty insert to the scene."
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        wm = context.window_manager
        dm = context.scene.mv.dm
        grp = fd_utils.create_group('INSERT',(18,-23,34))
        dm.add_group_to_scene(grp)
        grp.mv.build_cage()
        obj_bp = grp.mv.get_bp()
        obj_bp.select = True
        context.scene.objects.active = obj_bp
        return {'FINISHED'}
    
class OPS_add_empty_part(Operator):
    bl_idname = "fd_group.add_empty_part"
    bl_label = "Empty Part"
    bl_description = "This operator add a new empty part to the scene."
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        dm = context.scene.mv.dm
        grp = fd_utils.create_group('PART',(24,18,.75))
        dm.add_group_to_scene(grp)
        grp.mv.build_cage()
        obj_bp = grp.mv.get_bp()
        obj_bp.select = True
        context.scene.objects.active = obj_bp
        return {'FINISHED'}

class OPS_add_mesh_to_group(Operator):
    bl_idname = "fd_group.add_mesh_to_group"
    bl_label = "Add Mesh To Group"
    bl_options = {'UNDO'}
    
    group_name = StringProperty(name="Group Name")
    use_selected = BoolProperty(name="Use Selected",default=False)
    mesh_name = StringProperty(name="Mesh Name",default="New Mesh")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        dm = context.scene.mv.dm
        grp = bpy.data.groups[self.group_name]
        dim_x = grp.mv.get_x().location.x
        dim_y = grp.mv.get_y().location.y
        dim_z = grp.mv.get_z().location.z
        obj_mesh = None
        obj_bp = grp.mv.get_bp()
        
        if not self.use_selected:
            obj_mesh = fd_utils.create_cube_mesh(self.mesh_name,(dim_x,dim_y,dim_z))
        else:
            for obj in context.selected_objects:
                if len(obj.users_group) == 0:
                    obj_mesh = context.scene.objects.active
                    break
                
        if obj_mesh:
            obj_mesh.mv.name_object = self.mesh_name
            obj_mesh.mv.id_wall = grp.mv.id_wall
            obj_mesh.mv.id_product = grp.mv.id_product
            obj_mesh.mv.id_insert = grp.mv.id_insert
            obj_mesh.mv.id_part = grp.mv.id_part
            context.scene.objects.active = obj_mesh
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.editmode_toggle()
            if obj_bp:
                obj_mesh.parent = obj_bp
                
            grp.mv.add_object_to_group_collection(obj_mesh)
            dm.link_object_with_groups(obj_mesh)
            grp.mv.update_vector_groups()
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "mesh_name")
        layout.prop(self, "use_selected")

class OPS_add_empty_to_group(Operator):
    bl_idname = "fd_group.add_empty_to_group"
    bl_label = "Add Empty To Group"
    bl_options = {'UNDO'}
    
    group_name = StringProperty(name="Group Name")
    use_as_mesh_hook = BoolProperty(name="Use As Mesh Hook",default=False)
    empty_name = StringProperty(name="Empty Name",default="New Empty")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        dm = context.scene.mv.dm
        grp = bpy.data.groups[self.group_name]
        obj_bp = grp.mv.get_bp()
        
        #NOTE: Since Mesh hooks are maintained by object name
        #      You cannot have two emptyhooks with the same name.       
        for child in obj_bp.children:
            if child.type == 'EMPTY' and self.use_as_mesh_hook and child.mv.use_as_mesh_hook and child.mv.name_object == self.empty_name:
                bpy.ops.fd_general.error('INVOKE_DEFAULT',Message="A hook with that name already exists.")
                return {'CANCELLED'}
            
        #NOTE: Since Mesh hooks are maintained by object name
        #      These names are reserved the the visible prompts of the group
        if self.use_as_mesh_hook:
            if self.empty_name == 'Dimension X' or self.empty_name == 'Dimension Y' or self.empty_name == 'Dimension Z':
                bpy.ops.fd_general.error('INVOKE_DEFAULT',Message="That hook name are reserved for visible prompts")
                return {'CANCELLED'}
        
        bpy.ops.object.empty_add()
        obj_empty = context.active_object

        if obj_empty:
            obj_empty.mv.name_object = self.empty_name
            obj_empty.mv.id_wall = grp.mv.id_wall
            obj_empty.mv.id_product = grp.mv.id_product
            obj_empty.mv.id_insert = grp.mv.id_insert
            obj_empty.mv.id_part = grp.mv.id_part
            obj_empty.mv.use_as_mesh_hook = self.use_as_mesh_hook
            if obj_bp:
                obj_empty.parent = obj_bp
            
            context.scene.objects.active = obj_empty
            grp.mv.add_object_to_group_collection(obj_empty)
            dm.link_object_with_groups(obj_empty)
            grp.mv.update_vector_groups()
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "empty_name")
        layout.prop(self, "use_as_mesh_hook")
        
class OPS_add_curve_to_group(Operator):
    bl_idname = "fd_group.add_curve_to_group"
    bl_label = "Add Curve To Group"
    bl_options = {'UNDO'}
    
    group_name = StringProperty(name="Group Name")
    use_selected = BoolProperty(name="Use Selected",default=False)
    mesh_name = StringProperty(name="Mesh Name",default="New Mesh")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        dm = context.scene.mv.dm
        grp = bpy.data.groups[self.group_name]
        dim_x = grp.mv.get_x().location.x
        dim_y = grp.mv.get_y().location.y
        dim_z = grp.mv.get_z().location.z
        obj_mesh = None
        
        if not self.use_selected:
            obj_mesh = fd_utils.create_cube_mesh(self.mesh_name,(dim_x,dim_y,dim_z))
        else:
            for obj in context.selected_objects:
                if len(obj.users_group) == 0:
                    obj_mesh = context.scene.objects.active
                    break
                
        if obj_mesh:
            obj_mesh.mv.name_object = self.mesh_name
            obj_mesh.mv.id_wall = grp.mv.id_wall
            obj_mesh.mv.id_product = grp.mv.id_product
            obj_mesh.mv.id_insert = grp.mv.id_insert
            obj_mesh.mv.id_part = grp.mv.id_part
            context.scene.objects.active = obj_mesh
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.editmode_toggle()
            grp.mv.add_object_to_group_collection(obj_mesh)
            dm.link_object_with_groups(obj_mesh)
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "mesh_name")
        layout.prop(self, "use_selected")
        
class OPS_add_text_to_group(Operator):
    bl_idname = "fd_group.add_text_to_group"
    bl_label = "Add Text To Group"
    bl_options = {'UNDO'}
    
    group_name = StringProperty(name="Group Name")
    use_as_item_number = BoolProperty(name="Use As Item Number",default=False)
    text_name = StringProperty(name="Text Name",default="New Text")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        dm = context.scene.mv.dm
        grp = bpy.data.groups[self.group_name]
        obj_bp = grp.mv.get_bp()

        bpy.ops.object.text_add()
        obj_text = context.active_object

        if obj_text:
            obj_text.mv.name_object = self.text_name
            obj_text.mv.id_wall = grp.mv.id_wall
            obj_text.mv.id_product = grp.mv.id_product
            obj_text.mv.id_insert = grp.mv.id_insert
            obj_text.mv.id_part = grp.mv.id_part
            obj_text.mv.use_as_item_number = self.use_as_item_number
            if obj_bp:
                obj_text.parent = obj_bp
            
            context.scene.objects.active = obj_text
            grp.mv.add_object_to_group_collection(obj_text)
            dm.link_object_with_groups(obj_text)
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "text_name")
        layout.prop(self, "use_as_item_number")

class OPS_zoom_to_group(Operator):
    bl_idname = "fd_group.zoom_to_group"
    bl_label = "Zoom To Group"
    
    group_name = StringProperty(name="GroupName")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        dm = context.scene.mv.dm
        grp = None
        
        if self.group_name in bpy.data.groups:
            grp = bpy.data.groups[self.GroupName]
        else:
            if context.active_object:
                grp = dm.get_product_group(context.active_object)
                
        if grp:
            obj_bp = grp.mv.get_bp()
            obj_x = grp.mv.get_x()
            obj_y = grp.mv.get_y()
            obj_z = grp.mv.get_z()
            bpy.ops.object.select_all(action='DESELECT')
            obj_bp.select = True
            obj_x.select = True
            obj_y.select = True
            obj_z.select = True
            obj_x.hide = False
            obj_y.hide = False
            obj_z.hide = False

        bpy.ops.view3d.view_selected()
        return {'FINISHED'}

class OPS_connect_group_meshes_to_hooks(Operator):
    bl_idname = "fd_group.connect_group_meshes_to_hooks"
    bl_label = "Connect Group Meshes to Hooks"
    bl_options = {'UNDO'}
    
    group_name = StringProperty(name="GroupName")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        grp = bpy.data.groups[self.group_name]
        grp.mv.connect_meshes_to_hooks()
        return {'FINISHED'}
       
class OPS_bump_product_group_left(Operator):
    bl_idname = "fd_group.bump_product_group_left"
    bl_label = "Bump Product Group Left"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        dm = context.scene.mv.dm
        grp = dm.get_product_group(context.active_object)
        return grp

    def execute(self, context):
        dm = context.scene.mv.dm
        grp = dm.get_product_group(context.active_object)
        space = grp.mv.get_available_space('LEFT')
        grp.mv.get_bp().location.x -= space
        return {'FINISHED'}
        
class OPS_bump_product_group_right(Operator):
    bl_idname = "fd_group.bump_product_group_right"
    bl_label = "Bump Product Group Right"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        dm = context.scene.mv.dm
        grp = dm.get_product_group(context.active_object)
        return grp

    def execute(self, context):
        dm = context.scene.mv.dm
        grp = dm.get_product_group(context.active_object)
        space = grp.mv.get_available_space('RIGHT')
        grp.mv.get_bp().location.x += space
        return {'FINISHED'}

class OPS_stretch_product_group_left(Operator):
    bl_idname = "fd_group.stretch_product_group_left"
    bl_label = "Stretch Product Group Left"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        dm = context.scene.mv.dm
        grp = dm.get_product_group(context.active_object)
        return grp

    def execute(self, context):
        dm = context.scene.mv.dm
        grp = dm.get_product_group(context.active_object)
        space = grp.mv.get_available_space('LEFT')
        grp.mv.get_bp().location.x -= space
        if not grp.mv.get_x().lock_location[0]:
            grp.mv.get_x().location.x += space
        return {'FINISHED'}
        
class OPS_stretch_product_group_right(Operator):
    bl_idname = "fd_group.stretch_product_group_right"
    bl_label = "Stretch Product Group Right"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        dm = context.scene.mv.dm
        grp = dm.get_product_group(context.active_object)
        return grp

    def execute(self, context):
        dm = context.scene.mv.dm
        grp = dm.get_product_group(context.active_object)
        space = grp.mv.get_available_space('RIGHT')
        if not grp.mv.get_x().lock_location[0]:
            grp.mv.get_x().location.x += space
        return {'FINISHED'}

class OPS_create_group(Operator):
    bl_idname = "fd_group.create_group"
    bl_label = "Create Group"
    bl_options = {'UNDO'}

    object_name = StringProperty(name="Object Name")
    parent_group = StringProperty(name="Parent Group")

    @classmethod
    def poll(cls, context):
        dm = context.scene.mv.dm
        grp = dm.get_product_group(context.active_object)
        return grp

    def execute(self, context):
        dm = context.scene.mv.dm
        obj = bpy.data.objects[self.object_name]
        grp = bpy.data.groups[self.parent_group]
        for index, group_obj in enumerate(grp.mv.Objects.col_group):
            if obj.name == group_obj.name:
                grp.mv.Objects.col_group.remove(index)
        new_grp = fd_utils.make_group_from_base_point(obj,grp)
        obj_bp = new_grp.mv.get_bp()
        obj_bp.select = True
        context.scene.objects.active = obj_bp
        return {'FINISHED'}

class OPS_reload_collections(Operator):
    bl_idname = "fluidgroup.reload_collections"
    bl_label = "Reload Collections"
    bl_options = {'UNDO'}
    
    GroupName = StringProperty(name="GroupName")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        grp = bpy.data.groups[self.GroupName]
        if grp.mv.Type == 'PRODUCT':
            Product = grp.mv.GetProduct()
            Product.ReloadCollections(grp)
        if grp.mv.Type == 'INSERT':
            Insert = grp.mv.GetInsert()
            Insert.ReloadCollections(grp)
        if grp.mv.Type == 'PART':
            Part = grp.mv.GetPart()
            Part.ReloadCollections(grp)
        return {'FINISHED'}

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label("Do you want to reload the collections?")

        
class OPS_copy_fluid_group(Operator):
    bl_idname = "fluidgroup.copy_fluid_group"
    bl_label = "Copy Fluid Group"
    bl_options = {'UNDO'}
    
    GroupName = StringProperty(name="GroupName")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        grp = bpy.data.groups[self.GroupName]
        FluidGroup = None
        if grp.mv.Type == 'PRODUCT':
            grp = bpy.data.groups[self.GroupName]
            FluidGroup = grp.mv.GetProduct()
        if grp.mv.Type == 'INSERT':
            grp = bpy.data.groups[self.GroupName]
            FluidGroup = grp.mv.GetInsert()
        if grp.mv.Type == 'PART':
            grp = bpy.data.groups[self.GroupName]
            FluidGroup = grp.mv.GetPart()
            
        if FluidGroup:
            FluidGroup.Copy()
            return {'FINISHED'}
        else:
            return {'CANCELLED'}
    
class OPS_prepare_for_library(Operator):
    bl_idname = "fluidgroup.prepare_for_library"
    bl_label = "Prepare for Library"
    bl_options = {'UNDO'}
    
    GroupName = StringProperty(name="GroupName")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        grp = bpy.data.groups[self.GroupName]
        FluidGroup = None
        if grp.mv.Type == 'PRODUCT':
            grp = bpy.data.groups[self.GroupName]
            FluidGroup = grp.mv.GetProduct()
        if grp.mv.Type == 'INSERT':
            grp = bpy.data.groups[self.GroupName]
            FluidGroup = grp.mv.GetInsert()
            
        bpy.ops.fluidgroup.connect_group_meshes_to_hooks(GroupName=FluidGroup.Grp_LinkID)
            
        if grp.mv.Type == 'PRODUCT':
            for Insert in FluidGroup.COL_Insert:
                bpy.ops.fluidgroup.connect_group_meshes_to_hooks(GroupName=Insert.Grp_LinkID)
                for Part in Insert.COL_Part:
                    bpy.ops.fluidgroup.connect_group_meshes_to_hooks(GroupName=Part.Grp_LinkID)
            
        for Part in FluidGroup.COL_Part:
            bpy.ops.fluidgroup.connect_group_meshes_to_hooks(GroupName=Part.Grp_LinkID)

        ###HACK - for some reason connect_group_meshes_to_hooks will mute some
        ###       of the drivers this will unmute every object driver in the scene.
        for obj in bpy.data.objects:
            if obj.animation_data:
                for driver in obj.animation_data.drivers:
                    driver.mute = False
                    driver.driver.expression = driver.driver.expression
            
        return {'FINISHED'}
    
class OPS_equal_widths(Operator):
    bl_idname = "fluidgroup.equal_widths"
    bl_label = "Equal Widths"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if context.active_object:
            dm = context.scene.mv.dm
            grp_product = dm.get_product_group(context.active_object)
            grp_wall = dm.get_wall_group(context.active_object)
            if grp_product and grp_wall:
                return True
            else:
                return False
        else:
            return False

    def execute(self, context):
        dm = context.scene.mv.dm
        selected_objs = bpy.context.selected_objects
        list_bp = []
        
        #get selected BPs and store in list
        for obj in selected_objs:
            grp_product = dm.get_product_group(context.active_object)
            obj_bp = grp_product.mv.get_bp()
            list_bp.append(obj_bp)
        
        #sort selected BPs by X location greatest to smallest 
        list_bp.sort(key=lambda obj: obj.location.x, reverse=True)

        Obj_ProdLeftMostBP = list_bp[-1]
        Obj_ProdRightMostBP = list_bp[0]
        Prod_ProdRightMost = Obj_ProdRightMostBP.mv.GetProduct()
        Obj_ProdRightMostWidth = bpy.data.objects[Prod_ProdRightMost.Obj_XDimLinkID]


        Float_TotalLength = (Obj_ProdRightMostBP.location.x + Obj_ProdRightMostWidth.location.x) - Obj_ProdLeftMostBP.location.x
        Float_NewWidth = (Float_TotalLength)/len(list_bp)

        list_bp.reverse()

        Int_Productcounter = 0
        for index, obj in enumerate(list_bp):
            if index == 0:
                grp_product = dm.get_product_group(obj)
                Obj_ProductWidth = grp_product.mv.get_x()
                Obj_ProductWidth.location.x = Float_NewWidth
                Int_Productcounter += 1
                Float_LeftmostProdLoc = obj.location.x
            else:
                obj.location.x = ((Float_NewWidth) * Int_Productcounter) + Float_LeftmostProdLoc
                grp_product = dm.get_product_group(obj)
                Obj_ProductWidth = bpy.data.objects[Product.Obj_XDimLinkID]
                Obj_ProductWidth.mv.DimX = Float_NewWidth
                Int_Productcounter += 1

        return {'FINISHED'}        
    
class OPS_connect_products(Operator):
    bl_idname = "fluidgroup.connect_products"
    bl_label = "Connect Products"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if context.active_object:
            Product = context.active_object.mv.GetProduct()
            Wall = context.active_object.mv.GetWall()
            if Product and Wall:
                return True
            else:
                return False
        else:
            return False

    def execute(self, context):
        SelectedObjects = bpy.context.selected_objects
        SelectedBP = []

        CornerProduct = False
        
        #get selected BPs and store in list
        for obj in SelectedObjects:
            Product = obj.mv.GetProduct()
            if Product.CategoryType == 'CORNER':
                CornerProduct = True
                Obj_CornerProdYDim = bpy.data.objects[Product.Obj_YDimLinkID]
                
            objBP = bpy.data.objects[Product.Obj_BPLinkID]
            SelectedBP.append(objBP)
        
        #sort selected BPs by X location greatest to smallest 
        SelectedBP.sort(key=lambda obj: obj.location.x, reverse=True)

        #apply constraint
        for index, obj in enumerate(SelectedBP):
            if len(SelectedBP) >= index+2:
                if CornerProduct == True:
                    Obj_ConstraintTarget = Obj_CornerProdYDim
                    print("Obj_ConstraintTarget",Obj_ConstraintTarget)
                else:
                    Obj_TargetBP = SelectedBP[index + 1]
                    Prod_ConstraintTarget = Obj_TargetBP.mv.GetProduct()
                    Obj_ConstraintTarget = bpy.data.objects[Prod_ConstraintTarget.Obj_XDimLinkID]

                CopyLocConstraint = obj.constraints.new('COPY_LOCATION')
                CopyLocConstraint.target = Obj_ConstraintTarget
                CopyLocConstraint.use_x = True
                CopyLocConstraint.use_y = True
                CopyLocConstraint.use_z = True

        return {'FINISHED'}
        
class OPS_center_product_under_active(Operator):
    bl_idname = "fluidgroup.center_product_under_active"
    bl_label = "Center Product Under Active"


    @classmethod
    def poll(cls, context):
        if len(bpy.context.selected_objects) == 2:
            return True
        else:
            return False

    def execute(self,context):   
        for obj in bpy.context.selected_objects:
            if obj == bpy.context.active_object:
                TargetProduct = obj.mv.GetProduct()
            else:
                Product = obj.mv.GetProduct()
            
        Obj_ProductBP = bpy.data.objects[Product.Obj_BPLinkID]
        Obj_ProductWidth = bpy.data.objects[Product.Obj_XDimLinkID]
        Float_CenterOfProduct = (Obj_ProductWidth.location.x)/2
        
        Obj_TargetProductBP = bpy.data.objects[TargetProduct.Obj_BPLinkID]
        Obj_TargetProductWidth = bpy.data.objects[TargetProduct.Obj_XDimLinkID]    
        
        Float_CenterOfTargetProduct = (Obj_TargetProductWidth.location.x)/2
        
        Obj_ProductBP.location.x = (Obj_TargetProductBP.location.x + Float_CenterOfTargetProduct) - Float_CenterOfProduct
      
        return{'FINISHED'}    
    
#------REGISTER
classes = [
           OPS_rename_group,
           OPS_delete_fluid_group,
           OPS_add_empty_product,
           OPS_add_empty_insert,
           OPS_add_empty_part,
           OPS_add_mesh_to_group,
           OPS_add_empty_to_group,
           OPS_add_curve_to_group,
           OPS_add_text_to_group,
           OPS_zoom_to_group,
           OPS_connect_group_meshes_to_hooks,
           OPS_bump_product_group_left,
           OPS_bump_product_group_right,
           OPS_stretch_product_group_left,
           OPS_stretch_product_group_right,
           OPS_create_group
           ]

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
