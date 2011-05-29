import os
import pickle
import socket

def load(bot):
	return Seen(bot)

class Seen(object):
	def __init__(self, bot):
		self.bot = bot
		self.dataFilePath = '%s/.seen.data' % os.environ['HOME']
		self.data = {}
		self.sendNames = True
		self.updatesCounter = 0
		self.updatesBetweenSaves = 100
		self.__loadData()
		if self.sendNames:
			channels = self.bot.connection.channels
			successful = 0
			for channel in channels:
				if self.__sendNames(channel):
					successful += 1
			if successful == len(channels):
				self.sendNames = False
	
	def __getNick(self, nick):
		if self.__isEmpty(nick):
			return False
		if nick[0].isalpha() or nick[0] in ['[', ']', '{', '}', '`', '^', '_', '\\']:
			return nick
		else:
			return nick[1:]

	def __isBotCommand(self, message, command):
		if self.__isEmpty(message) or self.__isEmpty(command):
			return False
		parts = message.split(' ')
		if parts[0] == command:
			return True
		else:
			return False
	def __isChannelMessage(self, target):
		if self.__isEmpty(target):
			return False
		if target[0] in ['!', '#', '&', '+']:
			return True
		else:
			return False

	def __isEmpty(self, string):
		if type(string) != str:
			return True
		if len(string) == 0:
			return True
		return False

	def __loadData(self):
		try:
			dataFile = open('%s/.seen.data' % os.environ['HOME'], 'r')
			self.data = pickle.load(dataFile)
			dataFile.close()
			return True
		except IOError:
			return False
	
	def __saveData(self):
		try:
			dataFile = open('%s/.seen.data' % os.environ['HOME'], 'w')
			pickle.dump(self.data, dataFile)
			dataFile.close()
			return True
		except IOError:
			return False
	def __sendNames(self, channel):
		if self.__isEmpty(channel) or not self.bot.connection.connected:
			return False
		try:
			s = self.bot.connection.connection
			s.sendall('NAMES %s\r\n' % channel)
			return True
		except (socket.error, socket.herror, socket.gaierror, socket.timeout):
			return False
	
	def __sendNotice(self, nick, notice):
		if self.__isEmpty(nick) or not self.bot.connection.connected:
			return False
		try:
			s = self.bot.connection.connection
			s.sendall('NOTICE %s :%s\r\n' % (nick, notice))
			return True
		except (socket.error, socket.herror, socket.gaierror, socket.timeout):
			return False

	def getMessage(self, message):
		messageLog = open('%s/message.log' % os.environ['HOME'], 'a')
		messageLog.write(repr(message))
		messageLog.write('\n\n')
		messageLog.close()
		if self.sendNames:
			channels = self.bot.connection.channels
			successful = 0
			for channel in channels:
				if self.__sendNames(channel):
					successful += 1
			if successful == len(channels):
				self.sendNames = False
		if message['msgtype'] == '353':
			if self.__isEmpty(message['target']) or self.__isEmpty(message['params']):
				return
			parts = message['target'].split(' ')
			if len(parts) < 2:
				return
			channel = parts[2].strip()
			if channel not in self.data:
				self.data[channel] = {}
			parts = message['params'].split(' ')
			for i in parts:
				nick = self.__getNick(i.strip())
				self.data[channel][nick] = message['time']
		elif message['msgtype'] == 'NICK':
			if self.__isEmpty(message['nick']) or self.__isEmpty(message['params']):
				return
			nick = message['nick'].strip()
			newnick = message['params'].strip()
			for channel in self.data:
				if nick in self.data[channel]:
					self.data[channel][nick] = message['time']
				if newnick in self.data[channel]:
					self.data[channel][newnick] = message['time']
		elif message['msgtype'] == 'KICK':
			if self.__isEmpty(message['target']):
				return
			parts = message['target'].split(' ')
			if len(parts) < 2:
				return
			channel = parts[0]
			nick = parts[1]
			if len(channel) == 0 or len(nick) == 0:
				return
			if channel not in self.data:
				self.data[channel] = {}
			self.data[channel][nick] = message['time']
		elif message['msgtype'] == 'PRIVMSG':
			if not self.__isChannelMessage(message['target']):
				return
			channel = message['target'].strip()
			if self.__isBotCommand(message['params'], '!seen'):
				parts = message['params'].split(' ')
				if len(parts) == 1:
					self.__sendNotice(message['nick'], 'Usage: !seen <nickname>')
					return
				nick = parts[1]
				if channel not in self.data:
					self.__sendNotice(message['nick'], 'Never seen %s' % nick)
					return
				if nick not in self.data[channel]:
					self.__sendNotice(message['nick'], 'Never seen %s' % nick)
					return
				parts = ('%s' % self.data[channel][nick]).split('.')
				self.__sendNotice(message['nick'], '%s was last seen %s' % (nick, parts[0]))
			else:
				nick = message['nick'].strip()
				if channel not in self.data:
					self.data[channel] = {}
				self.data[channel][nick] = message['time']
		elif message['msgtype'] in ['JOIN', 'PART', 'NOTICE']:
			if self.__isEmpty(message['target']) or self.__isEmpty(message['nick']):
				return
			if not self.__isChannelMessage(message['target']):
				return
			channel = message['target'].strip()
			nick = message['nick'].strip()
			if channel not in self.data:
				self.data[channel] = {}
			self.data[channel][nick] = message['time']
		else:
			return
		self.updatesCounter += 1
		if self.updatesCounter == self.updatesBetweenSaves:
			self.__saveData()
			updatesCounter = 0

	def getCommand(self, command):
		pass

	def exit(self):
		self.__saveData()
