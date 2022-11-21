
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
from math import sin, cos, sqrt, asin, pi
import jvec
import pygame
import sys
from jSVG import getShapesFromSVG, walls
import globals

FPS=60

def rotate(p, angle):
    ret = [0, 0]
    cosang = cos(angle)
    sinang = sin(angle)
    ret[0] +=  cosang*p[0]
    ret[0] += -sinang*p[1]
    ret[1] +=  sinang*p[0]
    ret[1] +=  cosang*p[1]
    return ret

def rotateObject(a, obj):
    for i in range(len(obj)):
        obj[i] = rotate(obj[i], a)
    return obj

def rotateObjectVec(pos, obj):
    x,y = pos
    h = sqrt(x*x + y*y) 
    if h==0:
        return obj
    cosang = y/h
    sinang = x/h
    for i in range(len(obj)):
        obj[i] = (cosang*obj[i][0]-sinang*obj[i][1], sinang*obj[i][0]+cosang*obj[i][1])
    return obj

def translateObject(pos, obj):
    for i in range(len(obj)):
        obj[i] = (obj[i][0]-pos[0], obj[i][1]-pos[1])
    return obj


#class initialize:
#   pygame.init()

class nobackground:
    def __init__(self):
        pass
    def draw(self):
        pass
    def erase(self):
        pass
    def update(self):
        pass
    def cycle(self):
        pass
    def next(self):
        pass
    def previous(self):
        pass
    def cache(self):
        pass

angle = 0
class background:
    def __init__(self, tracks, screen):
        # self.angle=0
        self.screen=screen
        self.tracks=["tracks/"+x+"_gfx.svg" for x in tracks]
        (self.objects, dir, pos) = getShapesFromSVG(self.tracks[0], 0)  
        (self.nextobjects, dir, pos) = getShapesFromSVG(self.tracks[1], 0)  
        (self.prevobjects, dir, pos) = getShapesFromSVG(self.tracks[-1], 0) 
        self.pos = self.center(self.objects)
        self.nextpos = self.center(self.nextobjects)
        self.prevpos = self.center(self.prevobjects)
        self.update()

    def center(self, objects):
        minx, miny = 99999, 99999
        maxx, maxy = 0, 0
        sumx, sumy, count = 0,0,0
        for obj in objects:
            for pt in obj.seq:
                count+=1
                sumx += pt[0]
                sumy += pt[1]
                if pt[0] < minx:
                    minx=pt[0]
                if pt[0] > maxx:
                    maxx=pt[0]
                if pt[1] < miny:
                    miny=pt[1]
                if pt[1] > maxy:
                    maxy=pt[1]
        div = (maxx-minx + maxy-miny) * 0.75
        # scale = 1.2*(self.screen.get_width()-20)/div
        scale = 1.2*(self.screen.get_height()-20)/div
        for obj in objects:
            for i in range(len(obj.seq)):
                obj.seq[i] = jvec.scale(scale, jvec.add(obj.seq[i], (-minx, -miny)))
        return (scale*(sumx/count-minx), scale*(sumy/count-miny))
    
    def draw(self):
        for shape in self.world:
            pygame.draw.aalines(self.screen, globals.midCol, 0, shape, 3)
            # pygame.draw.aalines(self.screen, globals.midCol, 0, shape, 2)

    def cycle(self):
        self.erase()
        self.update()
        self.draw()

    def newScreen(self):
        globals.screen.fill(globals.backCol)

    def next(self):
        globals.tree = None
        self.prevobjects=self.objects
        self.objects=self.nextobjects
        self.nextobjects=None
        self.prevpos=self.pos
        self.pos=self.nextpos
        self.tracks.append(self.tracks.pop(0))

    def previous(self):
        globals.tree = None
        self.nextobjects=self.objects
        self.objects=self.prevobjects
        self.prevobjects=None
        self.nextpos=self.pos
        self.pos=self.prevpos
        self.tracks.insert(0,self.tracks.pop())

    def cache(self):
        if self.nextobjects==None:
            (self.nextobjects, dir, pos) = getShapesFromSVG(self.tracks[1], 0)  
            self.nextpos = self.center(self.nextobjects)
        if self.prevobjects==None:
            (self.prevobjects, dir, pos) = getShapesFromSVG(self.tracks[-1], 0) 
            self.prevpos = self.center(self.prevobjects)

    def update(self):
        global angle
        ORIGINX = self.screen.get_width()/2
        ORIGINY = self.screen.get_height()/2
        self.world=[]
        # self.angle += 0.0075
        angle += 0.0075
        for obj in self.objects:
            newShape = list(obj.seq)
            translateObject(self.pos, newShape)
            # rotateObject(self.angle, newShape)
            rotateObject(angle, newShape)
            for x in range(len(newShape)):
                newShape[x]=(newShape[x][0]+ORIGINX, newShape[x][1]+ORIGINY)
            self.world.append(newShape)

    def erase(self):
        for shape in self.world:
            pygame.draw.aalines(self.screen, globals.backCol, 0, shape, 0)

def main():
    pygame.event.clear([KEYDOWN])
    pygame.display.set_caption("Maximum Oversteer")
    pygame.mouse.set_visible(0)
    screen = pygame.display.set_mode((globals.XSIZE, globals.YSIZE))
    globals.screen = screen
    # Move origin to center of screen
    ORIGINX = screen.get_width()/2
    ORIGINY = screen.get_height()/2

    tracks = [ \
        ["runningManGfx",  "runningManBsp"],
        ["curvy", "curvyBsp"],
        ["starGfx", "starBsp"],
        ["geometric", "geometricBsp"] \
    ]
    tidx = 1

    # backgrnd = background("tracks/"+tracks[tidx][0]+".svg", screen)
    backgrnd = background("tracks/runningManGfx.svg", screen)
    gameClock = pygame.time.Clock()

    while 1:
        backgrnd.draw()
        gameClock.tick(FPS)
        pygame.display.flip()
        backgrnd.erase()
        backgrnd.update()

if __name__ == "__main__":
    main()

# vim:ts=4:sw=4
