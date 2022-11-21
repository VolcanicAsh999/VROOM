
# VROOM!!! Vector Graphic Gacing
# Copyright 2003-2007 George Gonzalez
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import sys, os
# If you already have Numeric isntalled you can delete the following line.
sys.path.insert(0, os.getcwd()+"/Numeric")

from pygame.locals import *
from math import sin, cos, sqrt, asin, pi
import jvec
import pygame
import lapTime2
import pickle
cPickle = pickle

import fontRenderer
import traceback
import scores2
import game
from jSVG import getShapesFromSVG, walls
from jBSP import leafTypes, leafCount
import gui2
import globals
from bsp import cbsp, intersection, whichSide
from struct import *
# import psyco ### ---NO--- ###

deltaFactor = None
timeDelta = None

def rotVel(p, rvel):
    cosang = cos(deltaFactor*timeDelta*rvel)
    sinang = sin(deltaFactor*timeDelta*rvel)
    a =  cosang*p[0]-sinang*p[1]-p[0]
    b =  sinang*p[0]+cosang*p[1]-p[1]
    return (a/(timeDelta*deltaFactor), b/(timeDelta*deltaFactor))

def invRotVel(b, v):
    r = deltaFactor*timeDelta*v/(2*b)
    if r>1:
        return pi/timeDelta
    if r<-1:
        return -pi/timeDelta
    return 2*asin(r)/(timeDelta*deltaFactor)

def rotateByAng(p, angle):
    ret = [0, 0]
    cosang = cos(angle)
    sinang = sin(angle)
    ret[0] +=  cosang*p[0]
    ret[0] += -sinang*p[1]
    ret[1] +=  sinang*p[0]
    ret[1] +=  cosang*p[1]
    return ret

def rotateByVec(p, pos):
    y, x = pos
    y = -y
    ret = [0, 0]
    h = sqrt(x*x + y*y) 
    sinang = y/h
    cosang = x/h
    ret[0] +=  cosang*p[0]
    ret[0] += -sinang*p[1]
    ret[1] +=  sinang*p[0]
    ret[1] +=  cosang*p[1]
    return ret

def translateObject(pos, obj):
    for i in range(len(obj)):
        obj[i] = (obj[i][0]-pos[0], obj[i][1]-pos[1])
    return obj

# psyco.bind(translateObject)

def rotateObject(obj, pos):
    x, y = pos
    h = sqrt(x*x + y*y) 
    if h==0:
        return obj
    cosang = y/h
    sinang = x/h
    for i in range(len(obj)):
        x1 = cosang*obj[i][0] - sinang*obj[i][1]
        y1 = sinang*obj[i][0] + cosang*obj[i][1]
        obj[i] = (x1, y1)

#psyco.bind(rotateObject)

def deltaVec(pos, tdelt):
    x, y = pos
    return (x*tdelt, y*tdelt)

def crossings(rotatedVertices0, rotatedVertices1, p0, p1, tree):
    rotatedVertexPairs = list(zip(rotatedVertices0, rotatedVertices1))
    xings = []
    for (r0, r1) in rotatedVertexPairs:
        u0 = jvec.add(p0, r0)
        u1 = jvec.add(p1, r1)
        clist = []
        tree.lineOfSight((u0,u1), clist)
        xings.append(clist)
    return xings

k_up = 8
k_down = 4
k_left = 2
k_right = 1
class car:
    def __init__(self):
        self.pos = [0, 0]
        self.vel = [0, 0]
        self.dir = [0, 1]
        self.rvel = 0.0

        self.lag = 0
        self.cornerLaps = 0
        self.laps = 0
        self.lap = 0
        self.poly =  [(-4, 5), (4, 5), (4, -5), (-4, -5), (-4, 5)]
        self.body=[]
        for file in ["car.svg", "carL.svg", "carR.svg"]: 
            svgData = getShapesFromSVG(file)
            self.body.append([x.seq for x in svgData[0]])
            apeture = self.body[-1].pop()
            min = apeture[1]
            max = apeture[0]
            xscale = 8.0/(max[0]-min[0])
            yscale = 10.0/(max[1]-min[1])
            xoff = (max[0]+min[0])/2.0
            yoff = (max[1]+min[1])/2.0
            for x in range(len(self.body[-1])):
                for y in range(len(self.body[-1][x])):
                    p = self.body[-1][x][y]
                    self.body[-1][x][y] = ( (p[0]-xoff)*xscale, (p[1]-yoff)*yscale )
        self.vertices = self.poly[:-1]
        self.vertexCount = len(self.vertices)
        self.elasticity = 0.4 
        self.svol=0
        if sounds:
            self.lastRev = sounds.revs[0]
            self.lastRev.set_volume(0)
            self.lastChan = self.lastRev.play(-1)
        self.firstCP = walls.cp[0]
        self.passedStart = 0
        self.crashVol = 0
        self.rect = pygame.rect.Rect(-6+globals.ORIGINX, -7+globals.ORIGINY, 12, 14)

    def affectMotion(self, collision, vertex):
        (p, adj, norm, type1) = collision
        ca = rotateByVec(vertex, self.dir)
        totalV = jvec.add(self.vel, rotVel(ca, self.rvel))
        bounceVel = jvec.scale(0.1*abs(jvec.dot(self.dir, jvec.norm(norm,1)))-jvec.dot(totalV, norm)*self.elasticity, norm)
        forwardVel = jvec.scale(0.7*jvec.dot(totalV, adj), adj)
        vertex_vel = jvec.add(bounceVel, forwardVel)
        self.nvel = vertex_vel
        if jvec.mag(self.nvel)>globals.VMAX:
            self.nvel=(0, 0)
        can = jvec.unit(jvec.norm(ca, 1))
        self.nrvel = 0.06*invRotVel(jvec.mag(vertex), jvec.dot(vertex_vel, can))
        self.crashVol = abs(jvec.dot(totalV, norm)) + abs(jvec.dot(vertex_vel, can))

    def processFinishLineCrossings(self, i, xings):
        lapinc = 0
        for (x0, x1) in list(zip(xings[i][:-1], xings[i][1:])):
            if x0[0]==walls.space and x1[0]==walls.start:
                lapinc+=1
            elif x1[0]==walls.space and x0[0]==walls.start:
                lapinc-=1
        return lapinc

    def processCheckPointCrossings(self, i, xings):
        lapinc = 0
        if self.checkPoint == self.lastCP:
            nextCP = self.firstCP
        else:
            nextCP = self.checkPoint+1
        for (x0, x1) in list(zip(xings[i][:-1], xings[i][1:])):
            if x1[0]==nextCP:
                if nextCP== self.firstCP:
                    lapinc = 4
                else:
                    if sounds:
                        sounds.lap.play()
                self.checkPoint = nextCP    
                break
        return lapinc

    def updateFromPacked(self, data, tree, tdelt):
        (   p0, p1,
            v0, v1,
            d0, d1,
            self.rvel,
            cd0, cd1,
            key) = unpack("9fi",data)
        self.pos = [p0,p1]
        self.vel = [v0,v1]
        self.dir = (d0,d1)
        self.update(key, tree, tdelt)
        return key

    def update(self, key, tree, tdelt):
        frictionRate = 0.02
        latFrictionRate = 0.4
        rfrictionRate = 0.05
        rollingSpeed = jvec.dot(self.vel, self.dir)
        self.speed = jvec.mag(self.vel)
        accellerationRate = 0.1 - abs(rollingSpeed) * 0.012
        if accellerationRate < 0.008:
            accellerationRate = 0.008
        k2 = 0.001 - abs(rollingSpeed)*0.00005
        screechVol = 0.0
        raccl = 0
        if key & k_left:
            raccl += rollingSpeed*k2
        if key & k_right:
            raccl -= rollingSpeed*k2
        else:
            screechVol = 0.0
        screechVol = 120*abs(self.rvel)*screechVol
        x1 = abs(rollingSpeed)
        # revIdx1 = int((700*x1+50)/50 - 1)
        revIdx1 = int(17*(abs(rollingSpeed))-15)
        revIdx2 = int(5*1.9*(abs(rollingSpeed)))
        revIdx =  int(5*1.5*(abs(rollingSpeed)))
        if revIdx1 <= 99:
            if revIdx1<0:
                revIdx1 = 0
            revIdx = revIdx1
        elif revIdx2 <= 99:
            revIdx = revIdx2
        if sounds:
            newRev = sounds.revs[revIdx]
            if newRev != self.lastRev:
                self.lastChan.queue(newRev)
                self.lastRev = newRev
        drive = (0,0)
        if key & k_up:
            if sounds:
                newRev.set_volume(0.3)  
            drive = jvec.scale(-accellerationRate, self.dir)
        elif key & k_down:
            if sounds:
                newRev.set_volume(0.3)  
            drive = jvec.scale(accellerationRate, self.dir)
        else:
            if sounds:
                newRev.set_volume(0.15) 
        latDir = jvec.norm(self.dir, 1)
        latVel = jvec.dot(latDir, self.vel)
        screechVol2 = 1.4*(abs(latVel)-0.25)
        if screechVol2 < 0:
            screechVol2 = 0
        latFriction = jvec.scale(-latVel*latFrictionRate, latDir)
        rollingFriction = jvec.scale(-frictionRate*rollingSpeed, self.dir)
        if key & k_up or key & k_down:
            accel = drive
        else:
            accel = rollingFriction
        latFriction = jvec.scale(-jvec.dot(self.vel, latDir)*latFrictionRate, latDir)
        latFricMag = jvec.mag(latFriction)
        if latFricMag > 0.18:
            latFriction = jvec.scale(0.11, jvec.unit(latFriction))
        rfriction = -self.rvel*rfrictionRate
        screechVol0 = (abs(rfriction)-0.004)*120
        if screechVol0<0:
            screechVol0=0
        tsVol = screechVol2 + screechVol + screechVol0
        self.svol += 0.4 * (tsVol - self.svol)
        if sounds:
            sounds.screech.set_volume(self.svol)
        totalRAccl = raccl+rfriction
        accel = jvec.add(latFriction, accel)
        self.npos = jvec.add(self.pos, deltaVec(self.vel, tdelt))
        self.ndir = rotateByAng(self.dir, tdelt*self.rvel)
        rotatedVertices0 = list(self.vertices)
        rotatedVertices1 = list(self.vertices)
        rotateObject(rotatedVertices0, (-self.dir[0], self.dir[1]))
        rotateObject(rotatedVertices1, (-self.ndir[0], self.ndir[1]))
        xings = crossings(rotatedVertices0, rotatedVertices1, self.pos, self.npos, tree)
        bounceCount = 0
        lapinc = 0 
        self.nrvel=0
        for i in range(len(self.vertices)):
            if len(xings[i])==1:
                continue
            last = xings[i][-1]
            if last[0] > 50: # if a wall was hit
                v = jvec.unit(jvec.diff(last[2][1], last[2][0]))
                n = jvec.norm(v, -1)
                self.affectMotion((last[1], v, n, last[0]), self.vertices[i])
                bounceCount += 1
            else:
                lapinc += self.processCrossings(i, xings)
        if bounceCount==0:
            self.nvel = jvec.add(self.vel, deltaVec(accel, tdelt))
            self.nrvel = self.rvel
            self.pos = self.npos
            self.dir = jvec.unit(self.ndir)
            self.cornerLaps+=lapinc
            laps = self.cornerLaps >> 2 # divided by 4
            if lapinc!=0 and ((laps==self.laps and self.cornerLaps%4) or laps>self.laps):
                self.laps += 1
                laptime = pygame.time.get_ticks()-globals.t0
                globals.t0 = pygame.time.get_ticks()
                if sounds:
                    sounds.lap.play()
                if self.passedStart:
                    lapTime2.end(laptime)
                else:
                    self.passedStart = 1
            self.nrvel += tdelt*totalRAccl
        else:
            if sounds:
                sounds.crash.set_volume(self.crashVol * 0.15)
                sounds.crash.play()

        self.vel, self.rvel = self.nvel, self.nrvel

# psyco.bind(car.update)

def stopSounds():
    sounds.screech.stop()
    sounds.screech.set_volume(0)
    sounds.lap.stop()

white = (globals.intensity,globals.intensity,globals.intensity)
black = (0, 0, 0)

def clipToView(obj, pos, dir):
    newShape = []
    pos1 = (pos[0]+32.3*dir[0], pos[1]+32.3*dir[1])
    split = (pos1, (pos1[0]-50*dir[1], pos1[1]+50*dir[0]))
    for x in range(len(obj)):
        p0 = obj[x-1]
        p1 = obj[x]
        if whichSide(split,p0)<0 and whichSide(split,p1)<0:
            newShape.append(p0)
            continue
        if whichSide(split,p0)>0 and whichSide(split,p1)>0:
            continue
        mid = intersection(split, (p0,p1))
        if whichSide(split,p1)>0:
            newShape.append(p0)
            newShape.append(mid)
        elif whichSide(split,p0)>0:
            newShape.append(mid)
    return newShape

# psyco.bind(clipToView)

def pDraw(newShape, world):
    for x in range(len(newShape)):
        px, py = newShape[x]
        dy = 1.0-0.01*py
        nx = px/dy
        ny = py/dy
        newShape[x]=(3*nx+globals.ORIGINX, 3*ny+globals.ORIGINY)
    if len(newShape)>1:
        pygame.draw.aalines(globals.screen, globals.foreCol, 1, newShape, 3)
        world.append(newShape)

# psyco.bind(pDraw)

def renderCar(objects, pos, dir, dirCar, world):
    for obj in objects:
        newShape = list(obj)
        rotateObject(newShape, (-dirCar[0], dirCar[1]))
        newShape2 = clipToView(newShape, pos, dir)
        translateObject(pos, newShape2)
        rotateObject(newShape2, dir)
        pDraw(newShape2, world)

def renderPlayer(objects, pos, dir, world):
    for obj in objects:
        newShape = list(obj)
        translateObject(pos, newShape)
        rotateObject(newShape, dir)
        pDraw(newShape, world)

def renderTrack(objects, pos, dir, world):
    for obj in objects:
        newShape = clipToView(obj, pos, dir)
        translateObject(pos, newShape)
        rotateObject(newShape, dir)
        pDraw(newShape, world)

from copy import copy

def main(objects, player):
    global timeDelta, deltaFactor
    screen = globals.screen
    gameClock = globals.gameClock

    if not globals.tree:
        dumpFile = open("bsp/"+game.settings.track[0]+"_bsp", 'rb')
        text = dumpFile.read().replace(b'\r\n', b'\n')
        globals.tree = cPickle.loads(text)
        dumpFile.close()
        globals.leafCount = leafCount(globals.tree.tree)
    tree = globals.tree
    ctree = cbsp(tree.tree) 
    ltypes = [x for x in leafTypes(tree.tree) if x<=walls.cp[-1] and x>=walls.cp[0]]
    ltypes.sort()
    if ltypes:
        player.lastCP = ltypes[-1]
        player.checkPoint = ltypes[-1]
        player.processCrossings = player.processCheckPointCrossings
    else:   
        player.processCrossings = player.processFinishLineCrossings
    globals.t0 = pygame.time.get_ticks()
    sampled = 0
    t0 = pygame.time.get_ticks()
    for i in range(60): 
        rads = pi*(i-1)*6/180
        tempdir = (sin(rads), -cos(rads))
        world = []
        renderTrack(objects, player.pos, tempdir, world)
        pygame.display.flip()
        for shape in world:
            pygame.draw.aalines(screen, globals.backCol, 0, shape, 0)
        for j in range(1,5):
            clist = []
            ctree.lineOfSight((player.pos,(player.pos[0]+1, player.pos[1]+1)), clist)
        for shape in world:
            pygame.draw.aalines(screen, globals.backCol, 1, shape, 0)
    t1 = pygame.time.get_ticks()
    FPS = 0.9 * 60000.0/float(t1-t0)
    for i in range(30): 
        gameClock.tick(FPS)
    fps = gameClock.get_fps()
    timeDelta, deltaFactor = globals.adjustForFrameRate(fps)
    if sounds:
        player.lastRev.set_volume(0.15)
    ocar = copy(player)
    carPos = list(player.pos)
    carDir = list(player.dir)
    count = 0
    lastKey = 0
    lastTime = pygame.time.get_ticks()-100
    lag = 0
    maxlag = 0
    packets = []
    while 1:
        count += 1
        fps = gameClock.get_fps()
        timeDelta, deltaFactor = globals.adjustForFrameRate(fps)
        pygame.event.pump()
        key = pygame.key.get_pressed()
        pkey = key[K_UP]<<3 | key[K_DOWN]<<2 | key[K_LEFT]<<1 | key[K_RIGHT]
        player.update(pkey, ctree, timeDelta)
        time = pygame.time.get_ticks()
        if player.passedStart:
            laptime = time-globals.t0
            if laptime / 1000000:
                laptime = 1000000
            lapTime2.displayTime(screen, laptime)
        world = []
        renderTrack(objects, player.pos, player.dir, world)
        pbody = player.body[0]
        if key[K_LEFT]:
            pbody = player.body[1]
        elif key[K_RIGHT]:
            pbody = player.body[2]
        renderPlayer(pbody, (0,0), (0,1), world)
        t0 = gameClock.tick(FPS)
        pygame.display.flip()
        pygame.draw.rect(screen, globals.backCol, player.rect)
        for shape in world:
            pygame.draw.aalines(screen, globals.backCol, 1, shape, 0)
        if key[K_ESCAPE]:
            pygame.event.clear([KEYUP])
            break
    getattr(player, 'lastRev', pygame.mixer.Sound("sounds/crash2.wav")).set_volume(0)

# psyco.bind(main)

def run():
    pygame.event.clear([KEYDOWN])
    pygame.display.set_caption(globals.gameTitle)
    icon = pygame.image.load("icon32.bmp")  
    pygame.display.set_icon(icon)
    pygame.mouse.set_visible(0)
    screen = None
    if globals.fullscreen[0]=="on":
        globals.screen = pygame.display.set_mode((globals.XSIZE, globals.YSIZE), FULLSCREEN)
    else:
        globals.screen = pygame.display.set_mode((globals.XSIZE, globals.YSIZE))
    screen = globals.screen
    globals.ORIGINX = screen.get_width()/2
    globals.ORIGINY = screen.get_height()*0.7
    loadedMusic = False
    while 1:
        pygame.event.clear([KEYDOWN, KEYUP])
        globals.gameClock = pygame.time.Clock()
        gui2.mainMenu()
        scores2.readScores()
        player = car()
        for x in range(len(player.poly)):
            player.poly[x]=(player.poly[x][0]+globals.ORIGINX, player.poly[x][1]+globals.ORIGINY)
        if sounds:
            sounds.screech.play(-1)
        (objects, player.dir, player.pos) = getShapesFromSVG("tracks/"+game.settings.track[0]+"_gfx.svg", 0)    
        objects = [x.seq for x in objects]
        screen.fill(globals.backCol)
        main(objects, player)
        if hasattr(player, "lastChan"): player.lastChan.stop()
        if sounds:
            stopSounds()
        scores2.showScores(scores2.scores, "local")
        try:
            scores2.saveScores()
        except error.vroomException as val:
            mso = error.errOut()
            print (val, file=mso)
            pygame.display.flip()
            pygame.time.delay(1000)
            globals.keyWaitDown()
        scores2.newScores=[]
        scores2.scores=[]

import error
try:
    global screen
    class initialize:
        pygame.mixer.pre_init(22050,-16,1,512)
        pygame.init()
        pygame.mixer.init()
        dinfo = pygame.display.Info()
        if dinfo.bitsize<24:
            screen = pygame.display.set_mode((640,480))
            pygame.display.set_caption(globals.gameTitle)
            font = pygame.font.Font("freesansbold.ttf", 18)
            dinfo = pygame.display.Info()
            text = "Current display mode is "+str(dinfo.bitsize)+" bits."
            size = font.size(text)
            ren = font.render(text, 0, (255,255,255))
            screen.blit(ren, (5, 0))
            text = "VROOM!!! only works in 24 or 32 bit mode."
            size = font.size(text)
            ren = font.render(text, 0, (255,255,255))
            screen.blit(ren, (5, 25))
            text = "Please set display mode to 24 or 32 bits and restart VROOM!!!"
            size = font.size(text)
            ren = font.render(text, 0, (255,255,255))
            screen.blit(ren, (5, 50))
            pygame.display.flip()
            globals.keyWaitDown()
            sys.exit(1)
        globals.fullscreen = game.settings.fullscreen
        globals.foreCol = globals.cmap[game.settings.colors[0]][0]
        globals.backCol = globals.cmap[game.settings.colors[0]][1]
        globals.midCol = (0.60*(globals.foreCol[0]-globals.backCol[0])+globals.backCol[0],
        0.60*(globals.foreCol[1]-globals.backCol[1])+globals.backCol[1],
        0.60*(globals.foreCol[2]-globals.backCol[2])+globals.backCol[2])
        fontRenderer.renderFonts()
        globals.t0 = pygame.time.get_ticks()
    try:
        """class sounds:
            crash = pygame.mixer.Sound("sounds/crash2.wav")
            lap = pygame.mixer.Sound("sounds/pling3mono.wav")
            screech = pygame.mixer.Sound("sounds/screech.wav")
            screech.set_volume(0)
            soundFile = open("engine.dat", 'rb')
            soundArrays = pickle.load(soundFile)
            soundFile.close()
            revs = []
            for a in soundArrays:
                revs.append(pygame.sndarray.make_sound(a))
            soundFile.close()"""
        sounds = None
    except:
        mso = error.errOut()
        traceback.print_exc(file=mso)
        mso.write(" ")
        mso.write("Sound will be disabled.  Hit any key to continue. ")
        try:
            errFile = open("vroomError.txt", 'w')
            traceback.print_exc(file=errFile)
            errFile.close()
        except:
            pass
        pygame.display.flip()
        globals.keyWaitDown()
        sounds = None
    run()
except (SystemExit, KeyboardInterrupt):
    sys.exit(0)
except error.vroomException as val:
    mso = error.errOut()
    print (val, file=mso)
    pygame.display.flip()
    pygame.time.delay(1000)
    globals.keyWaitDown()
except:
    mso = error.errOut()
    traceback.print_exc(file=mso)
    try:
        errFile = open("vroomError.txt", 'w')
        traceback.print_exc(file=errFile)
        errFile.close()
    except:
        pass
    pygame.display.flip()
    pygame.time.delay(1000)
    globals.keyWaitDown()

# vim:ts=4:sw=4
