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

import bpy,os

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

import math

#------OPERATORS
def IF(statement,true,false):
    """ Returns true if statement is true Returns false if statement is false:
        statement - conditional statement
        true - value to return if statement is True
        false - value to return if statement is False
    """
    if statement == True:
        return true
    else:
        return false

def EQ1(opening_quantity,start_point,end_point):
    """ Returns equal spacing based on the quantity and start and end point:
        Par1 - opening_quantity - Number of spliters in opening
        Par2 - start_point - Start point to calculate opening size (always smaller number)
        Par3 - end_point - End point to calculate opening size (always larger number)
    """
    opening_size = end_point-start_point
    if opening_quantity == 0:
        return 0
    else:
        mid_point = opening_size/(opening_quantity + 1)
    return mid_point

def CALCULATE_PRICE(ProductNumber):
    if ProductNumber == 0:
        return 100
    if ProductNumber == 1:
        return 150
    if ProductNumber == 2:
        return 175
    return 0
    
def UPDATE():
    """ This is a hack needed to update custom properties like quantity.
        Put this at the start or end of any formula to recal custom properties
        returns 0
    """
    bpy.context.scene.frame_current = bpy.context.scene.frame_current
    return 0

def register():
    bpy.app.driver_namespace["IF"] = IF
    bpy.app.driver_namespace["EQ1"] = EQ1
    bpy.app.driver_namespace["UPDATE"] = UPDATE
    bpy.app.driver_namespace["CALCULATE_PRICE"] = CALCULATE_PRICE

def unregister():
    pass

if __name__ == "__main__":
    register()
