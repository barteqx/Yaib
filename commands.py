# -*- coding: utf-8 -*-
import connection
import re
import socket
import time
import message
import datetime
import pluginapi


class Commands(object):

	def __init__(self, bot, console):
		self.bot = bot
		self.console = console
		self.language = self.console.language

	def join(self, params='', quiet=False):
		if not params:
			if not quiet: print 'join: %s' % self.language["Not enough parameters"]
		else:
			pattern = r'^(.*) *(.*)'
			pattern = re.compile(pattern)
			params = pattern.search(params)
			channel = params.groups()[0]
			password = params.groups()[1]
			try:
				self.bot.connection.join(channel, password)
				self.bot.configuration['channels'][channel] = password
			except connection.ChannelJoinedError:
				if not quiet: print 'join: %s' % self.language["Channel already '%s' joined"] % channel
			except connection.WrongChannelNameError:
				if not quiet: print 'join: %s' % self.language["Channel name wrong, try 'join #%s'"] % channel
			except (connection.NotConnectedToServerError, connection.IRCConnectionError):
				if not quiet: print 'join: %s' % self.language["Not connected to server"]
			except AttributeError:
				raise

	def nick(self, params='', quiet=False):
		if not params:
			if not quiet: print 'nick: %s' % self.language["Not enough parameters"]
		else:
			pattern = r'^(\w*) *(\w*)'
			pattern = re.compile(pattern)
			params = pattern.search(params)
			nick = params.groups()[0]
			option = params.groups()[1]
			if nick:
				try:
					if not option:
						self.bot.connection.change_nick(nick)
						self.console.temportaryNick = nick
					elif option == 'permanent':
						self.bot.connection.change_nick(nick, False)
						self.console.temportaryNick = nick
					else:
						if not quiet: print 'nick: %s' % self.language['Invalid option: %s'] % option
				except connection.NotConnectedToServerError:
					if not quiet: print "nick: %s" % self.language["Not connected to server"]
			else:
				if not quiet: print 'nick: %s' % self.language['Invalid nick: %s'] % nick

	def connect(self, params='', quiet=False):
		try:
			if not quiet: print self.language['Connecting...']
			self.bot.connection.connect()
			try:
				self.bot.receiveData.start()
			except RuntimeError:
				pass
			self.bot.receiveData.writing = True
			while self.bot.receiveData.writing:
				time.sleep(0.01)
			if self.bot.currentMessage['msgtype'] in ('372'):
				if not quiet: print self.language['Connected to %s'] % self.bot.configuration['host']
				self.console.autojoin()
				self.console.afterconnect()
			elif self.bot.currentMessage['msgtype'] == 'ERROR':
				pass
		except connection.AlreadyConnected:
			if not quiet: print 'connect: %s' % self.language['Already connected to %s'] % self.bot.configuration['host']
		except socket.error, msg:
			if not quiet: print 'connect: %s' % msg
		except connection.IRCConnectionError:
			if not quiet: print 'connect: %s' % self.language["could not connect with '%s' - check configuration"] % self.bot.configuration['host']
		except Exception, msg:
			if not quiet: print msg

	def configure(self, params='', quiet=False):
		if not params:
			self.bot.console.configure()
		else:
			try:
				params = params.split(' ', 1)
				key = params[0]
				value = params[1]
			except ValueError:
				key = params
				value = ''
			except IndexError:
				key = params
				value = ''
			if key and value:
				self.bot.configuration[key] = value
			elif not value:
				if not quiet: print "configure: %s" % self.language["'%s' parameter's value needed"] % key

			self.bot.configuration.saveFile()

	def quit(self, params='', quiet=False):
		try:
			self.bot.connection.quit(params)
		except connection.NotConnectedToServerError:
			if not quiet: print "quit: %s" % self.language["Not connected to server"]

	def part(self, params='', quiet=False):
		if not params:
			if not quiet: print "part: %s" % self.language["<channel> argument needed"]
		else:
			try:
				key, value = params.split(' ', 1)
			except ValueError:
				key = params
				value = ''
			try:
				self.bot.connection.part(key, value)
				del self.bot.configuration['channels'][key]
			except connection.ChannelNotJoinedError:
				if not quiet: print "part: %s" % self.language["Channel '%s' not joined"] % key
			except connection.NotConnectedToServerError:
				if not quiet: print "part: %s" % self.language["Not connected to server"]

	def send(self, params='', quiet=False):
		if not params:
			if not quiet: print "send: %s" % self.language["Specify message to send"]
		else:
			self.bot.connection.send(params+'\r\n')
			try:
				self.bot.lastMessage = message.parse('%s!%s@%s %s' % (self.bot.configuration['nick'], self.bot.configuration['username'], self.bot.configuration['hostname'], params))
			except:
				pass

	def message(self, params='', quiet=False):
		if not params:
			if not quiet: print "message: %s" % self.language["Specify message to send"]
		else:
			try:
				target, messagex = params.split(' ', 1)
				self.bot.connection.send('PRIVMSG %s :%s\r\n' % (target, messagex))
				self.bot.lastMessage = {'time': datetime.datetime.now(), #time
				'nick': self.bot.configuration['nick'],
				'username': self.bot.configuration['username'],
				'hostname': self.bot.configuration['hostname'],
				'msgtype': 'PRIVMSG',
				'target': target,
				'params': messagex}
			except ValueError:
				if not quiet: print "message: %s" % self.language["Specify message to send"]
			except connection.NotConnectedToServerError:
				if not quiet: print "message: %s" % self.language["Not connected to server"]

	def lastmessage(self, params='', quiet=False):
		if not params:
			lastMessage = self.bot.currentMessage
		else:
			try:
				lastMessage = self.bot.connection.channels[params].currentMessage
			except KeyError:
				if not quiet: print "lastmessage: %s" % self.language["Channel '%s' not joined"] % params
		try:
			if not quiet: print "%s\n[%d:%d:%d] <%s> %s: %s" % (lastMessage['target'], lastMessage['time'].hour, lastMessage['time'].minute, lastMessage['time'].second, lastMessage['nick'], lastMessage['msgtype'], lastMessage['params'])
		except:
			pass

	def list(self, params='', quiet=False):
		if not params:
			if not quiet: print "list: %s" % self.language["<channel> argument needed"]
		else:
			try:
				userstring = params
				for elem in self.bot.connection.channels[params].users.keys():
					userstring += '\n	'
					if self.bot.connection.channels[params].users[elem].isOp and not self.bot.connection.channels[params].users[elem].voice:
						userstring += '@ '
					elif not self.bot.connection.channels[params].users[elem].isOp and self.bot.connection.channels[params].users[elem].voice:
						userstring += ' +'
					elif self.bot.connection.channels[params].users[elem].isOp and self.bot.connection.channels[params].users[elem].voice:
						userstring += '@+'
					else:
						userstring += '  '
					userstring += elem
				if not quiet: print userstring
			except KeyError:
				if not quiet: print "list: %s" % self.language["Channel '%s' not joined"] % params

	def autorun(self, params='', kind='autorun'):
		if not params:
			if not quiet: print "%s: %s" % (kind, self.language["No command given"])
		else:
			pattern = r'^(\w*) *(.*)'
			pattern = re.compile(pattern)
			command = pattern.search(params).groups()
			if command[0] == 'set':
				self.bot.configuration[kind].append(command[1])
			elif command[0] == 'del':
				try:
					del self.bot.configuration[kind][int(command[1])-1]
				except ValueError:
					if not quiet: print "%s: %s" % (kind, self.language["Wrong command ID"])
				except IndexError:
					if not quiet: print "%s: %s" % (kind, self.language["Wrong command ID"])
			elif command[0] == 'list':
				num = 1
				if not quiet: print self.language["%s commands:"] % kind
				for elem in self.bot.configuration[kind]:
					if not quiet: print "%d: %s" % (num, elem)
					num += 1
			else:
				if not quiet: print "%s: %s" % (kind, self.language["Wrong parameters"])

	def afterconnect(self, params='', quiet=False):
		self.autorun(params, 'afterconnect')

	def plugin(self, params='', quiet=False):
		if not params:
			if not quiet: print 'plugin: %s' % self.language['No command specified']
		else:
			pattern = r'^(\w*) *(\w*)'
			pattern = re.compile(pattern)
			try:
				params = pattern.search(params).groups()
			except AttributeError:
				params = (None, None)
			if params[0] == 'run':
				if not params in self.bot.configuration['plugins']:
					if params[1]:
						try:
							self.console.pluginApi.execute(params[1])
							self.bot.configuration['plugins'].append(params[1])
						except ImportError, msg:
							if not quiet: print msg
							if not quiet: print 'plugin: %s' % self.language['plugin %s not installed'] % params[1]
						except OSError, msg:
							if not quiet: print msg
							if not quiet: print 'plugin: %s' % self.language['plugin %s not installed'] % params[1]
						except pluginapi.IncorrectPlugin:
							if not quiet: print 'plugin: %s' % self.language['%s failed to load'] % params[1]
					else:
						if not quiet: print 'plugin: not enough parameters'
				else:
					if not quiet: print 'plugin: %s' % self.language['plugin running']
			elif params[0] == 'stop':
				if params[1] in self.bot.configuration['plugins']:
					try:
						self.console.pluginApi.unload(params[1])
						i = 0
						for elem in self.bot.configuration['plugins']:
							if elem == params[1]:
								del self.bot.configuration['plugins'][i]
							i+=1
					except Exception, msg:
						if not quiet: print msg
				else:
					if not quiet: print 'plugin: %s' % self.language['plugin not running']
			elif params[0] == 'list':
				if not quiet: print self.language['plugins list:']
				for elem in self.console.pluginApi.plugins.keys():
					if not quiet: print '%s %s' % (elem, self.console.pluginApi.plugins[elem])
			else:
				if not quiet: print 'plugin: %s' % self.language['wrong command']

	def exit(self, params='', quiet=False):
		self.bot.working = False
		self.bot.receiveData.working = False
		for elem in self.console.pluginApi.plugins.values():
			elem.exit()
		try:
			self.quit()
		except:
			pass
		self.bot.configuration.saveFile()
		exit()
