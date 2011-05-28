# -*- coding: utf-8 -*-
import datetime
import threading
import time
import random
import re

import channel


class MessageMgmt(object):

	def __init__(self, bot):
		self.bot = bot

	def manage(self, current):
		try:
			msgtype = 'msg_%s' % current['msgtype'].lower()
			getattr(self, msgtype)(current)
		except AttributeError, msg:
			pass
		except KeyError, msg:
			pass

	def msg_join(self, message):
		if message['nick'] == self.bot.console.temportaryNick:
			self.bot.connection.channels[message['target']] = channel.Channel(self.bot, message['target'])
		self.bot.connection.channels[message['params']].addUser(message['nick'])

	def msg_part(self, message):
		self.bot.connection.channels[message['target']].removeUser(message['nick'])

	def msg_kick(self, message):
		if not message['target']:
			message['target'] = message['params']
		target = message['target'].split(' ')
		channel = target[0]
		users = target[1:]
		for user in users:
			self.bot.connection.channels[channel].removeUser(user)
			if user == self.bot.console.temportaryNick:
				del self.bot.connection.channels[channel]
				del self.bot.configuration['channels'][channel]

	def msg_ping(self, message):
		self.bot.connection.pong(message['params'])

	def msg_nick(self, message):
		for channel in self.bot.connection.channels.keys():
			if message['nick'] in self.bot.connection.channels[channel].users.keys():
				self.bot.connection.channels[channel].removeUser(message['nick'])
				self.bot.connection.channels[channel].addUser(message['params'])

	def msg_quit(self, message):
		for channel in self.bot.connection.channels.keys():
			if message['nick'] in self.bot.connection.channels[channel].users.keys():
				self.bot.connection.channels[channel].removeUser(message['nick'])

	def msg_353(self, message):
		pattern = r'(#[#a-zA-Z0-9]*)'
		pattern = re.compile(pattern)
		target = pattern.search(message['target']).groups()[0]
		namelist = message['params'].split(' ')
		for name in namelist:
			self.bot.connection.channels[target].addUser(name)

	def msg_433(self, message):
		self.bot.connection.quit()
		self.bot.console.temportaryNick = self.bot.configuration['nick']+str(random.randint(0, 1000))
		self.bot.connection.connect(self.bot.console.temportaryNick)

	def msg_error(self, message):
		try:
			self.bot.connection.quit()
		except:
			pass
		print "ERROR: %s" % message['params']
		self.bot.console.commandThread.connect()


def parse(message):
	"""IRC server message parsing method"""
	pattern = r'^(?:[:@]([^\s]+) )?([^\s]+)(?: ((?:[^:\s][^\s]* ?)*))?(?: ?:(.*))?$' #regular expression for message parsing
	pattern = re.compile(pattern)
	parsed_message = pattern.search(message)
	if parsed_message:

		try:
			nick = parsed_message.groups()[0].split("!")[0]
			username, hostname = parsed_message.groups()[0].split("!")[1].split('@')
		except IndexError:
			nick = None
			username = None
			hostname = parsed_message.groups()[0]
		except AttributeError:
			nick = None
			username = None
			hostname = parsed_message.groups()[0]
		message = {'time': datetime.datetime.now(), #time
				'nick': nick, #sender's nick
				'username': username, #sender's username
				'hostname': hostname, #sender's host
				'msgtype': parsed_message.groups()[1], #message type
				'target': parsed_message.groups()[2], #message target
				'params': parsed_message.groups()[3]} #message params
		if not message['target']:
			message['target'] = message['params']
		return message


	else:
		return {'time': datetime.datetime.now(), #time
			'msgtype': None, 'params': message}


def compose(msgtype, target, params=''): #gets data needed to create a message and composes string ready to send to server
		message = '%s %s' % (msgtype, params)
		if params:
			message += ' :%s' % params
		message = message + '\r\n'
		return message
