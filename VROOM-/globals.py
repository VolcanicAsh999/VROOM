
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

YSIZE = 480
XSIZE = 640
VMAX = 50.0
kick = 0.1
gameTitle = "VROOM!!!"
version = "1.6"
black = 0
intensity = 255
FPS = 90.0
timeDelta = None
deltaFactor = None
tracks = ["motorhead", "super_slalom", "circles", "crossroads", "chimera", "entanglement", "geometric", "the_running_man", "speedway"]
leafCount = 0
tree = None

def adjustForFrameRate(fps):
	"secs per frame, radians per sec"
	return 1.08*(60.0/fps), 0.02*fps

timeDelta, deltaFactor = adjustForFrameRate(FPS)

cmap = {
	"O-scope 2": ((80,255,120), (40,40,40)),
	"B&W 1": ((255,255,255), (20,20,20)),
 	"B&W 2": ((255,255,255), (40,40,40)),
	"B&W dark": ((255,255,255), (0,0,0)),
	"Radar": ((180,255,180), (20,20,40)),
	"Electric Avenue": ((160,100,255), (25,0,35)),
	"Virtual Boy": ((255,30,30), (30,30,30)),
	"O-scope 1": ((80,255,120), (20,20,20)),
}

backCol3D = (70,90,50)

rendererMap = {}

renderers = [
	"Perspective",
	"Top",
	"3-D Anaglyph"
	]

mvols = ['5','4','3','2','1','0','10','9','8','7','6']

colors = [
	"O-scope 2",
	"B&W 1",
	"B&W 2",
	"B&W dark",
	"Radar",
	"Electric Avenue",
	"Virtual Boy",
	"O-scope 1"]

fullscreen = ["on", "off"]
screen = None

import pygame
from pygame.locals import *

def keyWaitDown():
	pygame.event.clear([KEYDOWN])
	while 1:
		if pygame.event.wait().type in (QUIT, KEYDOWN, MOUSEBUTTONDOWN):
			break

def keyWaitUp():
	pygame.event.clear([KEYUP])
	while 1:
		event = pygame.event.poll()
		if event.type == KEYUP:
			break

def scoreFileName(settings):
	return settings.track[0]+"_scores.dat"

# vim:ts=4:sw=4
