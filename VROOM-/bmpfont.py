
## bmpfont.py
## By Paul Sidorsky - Freeware

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

import pygame.image
from pygame.locals import *

__all__ = ["BmpFont"]

allUpperCase = 1

class BmpFont:
	"""Provides an object for treating a bitmap as a font."""

	# Constructor - creates a BmpFont object.
	# Parameters:  idxfile - Name of the font index file.
	def __init__(self, width, height, mask, surf):
		# Setup default values.
		#self.alluppercase = 1
		self.chartable = {}
		self.width = width
		self.height = height
		self.transrgb = (0,0,0)

		# Read the font index.	File errors will bubble up to caller.
		f = open("font.idx", "r")

		for x in f.readlines():
			# Remove EOL, if any.
			if x[-1] == '\n':
				x = x[:-1]
			if x[-1] == '\r':
				x = x[:-1]
			words = x.split()

			if words[0] == "space":
				words[0] = ' '
			#if self.alluppercase:
			#	words[0] = words[0].upper()
			self.chartable[words[0]] = (int(words[1]) * self.width,
										int(words[2]) * self.height)
		f.close()

		# Setup the actual bitmap that holds the font graphics.
		# #surface1 = pygame.image.load(self.bmpfile)
		# #self.surface = pygame.image.load(self.bmpfile)
		# #self.surface = self.surface.convert(32)
		self.surface = surf
		# sarray = pygame.surfarray.pixels2d(self.surface)
		sarray = pygame.surfarray.pixels3d(self.surface)
		# sarray = bitwise_and(sarray, mask)
		sarray = sarray & mask
		pygame.surfarray.blit_array(self.surface, sarray)
		#self.surface = self.surface.convert(24)
		#self.surface.set_colorkey((0,0,255), RLEACCEL)

	# blit() - Copies a string to a surface using the bitmap font.
	# Parameters:  string	 - The message to render.  All characters
	#						   must have font index entries or a
	#						   KeyError will occur.
	#			   surf 	 - The pygame surface to blit string to.
	#			   pos		 - (x, y) location specifying location
	#						   to copy to (within surf).  Meaning
	#						   depends on usetextxy parameter.
	#			   usetextxy - If true, pos refers to a character cell
	#						   location.  For example, the upper-left
	#						   character is (0, 0), the next is (0, 1),
	#						   etc.  This is useful for screens with
	#						   lots of text.  Cell size depends on the
	#						   font width and height.  If false, pos is
	#						   specified in pixels, allowing for precise
	#						   text positioning.

	def blit(self, string, surf, pos = (0, 0), alpha=255, usetextxy = 1):
		"""Draw a string to a surface using the bitmapped font."""
		x, y = pos
		if usetextxy:
			x *= self.width
			y *= self.height
		surfwidth, surfheight = surf.get_size()
		fontsurf = self.surface.convert(surf)
		fontsurf.set_alpha(alpha)

		#if self.alluppercase: string = string.upper()
		if allUpperCase:
			string = string.upper()

		# Render the font.
		for c in string:
			# Perform automatic wrapping if we run off the edge of the
			# surface.
			if x >= surfwidth:
				x -= surfwidth
				y += self.height
				if y >= surfheight:
					y -= surfheight

			surf.blit(fontsurf, (x, y),
					 (self.chartable[c], (self.width, self.height)))
			x += self.width
		return ((pos[0]*self.width, pos[1]*self.height), (x, y+self.height))

	def center(self, str, screen, row, alpha=255):
		return self.blit(str, screen, ((screen.get_width()-len(str)*self.width)/float(2*self.width), row), alpha) 

