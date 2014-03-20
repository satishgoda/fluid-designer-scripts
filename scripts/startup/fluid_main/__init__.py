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
        image.filepath_raw = 'C://fluidtextures//' + image.name #TODO: REPLACE THIS WITH USER PREFS PATH

bpy.app.handlers.load_post.append(set_default_user_prefs)
bpy.app.handlers.load_post.append(load_pyfunctions)
bpy.app.handlers.load_post.append(load_libraries)
bpy.app.handlers.load_post.append(fix_texture_paths)

def register():
    import sys
    
    if os.path.exists(r'C:\Program Files\eclipse\plugins\org.python.pydev_2.8.2.2013090511\pysrc'):
        PYDEV_SOURCE_DIR = r'C:\Program Files\eclipse\plugins\org.python.pydev_2.8.2.2013090511\pysrc'
        if sys.path.count(PYDEV_SOURCE_DIR) < 1:
            sys.path.append(PYDEV_SOURCE_DIR)    
            
    elif os.path.exists(r'C:\Program Files (x86)\eclipse\plugins\org.python.pydev_2.8.2.2013090511\pysrc'):
        PYDEV_SOURCE_DIR = r'C:\Program Files (x86)\eclipse\plugins\org.python.pydev_2.8.2.2013090511\pysrc'
        if sys.path.count(PYDEV_SOURCE_DIR) < 1:
            sys.path.append(PYDEV_SOURCE_DIR)    
    else:
        print("NO DEBUG ATTACHED")
    
def unregister():
    pass
