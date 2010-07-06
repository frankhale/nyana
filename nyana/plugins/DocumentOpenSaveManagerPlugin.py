# DocumentOpenSaveManager - Provides a mechanism to open / save a document within the editor.
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
import gtk.gdk
import os.path

class DocumentOpenSaveManagerPlugin(object):
	metadata = {
		"name" : "Document Open/Save Manager Plugin", 
		"authors" : ["Frank Hale <frankhale@gmail.com>"],
		"website" : "http://github.com/frankhale/nyana",
		"version" : "0.1",
		"development status" : "beta",
		"date" : "13 Oct 2006",
		"enabled" : True,
		"short description" : "Manages opening and saving of documents",
		"long description" : "Provides the ability to open and save documents graphically using GTK dialogs"
	}
	
	def __init__(self, editor):
		self.editor = editor
		self.opened_file=None

		self.editor.event_manager.register_listener("open_file", self.open_file_cb)

	def load(self):
		self.editor.accel_group.connect_group(110, gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, self.new_instance)
		self.editor.accel_group.connect_group(111, gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, self.open_dialog)
		self.editor.accel_group.connect_group(115, gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, self.save_dialog)

	def unload(self):
		# Unregister key-combo
		# Unregister events
		pass

	def new_instance(self, accel_group, acceleratable, keyval, modifier):
		self.editor.new_instance()

	def open_file_cb(self, parms):
		if(parms.has_key("filename")):
			self.file_open(parms["filename"])

	def file_open(self, filename):
		text = self.editor.document_manager.open_document(filename)

		self.opened_file = filename
		
		parms = { "filename" : filename, "text" : text }
		self.editor.event_manager.fire_event("buffer_change", parms)
		
		self.editor.window.set_title(self.editor.name + " [" + os.path.basename(filename) + "]")

		parms = { "message_pane_one" : "File: " + filename }
		self.editor.event_manager.fire_event("status_message_change", parms)
		
	def file_save_as(self, filename):
		text = self.editor.get_text()
		
		self.editor.document_manager.save_document(filename, text)

		self.opened_file = filename

		parms = { "filename" : filename, "text" : text }
		self.editor.event_manager.fire_event("buffer_change", parms)
		
		self.editor.window.set_title(self.editor.name + " [" + os.path.basename(filename) + "]")
	
		parms = { "message_pane_one" : "File: " + filename }
		self.editor.event_manager.fire_event("status_message_change", parms)

	def file_save(self):
		text = self.editor.get_text()

		self.editor.document_manager.save_document(self.opened_file, text)

	def open_dialog(self, accel_group, acceleratable, keyval, modifier):
		# Create a new file selection widget
        	diag = gtk.FileChooserDialog("Open File...", None, 
				gtk.FILE_CHOOSER_ACTION_OPEN, 
				(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))

		response = diag.run()
      	
		if response == gtk.RESPONSE_OK:
          		self.file_open(diag.get_filename())
			diag.destroy()
      		elif response == gtk.RESPONSE_CANCEL:
      			diag.destroy()

    	def save_dialog(self, accel_group, acceleratable, keyval, modifier):
		# Create a new file selection widget
        	if(self.opened_file):
			self.file_save()
			return
	
		diag = gtk.FileChooserDialog("File Save As...", None, 
				gtk.FILE_CHOOSER_ACTION_SAVE, 
				(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))

		response = diag.run()
      	
		if response == gtk.RESPONSE_OK:
          		self.file_save_as(diag.get_filename())
			diag.destroy()
      		elif response == gtk.RESPONSE_CANCEL:
      			diag.destroy()
