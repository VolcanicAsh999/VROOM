
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

from jSVG import walls
import jvec

# import psyco
# psyco = bpsyco

def trans(a, b):
    return (a[0]-b[0], a[1]-b[1])


def whichSide(seg, p):
    a = trans(seg[0], seg[1])
    b = trans(p, seg[1])
    x = a[0]*b[1]-a[1]*b[0]
    if x>0:
        return 1
    if x<0:
        return -1
    return 0

# psyco.bind(whichSide)

def intersection(poses):
    pos1, pos2, pos3, pos4 = poses
    x1,y1, x2,y2, x3,y3, x4,y4 = pos1,pos2,pos3,pos4
    tiny = 0.0001
    if abs(x2 - x1) < tiny:
        x = x1
        m3 = (y4-y3)/(x4-x3)
        y = x1*m3-x3*m3+y3  
    elif abs(x3 - x4) < tiny:
        m1 = (y2-y1)/(x2-x1)
        x = x3
        y = x3*m1-x1*m1+y1
    elif abs(y2 - y1) < tiny:
        z3 = (x4-x3)/(y4-y3)
        y = y1
        x = x3-y3*z3+y1*z3
    elif abs(y4 - y3) < tiny:
        z1 = (x2-x1)/(y2-y1)
        y = y3
        x = x1-y1*z1+y3*z1
    else:
        m1 = (y2-y1)/(x2-x1)
        m3 = (y4-y3)/(x4-x3)
        x = (x1*m1-x3*m3+y3-y1)/(m1-m3) 
        z1 = 1/m1
        z3 = 1/m3
        y = (y1*z1-y3*z3+x3-x1)/(z1-z3) 
    return (x,y)


class leaf:
    def __init__(self, type):
        self.type = type
        self.isLeaf = 1

class node:
    def __init__(self, split, pos, neg):
        self.split = split
        self.branches = [leaf(0), pos, neg]
        self.isLeaf = 0


def findSplit(segs, types):
    points = {}
    for seg in segs:
        points[seg[0]]=1
        points[seg[1]]=1
    points = points.keys()
    # points.sort() # seems to give a smaller file in some cases
    size = len(points)
    bestSplit = []
    bestSegCount = 0
    leastCost=(99999, 99999, 99999, 1)
    for i in range(size):
        for j in range(size):
            if i == j:
                continue
            split = [points[i], points[j]]
            notAxisAligned = not (split[0][0]==split[1][0] or split[0][1]==split[1][1])
            posCount, negCount, segCount = 0, 0, 0
            for k in points:
                if whichSide(split, k) < 0:
                    negCount+=1
                if whichSide(split, k) > 0:
                    posCount+=1
            cuts = 0
            segDir=99999
            segType=None
            if types.has_key( (split[0], split[1]) ):
                segType = types[ (split[0], split[1]) ]
            if types.has_key( (split[1], split[0]) ):
                segType = types[ (split[1], split[0]) ]
            illegal=0
            for k in segs:
                sideK0 = whichSide(split, k[0])
                sideK1 = whichSide(split, k[1])
                if abs(sideK0 - sideK1) == 2: # If split bisects k
                    cuts += 1
                if sideK0==0 and sideK1==0:
                    if segType==None:
                        illegal=1
                    segCount += 1
                    if jvec.dot(jvec.diff(split[0],split[1]), jvec.diff(k[0],k[1])) < 0:
                        segDir=0
                    else:
                        if segDir==0:
                            illegal=1
                        split[0], split[1] = split[1], split[0]
                        segDir=0
                    if segType != None: # If 2 or more segs don't share same seg type...
                        if types[k]!=segType:
                            illegal=1   # ...don't allow.
                    else:
                        segType = types[k]
            balance = abs(posCount-negCount)
            if 2*segCount > balance:
                balance = 0
            else:
                balance = balance-2*segCount
            if not illegal and (balance, cuts, notAxisAligned)<leastCost:
                leastCost = (balance, cuts, notAxisAligned)
                bestSplit = split
                bestSegType = segType
                bestSegCount = segCount
    return (bestSplit, bestSegType)

# psyco.bind(findSplit)

def makeBSP(segs, types):
    (split, segType) = findSplit(segs, types)
    pos = []
    neg = []
    for k in segs:
        s0 = whichSide(split, k[0])
        s1 = whichSide(split, k[1])
        if abs(s0-s1) == 2: # If split bisects k
            mid = intersection(split, k)
            types[(k[0], mid)]=types[k]
            types[(mid, k[1])]=types[k]
            if s0==1:
                pos.append( (k[0], mid) )
                neg.append( (mid, k[1]) )
            else:
                neg.append( (k[0], mid) )
                pos.append( (mid, k[1]) )
            pass
        elif s0==1 or s1==1:
            pos.append(k)
        elif s0==-1 or s1==-1:
            neg.append(k)
    if len(pos):
        pNode = makeBSP(pos, types)
    else:
        pNode = leaf(segType[0])
    if len(neg):
        nNode = makeBSP(neg, types)
    else:
        nNode = leaf(segType[1])
    return node(split, pNode, nNode)


def lineOfSight(tree, k, s, clist):
    if tree.isLeaf:
        if not clist or tree.type!=clist[-1][0]:
            clist.append((tree.type, k[0], s))
        return tree.type
    s0 = whichSide(tree.split, k[0])
    s1 = whichSide(tree.split, k[1])
    if abs(s0-s1) == 2: # If split bisects k
        mid = intersection(tree.split, k)
        type = lineOfSight(tree.branches[s0], (k[0], mid), s, clist)
        if type>50: # if a solid was hit...
            return type #...we don't need to process collisions behind it.
        return lineOfSight(tree.branches[s1], (mid, k[1]), tree.split, clist)
    elif s0==-1 or s0==1: # s1 is on the split
        return lineOfSight(tree.branches[s0], k, s, clist)
    elif s1==-1 or s1==1: # s0 is on the split
        return lineOfSight(tree.branches[s1], k, s, clist)
    else:
        raise "Unhandled case."

# psyco.bind(lineOfSight)

def leafCountInner(tree, count, visited):
    visited[tree]=1
    if not tree.isLeaf:
        #if not visited.has_key(tree.branches[-1]):
        if not tree.branches[-1] in visited.keys():
            count = leafCountInner(tree.branches[-1], count, visited)
        #if not visited.has_key(tree.branches[1]):
        if not tree.branches[1] in visited.keys():
            count = leafCountInner(tree.branches[1], count, visited)
        return count
    else:
        return count+1

def leafTypesInner(tree, tdict, visited):
    visited[tree]=1
    if not tree.isLeaf:
        #if not visited.has_key(tree.branches[-1]):
        if not tree.branches[-1] in visited.keys():
            leafTypesInner(tree.branches[-1], tdict, visited)
        #if not visited.has_key(tree.branches[1]):
        if not tree.branches[1] in visited.keys():
            leafTypesInner(tree.branches[1], tdict, visited)
    else:
        tdict[tree.type]=1

def leafTypes(tree):
    tdict = {}
    visited = {}
    leafTypesInner(tree, tdict, visited)
    return list(tdict.keys())

def leafCount(tree):
    visited = {}
    count = 0
    return leafCountInner(tree, count, visited)

class bspTree:
    def __init__(self, objects):
        segs=[]
        segMap = {}
        types={}
        segCount1 = 0
        segCount2 = 0
        for obj in objects:
            objSegs=map(None, obj.seq[:-1], obj.seq[1:])
            for seg in objSegs:
                seg2 = ((round(seg[0][0], 3), round(seg[0][1], 3)), 
                    (round(seg[1][0], 3), round(seg[1][1], 3)))
                seg = seg2
                segCount1+=1
                key = list(seg)
                key.sort()
                key = tuple(key)
                if segMap.has_key(key):
                    segMap[key].append((obj.type, key!=seg))
                else:
                    segMap[key] = [(obj.type, key!=seg)]
        for (key, typeList) in segMap.items():
            if len(typeList)==1:
                (objType, swapped) = typeList[0]
                if swapped:
                    seg = (key[1], key[0])
                else:
                    seg = key
                types[seg]=(walls.space, objType)
                segs.append(seg)
            elif len(typeList)==2:
                if typeList[0][0] > 50: # if a solid wall was hit
                    idx1, idx2 = 0, 1
                else:
                    idx1, idx2 = 1, 0
                (objType1, swapped) = typeList[idx1]
                if swapped:
                    seg = (key[1], key[0])
                else:
                    seg = key
                objType2 = typeList[idx2][0]

                types[seg]=(objType2, objType1)
                segs.append(seg)
            else:
                print (len(typeList))
                raise "Unhandled case."

        segs.sort()
        for seg in segs:
            segCount2+=1

        self.tree = makeBSP(segs, types)

    def check(self, p):
        idx = self.tree
        while not idx.isLeaf:
            idx = idx.branches[whichSide(idx.split, p)]
        return idx.type

# vim:ts=4:sw=4
