
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

import cPickle
import jSVG
from jBSP import bspTree
import sys

if len(sys.argv)<2:
	print "Usage: makeBsp [track name]"

track = sys.argv[1]

(objects, dir, pos) = jSVG.getShapesFromSVG("tracks/"+track+".svg", 1)	

print "Making bsp..."
tree = bspTree(objects)	
dumpFile = open(track+"_bsp", 'w')
cPickle.dump(tree, dumpFile)
dumpFile.close()
print "done."
