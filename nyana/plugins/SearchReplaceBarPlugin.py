# SearchReplaceBarPlugin - Provides a search and replace bar for the editor.
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
import re

class SearchReplaceBarPlugin(object):
	metadata = {
		"name" : "Search / Replace Bar Plugin", 
		"authors" : ["Frank Hale <frankhale@gmail.com>"],
		"website" : "http://nyana.sourceforge.net",
		"version" : "0.6",
		"development status" : "alpha",
		"date" : "30 Oct 2006",
		"enabled" : True,
		"short description" : "A search / replace bar plugin",
		"long description" : "A search / replace bar plugin that allows you to search for terms and optionally replace them with new terms."
	}
	
	def __init__(self, editor):
		self.editor = editor
		self.bar_visible = False
		self.bar_table = gtk.Table(2, 12)
		self.bar_table.set_col_spacings(5)
		self.bar_table.set_row_spacings(1)		
		self.find_tag = self.editor.buff.create_tag("find_tag", background="green")
		self.current_match=-1
		self.match_case = False
		self.match_word = False
		self.regex = False
		self.find_tags_applied = False
		self.match_marks = []
		self.next=0
		self.prev=0
		
	def search_entry_changed_cb(self, data=None):
		if(self.match_marks):
			self.remove_all_match_marks()
			self.current_match=0
			self.editor.event_manager.fire_event("clear_status_pane_two")

	def clear_applied_tags(self, data=None):
		if(self.find_tags_applied):
			self.remove_find_tags()
			
			if(self.match_marks):
				self.remove_all_match_marks()

	def match_word_cb(self, data=None):
		self.current_match=-1
	
		if(self.match_word):
			self.match_word=False
		else:
			self.match_word=True
			
		if(self.match_marks):
			self.remove_all_match_marks()
		
	def match_case_cb(self, data=None):
		self.current_match=-1
	
		if(self.match_case):
			self.match_case=False
		else:
			self.match_case=True
			
		if(self.match_marks):
			self.remove_all_match_marks()

	def regex_cb(self, data=None):
		self.current_match=-1
	
		if(self.regex):
			self.regex=False
		else:
			self.regex=True

		if(self.match_marks):
			self.remove_all_match_marks()

	def find_prev_cb(self, data=None):
		self.remove_find_tags()

		text = self.editor.get_text()
		find_me = self.search_entry.get_text()
		
		if(find_me):
			self.find_prev(find_me, text)

	def find_next_cb(self, data=None):
		self.remove_find_tags()

		text = self.editor.get_text()
		find_me = self.search_entry.get_text()
		
		if(find_me):
			self.find_next(find_me, text)

	def find_all_cb(self, data=None):
		self.remove_find_tags()

		text = self.editor.get_text()
		find_me = self.search_entry.get_text()
		
		if(find_me):
			self.find_all(find_me, text)

	def find_prev(self, find_me, text):
		if not (self.match_marks):
			self.match_marks = self.get_all_match_marks(find_me, text, self.match_word, self.match_case, self.regex)
		
		if(self.match_marks):
			if(self.prev is 1 or self.next is 1):
				self.current_match = self.current_match - 1
				self.prev=0
	
			self.prev = self.prev + 1
	
			if(self.current_match>=len(self.match_marks) or self.current_match<0):
				self.current_match=len(self.match_marks)-1		
					
			match = self.match_marks[self.current_match]

			parms = { "message_pane_two" : "match: %d of %d" % (self.current_match+1, len(self.match_marks)) }
			self.editor.event_manager.fire_event("status_message_change", parms)

			self.editor.source_view.scroll_mark_onscreen(match[0])
			
			start_iter = self.editor.buff.get_iter_at_mark(match[0])
			end_iter = self.editor.buff.get_iter_at_mark(match[1])
			
			self.editor.buff.apply_tag(self.find_tag, start_iter, end_iter)

			self.find_tags_applied = True		

	def find_next(self, find_me, text):
		if not (self.match_marks):
			self.match_marks = self.get_all_match_marks(find_me, text, self.match_word, self.match_case, self.regex)
		
		if(self.match_marks):
			if(self.next is 1 or self.prev is 1):
				self.current_match = self.current_match + 1
				self.next=0
			
			self.next = self.next + 1
			
			if(self.current_match>=len(self.match_marks) or self.current_match<0):
				self.current_match=0		
		
			match = self.match_marks[self.current_match]

			parms = { "message_pane_two" : "match: %d of %d" % (self.current_match+1, len(self.match_marks)) }
			self.editor.event_manager.fire_event("status_message_change", parms)

			self.editor.source_view.scroll_mark_onscreen(match[0])
			
			start_iter = self.editor.buff.get_iter_at_mark(match[0])
			end_iter = self.editor.buff.get_iter_at_mark(match[1])
			
			self.editor.buff.apply_tag(self.find_tag, start_iter, end_iter)

			self.find_tags_applied = True		

	def find_all(self, find_me, text):
		if not (self.match_marks):
			self.match_marks = self.get_all_match_marks(find_me, text, self.match_word, self.match_case, self.regex)
		
		if(self.match_marks):
			for match in self.match_marks:
				
				start_iter = self.editor.buff.get_iter_at_mark(match[0])
				end_iter = self.editor.buff.get_iter_at_mark(match[1])
			
				self.editor.buff.apply_tag(self.find_tag, start_iter, end_iter)

				if not(self.find_tags_applied):
					self.find_tags_applied = True

	def remove_find_tags(self):
		self.start_iter = self.editor.buff.get_start_iter()
		self.end_iter = self.editor.buff.get_end_iter()
		self.editor.buff.remove_tag(self.find_tag, self.start_iter, self.end_iter)
		self.find_tags_applied = False

	def get_all_match_indicies(self, search_string, search_text, match_word=False, match_case=False, regex=False):
		raw_matches = []
		indicies = []

		if not (regex):
			search_string = re.escape(search_string)
	
		if(match_word):
			search_string = "\\b" + search_string
				
		if(match_case):
			raw_matches = re.finditer(search_string, search_text)
		else:
			raw_matches = re.finditer(search_string, search_text, re.IGNORECASE)
	
		for m in raw_matches:
			indicies.append(m.span())
			
		return indicies

	def get_all_match_marks(self, search_string, text, match_word=False, match_case=False, regex=False):
		indicies = self.get_all_match_indicies(search_string, text, match_word, match_case, regex)
	
		match_marks = []
		
		for i in indicies:
			start_iter = self.editor.buff.get_iter_at_offset(i[0])
			end_iter = self.editor.buff.get_iter_at_offset(i[1])
			
			start_mark = self.editor.buff.create_mark(None, start_iter, True)
			end_mark = self.editor.buff.create_mark(None, end_iter, False)

			match_marks.append( (start_mark, end_mark) )	
			
		return match_marks				

	def replace_cb(self, data=None):
		find_me = self.search_entry.get_text()
		replace_with = self.replace_entry.get_text()
		text = self.editor.get_text()
				
		if(find_me and replace_with and text):
			self.replace(find_me, replace_with, text)
						
	def replace_all_cb(self, data=None):
		find_me = self.search_entry.get_text()
		replace_with = self.replace_entry.get_text()
		text = self.editor.get_text()
		
		if(find_me and replace_with and text):
			self.replace_all(find_me, replace_with, text)
			
	def replace_all(self, find_me, replace_with, text):
		if not (self.match_marks):
			self.match_marks = self.get_all_match_marks(find_me, text, self.match_word, self.match_case, self.regex)
		
		if(self.match_marks):
			self.current_match=0	
			
			total_matches = len(self.match_marks)
			
			while (self.match_marks):
				match = self.match_marks[0]
				start_iter = self.editor.buff.get_iter_at_mark(match[0])
				end_iter = self.editor.buff.get_iter_at_mark(match[1])			
				self.editor.buff.delete(start_iter, end_iter)
				self.editor.buff.insert(start_iter, replace_with)
				self.remove_match_marks(match)		

				self.current_match = self.current_match+1
		
				parms = { "message_pane_two" : "replacing: %d of %d" % (self.current_match, total_matches) }
				self.editor.event_manager.fire_event("status_message_change", parms)

	def remove_match_marks(self, item):
		if(self.match_marks):
			if(item):
				self.editor.buff.delete_mark(item[0])
				self.editor.buff.delete_mark(item[1])
				self.match_marks.remove(item)

	def replace(self, find_me, replace_with, text):
		if not (self.match_marks):
			self.match_marks = self.get_all_match_marks(find_me, text, self.match_word, self.match_case, self.regex)
			self.current_match=0
		
		if(self.match_marks):
			if(self.current_match>=len(self.match_marks) or self.current_match<0):
				#self.current_match=0
				return	
			
			match=self.match_marks[self.current_match]

			if(match):
				parms = { "message_pane_two" : "replacing: %d of %d" % (self.current_match+1, len(self.match_marks)) }
				self.editor.event_manager.fire_event("status_message_change", parms)

				start_iter = self.editor.buff.get_iter_at_mark(match[0])
				end_iter = self.editor.buff.get_iter_at_mark(match[1])		

				self.editor.buff.delete(start_iter, end_iter)
				self.editor.buff.insert(start_iter, replace_with)

				start_iter = self.editor.buff.get_iter_at_mark(match[0])
				end_iter = self.editor.buff.get_iter_at_mark(match[1])		
				
				self.editor.buff.apply_tag(self.find_tag, start_iter, end_iter)

				if not(self.find_tags_applied):
					self.find_tags_applied = True
			
				self.current_match=self.current_match+1
			
				#self.remove_match_marks(match)

	def remove_all_match_marks(self):
		if(self.match_marks):
			for i in self.match_marks:
				self.editor.buff.delete_mark(i[0])
				self.editor.buff.delete_mark(i[1])
				
			self.match_marks=[]
			self.current_match=0
			self.next=0
			self.prev=0
			
			self.editor.event_manager.fire_event("clear_status_pane_two")

			
	def create_search_bar(self):
		self.search_label = gtk.Label("Find:")
		self.search_entry = gtk.Entry()		
		self.search_entry.connect("changed", self.search_entry_changed_cb)

		self.search_align = gtk.Alignment(1.0,0.5)
		self.search_align.add(self.search_label)

		self.button_find = gtk.Button("Next")
		self.button_find.connect("clicked", self.find_next_cb)

		self.button_prev = gtk.Button("Prev")
		self.button_prev.connect("clicked", self.find_prev_cb)

		self.button_find_all = gtk.Button("Find All")
		self.button_find_all.connect("clicked", self.find_all_cb)

		self.match_label = gtk.Label("Match Case:")
		self.match_check_button = gtk.CheckButton()
		self.match_check_button.connect("toggled", self.match_case_cb)

		self.match_word_label = gtk.Label("Match Word:")
		self.match_word_check_button = gtk.CheckButton()
		self.match_word_check_button.connect("toggled", self.match_word_cb)

		self.regex_label = gtk.Label("Regex:")
		self.regex_check_button = gtk.CheckButton()
		self.regex_check_button.connect("toggled", self.regex_cb)

		self.bar_table.attach(self.search_align, 0,1,0,1, gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL, 0, 0)
		self.bar_table.attach(self.search_entry, 1,2,0,1, gtk.SHRINK|gtk.FILL,gtk.EXPAND|gtk.FILL, 0, 0)
		self.bar_table.attach(self.button_find, 2,3,0,1, gtk.SHRINK|gtk.FILL,gtk.EXPAND|gtk.FILL, 0, 0)
		self.bar_table.attach(self.button_prev, 3,4,0,1, gtk.SHRINK|gtk.FILL,gtk.EXPAND|gtk.FILL, 0, 0)
		self.bar_table.attach(self.button_find_all, 4,5,0,1, gtk.SHRINK|gtk.FILL,gtk.EXPAND|gtk.FILL, 0, 0)			
		self.bar_table.attach(gtk.VSeparator(), 5,6,0,1, gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL, 0, 0)
		self.bar_table.attach(self.match_label, 6,7,0,1, gtk.SHRINK|gtk.FILL,gtk.EXPAND|gtk.FILL, 0, 0)
		self.bar_table.attach(self.match_check_button, 7,8,0,1, gtk.SHRINK|gtk.FILL,gtk.EXPAND|gtk.FILL, 0, 0)
		self.bar_table.attach(self.match_word_label, 8,9,0,1, gtk.SHRINK|gtk.FILL,gtk.EXPAND|gtk.FILL, 0, 0)
		self.bar_table.attach(self.match_word_check_button, 9,10,0,1, gtk.SHRINK|gtk.FILL,gtk.EXPAND|gtk.FILL, 0, 0)
		self.bar_table.attach(self.regex_label, 10,11,0,1, gtk.SHRINK|gtk.FILL,gtk.EXPAND|gtk.FILL, 0, 0)
		self.bar_table.attach(self.regex_check_button,11,12,0,1, gtk.SHRINK|gtk.FILL,gtk.EXPAND|gtk.FILL, 0, 0)

		self.editor.accel_group.connect_group(102, gtk.gdk.CONTROL_MASK, gtk.ACCEL_LOCKED, self.show_search_bar)
	
	def create_replace_bar(self):
		self.replace_label = gtk.Label("Replace:")
		self.replace_entry = gtk.Entry()		
		
		self.replace_label_align = gtk.Alignment(1.0,0.5)
		self.replace_label_align.add(self.replace_label)

		self.button_replace = gtk.Button("Replace")
		self.button_replace.connect("clicked", self.replace_cb)
		
		self.button_replace_all = gtk.Button("Replace All")
		self.button_replace_all.connect("clicked", self.replace_all_cb)

		self.button_clear_tags = gtk.Button("Clear Find Tags")
		self.button_clear_tags.connect("clicked", self.clear_applied_tags)

		self.bar_table.attach(self.replace_label_align, 0,1,1,2, gtk.SHRINK|gtk.FILL,gtk.EXPAND|gtk.FILL, 0, 0)
		self.bar_table.attach(self.replace_entry, 1,2,1,2, gtk.SHRINK|gtk.FILL,gtk.EXPAND|gtk.FILL, 0, 0)		
		self.bar_table.attach(self.button_replace, 2,3,1,2, gtk.SHRINK|gtk.FILL,gtk.EXPAND|gtk.FILL, 0, 0)
		self.bar_table.attach(self.button_replace_all, 3,4,1,2, gtk.SHRINK|gtk.FILL,gtk.EXPAND|gtk.FILL, 0, 0)
		self.bar_table.attach(self.button_clear_tags, 4,5,1,2, gtk.SHRINK|gtk.FILL,gtk.EXPAND|gtk.FILL, 0, 0)

	def load(self):
		self.create_search_bar()
		self.create_replace_bar()
		self.editor.bottom_vbox.pack_end(self.bar_table, False, False, 0)

	def show_search_bar(self, accel_group, acceleratable, keyval, modifier):
		if(self.bar_visible):
			self.bar_table.hide_all()
			self.bar_visible=False

			self.remove_find_tags()
		else:
			self.bar_table.show_all()
			self.bar_visible=True

			self.search_entry.grab_focus()
	
	def unload(self):
		pass
