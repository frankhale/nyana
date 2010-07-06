# StatusbarPlugin - Provides a status bar plugin for the editor
#
# Copyright (C) 2006-2010 Frank Hale <frankhale@gmail.com>
#
# ##sandbox - irc.freenode.net
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
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
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pygtk 
pygtk.require('2.0')

import gtk

class StatusbarPlugin(object):
	metadata = {
		"name" : "Statusbar Plugin", 
		"authors" : ["Frank Hale <frankhale@gmail.com>"],
		"website" : "http://github.com/frankhale/nyana",
		"version" : "0.1",
		"development status" : "beta",
		"date" : "13 Oct 2006",
		"enabled" : True,
		"short description" : "A status bar plugin",
		"long description" : "A status bar plugin that allows for status information to be displayed."
	}
	
	def __init__(self, editor):
		self.editor = editor
		self.status = None

		self.editor.event_manager.register_listener("status_message_change", self.change_status_message)
		self.editor.event_manager.register_listener("clear_status_pane_one", self.clear_status_pane_one)
		self.editor.event_manager.register_listener("clear_status_pane_two", self.clear_status_pane_two)

	def clear_status_pane_one(self, parms=None):
		self.status_one.pop(self.status_pane_one)

	def clear_status_pane_two(self, parms=None):
		self.status_two.pop(self.status_pane_two)

	def change_status_message(self, parms):
		if(parms.has_key("message_pane_one")):
			self.status_one.pop(self.status_pane_one)
			self.status_one.push(self.status_pane_one, parms["message_pane_one"])
			
		if(parms.has_key("message_pane_two")):
			self.status_two.pop(self.status_pane_two)
			self.status_two.push(self.status_pane_two, parms["message_pane_two"])

		#if(parms.has_key("message_pane_three")):
		#	self.status_three.push(self.status_pane_three, parms["message_pane_three"])

	def load(self):
		self.status_one = gtk.Statusbar()
		self.status_pane_one = self.status_one.get_context_id("status_pane_one")
		
		self.status_two = gtk.Statusbar()
		self.status_pane_two = self.status_two.get_context_id("status_pane_two")

		#self.status_three = gtk.Statusbar()
		#self.status_pane_three = self.status_three.get_context_id("status_pane_three")
		
		self.status_one.set_has_resize_grip(False)
		#self.status_two.set_has_resize_grip(False)
	
		self.status_one.set_property("width-request", 500)
		
		#self.status_one.push(self.status_pane_one, "foo")
		#self.status_two.push(self.status_pane_two, "bar")
		
		self.hbox = gtk.HBox()
		self.hbox.pack_start(self.status_one, True, True, 0)
		self.hbox.pack_start(gtk.VSeparator(), False, False, 0)
		self.hbox.pack_end(self.status_two, True, True, 0)
		#self.hbox.pack_start(gtk.VSeparator(), False, False, 0)
		#self.hbox.pack_start(self.status_three, True, True, 0)
			
		self.editor.status_bar_vbox.pack_start(self.hbox, False, False, 0)

		self.hbox.show_all()

	def unload(self):
		pass
