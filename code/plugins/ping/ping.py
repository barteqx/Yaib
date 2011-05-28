#*-* coding: utf-8 *-*
import os
import sys

def load(bot):
	return IRCPing(bot)
	
class IRCPing(object):
	def __init__(self, bot):
		self.bot = bot
		self.name = "ping"
		sys.path.append(self.bot.mainpath)
		import configuration
		self.configuration = configuration.ConfigFile('ping.cfg')
		try:
			self.configuration.loadFile()
		except configuration.LoadingError:
			self.configuration['message'] = 'PONG!'
			self.configuration.saveFile()
			
	def getMessage(self, message):
		try:
			msg = message['params'].split(' ', 1)
			if msg[0] == '!ping':
				try:
					self.bot.connection.send_msgs('PRIVMSG %s :%s\r\n' % (message['nick'], self.configuration['message'] % message['nick']))
				except:
					self.bot.connection.send_msgs('PRIVMSG %s :%s\r\n' % (message['nick'], self.configuration['message']))
		except:
			pass
		
	def getCommand(self, command, quiet=False):
		cmd = command['params'].split(' ', 1)
		if command['command'] == 'ping' and cmd[0] == 'message':
			self.bot.console.pluginApi.lock = True
			self.bot.console.lock = True
			self.configuration['message'] = cmd[1]
			self.configuration.saveFile()
		self.bot.console.lock = False
		
	def exit(self):
		self.configuration.saveFile()
