
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
import os
import string
import fpformat
import game
import globals
from backgrounds import nobackground
import pickle as cPickle
import bmpfont
import gui2
import error
from pygame.locals import *

scores = []
newScores = []
scoreEntry = "ZZWZZZZZZAEFQFZA"  # An unlikely string.

def readScores():
    global scores, newScores
    scores = []
    newScores = []
    try:
        # print "reading scores in", globals.scoreFileName(game.settings)
        scoreFile = open(globals.scoreFileName(game.settings), 'r')
        line = scoreFile.readline()
        while line:
            line = line[:-1]
            if not line:
                line = scoreFile.readline()
                continue
            lC = line[:line.index(":")]
            line=line[line.index(":")+1:]
            elems = [line[:7], line[8:], eval(lC)]
            scores.append(elems)
            line = scoreFile.readline()
        scoreFile.close()
    except IOError as err:
        pass
    

def isTop(time, x):
    ref = eval(string.split(scores[x-1])[0])
    test = float(time)/1000
    if test < ref:
        return 1
    return 0

listMax = 20

def registerScore(time):
    new = [fpformat.fix(float(time)/1000, 2).rjust( 7), scoreEntry, 5]
    a=new[0]
    if a[-2] == '.': a += '0' #fix it so scores aren't messed up
    new[0]=a
    if len(scores)==listMax and new > scores[-1]:
        return
    newScores.append(new)
    length = len(scores)
    if length==0 or ( length < listMax and new[:-1] > scores[-1][:-1] ):
        scores.append(new)
        return len(scores)
    idx = 0
    while idx < length:
        if new[:-1] < scores[idx][:-1]:
            scores.insert(idx, new)
            break
        idx+=1
    if length == listMax:
        scores.pop()
    return idx

def saveScores():
    if not newScores:
        return
    try:
        scoreFile = open(globals.scoreFileName(game.settings), 'w')
    except:
        raise error.vroomException("Couldn't open score file.\n Check file permissions.\n  Scores not saved.")
    for score in scores[:20]:
        print (str(score[2])+":"+score[0]+" "+score[1], file=scoreFile);
    scoreFile.close()

def showScores(scores, type, page=0):
    screen = globals.screen
    font = globals.font12x9
    font2 = globals.font21x12
    pygame.event.clear([KEYDOWN])
    blackScreen = screen.convert(screen)
    screenRect = blackScreen.get_rect()
    pygame.draw.rect(blackScreen, globals.backCol, screenRect)
    screen.blit(blackScreen, (0,0))
    tab = 15

    if newScores:
        event = pygame.event.poll()
        while event.type != KEYUP:
            event = pygame.event.poll()
        title=["congratulations",
            "adept racer",
            "you qualify for",
            "the leader board"]
        entries = [["enter name", game.settings.racerName, 35],]
        entries = gui2.getTextInput(title, entries, globals.font12x9)
        game.settings.racerName = entries[0][1]

    blinks = {}
    for score in scores:
        if score[1]==scoreEntry:
            score[1] = game.settings.racerName
            blinks[tuple(score)] = 1
        else:
            blinks[tuple(score)] = 0

    font2.center(game.settings.track[0].replace("_"," ") + " " +type+" leaders", blackScreen, 1)

    offset= 6
    idx = 1
    bmpfont.allUpperCase = 0
    for score in scores[page*20:(page*20)+20]:
        font.blit(score[0], blackScreen, (tab,offset))
        x1 = [4,5][(idx+page*20)<10]
        font.blit(str(idx+page*20)+".", blackScreen, (tab-7+x1, offset))
        font.blit(score[1], blackScreen, (tab+9,offset))
        offset+=1.5
        idx+=1
    reset = 0
    exit = 0
    xa=295
    xb=345
    y1=450
    shape1 = [(xa, y1),
        (xa, y1+12),
        (xa-8, y1+6)]
    shape2 = [(xb, y1),
        (xb, y1+12),
        (xb+8, y1+6)]
    while 1:
        t1 = pygame.time.get_ticks()
        cb = ((t1 >> 8) & 1)
        offset= 6
        idx = 1
        bmpfont.allUpperCase = 0
        for score in scores[page*20:(page*20)+20]:
            if blinks[tuple(score)]:
                if cb:
                    font.blit(score[0], blackScreen, (tab,offset))
                    x1 = [4,5][(idx+page*20)<10]
                    font.blit(str(idx+page*20)+".", blackScreen, (tab-7+x1, offset))
                    font.blit(score[1], blackScreen, (tab+9,offset))
                else:
                    font.blit("                                           ",
                        blackScreen, (tab-4+x1,offset))
            idx+=1
            offset+=1.5
        bmpfont.allUpperCase = 1
        screen.blit(blackScreen, (0,0))
        if page>0:
            textRect = font.center("page "+str(page+1), blackScreen, 37.5)
            arrows = gui2.getArrows(textRect)
            if cb:
                pygame.draw.aalines(globals.screen, globals.foreCol, 1, arrows[0], 1)
            else:
                pygame.draw.aalines(globals.screen, globals.backCol, 1, arrows[0], 1)
        if len(scores)>page*20+20:
            textRect = font.center("page "+str(page+1), blackScreen, 37.5)
            arrows = gui2.getArrows(textRect)
            if cb:
                pygame.draw.aalines(globals.screen, globals.foreCol, 1, arrows[1], 1)
            else:
                pygame.draw.aalines(globals.screen, globals.backCol, 1, arrows[1], 1)
        pygame.display.flip()

        event = pygame.event.poll()
        if not reset:
            if event.type == KEYUP:
                reset = 1
        else:
            if event.type==KEYDOWN:
                if event.key==K_RIGHT:
                    if len(scores)>page*20+20:
                        quit = showScores(scores, type, page+1) 
                        if quit:
                            return 1
                elif event.key==K_LEFT:
                    if page>0:
                        return 0
                else:
                    pygame.time.delay(40)
                    return 1

