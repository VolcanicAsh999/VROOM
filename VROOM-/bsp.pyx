
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

cdef extern from "math.h":
	double fabs(double x)

ctypedef int size_t

cdef extern from "stdlib.h":
	void* malloc(size_t size)
	void free(void* ptr)
	int abs(int i)

ctypedef struct point:
	double p[2]

ctypedef struct seg:
	double p0[2]
	double p1[2]
	
cdef struct bspFork
cdef union bspNodeData
cdef struct bspNode

cdef struct bspFork:
	double split[2][2]
	bspNode *pos, *neg

cdef union bspNodeData:
	int mediumType
	bspFork fork

cdef struct bspNode:
	int isLeaf
	bspNodeData nd

cdef bspNode* createLeaf(int medType):
	cdef bspNode* n
	n = <bspNode*>malloc(sizeof(bspNode))
	n[0].isLeaf=1
	n[0].nd.mediumType=medType
	return n

cdef bspNode* createFork(double split[2][2]):
	cdef bspNode* n
	n = <bspNode*>malloc(sizeof(bspNode))
	n[0].isLeaf=0
	n[0].nd.fork.split[0][0]=split[0][0]
	n[0].nd.fork.split[0][1]=split[0][1]
	n[0].nd.fork.split[1][0]=split[1][0]
	n[0].nd.fork.split[1][1]=split[1][1]
	n[0].nd.fork.pos=NULL
	n[0].nd.fork.neg=NULL
	return n


cdef deleteTree(bspNode* n):
	if n[0].isLeaf==0:
		deleteTree(n[0].nd.fork.pos)
		deleteTree(n[0].nd.fork.neg)
	free(n)

cdef bspNode* makeC_BSP(node):
	cdef bspNode *n
	cdef double csplit[2][2]
	if not node.isLeaf:
		csplit[0][0] = node.split[0][0]
		csplit[0][1] = node.split[0][1]
		csplit[1][0] = node.split[1][0]
		csplit[1][1] = node.split[1][1]
		n = createFork(csplit)
		n[0].nd.fork.pos = makeC_BSP(node.branches[1])
		n[0].nd.fork.neg = makeC_BSP(node.branches[-1])
	else:
		n = createLeaf(node.type)
	return n


cdef point trans(double a[2], double b[2]):
	cdef point val
	val.p[0]=a[0]-b[0]
	val.p[1]=a[1]-b[1]
	return val

cdef int whichSideC(double seg[2][2], double p[2]):
	cdef point a, b
	cdef double x
	a = trans(<double*>seg[0], <double*>seg[1])
	b = trans(<double*>p, <double*>seg[1])
	x = a.p[0]*b.p[1]-a.p[1]*b.p[0]
	if x>0:
		return 1
	if x<0:
		return -1
	return 0


def whichSide(segm, pt):
	cdef double p[2]
	cdef double s[2][2]
	p[0], p[1] = pt[0], pt[1]
	s[0][0], s[0][1] = segm[0][0], segm[0][1]
	s[1][0], s[1][1] = segm[1][0], segm[1][1]
	return whichSideC(s, p)
	

cdef point intersectionC(double l1[2][2], double l2[2][2]):
	cdef double x1, y1, x2, y2, x3, y3, x4, y4, tiny
	cdef point pt
	x1, y1, x2, y2 = l1[0][0], l1[0][1], l1[1][0], l1[1][1]
	x3, y3, x4, y4 = l2[0][0], l2[0][1], l2[1][0], l2[1][1]
	tiny = 0.0001
	if fabs(x2 - x1) < tiny:
		pt.p[0] = x1
		m3 = (y4-y3)/(x4-x3)
		pt.p[1] = x1*m3-x3*m3+y3	
	elif fabs(x3 - x4) < tiny:
		m1 = (y2-y1)/(x2-x1)
		pt.p[0] = x3
		pt.p[1] = x3*m1-x1*m1+y1
	elif fabs(y2 - y1) < tiny:
		z3 = (x4-x3)/(y4-y3)
		pt.p[1] = y1
		pt.p[0] = x3-y3*z3+y1*z3
	elif fabs(y4 - y3) < tiny:
		z1 = (x2-x1)/(y2-y1)
		pt.p[1] = y3
		pt.p[0] = x1-y1*z1+y3*z1
	else:
		m1 = (y2-y1)/(x2-x1)
		m3 = (y4-y3)/(x4-x3)
		pt.p[0] = (x1*m1-x3*m3+y3-y1)/(m1-m3)	
		z1 = 1/m1
		z3 = 1/m3
		pt.p[1] = (y1*z1-y3*z3+x3-x1)/(z1-z3)	
	return pt

def intersection(l1, l2):
	cdef double line1[2][2]
	cdef double line2[2][2]
	cdef point pt
	line1[0][0], line1[0][1] = l1[0][0], l1[0][1]
	line1[1][0], line1[1][1] = l1[1][0], l1[1][1]
	line2[0][0], line2[0][1] = l2[0][0], l2[0][1]
	line2[1][0], line2[1][1] = l2[1][0], l2[1][1]
	pt = intersectionC(line1, line2)
	return (pt.p[0], pt.p[1]) 

cdef int lineOfSightC(bspNode *tree, double k[2][2], double s[2][2], clist):
	cdef int s0, s1
	cdef point mid
	cdef double newSeg[2][2]
	cdef bspNode* next
	if tree.isLeaf:
		if not clist or tree[0].nd.mediumType!=clist[-1][0]:
			clist.append((tree[0].nd.mediumType, (k[0][0],k[0][1]),
				((s[0][0],s[0][1]), (s[1][0],s[1][1])) ))
		return tree[0].nd.mediumType
	s0 = whichSideC(tree[0].nd.fork.split, <double*>k[0])
	s1 = whichSideC(tree[0].nd.fork.split, <double*>k[1])
	if abs(s0-s1) == 2: # If split bisects k
		mid = intersectionC(tree[0].nd.fork.split, k)
		newSeg[0][0], newSeg[0][1] =k[0][0], k[0][1]
		newSeg[1][0], newSeg[1][1] = mid.p[0], mid.p[1]
		if s0==1:
			type = lineOfSightC(tree[0].nd.fork.pos, newSeg, s, clist)
		else:
			type = lineOfSightC(tree[0].nd.fork.neg, newSeg, s, clist)
		if type>50: # if a solid was hit, don't need to process collisions behind it.
			return type
		newSeg[0][0], newSeg[0][1] = mid.p[0], mid.p[1]
		newSeg[1][0], newSeg[1][1] =k[1][0], k[1][1]
		if s1==1:
			next = tree[0].nd.fork.pos
		else:
			next = tree[0].nd.fork.neg
		return lineOfSightC(next, newSeg, tree[0].nd.fork.split, clist)
	elif s0==-1 or s0==1: # s1 is on the split
		if s0==1:
			next = tree[0].nd.fork.pos
		else:
			next = tree[0].nd.fork.neg
		return lineOfSightC(next, k, s, clist)
	elif s1==-1 or s1==1: # s0 is on the split
		if s1==1:
			next = tree[0].nd.fork.pos
		else:
			next = tree[0].nd.fork.neg
		return lineOfSightC(next, k, s, clist)
	else:
		raise "Unhandled case."

cdef class cbsp:
	cdef bspNode *tree

	def __cinit__(self, node):
		self.tree = makeC_BSP(node)

	def __dealloc__(self):
		deleteTree(self.tree)

	def lineOfSight(self, k, clist):
		cdef double z[2][2]
		cdef double y[2][2]
		z[0][0], z[0][1] = k[0][0], k[0][1]
		z[1][0], z[1][1] = k[1][0], k[1][1]
		y[0][0], y[0][1] = 0, 0
		y[1][0], y[1][1] = 0, 0
		lineOfSightC(self.tree, z, y, clist)

# vim:syntax=python
