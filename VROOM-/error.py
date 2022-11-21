
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

import globals
import pygame

class errOut:
    lineNo = 0
    def __init__(self, ptsize=18):
        self.font = pygame.font.Font("freesansbold.ttf", ptsize)
    def write(self, x):
        """if not globals.screen:
            globals.screen = pygame.display.set_mode((640,480))
            pygame.display.set_caption(globals.gameTitle)
        if self.lineNo == 0:
            globals.screen.fill((0,0,0))
        strings=x.split("\n")
        for s in strings:
            ren = self.font.render(s, 1, (255,255,255))
            globals.screen.blit(ren, (5, 15*self.lineNo))
            self.lineNo+=1"""
        print(x, end='')

class vroomException(Exception):
    def __init__(self, msg):
        self.str = msg
    def __str__(self):
        return self.str
