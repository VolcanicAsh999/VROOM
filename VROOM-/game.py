
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

import pickle as cPickle
import globals

class defaultSettings:
	def __init__(self):
		self.leaderBoard = "local"
		self.sound = ["on", "off"]
		self.fullscreen = ["off", "on"]
		self.httpConnection = ["direct", "proxy"]
		self.track = globals.tracks
		self.fps = 50.0
		self.colors = globals.colors
		self.mvols = globals.mvols
		self.renderers = globals.renderers
		self.racerName = "anonymous"
		self.httpProxy = "http://"
		self.bkgnds=[]

def saveSettings():
	dumpFile = open("settings", 'wb')
	cPickle.dump(settings, dumpFile)
	dumpFile.close()

try:
	settingsFile = open("settings", 'rb')
	settings = cPickle.load(settingsFile)
	settingsFile.close()
except (IOError, EOFError) as e:
	settings = defaultSettings()

