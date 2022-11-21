
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

from jvec import scale, unit, diff, angle
import re
from math import sqrt

class object:
	def __init__(self, seq, type):
		self.seq = seq
		self.type = type 

codes = [ "0000ff", "00ffff", "ff00ff", "ffff00", \
"7f0000", "007f00", "00007f", "007f7f", "7f007f", \
"7f7f00", "2e4f4f", "696969", "6f8090", "778799"]

alternateCodes = [ "0000ff", "00ffff", "ff00ff", "ffff00", \
"7e0000", "007f00", "00007f", "007f7f", "7f007f", \
"7f7f00", "2e4f4f", "696969", "6f8090", "778799"]

class walls:
	space = 0
	start = 1
	border = 2
	cp=list(range(4,18)) # checkpoints
	ice = 20
	boost = 21
	bounce = 51
	solid = 52
	l1 = list(zip(codes, cp))
	l1.append(("000000", solid))
	l1.append(("ff0000", border))
	l1.append(("00ff00", start))
	l2 = list(zip(alternateCodes, cp))
	type = dict(l1+l2)


def getShapesFromSVG(fileName, redirect=1):
	file = open(fileName, 'r')	
	line = file.readline()
	shapes = []
	wPat = re.compile('width=\"([0-9.]*)\"')
	hPat = re.compile('height=\"([0-9.]*)\"')
	sPat = re.compile('stroke:#([a-z0-9.]*);')
	while line:
		if line[:5]=="<svg ":
			width = eval(wPat.search(line).group(1))
			height = eval(hPat.search(line).group(1))
		if line[:5]!="<path":
			line = file.readline()
			continue
		stroke = sPat.search(line).group(1)
		data = line[line.find(" d=")+4:-4]
		data2 = data.split("M ")
		for item in data2[1:]:
			if item[-1]=='z':
				item=item[:-1]
			data3=item.split("L ")
			shape = [(eval(x.split()[0]), eval(x.split()[1])) for x in data3]
			shapes.append(object(shape, walls.type[stroke]))
		line = file.readline()

	# Remove zero-length segments
	for shape in shapes:
		i=0
		while i < len(shape.seq)-1:
			if shape.seq[i]==shape.seq[i+1]:
				shape.seq.pop(i)
			else:
				i+=1

	pos = (shapes.pop(-1)).seq
	a = pos[1][0]-pos[0][0]
	b = pos[1][1]-pos[0][1]
	startDir = unit((a,b))
	c = sqrt(a*a+b*b)
	sc = 20/c
	dx = width/2
	dy = height/2
	startPos = scale(sc, (pos[0][0]-dx, pos[0][1]-dy))

	objects=[]
	for x in range(len(shapes)):
		seq = list(zip(shapes[x].seq[:-1], shapes[x].seq[1:]))
		if redirect and len(seq)>2: # Don't mess with direction of lines.
			sum = 0
			for i in range(len(seq)):
				sum+=angle(diff(seq[i-1][1],seq[i-1][0]), diff(seq[i][1],seq[i][0]))
			if sum<0 and x>0 or sum>0 and x==0:
				shapes[x].seq.reverse()
		objects.append(shapes[x])

	for obj in objects:
		for x in range(len(obj.seq)):
			obj.seq[x] = scale(sc, (obj.seq[x][0]-dx, obj.seq[x][1]-dy))	
	return (objects, startDir, startPos)


