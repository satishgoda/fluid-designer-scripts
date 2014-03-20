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

import bpy, bmesh
from bpy_extras import view3d_utils, object_utils

reg_key = r"Software\Microvellum\Fluid Designer\R2.7\Fluid Designer"

def select_cursor_object(context, event, ray_max=10000.0):
    """ This is a function that can be run from a modal operator
        to select the 3D object the mouse is hovered over.
    """
    # get the context arguments
    scene = context.scene
    region = context.region
    rv3d = context.region_data
    coord = event.mouse_region_x, event.mouse_region_y
    bpy.ops.object.select_all(action='DESELECT')
    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
    ray_target = ray_origin + (view_vector * ray_max)

    def visible_objects_and_duplis():
        """Loop over (object, matrix) pairs (mesh only)"""

        for obj in context.visible_objects:
            if obj.type == 'MESH':
                if obj.mv.type != 'BPPRODUCT' or obj.mv.type != 'BPPINSERT' or obj.mv.type != 'BPPART' or obj.mv.type != 'BPWALL' or obj.mv.type != 'BPPLANE':
                    yield (obj, obj.matrix_world.copy())

            if obj.dupli_type != 'NONE':
                obj.dupli_list_create(scene)
                for dob in obj.dupli_list:
                    obj_dupli = dob.object
                    if obj_dupli.type == 'MESH':
                        yield (obj_dupli, dob.matrix.copy())

            obj.dupli_list_clear()

    def obj_ray_cast(obj, matrix):
        """Wrapper for ray casting that moves the ray into object space"""
        
        try:
            # get the ray relative to the object
            matrix_inv = matrix.inverted()
            ray_origin_obj = matrix_inv * ray_origin
            ray_target_obj = matrix_inv * ray_target
    
            # cast the ray
            if obj.mv.type != 'BPPRODUCT' or obj.mv.type != 'BPPINSERT' or obj.mv.type != 'BPPART' or obj.mv.type != 'BPWALL' or obj.mv.type != 'BPPLANE':
                hit, normal, face_index = obj.ray_cast(ray_origin_obj, ray_target_obj)
    
            if face_index != -1:
                return hit, normal, face_index
            else:
                return None, None, None
        finally:
            pass

    # cast rays and find the closest object
    best_length_squared = ray_max * ray_max
    best_obj = None

    for obj, matrix in visible_objects_and_duplis():
        if obj.type == 'MESH':
            if len(obj.data.vertices) >= 4:
                if obj.mv.type != 'BPPRODUCT' or obj.mv.type != 'BPPINSERT' or obj.mv.type != 'BPPART' or obj.mv.type != 'BPWALL' or obj.mv.type != 'BPPLANE':
                    hit, normal, face_index = obj_ray_cast(obj, matrix)
                    if hit is not None:
                        hit_world = matrix * hit
                        length_squared = (hit_world - ray_origin).length_squared
                        if length_squared < best_length_squared:
                            best_length_squared = length_squared
                            best_obj = obj

    # now we have the object under the mouse cursor,
    # we could do lots of stuff but for the example just select.
    if best_obj is not None:
        best_obj.select = True
        context.scene.objects.active = best_obj
    else:
        context.scene.objects.active = None

def get_library_data_path():
    """ This will return the path to the data
        that is stored in the registry
    """
    import winreg
    hkey_user = winreg.ConnectRegistry(None,winreg.HKEY_CURRENT_USER)
    app_settings = winreg.OpenKey(hkey_user, reg_key + "\ApplicationSettings")
    last_config = winreg.QueryValueEx(app_settings, "LastConfig")
    print(last_config,'LASTCONG')
    main_key = winreg.OpenKey(hkey_user, reg_key + "\\Configurations\\" + last_config[0])
    data_path = winreg.QueryValueEx(main_key, "PathToMicrovellumData")
    return data_path[0]

def create_bp_mesh(obj_type):
    """ This function creates and returns 
        a mesh object that has one vertex.
        These are used for the Base Point of groups.
        arg1: Type of base point to create
    """
    verts = [(0, 0, 0)]
    mesh = bpy.data.meshes.new("Base Point")
    bm = bmesh.new()
    for v_co in verts:
        bm.verts.new(v_co)
    bm.to_mesh(mesh)
    mesh.update()
    obj_base = object_utils.object_data_add(bpy.context,mesh)
    obj = obj_base.object
    obj.mv.type = obj_type
    obj.mv.name_object = 'Base Point'
    return obj

def create_vp_empty(grp_type,obj_type):
    """ This function creates and returns 
        an object to be used as a visible prompt.
        These are used for the Base Point of groups.
        arg1: Type of group it is assigned to {'PRODUCT','INSERT','PART','WALL'}
        arg2: Type VP to create: {'VPDIMX','VPDIMY','VPDIMZ'}
    """
    bpy.ops.object.empty_add()
    bpy.context.active_object.location = (0,0,0)
    
    obj = bpy.context.active_object
    obj.mv.type = obj_type
    obj_name = ""
    if obj_type == 'VPDIMX':
        obj.lock_location[1] = True
        obj.lock_location[2] = True
        obj_name = 'X Dim'
        
    if obj_type == 'VPDIMY':
        obj.lock_location[0] = True
        obj.lock_location[2] = True
        obj_name = 'Y Dim'
        
    if obj_type == 'VPDIMZ':
        obj.lock_location[0] = True
        obj.lock_location[1] = True
        obj_name = 'Z Dim'
        
    if grp_type == 'PRODUCT':
        obj.empty_draw_type = 'CUBE'
        obj.empty_draw_size = 1
        obj.mv.name_object = "Product " + obj_name
        
    if grp_type == 'INSERT':
        obj.empty_draw_type = 'SPHERE'
        obj.empty_draw_size = .5
        obj.mv.name_object = "Insert " + obj_name
        
    if grp_type == 'PART':
        obj.empty_draw_type = 'PLAIN_AXES'
        obj.empty_draw_size = 1
        obj.mv.name_object = "Part " + obj_name
        
    if grp_type == 'WALL':
        obj.empty_draw_type = 'CUBE'
        obj.empty_draw_size = 6.0
        obj.mv.name_object = "Wall " + obj_name

    return obj

def create_object_from_verts_and_faces(verts,faces,name):
    """ Creates an object from Verties and Faces
        arg1: Verts List of tuples [(float,float,float)]
        arg2: Faces List of ints
    """
    mesh = bpy.data.meshes.new(name)
    
    bm = bmesh.new()

    for v_co in verts:
        bm.verts.new(v_co)
    
    for f_idx in faces:
        bm.faces.new([bm.verts[i] for i in f_idx])
    
    bm.to_mesh(mesh)
    
    mesh.update()
    
    obj_new = bpy.data.objects.new(mesh.name, mesh)
    
    bpy.context.scene.objects.link(obj_new)
    return obj_new

def create_floor_mesh(name,size):
    
    verts = [(0.0, 0.0, 0.0),
             (0.0, size[1], 0.0),
             (size[0], size[1], 0.0),
             (size[0], 0.0, 0.0),
            ]

    faces = [(0, 1, 2, 3),
            ]

    return create_object_from_verts_and_faces(verts,faces,name)

def create_wall_mesh(name,size):
    
    verts = [(0.0, 0.0, 0.0),
             (0.0, 0.0, size[2]),
             (size[0], 0.0, size[2]),
             (size[0], 0.0, 0.0),
            ]

    faces = [(0, 1, 2, 3),
            ]

    return create_object_from_verts_and_faces(verts,faces,name)
    
def create_cube_mesh(name,size):
    
    verts = [(0.0, 0.0, 0.0),
             (0.0, size[1], 0.0),
             (size[0], size[1], 0.0),
             (size[0], 0.0, 0.0),
             (0.0, 0.0, size[2]),
             (0.0, size[1], size[2]),
             (size[0], size[1], size[2]),
             (size[0], 0.0, size[2]),
             ]

    faces = [(0, 1, 2, 3),
             (4, 7, 6, 5),
             (0, 4, 5, 1),
             (1, 5, 6, 2),
             (2, 6, 7, 3),
             (4, 0, 3, 7),
            ]
    
    return create_object_from_verts_and_faces(verts,faces,name)

def create_countertop_mesh(name,size):
    
    verts = [(0.0, 0.0, 0.0),
             (0.0, size[1], 0.0),
             (size[0], size[1], 0.0),
             (size[0], 0.0, 0.0),
            ]

    faces = [(0, 1, 2, 3),
            ]

    return create_object_from_verts_and_faces(verts,faces,name)

def create_corner_countertop_mesh(name,size):
    print(size)
    
    verts = [(0.0, 0.0, 0.0),
             (0.0, size[1], 0.0),
             (size[2], size[1], 0.0),
             (size[2], -(size[3]), 0.0),
             (size[0], -(size[3]), 0.0),
             (size[0], 0.0, 0.0)
            ]

    faces = [(0, 1, 2, 3, 4, 5),
            ]

    return create_object_from_verts_and_faces(verts,faces,name)
    
def create_wall_group(size):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.group.create(name="Wall")
    grp = bpy.data.groups["Wall"]
    grp.mv.type = 'WALL'
    grp.mv.name_group = 'Wall'

    obj_parent = create_bp_mesh('BPWALL')
    bpy.ops.object.group_link(group=grp.name)

    obj_x = create_vp_empty('WALL','VPDIMX')
    obj_x.mv.name = obj_x.name
    obj_x.parent = obj_parent
    bpy.ops.object.group_link(group=grp.name)

    obj_y = create_vp_empty('WALL','VPDIMY')
    obj_y.mv.name = obj_y.name
    obj_y.parent = obj_parent
    bpy.ops.object.group_link(group=grp.name)

    obj_z = create_vp_empty('WALL','VPDIMZ')
    obj_z.mv.name = obj_z.name
    obj_z.parent = obj_parent
    bpy.ops.object.group_link(group=grp.name)

    obj_wall = create_cube_mesh(grp.mv.name_group,size)
    obj_wall.mv.name_object = "Wall"
    obj_wall.parent = obj_parent
    obj_wall.location = (0,0,0)
    bpy.context.scene.objects.active = obj_wall
    bpy.ops.object.group_link(group=grp.name)
    
    obj_x.location.x = size[0]
    obj_y.location.y = size[1]
    obj_z.location.z = size[2]
    
    create_vertex_group_for_hooks(obj_wall,[2,3,6,7],'X Dimension')
    create_vertex_group_for_hooks(obj_wall,[1,2,5,6],'Y Dimension')
    create_vertex_group_for_hooks(obj_wall,[4,5,6,7],'Z Dimension')
    hook_vertex_group_to_object(obj_wall,'X Dimension',obj_x)
    hook_vertex_group_to_object(obj_wall,'Y Dimension',obj_y)
    hook_vertex_group_to_object(obj_wall,'Z Dimension',obj_z)
    
    #HACK: This is a test to try to resolve blenders crashing problem
    obj_parent.location = (0,0,0)
    obj_parent.rotation_euler = (0,0,0)
    return grp
    
def create_group(type,size=(10,10,10)):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.group.create(name=type)
    grp = bpy.data.groups[type]
    grp.mv.type = type
    grp.mv.name_group = 'NEW ' + type
    
    if type == 'PART':
        obj_parent = create_bp_mesh('BPPART')
        bpy.ops.object.group_link(group=grp.name)
    if type == 'INSERT':
        obj_parent = create_bp_mesh('BPINSERT')
        bpy.ops.object.group_link(group=grp.name)
    if type == 'PRODUCT':
        obj_parent = create_bp_mesh('BPPRODUCT')
        bpy.ops.object.group_link(group=grp.name)
        
    obj_x = create_vp_empty(type,'VPDIMX')
    obj_x.mv.name = obj_x.name
    obj_x.parent = obj_parent
    bpy.ops.object.group_link(group=grp.name)

    obj_y = create_vp_empty(type,'VPDIMY')
    obj_y.mv.name = obj_y.name
    obj_y.parent = obj_parent
    bpy.ops.object.group_link(group=grp.name)

    obj_z = create_vp_empty(type,'VPDIMZ')
    obj_z.mv.name = obj_z.name
    obj_z.parent = obj_parent
    bpy.ops.object.group_link(group=grp.name)
    
    obj_x.location.x = size[0]
    obj_y.location.y = size[1]
    obj_z.location.z = size[2]
    
    #HACK: This is a test to try to resolve blenders crashing problem
    obj_parent.location = (0,0,0)
    obj_parent.rotation_euler = (0,0,0)
    return grp
    
def create_vertex_group_for_hooks(obj_mesh,vert_list,vgroupname):
    """ Adds a new vertex group to a mesh. if the group already exists
        Then no group is added. The second parameter allows you to assign
        verts to the vertex group.
        Arg1: bpy.data.Object | Mesh Object to operate on
        Arg2: [] of int | vertext indexs to assign to group
        Arg3: string | vertex group name
    
    """
    if vgroupname not in obj_mesh.vertex_groups:
        obj_mesh.vertex_groups.new(name=vgroupname)
        
    vgroup = obj_mesh.vertex_groups[vgroupname]
    vgroup.add(vert_list,1,'ADD')
    
def apply_hook_modifiers(obj):
    obj.hide = False
    obj.select = True
    bpy.context.scene.objects.active = obj
    for mod in obj.modifiers:
        if mod.type == 'HOOK':
            bpy.ops.object.modifier_apply(modifier=mod.name)
    
def hook_vertex_group_to_object(obj_mesh,vertex_group,obj_hook):
    bpy.ops.object.select_all(action = 'DESELECT')
    obj_hook.hide = False
    obj_hook.hide_select = False
    obj_hook.select = True
    obj_mesh.hide = False
    obj_mesh.hide_select = False

    if vertex_group in obj_mesh.vertex_groups:
        vgroup = obj_mesh.vertex_groups[vertex_group]
        obj_mesh.vertex_groups.active_index = vgroup.index

        bpy.context.scene.objects.active = obj_mesh
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.vertex_group_select()
        if obj_mesh.data.total_vert_sel > 0:
            bpy.ops.object.hook_add_selob()
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.editmode_toggle()
    
def delete_obj_list(obj_list):
    bpy.ops.object.select_all(action='DESELECT')
    
    for obj in obj_list:
        obj.hide_select = False
        obj.hide = False
        obj.select = True

    bpy.ops.group.objects_remove()
    bpy.ops.object.delete(use_global=True)
    
    # TODO: MAKE SURE THIS IS THIS CORRECT. I HAVE HAD PROBLEMS WITH THIS CRASHING BLENDER
    for obj in obj_list:
        obj.user_clear()
        bpy.data.objects.remove(obj)

def connect_objects_location(anchor_obj,obj):
    constraint = obj.constraints.new('COPY_LOCATION')
    constraint.target = anchor_obj
    constraint.use_x = True
    constraint.use_y = True
    constraint.use_z = True

def get_driver(obj,data_path,array_index):
    if obj.animation_data:
        for DR in obj.animation_data.drivers:
            if DR.data_path == data_path and DR.array_index == array_index:
                return DR

def draw_driver_expression(layout,driver):
    row = layout.row(align=True)
    if driver.driver.is_valid:
        row.prop(driver.driver,'show_debug_info',text="",icon='OOPS')
        row.prop(driver.driver,"expression",text="",expand=True,icon='FILE_TICK')
        if driver.mute:
            row.prop(driver,"mute",text="",icon='OUTLINER_DATA_SPEAKER')
        else:
            row.prop(driver,"mute",text="",icon='OUTLINER_OB_SPEAKER')
    else:
        row.prop(driver.driver,"expression",text="",expand=True,icon='ERROR')
        if driver.mute:
            row.prop(driver,"mute",text="",icon='OUTLINER_DATA_SPEAKER')
        else:
            row.prop(driver,"mute",text="",icon='OUTLINER_OB_SPEAKER')

def draw_driver_variables(layout,driver,object_name):
    for var in driver.driver.variables:
        col = layout.column()
        boxvar = col.box()
        row = boxvar.row(align=True)
        row.prop(var,"name",text="",icon='FORWARD')
        
        props = row.operator("fd_driver.remove_variable",text="",icon='X',emboss=False)
        props.object_name = object_name
        props.data_path = driver.data_path
        props.array_index = driver.array_index
        props.var_name = var.name
        for target in var.targets:
            if driver.driver.show_debug_info:
                row = boxvar.row()
                row.prop(var,"type",text="")
                row = boxvar.row()
                row.prop(target,"id",text="")
                row = boxvar.row(align=True)
                props = row.operator("fd_driver.add_data_path_to_variable",text="",icon='WORDWRAP_ON')
                props.object_name = object_name
                props.data_path = driver.data_path
                props.array_index = driver.array_index
                props.variable_name = var.name
                row.prop(target,"data_path",text="",icon='ANIM_DATA')
                
            if id:
                value = eval('bpy.data.objects["' + target.id.name + '"]'"." + target.data_path)
            else:
                value = "ERROR#"
            
            row = boxvar.row()
            row.label("     ")
            row.label("Value: " + str(value))
            row.label("     ")

def check_for_group_height_collision(grp1,grp2):
    if grp1 and grp2:

        if grp1.mv.get_z().location.z < 0:
            grp1_z_1 = grp1.mv.get_z().matrix_world[2][3]
            grp1_z_2 = grp1.mv.get_bp().matrix_world[2][3]
        else:
            grp1_z_1 = grp1.mv.get_bp().matrix_world[2][3]
            grp1_z_2 = grp1.mv.get_z().matrix_world[2][3]
        
        if grp2.mv.get_z().location.z < 0:
            grp2_z_1 = grp2.mv.get_z().matrix_world[2][3]
            grp2_z_2 = grp2.mv.get_bp().matrix_world[2][3]
        else:
            grp2_z_1 = grp2.mv.get_bp().matrix_world[2][3]
            grp2_z_2 = grp2.mv.get_z().matrix_world[2][3]
    
        if grp1_z_1 >= grp2_z_1 and grp1_z_1 <= grp2_z_2:
            return True
            
        if grp1_z_2 >= grp2_z_1 and grp1_z_2 <= grp2_z_2:
            return True

def make_group_from_base_point(obj,self):
    bpy.ops.object.select_all(action='DESELECT')
    group_name = obj.mv.name_object + "temp"
    bpy.ops.group.create(name=obj.mv.name_object + "temp")
    grp = bpy.data.groups[obj.mv.name_object + "temp"]
    bpy.context.scene.objects.active = obj
    obj.select = True
    bpy.ops.object.group_link(group=group_name)
    assign_child_objects_to_groups(obj,group_name)
    
    if obj.mv.type == 'BPPART':
        dm = bpy.context.scene.mv.dm
        grp.mv.type = 'PART'
        if obj.parent:
            if obj.parent.mv.type == 'BPPRODUCT':
                dm.add_grp_to_product(grp,self)
            else:
                dm.add_part_to_insert(grp,self)
        
    if obj.mv.type == 'BPINSERT':
        dm = bpy.context.scene.mv.dm
        grp.mv.type = 'INSERT'
        dm.add_grp_to_product(grp,self)
        
    return grp

def assign_child_objects_to_groups(obj,group_name):
    for child in obj.children:
        child.hide = False
        child.select = True
        bpy.context.scene.objects.active = child
        bpy.ops.object.group_link(group=group_name)
        if child.mv.type == 'BPPART':
            assign_child_objects_to_groups(child,group_name)

def get_product_list_from_selected(list_obj):
    """ Returns a list of products based on the selected
        objects. This will not return duplicate products.
    """
    dm = bpy.context.scene.mv.dm
    product_list = []
    for obj in list_obj:
        product = dm.get_product_group(obj)
        if product:
            if product not in product_list:
                product_list.append(product)
    return product_list
        
        
























