
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
import bmpfont
from pygame.locals import *

from backgrounds import background, nobackground
from fontRenderer import renderFonts

import globals
import game
import sys
import types
import scores2

def getBox(pos):
    p1,p2 = pos
    return [(p1[0]-3, p1[1]-3),
        (p2[0]+3, p1[1]-3),
        (p2[0]+3, p2[1]+3),
        (p1[0]-3, p2[1]+3)]

def getArrows(pos):
    p1,p2 = pos
    return [
        [(p1[0]-3, p1[1]),
        (p1[0]-6, (p1[1]+p2[1])/2.0),
        (p1[0]-3, p2[1]),
        (p1[0]-14, (p1[1]+p2[1])/2.0)],
        [(p2[0]+3, p1[1]),
        (p2[0]+6, (p1[1]+p2[1])/2.0),
        (p2[0]+3, p2[1]),
        (p2[0]+14, (p1[1]+p2[1])/2.0)]
        ]

def doMenu(title, items, cfn):
    globals.screen.fill(globals.backCol)
    selected = 0
    t0 = 0
    H, W = globals.font12x9.height, globals.font12x9.width
    tabWidth = 15
    escapeFn=None
    if type(items[-1][0]==int) and items[-1][0]==K_ESCAPE:
        escapeFn = items[-1][1]
        items=items[:-1]
    textshape = None
    arrowshapes = None
    while 1:
        if cfn:
            cfn.erase()
        row0 = 1
        for t in title: 
            globals.font21x12.center(t, globals.screen, row0) 
            row0+=1
        row0+=3
        t1 = pygame.time.get_ticks()
        blink = not (t1-t0 >> 8) & 1
        lineColor = globals.backCol
        if blink:
            lineColor = globals.foreCol
        row = 3+row0
        for item in items:
            text0, fn, choices = item[:3]
            text = text0
            if choices:
                text = text0 + " " + choices[0].replace('_',' ')
            textrect = globals.font12x9.blit(text, globals.screen, (tabWidth, row), 255)
            if text0==items[selected][0]: 
                if choices:
                    arrowshapes = getArrows(textrect)
                    pygame.draw.aalines(globals.screen, lineColor, 1, arrowshapes[0], blink)
                    pygame.draw.aalines(globals.screen, lineColor, 1, arrowshapes[1], blink)
                else:
                    textshape = getBox(textrect)
                    pygame.draw.lines(globals.screen, lineColor, 1, textshape)
            row+=2
        if cfn:
            cfn.update()
            cfn.draw()

        pygame.display.flip()
        if textshape:
            pygame.draw.lines(globals.screen, globals.backCol, 1, textshape)
            textshape = None
        if arrowshapes:
            pygame.draw.aalines(globals.screen, globals.backCol, 1, arrowshapes[0], 0)
            pygame.draw.aalines(globals.screen, globals.backCol, 1, arrowshapes[1], 0)
            arrowshapes = None
        cfn.cache()
        globals.gameClock.tick(globals.FPS)

        choices = items[selected][2] 
        
        e = pygame.event.poll()
        if e.type==KEYDOWN:
            t0=t1
            if e.key==K_DOWN:
                if selected == len(items)-1:
                    selected=0
                else:
                    selected+=1
                    if not items[selected][0]:
                        selected+=1
            elif e.key==K_UP:
                if selected == 0:
                    selected = len(items)-1
                else:
                    selected-=1
                    if not items[selected][0]:
                        selected-=1
            elif choices and (e.key==K_RIGHT or e.key==K_LEFT): 
                text = items[selected][0].replace('_', ' ') + " " + choices[0]
                pygame.draw.rect(globals.screen, globals.backCol, ((W*tabWidth, (selected*2+4)*H), (len(text)*W, H)) )
                if e.key==K_RIGHT:
                    choices.append(choices.pop(0))
                    items[selected][1].next()
                else:
                    choices.insert(0,choices.pop())
                    items[selected][1].previous()
                if cfn:
                    cfn.newScreen()
            elif e.key==K_RETURN:
                if choices:
                    if items[selected][3]:
                        return items[selected][3]
                else:
                    return items[selected][1]
            elif escapeFn and e.key==K_ESCAPE:
                return escapeFn


def doText(yPos, text, cpos, limit, fnt, idx):
    done = 0
    screen = globals.screen
    H, W = fnt.height, fnt.width
    sWid = screen.get_width()
    x2 = (sWid-limit*W)/2.0
    t0 = pygame.time.get_ticks()
    allDone = 0
    inc = 0
    while not done:
        try:        
            pygame.draw.rect(screen, globals.backCol, ((x2, H*(yPos-1)), (limit*W, H)) )
            text2 = text
            if len(text)<limit and cpos==len(text):
                text2+=" "
            fnt.center(text2, screen, yPos-1)
        except KeyError as x:
            text = text[:-1]
            cpos-=1
            continue
        t1 = pygame.time.get_ticks()
        cb = (t1-t0 >> 8) & 1
        cursorCol = [globals.foreCol, globals.backCol][cb]
        l = len(text)
        x0 = sWid-(sWid-len(text)*W)/2.0 - W*(len(text)-cpos)
        if cpos==len(text):
            x0 = sWid-(sWid-len(text)*W+W)/2.0
        x1 = x0+W
        if cpos!=limit:
            pygame.draw.aaline(screen, cursorCol, (x0, H*yPos), (x1, H*yPos), 1)
        pygame.display.flip()
        if cpos!=limit:
            pygame.draw.aaline(screen, globals.backCol, (x0, H*yPos), (x1, H*yPos), 0)
        e = pygame.event.poll()
        if e.type==KEYDOWN:
            t0=t1
            if e.key==K_RIGHT:
                if cpos<len(text):
                    cpos+=1
                else:
                    done = 1 
                    inc = 1
                    break
            elif e.key==K_LEFT:
                if cpos>0:
                    cpos-=1
                else:
                    done = 1 
                    inc = -1
                    break
            if e.key==K_UP:
                done = 1 
                inc = -1
                break
            elif e.key==K_DOWN:
                done = 1 
                inc = 1
                break
            if e.key==K_DELETE or e.key==K_BACKSPACE:
                if text and cpos>0:
                    cpos-=1
                    text = text[:cpos]+text[cpos+1:]
            elif e.key == K_ESCAPE:
                pass
            elif e.key == K_TAB:
                done = 1 
                inc = 1
                break
            elif e.key == K_RETURN:
                done = 1 
                allDone = 1 
                break
            else:
                if e.key<128 and e.unicode and len(text) < limit:
                    text=text[:cpos]+chr(ord(e.unicode))+text[cpos:]
                    cpos+=1
    return (text, allDone, cpos, inc)


def getTextInput(title, entries, fnt):
    screen = globals.screen
    pygame.event.clear([KEYDOWN])
    globals.screen.fill(globals.backCol)
    pygame.key.set_repeat(500, 30)
    row = 3
    for i in title:
        globals.font21x12.center(i, screen, row)
        row+=1.5
    row = 20
    cpos = {}
    H, W = fnt.height, fnt.width
    sWid = screen.get_width()
    for idx in range(len(entries)):
        x2 = (sWid-entries[idx][2]*W)/2.0
        cpos[idx] = len(entries[idx][1])
        fnt.center(entries[idx][0], screen, row-2.5+6*idx)
        yPos = row+6*idx
        pygame.draw.rect(screen, globals.foreCol, ((x2-4, H*(yPos-1)-4), (entries[idx][2]*W+8, H+8)), 1 )
    inc = 0
    done = 0
    idx = 0
    bmpfont.allUpperCase = 0
    while not done:
        limit = entries[idx][2]
        if inc<0:
            cpos[idx] = len(entries[idx][1])
        if inc>0:
            cpos[idx] = 0
        (entries[idx][1], done, cpos[idx], inc)=doText(row+6*idx, entries[idx][1], cpos[idx], limit, fnt, idx)
        idx+=inc
        idx = idx % len(entries)
    bmpfont.allUpperCase = 1
    pygame.key.set_repeat()
    return entries


def raceFn():
    pass

def aboutFn():
    globals.screen.fill(globals.backCol)
    globals.font21x12.center(globals.gameTitle, globals.screen, 8) 
    globals.font12x9.center("Vector graphic racing", globals.screen, 17) 
    globals.font9x6.center("Copyright 2003-2007 George Gonzalez.", globals.screen, 28) 
    pygame.display.flip()
    globals.keyWaitDown()
    mainMenu()

def quitFn():
    game.saveSettings()
    sys.exit(0)

def resetYesFn():
    scoreFile = open(game.settings.track[0]+"_scores.dat", 'w')
    scoreFile.close()
    scores2.scores=[]
    # leaderFn()
    mainMenu()

def resetFn():
    title = [game.settings.track[0].replace('_',' '), "", "Reset leader", "board?"]
    items = [ \
        ["no",  leaderFn,   []],
        ["yes", resetYesFn, []] ]
    doMenu(title, items, nobackground()) ()

def localFn():
    scores2.readScores()
    scores2.showScores(scores2.scores, "local")
    globals.keyWaitUp()
    mainMenu()

def leaderFn():
    bkgnd = background(game.settings.track, globals.screen)
    title = ["", "", "", "LEADER BOARD OPTIONS"]
    items = [ \
        ["View local leaders", localFn, []],
        ["Reset local board", resetFn, []],
        ["", mainMenu, []],
        ["Previous menu", mainMenu, []],
        [K_ESCAPE, mainMenu, []],
    ]
    doMenu(title, items, bkgnd) ()

class updateRenderer:
    def __init__(self, renderers):
        self.renderers = renderers
    def next(self):
        globals.renderer = globals.rendererMap[self.renderers[0]]
        if self.renderers[0]=="3-D Anaglyph" and game.settings.colors[0]!="B&W 2":
            while game.settings.colors[0]!="B&W 2":
                game.settings.colors.append(game.settings.colors.pop(0))
            globals.foreCol = globals.cmap["B&W 2"][0]
            globals.backCol = globals.cmap["B&W 2"][1]
            globals.midCol = (0.60*(globals.foreCol[0]-globals.backCol[0])+globals.backCol[0],
                0.60*(globals.foreCol[1]-globals.backCol[1])+globals.backCol[1],
                0.60*(globals.foreCol[2]-globals.backCol[2])+globals.backCol[2])
            renderFonts()
    def previous(self):
        self.next()

class updateFullscreen:
    def __init__(self):
        pass
    def next(self):
        if globals.fullscreen[0]=="on":
            globals.screen = pygame.display.set_mode((globals.XSIZE, globals.YSIZE), FULLSCREEN)
        else:
            globals.screen = pygame.display.set_mode((globals.XSIZE, globals.YSIZE))
    def previous(self):
        self.next()

class updateColors:
    def __init__(self, colors):
        self.colors = colors
    def next(self):
        if game.settings.renderers[0]=="3-D Anaglyph":
            game.settings.renderers.append(game.settings.renderers.pop(0))
            globals.renderer = globals.rendererMap[game.settings.renderers[0]]
        globals.foreCol = globals.cmap[self.colors[0]][0]
        globals.midCol = (0.60*(globals.foreCol[0]-globals.backCol[0])+globals.backCol[0],
            0.60*(globals.foreCol[1]-globals.backCol[1])+globals.backCol[1],
            0.60*(globals.foreCol[2]-globals.backCol[2])+globals.backCol[2])
        globals.backCol = globals.cmap[self.colors[0]][1]
        renderFonts()
    def previous(self):
        self.next()

def mainMenu():
    bkgnd = background(game.settings.track, globals.screen)
    colors = updateColors(game.settings.colors)
    fullscreen = updateFullscreen()
    displaymode = updateRenderer(game.settings.renderers)
    title = ["", "", "", "MAIN MENU"]
    items = [ \
        ["Start Race", raceFn,  []],
        ["Track:", bkgnd, game.settings.track, raceFn],
        ["Colors:", colors, game.settings.colors, None],
        ["Fullscreen Mode:", fullscreen, game.settings.fullscreen, None],
        ["Leader Board", leaderFn,  []],
        ["About VROOM!!!",  aboutFn, []],
        ["", quitFn, []],
        ["Quit Game", quitFn, []],
        [K_ESCAPE, quitFn, []],
    ]
    doMenu(title, items, bkgnd) ()

