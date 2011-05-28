#*-* coding: utf-8 *-*
import threading
import commands
import language
import configuration
import re
import datetime
import time
import pluginapi
import os
import socket

class Console(threading.Thread):
	
	def __init__(self, bot):
		threading.Thread.__init__(self)
		self.bot = bot
		self.working = True
		self.bot.configuration = configuration.ConfigFile('console.cfg', self.bot.path)
		try:
			self.bot.configuration.loadFile()
		except configuration.LoadingError:
			self.configure()
		self.language = language.Language(self.bot.configuration['lang'])
		self.commandThread = CommandThread(self)
		self.currentCommand = {'command': None, 'params': None, 'time': None, 'source': None}
		self.lastCommand = {'command': None, 'params': None, 'time': None, 'source': None}
		self.commands = commands.Commands(bot, self)
		self.pluginApi = pluginapi.PluginAPI(self.bot)
		self.lock = False
		self.temportaryNick = self.bot.configuration['nick']
		
		
	def parseCommand(self, command, source = 'console'):
		parsedCommand = command.split(' ',1)
		if parsedCommand:
			self.currentCommand['command'] = parsedCommand[0]
			try:
				self.currentCommand['params'] = parsedCommand[1]
			except IndexError:
				self.currentCommand['params'] = None
			self.currentCommand['time'] = datetime.datetime.now()
			self.currentCommand['source'] = source
		else:
			pass
		return self.currentCommand
			
		
	def run(self):
		print self.language["Yet Another IRC Bot v. %s\nType 'help' to get some help"] % self.bot.version
		self.autorun()
		self.commandThread.start()
				
	def getCommand(self, command, quiet=False):
		try:
			getattr(self.commands, command['command'])(params = command['params'], quiet=quiet)
		except AttributeError, msg:
			try:
				self.pluginApi.getCommand(self.currentCommand, quiet)
			except AttributeError:
				if not quiet:
					print self.language["%s: command not found"] % command['command']
				else:
					raise AttributeError
		except socket.error, msg:
			print msg
		except TypeError:
			print self.language["%s: command not found"] % command['command']
			
	def autorun(self):
		for command in self.bot.configuration['autorun']:
			self.parseCommand(command)
			self.getCommand(self.currentCommand)
		for plugin in self.bot.configuration['plugins']:
			try:
				self.pluginApi.execute(plugin)
			except pluginapi.IncorrectPlugin:
				del plugin
	def afterconnect(self):
		for command in self.bot.configuration['afterconnect']:
			self.parseCommand(command)
			self.getCommand(self.currentCommand)
			
	def autojoin(self):
		for channel in self.bot.configuration['channels'].keys():
			try:
				self.bot.connection.join(channel, self.bot.configuration['channels'][channel])
			except:
				pass
				
	def configure(self, key = '', value = ''):
		if not key:
			self.bot.configuration['nick'] = raw_input('Nick:\n> ')
			self.bot.configuration['pass'] = raw_input('Password (can be empty):\n> ')
			self.bot.configuration['host'] = raw_input('Host:\n> ')
			self.bot.configuration['port'] = raw_input('Port:\n> ')
			self.bot.configuration['username'] = raw_input('Username:\n> ')
			self.bot.configuration['realname'] = raw_input('Real name:\n> ')
			self.bot.configuration['lang'] = raw_input('Language:\n> ')
			self.bot.configuration['autorun'] = []
			self.bot.configuration['afterconnect'] = []
			self.bot.configuration['plugins'] = ['ping', 'kiss', 'seen']
			self.bot.configuration['channels'] = {}
			self.bot.configuration.saveFile()
		
		else:
			if key in self.bot.configuration.keys() and value:
				self.bot.configuration[key] = value
				
			else:
				print self.language['Not enough parameters']

class CommandThread(threading.Thread):
	def __init__(self, console):
		threading.Thread.__init__(self)
		self.console = console
	
	def run(self):
		while self.console.working:
			os.chdir(self.console.bot.mainpath)
			while not self.console.lock:
				self.console.parseCommand(raw_input('%s >>> ' % self.console.bot.configuration['nick']))		
				self.console.getCommand(self.console.currentCommand)
