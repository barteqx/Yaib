#*-* coding: utf-8 *-*
import sys
sys.path.append('../..')
import configuration

def load(bot):
	return Auth(bot)
	
class Auth(object):
	
	def __init__(self, bot):
		self.bot = bot
		self.configuration = configuration.ConfigFile('auth.cfg')
		try:
			self.configuration.loadFile()
		except configuration.LoadingError:
			self.configuration.saveFile()
	def getCommand(self, command, quiet=False):
		if command['command'] == 'auth':
			self.bot.console.pluginApi.lock = True
			self.bot.console.lock = True
			params = command['params'].split(' ', 2)
			if params[0] == 'list':
				for user in self.configuration.configuration.keys():
					if not quiet: print "%s %s %s" % (user.ljust(20), self.configuration[user]['pass'].ljust(20), self.configuration[user]['online'])
			elif params[0] == 'set':
				try:
					self.configuration[params[1]] = {'pass': params[2], 'online': False}
				except IndexError:
					if not quiet: print "auth: not enough parameters for 'set' command"
			
			elif params[0] == 'del':
				try:
					del self.configuration[params[1]]
				except (KeyError, IndexError):
					if not quiet: print "auth: invalid <user> parameter"
			else:
				if not quiet: print "auth: invalid parameter(s)"

			self.bot.console.lock = False
	
	def getMessage(self, message):
		try:
			params = message['params'].split(' ', 1)
		except:
			pass
		try:
			if message['nick'] in self.configuration.configuration.keys() and self.configuration[message['nick']]['user'] != message['username'] or self.configuration[message['nick']]['host'] != message['hostname']:
				self.configuration[message['nick']]['online'] = False
		except:
			pass
		if message['msgtype'] == 'QUIT' and message['nick'] in self.configuration.configuration.keys():
				self.configuration[message['nick']]['online'] = False
				
		if message['msgtype'] == 'PRIVMSG' and params[0] == '!auth':
			if message['nick'] in self.configuration.configuration.keys():
				if params[1] == self.configuration[message['nick']]['pass']:
					self.configuration[message['nick']]['online'] = True
					self.configuration[message['nick']]['host'] = message['hostname']
					self.configuration[message['nick']]['user'] = message['username']
					self.bot.connection.send_msgs('NOTICE %s :You are authenticated\r\n' % message['nick'])
				else:
					self.bot.connection.send_msgs('NOTICE %s :Invalid password\r\n' % message['nick'])
		if message['msgtype'] == 'PRIVMSG' and message['nick'] in self.configuration.configuration.keys() and self.configuration[message['nick']]['online'] and params[0] == '!c':
				try:
					command = self.bot.console.parseCommand(params[1])
					if command:
						self.bot.console.getCommand(command=command, quiet=True)
					else: raise AttributeError
				except IndexError:
					self.bot.connection.send_msgs('NOTICE %s :No command given\r\n' % message['nick'])
				except AttributeError:
					self.bot.connection.send_msgs('NOTICE %s :Invalid command\r\n' % message['nick'])

				
	def exit(self):
		for user in self.configuration.configuration.values():
			user['online'] = False
		self.configuration.saveFile()
