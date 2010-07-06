# TerminalPlugin - Provides a vte based terminal bar plugin for the editor
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
from vte import Terminal

class TerminalPlugin(object):
	metadata = {
		"name" : "Terminal Plugin", 
		"authors" : ["Frank Hale <frankhale@gmail.com>"],
		"website" : "http://github.com/frankhale/nyana",
		"version" : "0.1",
		"development status" : "alpha",
		"date" : "29 Oct 2006",
		"enabled" : True,
		"short description" : "A VTE based terminal plugin",
		"long description" : "Provides an embedded terminal inside the editor"
	}
	
	def __init__(self, editor):
		self.editor = editor
		self.visible = False

	def load(self):
		self.editor.accel_group.connect_group(116, gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, self.show_cb)
		
		self.bar_table = gtk.Table(3, 3)
		self.bar_table.set_col_spacings(10)
		self.bar_table.set_row_spacings(10)		
	
		self.initiate_terminal()
						
	def initiate_terminal(self):
		self.terminal = Terminal()
		self.terminal.set_emulation("xterm")
		self.terminal.set_audible_bell(False)
		self.terminal.set_scrollback_lines(100)
		self.terminal.set_size_request(80,140)
		self.terminal.connect("child-exited", self.terminal_exited)
		self.terminal.fork_command()		

		self.scrollbar = gtk.VScrollbar()
		self.scrollbar.set_adjustment(self.terminal.get_adjustment())

		self.hbox = gtk.HBox()
		self.hbox.pack_start(self.terminal, True, True, 0)
		self.hbox.pack_end(self.scrollbar, False, False, 0)
				
		self.bar_table.attach(self.hbox, 1,2,1,2, gtk.EXPAND|gtk.FILL,gtk.EXPAND|gtk.FILL, 0, 0)
		self.editor.bottom_vbox.pack_end(self.bar_table, False, False, 0)
				
	def terminal_exited(self, term):
		term.feed("Terminal exited\r\n", "1;34")
    term.feed("Press any key to close.")
    term.connect("commit", self.restart_cb)
		
  def restart_cb(self, term, data, datalen):
    self.terminal.reset(True, True)
    self.terminal.destroy()
    self.show()
    self.editor.bottom_vbox.remove(self.bar_table)
    self.initiate_terminal()
        	   
  def show(self):
    if(self.visible):
    self.bar_table.hide_all()
    self.visible=False
  else:
    self.bar_table.show_all()
    self.visible=True
    self.terminal.grab_focus()
        	        	
	def show_cb(self, accel_group, acceleratable, keyval, modifier):
		self.show()

	def unload(self):
		pass
