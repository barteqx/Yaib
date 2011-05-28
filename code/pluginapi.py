#*-* coding: utf-8 *-*
import threading
import os
import sys
try:
	sys.path.append('/usr/share/lib/yaib/')
except:
	pass
	
class IncorrectPlugin(Exception):
	pass

class PluginAPI(threading.Thread):
	
	def __init__(self, bot):
		threading.Thread.__init__(self)
		self.bot = bot
		self.plugins = {}
		self.lock = False
		
	def getMessage(self, message):
		for plugin in self.plugins.keys():
			try:
				self.plugins[plugin].getMessage(message)
			except:
				del self.plugins[plugin]
			
	def getCommand(self, command, quiet=False):
		for plugin in self.plugins.keys():
			try:
				self.plugins[plugin].getCommand(command, quiet)
			except:
				del self.plugins[plugin]
		if self.lock == False:
			raise AttributeError
		self.lock = False
			
	def execute(self, plugin):
		sys.path.append('%s/plugins/%s' % (self.bot.mainpath, plugin))
		plug = __import__(plugin)
		self.plugins[plugin] = plug.load(self.bot)
		try:
			if not callable(self.plugins[plugin].getCommand) or not callable(self.plugins[plugin].getMessage):
				del self.plugins[plugin]
				raise IncorrectPlugin
		except AttributeError:
			del self.plugins[plugin]
			raise IncorrectPlugin
	
	def unload(self, plugin):
		self.plugins[plugin].exit()
		del self.plugins[plugin]
