# SamplePlugin - Provides a sample to show plugin structure
#
# Copyright (C) 2006 Frank Hale <frankhale@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import pygtk 
pygtk.require('2.0')

import gtk

class SamplePlugin(object):
	metadata = {
		"name" : "Sample Plugin", 
		"authors" : ["Frank Hale <frankhale@gmail.com>"],
		"website" : "http://nyana.sourceforge.net",
		"version" : "0.1",
		"development status" : "stable",
		"date" : "29 Oct 2006",
		"enabled" : True,
		"short description" : "A sample plugin",
		"long description" : "A sample plugin that does absolutely nothing."
	}
	
	def __init__(self, editor):
		# Gives you access to the editor foundation
		self.editor = editor

	def load(self):
		pass

	def unload(self):
		pass
