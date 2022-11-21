
# VROOM!!! Vector Graphic Gacing
# Copyright 2003-2007 George Gonzalez
#
# This file is part of VROOM!!!
# 
# VROOM!!! is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# VROOM!!! is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with VROOM!!!; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from pygame.locals import *
from jvec import scale, unit, cross, diff, dot, angle
import re
from math import sqrt, acos, pi
import pygame
import copy
import globals
from bmpfont import *

dx = 0
dy = 0

def getShapesFromFig(xyo, divX, divY):
    xo,yo = xyo
    global sc, dx, dy
    file = open("myFont.fig", 'r')  
    line = file.readline()
    shapes = []
    while line[0]!='2':
        line = file.readline()

    while 1:
        line = file.readline()
        shape=[]
        while line and line[0]!='2':
            items = [float(eval(x)) for x in line.split()]
            shape+= list(zip([items[x]/divX-xo for x in range(len(items)) if (x+1)%2],
                [items[x]/divY-yo for x in range(len(items)) if (x)%2]))
            line = file.readline()
        shapes.append(shape)
        if not line:
            break
        
    # Remove zero-length segments
    for shape in shapes:
        i=0
        while i < len(shape)-1:
            if shape[i]==shape[i+1]:
                shape.pop(i)
            else:
                i+=1

    file.close()
    return shapes


def render(fore, back, dim):
    (width, height) = dim
    screen = pygame.Surface((width*10+1, height*10+1))
    screen.fill(back)
    divX = 450/float(width)
    divY = 900/float(height)
    xoffset = float(dim[0]%6)/6.0
    yoffset = float(dim[1]%6)/6.0
    shapes = getShapesFromFig((xoffset, yoffset), divX, divY)
    for i in [1]:
        shapes2 = copy.deepcopy(shapes) 
        for shape in shapes2:
            for x in range(len(shape)):
                shape[x] = scale(i, (shape[x][0]-dx, shape[x][1]-dy))   
        for shape in shapes2:
            if len(shape)>1:
                pygame.draw.aalines(screen, fore, 0, shape, 1)
    return screen


def renderFonts():
    s1 = render(globals.foreCol, globals.backCol, (9,12))
    globals.font12x9 = BmpFont(9, 12, 0xffffff, s1)
    #s1 = render(globals.foreCol, globals.backCol, (6,12))
    #globals.font12x6 = BmpFont(6, 12, 0xffffff, s1)
    #s1 = render(globals.foreCol, globals.backCol, (9,9))
    #globals.font9x9 = BmpFont(9, 9, 0xffffff, s1)
    s1 = render(globals.foreCol, globals.backCol, (6,9))
    globals.font9x6 = BmpFont(6, 9, 0xffffff, s1)
    #s1 = render(globals.foreCol, globals.backCol, (12,15))
    #globals.font15x12 = BmpFont(12, 15, 0xffffff, s1)
    #s1 = render(globals.foreCol, globals.backCol, (12,12))
    #globals.font12x12 = BmpFont(12, 12, 0xffffff, s1)
    s1 = render(globals.foreCol, globals.backCol, (12,21))
    globals.font21x12 = BmpFont(12, 21, 0xffffff, s1)
    #s1 = render(globals.foreCol, globals.backCol, (15,18))
    #globals.font15x18 = BmpFont(15, 18, 0xffffff, s1)
    #s1 = render(globals.foreCol, globals.backCol, (18,18))
    #globals.font18x18 = BmpFont(18, 18, 0xffffff, s1)

if __name__ == "__main__":
    render((0,0,0), (255,255,20))
