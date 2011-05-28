# -*- coding: utf-8 -*-
import configuration
import os
import shutil
import socket


def load(bot):
	return Seen(bot)


class Seen(object):

	def __init__(self, bot):
		self.bot = bot
		self.data = configuration.ConfigFile('seen.data')
		self.data.module = 'pickle'
		try:
			self.data.loadFile()
		except configuration.LoadingError:
			pass
		self.send_names_message = True
		if self.send_names_message:
			channels = self.bot.connection.channels
			successful = 0
			for channel in channels:
				if self.send_names(channel):
					successful += 1
			if successful == len(channels):
				self.send_names_message = False

	def get_nick(self, nick):
		if self.is_empty(nick):
			return False
		if nick[0].isalpha() or nick[0] in ['[', ']', '{', '}', '`', '^', '_', '\\']:
			return nick
		else:
			return nick[1:]

	def is_bot_command(self, message, command):
		if self.is_empty(message) or self.is_empty(command):
			return False
		parts = message.split(' ')
		if parts[0] == command:
			return True
		else:
			return False

	def is_channel_name(self, target):
		if self.is_empty(target):
			return False
		if target[0] in ['!', '#', '&', '+']:
			return True
		else:
			return False

	def is_empty(self, string):
		if type(string) != str:
			return True
		if len(string) == 0:
			return True
		return False

	def send_names(self, channel):
		if self.is_empty(channel) or not self.bot.connection.connected:
			return False
		try:
			s = self.bot.connection.socket
			s.sendall('NAMES %s\r\n' % channel)
			return True
		except (socket.error, socket.herror, socket.gaierror, socket.timeout):
			return False

	def send_notice(self, nick, notice):
		if self.is_empty(nick) or not self.bot.connection.connected:
			return False
		try:
			s = self.bot.connection.socket
			s.sendall('NOTICE %s :%s\r\n' % (nick, notice))
			return True
		except (socket.error, socket.herror, socket.gaierror, socket.timeout):
			return False

	def getMessage(self, message):
		if self.send_names_message:
			channels = self.bot.connection.channels
			successful = 0
			for channel in channels:
				if self.send_names(channel):
					successful += 1
			if successful == len(channels):
				self.send_names_message = False
		if message['msgtype'] == '353':
			if self.is_empty(message['target']) or self.is_empty(message['params']):
				return
			parts = message['target'].split(' ')
			if len(parts) < 2:
				return
			channel = parts[2].strip()
			if channel not in self.data:
				self.data[channel] = {}
			parts = message['params'].split(' ')
			for i in parts:
				nick = self.get_nick(i.strip())
				self.data[channel][nick] = message['time']
		elif message['msgtype'] == 'NICK':
			if self.is_empty(message['nick']) or self.is_empty(message['params']):
				return
			nick = message['nick'].strip()
			newnick = message['params'].strip()
			for channel in self.data.configuration.keys():
				if nick in self.data[channel]:
					self.data[channel][nick] = message['time']
				if newnick in self.data[channel]:
					self.data[channel][newnick] = message['time']
		elif message['msgtype'] == 'KICK':
			if self.is_empty(message['target']):
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
			if not self.is_channel_name(message['target']):
				return
			channel = message['target'].strip()
			if self.is_bot_command(message['params'], '!seen'):
				parts = message['params'].split(' ')
				if len(parts) == 1:
					self.send_notice(message['nick'], 'Usage: !seen <nickname>')
					return
				nick = parts[1]
				if nick == message['nick']:
					self.send_notice(message['nick'], 'Look in the mirror')
					return
				if nick == self.bot.configuration['nick']:
					self.send_notice(message['nick'], 'What do you want sweetheart?')
					return
				if channel in self.bot.connection.channels:
					if nick in self.bot.connection.channels[channel].users:
						self.send_notice(message['nick'], '%s is on channel' % nick)
						return
				if channel not in self.data:
					self.send_notice(message['nick'], 'Never seen %s' % nick)
					return
				if nick not in self.data[channel]:
					self.send_notice(message['nick'], 'Never seen %s' % nick)
					return
				parts = ('%s' % self.data[channel][nick]).split('.')
				self.send_notice(message['nick'], '%s was last seen %s' % (nick, parts[0]))
			else:
				nick = message['nick'].strip()
				if channel not in self.data:
					self.data[channel] = {}
				self.data[channel][nick] = message['time']
		elif message['msgtype'] in ['JOIN', 'PART', 'NOTICE']:
			if self.is_empty(message['target']) or self.is_empty(message['nick']):
				return
			if not self.is_channel_name(message['target']):
				return
			channel = message['target'].strip()
			nick = message['nick'].strip()
			if channel not in self.data:
				self.data[channel] = {}
			self.data[channel][nick] = message['time']

	def getCommand(self, command, quiet):
		pass

	def exit(self):
		try:
			self.data.saveFile()
		except configuration.SavingError:
			pass
