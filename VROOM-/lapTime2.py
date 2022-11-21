
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

import pygame
import string
import fpformat
import scores2
import globals

endtime = 0
laptime = 0

def end(time):
	global endtime, laptime, str
	endtime = pygame.time.get_ticks()
	laptime = time
	rank = scores2.registerScore(time)

def displayTime(screen, time):
	global endtime, laptime
	str = fpformat.fix(float(laptime)/1000, 2).rjust( 6)
	str2 = fpformat.fix(float(time)/1000, 2).rjust( 6)
	globals.font12x9.blit(str2, screen, (2,0.5), 80)
	if endtime!=0:
		t = pygame.time.get_ticks() - endtime	
		if t > 3000:
			endtime=0
		globals.font12x9.center("TIME:"+str, screen, 19)
		globals.font12x9.center("              ", screen, 19, int(255*(float(t)/3000)) )
	
