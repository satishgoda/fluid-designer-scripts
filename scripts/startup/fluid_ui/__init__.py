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
from fd_datablocks import const
import fd_utils
from bpy.app.handlers import persistent
import os
import math

@persistent
def set_default_user_prefs(scene):
    bpy.context.user_preferences.system.use_scripts_auto_execute = True

@persistent
def load_pyfunctions(scene):
    if 'IF' not in bpy.app.driver_namespace: # I cannot find a better way to load custom functions
        from . import driver_functions
        driver_functions.register()
        
@persistent
def load_libraries(scene):
    dm = bpy.context.scene.mv.dm
    default_path = dm.Libraries.path
    if os.path.exists(default_path):
        dm.Libraries.path = default_path #FORCE EVENT TO REBUILD LIBRARIES
        if os.path.exists(os.path.join(dm.Libraries.path,const.filename_specgroup)):
            dm.Specgroups.rebuild_specgroups_from_xml()
    else:
        path = fd_utils.get_library_data_path()
        if os.path.exists(path):
            dm.Libraries.path = path #FORCE EVENT TO REBUILD LIBRARIES
            if os.path.exists(os.path.join(dm.Libraries.path,const.filename_specgroup)):
                dm.Specgroups.rebuild_specgroups_from_xml()

@persistent   
def fix_texture_paths(scene):
    for image in bpy.data.images:
        print(image.filepath_raw)
        image.filepath_raw = 'C://fluidtextures//' + image.name #TODO: REPLACE THIS WITH USER PREFS PATH
        print("UPDATED:",image.filepath_raw)
            
bpy.app.handlers.load_post.append(set_default_user_prefs)
bpy.app.handlers.load_post.append(load_pyfunctions)
bpy.app.handlers.load_post.append(load_libraries)
bpy.app.handlers.load_post.append(fix_texture_paths)

def register():
    import sys
    
    if os.path.exists(r'C:\Program Files\eclipse\plugins\org.python.pydev_2.8.2.2013090511\pysrc'):
        PYDEV_SOURCE_DIR = r'C:\Program Files\eclipse\plugins\org.python.pydev_2.8.2.2013090511\pysrc'
        #
        if sys.path.count(PYDEV_SOURCE_DIR) < 1:
            sys.path.append(PYDEV_SOURCE_DIR)    
            
    elif os.path.exists(r'C:\Program Files (x86)\eclipse\plugins\org.python.pydev_2.8.2.2013090511\pysrc'):
        PYDEV_SOURCE_DIR = r'C:\Program Files (x86)\eclipse\plugins\org.python.pydev_2.8.2.2013090511\pysrc'
        #
        if sys.path.count(PYDEV_SOURCE_DIR) < 1:
            sys.path.append(PYDEV_SOURCE_DIR)    
    else:
        print("NO DEBUG ATTACHED")
    
    #HARD LOCKED KEYMAPS
#     km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
#     kmi = km.keymap_items.new("fluidgeneral.toggle_editmode", 'F', 'PRESS')
#     
#     from . import driver_functions
    from . import lists
#     from . import menus_fluidlibrary
    from . import menus_right_click
    from . import fd_menus
    from . import space_fluid_file_header
    from . import space_fluid_info_header
    from . import space_fluid_view3d_header
    from . import space_fluid_view3d_properties
    from . import space_fluid_view3d_tools
# 	
#     driver_functions.register()
    lists.register()
#     menus_fluidlibrary.register()
    menus_right_click.register()
    fd_menus.register()
    space_fluid_file_header.register()
    space_fluid_info_header.register()
    space_fluid_view3d_header.register()
    space_fluid_view3d_properties.register()
    space_fluid_view3d_tools.register()

def unregister():
    pass
#     from . import driver_functions
    from . import lists
#     from . import menus_fluidlibrary
    from . import menus_right_click
    from . import fd_menus
    from . import space_fluid_file_header
    from . import space_fluid_info_header
    from . import space_fluid_view3d_header
    from . import space_fluid_view3d_properties
    from . import space_fluid_view3d_tools
# 
#     driver_functions.unregister()
    lists.unregister()
#     menus_fluidlibrary.unregister()
    menus_right_click.unregister()
    fd_menus.unregister()
    space_fluid_file_header.unregister()
    space_fluid_info_header.unregister()
    space_fluid_view3d_header.unregister()
    space_fluid_view3d_properties.unregister()
    space_fluid_view3d_tools.unregister()
    
    