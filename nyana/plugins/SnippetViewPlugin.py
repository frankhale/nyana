# SnippetViewPlugin - Provides a templated/abbreviation expansion mechanism for 
# the editor.
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

import gio
import gtk
import gtk.gdk
import gtksourceview2
import pango
import re
import datetime
import os.path
import xml.etree.ElementTree as ET

SNIPPET_XML = "snippets.xml"

MIME_ALIAS = { 
	"text/x-python" : ["python"], 
	"application/x-ruby" : ["ruby", "rails"]
}

# Change Date/Time formats as needed
DATE_FORMAT = "%B %d %Y"
TIME_FORMAT = "%H:%M"

DATE = datetime.datetime.now().strftime(DATE_FORMAT)
TIME = datetime.datetime.now().strftime(TIME_FORMAT)
DATETIME = "%s @ %s" % (datetime.datetime.now().strftime(DATE_FORMAT), datetime.datetime.now().strftime(TIME_FORMAT))

class Snippet:
	def __init__(self):
		self.language=""
		self.shortcut=""
		self.snippet=""

	def mimetype(self):
		return MIME[self.language]

class SnippetLoader:
	def load_all(self):
		SNIPPETS = []

		root = ET.parse(SNIPPET_XML)

		for snippet in root.getiterator("snippet"):
			if snippet.get("language") and snippet.get("shortcut"):
				snip = Snippet()
				snip.language = snippet.get("language")
				snip.shortcut = snippet.get("shortcut")
				snip.snippet = snippet.text.strip()

				SNIPPETS.append(snip)

		return SNIPPETS

	def load(self, language):
		all_snips = self.load_all()

		return [s for s in all_snips if s.language==language]

	def get_common(self):
		return self.load("common")

# Common snippets that are useful regardless of document, used for built in snippets
COMMON_SNIPPETS = {
	"^d" 	: DATE, # expands to the current date supplied by the date format above
	"^t" 	: TIME, # expands to the current time supplied by the time format above
	"^dt" 	: DATETIME # expands to a combination of the date and time supplied by the formats above
}

BUILT_IN_SNIPPETS = []

# For each of the common snippets make a Snippet object, plug in the key,value and add it to the built in snippets
# list
for KEY,VALUE in COMMON_SNIPPETS.items():
	s = Snippet()
	s.shortcut = KEY
	s.snippet = VALUE
	s.language = "common"

	BUILT_IN_SNIPPETS.append(s)

class SnippetViewPlugin(object):
	metadata = {
		"name" : "Snippet Source View Plugin", 
		"authors" : ["Frank Hale <frankhale@gmail.com>"],
		"website" : "http://github.com/frankhale/nyana",
		"version" : "0.6.0",
		"development status" : "beta",
		"date" : "31 JULY 2007",
		"enabled" : True,
		"short description" : "Provides abbreviation expansion via tab key",
		"long description" : "Provides a snippet feature which allows one to create abbreviations that are expandable by hitting the tab key. Special variables can be inserted into the snippets to make them tabbable and provide a quick way to create code."
	}
	
	def __init__(self, editor):
		self.editor = editor
		
		self.editor.event_manager.register_listener("buffer_change", self.event_buffer_change)
		self.editor.event_manager.register_listener("scroll_to_insert", self.scroll_to_insert)

		self.editor.source_view.set_highlight_current_line(True)
		self.editor.source_view.set_wrap_mode(gtk.WRAP_NONE)

		# regular expression used to find our special variables.
		# 
		# variables look like ${foo}
		self.variable_re = re.compile('\${([^\${}]*)}')

		self.SNIPPETS = []

		self.SNIPPET_MARKS = []
		self.SNIPPET_OFFSETS = []

		self.SNIPPET_START_MARK = None
		self.SNIPPET_END_MARK = None
		self.IN_SNIPPET = False	
		self.HAS_NO_VARIABLES=False
		self.TABBED = True

		self.mime_type = None
		
		self.editor.source_view.set_show_line_numbers(True)
		self.editor.source_view.set_auto_indent(True)
		self.editor.source_view.set_resize_mode(gtk.RESIZE_PARENT)
		
		### Comment this out if you don't want Monospace and want the default
		### system font. Or change to suit your needs. 
		default_font = pango.FontDescription("Monospace 10")
		
		if default_font:
			self.editor.source_view.modify_font(default_font)
		### -------------------------------------------------------- ###
				
		self.editor.source_view.connect("key-press-event", self.key_event)
		self.editor.buff.connect("mark-set", self.mark_set)

		self.SL = SnippetLoader()

		self.SNIPPETS.extend(self.SL.get_common())
		self.SNIPPETS.extend(BUILT_IN_SNIPPETS)

		# For testing purposes.
		#self.syntax_highlight(os.path.abspath("/home/majyk/dev/python/test.py"))
		
	def load_snippets(self):
		types = []

		try:
			types = MIME_ALIAS[self.mime_type]
		except KeyError:
			print "This mime-type has no snippets defined"
			types=None

		if not types == None:
			print types

			if len(types)==1:
				self.SNIPPETS.extend(self.SL.load(types[0]))
			elif len(types)>1:
				for t in types:
					self.SNIPPETS.extend(self.SL.load(t))

			#print "snippets available:"		
				
			#for s in self.SNIPPETS:
			#	print s.shortcut

	def scroll_to_insert(self, parms=None):
		self.editor.source_view.scroll_mark_onscreen( self.editor.buff.get_mark("insert"))

	def event_buffer_change(self, parms):
		if(parms.has_key("filename") and parms.has_key("text")):
			self.set_text(parms["filename"], parms["text"])

	def set_text(self, filename, text):
		if(filename):
			self.syntax_highlight(filename)
			self.editor.buff.set_text(text)
			self.editor.buff.place_cursor(self.editor.buff.get_start_iter())
		
	def mark_set(self, textbuffer, _iter, textmark):
		# if we are in a snippet and the user moves the cursor out of the snippet bounds without
		# finishing the snippet then we need to clean up and turn the snippet mode off		
		if self.IN_SNIPPET and self.SNIPPET_START_MARK and self.SNIPPET_END_MARK:
			SNIPPET_START_ITER = self.editor.buff.get_iter_at_mark(self.SNIPPET_START_MARK)
			SNIPPET_END_ITER = self.editor.buff.get_iter_at_mark(self.SNIPPET_END_MARK)
			
			curr_iter = self.get_cursor_iter()
				
			if not curr_iter.in_range(SNIPPET_START_ITER, SNIPPET_END_ITER):
				if self.SNIPPET_START_MARK and self.SNIPPET_END_MARK:
					self.IN_SNIPPET = False

	# Do mime-type magic and switch the language syntax highlight mode and snippets
	def syntax_highlight(self, filename):
		if not (os.path.exists(filename)):
			print "(%s) does not exist" % (filename)
			return

		print "filename = (%s)" % (filename)
		
		language = self.get_language(filename)

		if language:
			self.editor.buff.set_highlight_syntax(True)
			self.editor.buff.set_language(language)

			#print "Setting the snippets to the following language mime-type: " + mime_type
	
			self.load_snippets()
		else:
			print "A syntax highlight mode for this mime-type does not exist."
			self.editor.buff.set_highlight_syntax(False)

	def complete_special_chars(self, widget, char):
		curr_iter = self.editor.buff.get_iter_at_mark( self.editor.buff.get_insert() )
		self.editor.buff.insert(curr_iter, char)
		curr_iter = self.editor.buff.get_iter_at_mark( self.editor.buff.get_insert() )
		curr_iter.backward_chars(1)
		self.editor.buff.place_cursor(curr_iter)

	def get_cursor_iter(self):
		cursor_mark = self.editor.buff.get_insert()
		cursor_iter = self.editor.buff.get_iter_at_mark(cursor_mark)
		return cursor_iter

	def get_line_number(self):
		cursor_iter = self.get_cursor_iter(self.editor.buff)
		line_number = cursor_iter.get_line()
		return line_number

	# Adds marks into the buffer for the start and end offsets for each variable
	def mark_variables(self, offsets):
		marks = []

		for o in offsets:
			start_iter = self.editor.buff.get_iter_at_offset(o["start"])
			end_iter = self.editor.buff.get_iter_at_offset(o["end"])
		
			start_mark = self.editor.buff.create_mark(None, start_iter, True)
			end_mark = self.editor.buff.create_mark(None, end_iter, False)
			
			insert_mark = { "start" : start_mark, 
					"end" : end_mark }
					
			marks.append(insert_mark)
		
		return marks

	# This algorithm gets variable offsets so that we can use those offsets
	# to get iterators to create marks, the marks are used in order to select
	# the text and move the cursor using the tab key
	#
	# This does a little more than just get the variable offsets, it also
	# deletes the variable and replaces it with just the word identifier
	#
	# If the variable is a ${cursor} it will delete it and get it's start offset
	# so when we mark it we can tab to a nonvisibly marked location in the snippet.
	def get_variable_offsets(self,string, current_offset):
		offsets = []
		start_and_end_offsets = {}
		
		# use the regular expression to get an iterator over our string
		# variables will hold match objects
		variables = self.variable_re.finditer(string)
		
		for var in variables:
			occur_offset_start = current_offset + var.span()[0]
			occur_offset_end = current_offset + var.span()[1]
			
			start_iter = self.editor.buff.get_iter_at_offset(occur_offset_start)
			end_iter = self.editor.buff.get_iter_at_offset(occur_offset_end)
			
			# delete the full variable
			self.editor.buff.delete(start_iter, end_iter)

			# if it's a ${cursor} variable we don't want to insert
			# any new text. Just go to the else and get it's start
			# offset, used later to mark that location
			if not var.group() == "${cursor}":

				# insert the variable identifier into the buffer
				# at the start location
				self.editor.buff.insert(start_iter, var.group(1))

				current_offset = current_offset-3

				# record our start and end offsets used later
				# to mark these variables so we can select the text
				start_and_end_offsets = { 
					"start" : occur_offset_start,
					"end"   : occur_offset_end-3
				}

				#print "START = %d | END = %d" % (start_and_end_offsets["start"], start_and_end_offsets["end"])
			else:
				# if we have a ${cursor} then we want a 
				# marker added with no text so we can
				# tab to it.
				start_and_end_offsets = { 
					"start" : occur_offset_start,
					"end"   : occur_offset_start
				}
			
				current_offset = current_offset-len(var.group())
			
			# put the start/end offsets into a list of dictionaries	
			offsets.append( start_and_end_offsets )
			
		return offsets

	# This functions purpose is to add spaces/tabs to the snippets according
	# to what level we have indented to
	def auto_indent_snippet(self, snippet):
		cursor_iter = self.get_cursor_iter()
		line_number = cursor_iter.get_line()
		start_of_current_line_iter = self.editor.buff.get_iter_at_line(line_number)
	
		text = self.editor.buff.get_text(cursor_iter, start_of_current_line_iter)
	
		space_re = re.compile(' ')
		tab_re = re.compile('\t')
		
		tab_count = len(tab_re.findall(text))
		space_count = len(space_re.findall(text))
		
		lines = snippet.split("\n")

		new_lines = []
		tabs = ""	
		spaces = ""
	
		if tab_count > 0:
			for i in range(tab_count):
				tabs = tabs + "\t"	
	
		if space_count > 0:
			for i in range(space_count):
				spaces = spaces + " "	
			
		for i,line in enumerate(lines):
			# don't add any of the spaces/tabs to the first
			# line in the snippet
			if not i == 0:
				snip = tabs + spaces + line
				new_lines.append(snip)
			else:
				new_lines.append(line)
		
		return "\n".join(new_lines)

	def snippet_completion(self):
		cursor_iter = self.get_cursor_iter()
		line_number = cursor_iter.get_line()
		start_of_current_line_iter = self.editor.buff.get_iter_at_line(line_number)
				
		text = self.editor.buff.get_text(start_of_current_line_iter, cursor_iter)
		
		words = text.split()
	
		if words:
			word_last_typed = words.pop()
		
			word_index = text.find(word_last_typed)

			# Run through all snippets trying to find a match
			for s in self.SNIPPETS:
				key=s.shortcut
				value=s.snippet

				if word_last_typed == key:
					self.TABBED = True

					value = self.auto_indent_snippet(value)

					word_index = text.rfind(word_last_typed)
					index_iter = self.editor.buff.get_iter_at_line_offset(line_number, word_index)
					end_iter = self.editor.buff.get_iter_at_line_offset(line_number, word_index+len(word_last_typed))
				
					self.editor.buff.delete(index_iter, end_iter)				
					overall_offset = index_iter.get_offset()
						
					self.editor.buff.insert(index_iter, value)
	
					start_mark_iter = self.editor.buff.get_iter_at_line_offset(line_number, word_index)
					end_mark_iter = self.editor.buff.get_iter_at_offset(start_mark_iter.get_offset()+len(value))
					self.SNIPPET_START_MARK = self.editor.buff.create_mark(None, start_mark_iter, True)
					self.SNIPPET_END_MARK = self.editor.buff.create_mark(None, end_mark_iter, False)
					
					offsets = self.get_variable_offsets(value, overall_offset)
							
					if offsets:				
						marks = self.mark_variables(offsets)
						
						if marks:
							_iter = self.editor.buff.get_iter_at_offset( offsets[0]["start"] )
							
							self.editor.buff.place_cursor(_iter)
	
							marks.reverse()
	
							for mark in marks:
								self.SNIPPET_MARKS.insert(0, mark)
	
							offsets.reverse()
	
							for offset in offsets:
								self.SNIPPET_OFFSETS.insert(0,offset)

							self.IN_SNIPPET = True
					else:
						self.HAS_NO_VARIABLES=True

	def pair_text(self, pair_chars):
		selection = self.editor.buff.get_selection_bounds()
	
		if(selection):
			selected_text = self.editor.buff.get_text(selection[0], selection[1])
			self.editor.buff.delete(selection[0], selection[1])				
			self.editor.buff.insert_at_cursor("%s%s%s" % (pair_chars[0],selected_text,pair_chars[1]))
			return True
	
		return False

	def comment_line(self, comment_char):
		selection = self.editor.buff.get_selection_bounds()
		
		if(selection):
			selected_text = self.editor.buff.get_text(selection[0], selection[1])
			
			self.editor.buff.delete(selection[0], selection[1])				
			
			for line in selected_text.splitlines(True):
				self.editor.buff.insert_at_cursor("%s %s" % (comment_char, line))
			
			return True
			
		return False
	
	def key_event(self, widget, key_press):
		keycodes = {
			"space" 	: 32,
			"tab" 		: 65289,
			"quote" 	: 34,
			"open_brace" 	: 123,
			"open_bracket" 	: 91,
			"open_paren" 	: 40,
			"less_than" 	: 60,
			"single_quote" 	: 39,
			"pound"		: 35
		}
	
		# Need to add a new key, just uncomment this, run the program
		# and look at the output from the key press
		#print key_press.keyval

		if not key_press.keyval == keycodes["tab"]:
			self.TABBED = False

		if key_press.keyval == keycodes["pound"]:
			if key_press.state & gtk.gdk.SHIFT_MASK:
			
				comment_char = None
				
				if(self.mime_type == ("text/x-python") or 
				   self.mime_type == ("application/x-ruby") or
				   self.mime_type == ("application/x-shellscript")
				   ):
					comment_char = "#"
				elif (self.mime_type == ("text/x-java") or
				      self.mime_type == ("text/x-c++src") 
				):
					comment_char = "//"
				
				if(comment_char):			
					if(self.comment_line(comment_char)):
						return True
		
		if key_press.keyval == keycodes["quote"]:
			if (self.pair_text(["\"", "\""])):
				return True
		
		elif key_press.keyval == keycodes["open_brace"]:
			if (self.pair_text(["{", "}"])):
				return True
		
		elif key_press.keyval == keycodes["open_bracket"]:
			if (self.pair_text(["[", "]"])):
				return True
		
		elif key_press.keyval == keycodes["open_paren"]:
			if (self.pair_text(["(", ")"])):
				return True
		
		elif key_press.keyval == keycodes["less_than"]:
			if (self.pair_text(["<", ">"])):
				return True
		
		elif key_press.keyval == keycodes["single_quote"]:
			if (self.pair_text(["\'", "\'"])):
				return True
		
		elif key_press.keyval == keycodes["tab"]:
			if not self.TABBED:	
				self.snippet_completion()
				
				if self.HAS_NO_VARIABLES:
					self.HAS_NO_VARIABLES=False
					return True

			if(len(self.SNIPPET_MARKS)>0):
				for i, v in enumerate(self.SNIPPET_MARKS):
					if len(self.SNIPPET_MARKS)>1:
						self.editor.source_view.scroll_mark_onscreen(self.SNIPPET_MARKS[i+1]["start"])
		
					_iter = self.editor.buff.get_iter_at_mark(v["start"])
					mark_offset = _iter.get_offset()
						
					self.editor.buff.select_range( self.editor.buff.get_iter_at_mark(v["start"]),  self.editor.buff.get_iter_at_mark(v["end"]))
		
					self.editor.buff.delete_mark(v["start"])
					self.editor.buff.delete_mark(v["end"])
						
					del self.SNIPPET_MARKS[i]
					del self.SNIPPET_OFFSETS[i]
		
					if (i==len(self.SNIPPET_OFFSETS)):
						self.IN_SNIPPET = False
						
						self.editor.buff.delete_mark(self.SNIPPET_START_MARK)
						self.editor.buff.delete_mark(self.SNIPPET_END_MARK)
									
					break

				return True
			
			return False

	def load(self):
		pass
	
	def unload(self):
		pass
  
	def __get_language_for_mime_type(self, mime):
		from gtksourceview2 import language_manager_get_default
		lang_manager = language_manager_get_default()
		lang_ids = lang_manager.get_language_ids()
		for i in lang_ids:
			lang = lang_manager.get_language(i)
			for m in lang.get_mime_types():
				if m == mime: return lang
		return None

	def get_language(self, uri):
		try:
			if uri is None: return None
			from gnomevfs import get_mime_type
		
			self.mime_type = gio.File(uri.strip()).query_info("*").get_content_type()

			language = self.__get_language_for_mime_type(self.mime_type)
		except RuntimeError:
			print "Caught runtime error when determining mimetype or language"
			return None
		return language

