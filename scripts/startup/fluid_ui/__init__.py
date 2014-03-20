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

def register():
    from . import lists
    from . import menus
    from . import space_fluid_file_header
    from . import space_fluid_info_header
    from . import space_fluid_view3d_header
    from . import space_fluid_view3d_properties
    from . import space_fluid_view3d_tools

    lists.register()
    menus.register()
    space_fluid_file_header.register()
    space_fluid_info_header.register()
    space_fluid_view3d_header.register()
    space_fluid_view3d_properties.register()
    space_fluid_view3d_tools.register()

def unregister():

    from . import lists
    from . import menus
    from . import space_fluid_file_header
    from . import space_fluid_info_header
    from . import space_fluid_view3d_header
    from . import space_fluid_view3d_properties
    from . import space_fluid_view3d_tools

    lists.unregister()
    menus.unregister()
    space_fluid_file_header.unregister()
    space_fluid_info_header.unregister()
    space_fluid_view3d_header.unregister()
    space_fluid_view3d_properties.unregister()
    space_fluid_view3d_tools.unregister()
