import pygtk 
pygtk.require('2.0')

import gtk

class WordCompletionPlugin(object):
	metadata = {
		"name" : "Word Completion Plugin", 
		"authors" : ["Frank Hale <frankhale@gmail.com>"],
		"website" : "http://nyana.sourceforge.net",
		"version" : "0.1",
		"development status" : "pre-alpha",
		"date" : "2 DEC 2006",
		"enabled" : False,
		"short description" : "Provides suggestions for word completion",
		"long description" : "Provides suggestions as you type based on words you have already used in order to speed up your writing/coding."
	}

	def __init__(self, editor):
		self.editor = editor

		self.editor.buff.connect("changed", self.buffer_changed)

	def buffer_changed(self, textbuffer, user_parm=None):
		start=textbuffer.get_start_iter()
		end=textbuffer.get_end_iter()

		text = textbuffer.get_text(start, end)

		unique_list = [word for word in list(set(text.split())) if len(word)>3]
		
		print unique_list	

	def load(self):
		pass
	
	def unload(self):
		pass
