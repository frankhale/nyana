# Editor Foundation - Provides the core foundation for a GTK+ based editor.
#
# Copyright (C) 2006-2007 Frank Hale <frankhale@gmail.com>
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

import inspect
import imp
import os.path

class Document(object):
	def __init__(self, filename):
		self.text = None
		self.filename = filename
				
	def open_document(self):
		if(os.path.exists(self.filename)):
			handle = open(self.filename, 'r')
			self.text = handle.read()
			handle.close()		

	def save_document(self, text):
		handle = open (self.filename, 'w')
		handle.write(text)
		handle.close()

class DocumentManager(object):
	def __init__(self):
		self.documents = {}

	def open_document(self, filename):
		doc = Document(filename)
		self.documents[filename]=doc
		
		doc.open_document()
		
		return doc.text

	def save_document(self, filename, text):
		if(filename):		
			if(self.documents.has_key(filename)):
				self.documents[filename].save_document(text)
			else:
				doc = Document(filename)
				self.documents[filename]=doc
				doc.save_document(text)

	def close_document(self, filename):
		if(self.documents.has_key[filename]):
			del self.documents[filename]

class EventManager(object):
	def __init__(self, editor):
		self.editor = editor
		self.event_listeners = {}
		
	def register_listener(self, event_name, callback):
		if(event_name and callback):
			if(self.event_listeners.has_key(event_name)):
				registered_callbacks = self.event_listeners[event_name]
				registered_callbacks.append(callback)
			else:
				self.event_listeners.update( { event_name : [ callback ] })				

	def unregister_listener(self, event_name, callback):
		if(event_name and callback):
			if(self.event_listeners.has_key(event_name)):
				registered_callbacks = self.event_listeners[event_name]
				
				if(callback in registered_callbacks):
					registered_callback.remove(callback)

	def get_registered_event_names(self):
		return [name for name in self.event_listeners.keys()]

	def fire_event(self, event_name, parms=None):
		if (event_name):
			if(self.event_listeners.has_key(event_name)):
				registered_callbacks = self.event_listeners[event_name]
				
				for callback in registered_callbacks:
					callback(parms)

class PluginManager(object):
	def __init__(self, editor):
		self.editor = editor

		# This is a tuple of key=value pairs which represent the plugin name and 
		# it's associated object created at plugin load time
		self.managed_plugins = {}	

	def intialize_plugins(self, plugin_dir):
		if(os.path.exists(plugin_dir)):			
			if(os.path.exists(os.path.join(plugin_dir, "__init__.py"))):				

				plugin_dir = os.path.abspath(plugin_dir)

				filenames = os.listdir(plugin_dir)			
				
				for filename in filenames:
					if(filename.endswith(".py") and not
					   filename.startswith("__init__")):
						obj_name = filename.strip(".py")						
						
						plugin_module = imp.load_source(obj_name, os.path.join(plugin_dir, filename))

						obj = getattr(plugin_module, obj_name)

						# Our plugin should be a class object		
						if(inspect.isclass(obj)):
							if(hasattr(obj, "__init__") and
			   				   hasattr(obj, "metadata") and
							   hasattr(obj, "load") and
							   hasattr(obj, "unload")
							):
								members = inspect.getargspec(obj.__init__)

								if("editor" in members[0]):
									if(obj.metadata.has_key("enabled")):
										if(obj.metadata["enabled"] is True):
											#print "Plugin Manager: loading %s" % (obj.metadata["name"])
										
											plugin = obj(self.editor)
											plugin.load()
								
											self.managed_plugins[obj_name] = plugin
								else:
									self.print_error(filename, "missing 'editor' argument in plugin __init__() method")	
						else:
							self.print_error(filename, "can't find class object")
		
	def print_error(self, filename, msg):
		print "Plugin Manager: (%s) does not conform to plugin protocol, %s" % (filename, msg)
						
	def tear_down_plugin(self, obj_name):
		if self.managed_plugins.has_key[obj_name]:
			self.managed_plugins[obj_name].unload()
			del self.managed_plugins[obj_name]

	def tear_down_all_plugins(self):
		for obj_name, plugin in self.managed_plugins.items():
			#print "Plugin Manager: unloading %s" % (plugin.metadata["name"])			
			plugin.unload()
			del obj_name
