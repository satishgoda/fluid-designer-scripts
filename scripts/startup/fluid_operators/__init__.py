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

def register():
    from . import fd_dragdrop
    from . import fd_driver
    from . import fd_general
    from . import fd_group
    from . import fd_library
    from . import fd_material
    from . import fd_object
    from . import fd_prompts
    from . import fd_scene
    from . import fd_wall

    fd_dragdrop.register()
    fd_driver.register()
    fd_general.register()
    fd_group.register()
    fd_library.register()
    fd_material.register()
    fd_object.register()
    fd_prompts.register()
    fd_scene.register()
    fd_wall.register()

def unregister():
    from . import fd_dragdrop
    from . import fd_driver
    from . import fd_general
    from . import fd_group
    from . import fd_library
    from . import fd_material
    from . import fd_object
    from . import fd_prompts
    from . import fd_scene
    from . import fd_wall

    fd_dragdrop.unregister()
    fd_driver.unregister()
    fd_general.unregister()
    fd_group.unregister()
    fd_library.unregister()
    fd_material.unregister()
    fd_object.unregister()
    fd_prompts.unregister()
    fd_scene.unregister()
    fd_wall.unregister()