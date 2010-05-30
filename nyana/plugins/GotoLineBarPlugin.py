# GotoLineBarPlugin - Provides a goto line bar which allows you to change lines within the editor easily
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
import gtk.gdk

class GotoLineBarPlugin(object):
	metadata = {
		"name" : "Goto Line Bar Plugin", 
		"authors" : ["Frank Hale <frankhale@gmail.com>"],
		"website" : "http://nyana.sourceforge.net",
		"version" : "0.2",
		"development status" : "beta",
		"date" : "13 Oct 2006",
		"enabled" : True,
		"short description" : "A goto line bar plugin",
		"long description" : "Provides a goto line bar that allows you to easily switch lines or jump to a new line."
	}
	
	def __init__(self, editor):
		self.editor = editor
		self.visible = False
		self.total_lines = 0
		self.current_line = 0

	def load(self):
		self.bar_table = gtk.Table(1, 3)
		self.bar_table.set_col_spacings(5)
		self.bar_table.set_row_spacings(1)		

		self.goto_label = gtk.Label("Goto Line:")
		self.adjustment = gtk.Adjustment(value=0, lower=0, upper=0, step_incr=1, page_incr=0, page_size=0)
		self.goto_button = gtk.SpinButton(self.adjustment, 0, 0)
		self.goto_button.connect("value-changed", self.switch_line)
		
		self.total_lines_label = gtk.Label()
		self.total_lines_label_align = gtk.Alignment(1.0,0.5)
		self.total_lines_label_align.add(self.total_lines_label)
				
		self.goto_label_align = gtk.Alignment(1.0,0.5)
		self.goto_label_align.add(self.goto_label)

		self.bar_table.attach(self.goto_label_align,0,1,1,2, gtk.SHRINK|gtk.FILL,gtk.EXPAND|gtk.FILL, 0, 0)
		self.bar_table.attach(self.goto_button,1,2,1,2, gtk.SHRINK|gtk.FILL,gtk.EXPAND|gtk.FILL, 0, 0)		
		self.bar_table.attach(self.total_lines_label_align,2,3,1,2, gtk.SHRINK|gtk.FILL,gtk.EXPAND|gtk.FILL, 0, 0)		

		self.editor.accel_group.connect_group(103, gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, self.show)
		self.editor.bottom_vbox.pack_end(self.bar_table, False, False, 0)
		
		self.editor.buff.connect("changed", self.update_ui)
		self.editor.buff.connect("mark-set", self.cursor_moved)

		self.update_move()		
		self.update_ui()

	def update_move(self):
		line_iter = self.editor.buff.get_iter_at_mark(self.editor.buff.get_insert())
		line = line_iter.get_line()+1 
		
		if not (self.current_line is line):
			self.current_line=line
			self.goto_button.set_text("%d" % (self.current_line))

	def cursor_moved(self, textbuffer, _iter, textmark, data=None):
		if(self.editor.buff.get_mark("insert")):
			self.update_move()

	def switch_line(self, data=None):
		line_iter = self.editor.buff.get_iter_at_line_offset((self.goto_button.get_value_as_int()-1), 0)
		line = self.goto_button.get_value_as_int()

		if not (self.current_line is line):
			self.editor.buff.place_cursor(line_iter)
			self.editor.source_view.grab_focus()
			
			self.editor.event_manager.fire_event("scroll_to_insert")

	def update_ui(self, data=None):
		# get total lines
		lines = self.editor.buff.get_line_count()
		
		if not(lines == self.total_lines):
			self.total_lines = lines
			
			# update total lines label and adjustments			
			self.total_lines_label.set_text( ("of %d" % (self.total_lines)) )
			self.goto_button.set_range(1, self.total_lines)
				
	def unload(self):
		pass

	def show(self, accel_group, acceleratable, keyval, modifier):
		if(self.visible):
			self.bar_table.hide_all()
			self.visible=False
		else:
			self.bar_table.show_all()
			self.visible=True
	
			# This is a hack, Maybe there is a bug in the spin button
			# unless the widget is in a shown state it doesn't appear to
			# update even though the code in the update_move method would
			# have already set the text on this widget.
			self.goto_button.set_text("%d" %(self.current_line))
