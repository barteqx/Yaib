#*-* coding: utf-8

import user
import re
import message
import threading
import configuration
import os
import time

class Channel(object):
	
	def __init__(self, bot, channel):
		self.name = channel
		self.working = False
		self.bot = bot
		self.topic = ""
		self.users = {}
		self.currentMessage = {}
		self.lastMessage = {}

		
	def run(self):
		self.working = True
		self.watchMessage()
		
	def getMessage(self, message):
			try:
				try:
					message['target']
				except KeyError:
					message['target'] = message['params']
				if self.name in message['target'] or (message['msgtype'] == 'QUIT' and message['nick'] in self.users.keys()):
						self.currentMessage = message
						try:
							self.users[self.currentMessage['nick']].currentMessage = self.currentMessage
						except KeyError:
							pass	
						if self.currentMessage['msgtype'] == 'MODE' and self.currentMessage['target'].split(' ')[1] == '+o':
							self.users[self.currentMessage['target'].split(' ')[2]].isOp = True
					
						if self.currentMessage['msgtype'] == 'MODE' and self.currentMessage['target'].split(' ')[1] == '-o':
							self.users[self.currentMessage['target'].split(' ')[2]].isOp = False
							
						if self.currentMessage['msgtype'] == 'MODE' and self.currentMessage['target'].split(' ')[1] == '+v':
							self.users[self.currentMessage['target'].split(' ')[2]].voice = True
							
						if self.currentMessage['msgtype'] == 'MODE' and self.currentMessage['target'].split(' ')[1] == '-v':
							self.users[self.currentMessage['target'].split(' ')[2]].voice = False
						self.lastMessage = self.currentMessage
			except TypeError:
				pass
						
	def addUser(self, nick, isop=False):
		if not isop:
			pattern = r"([@+]*)(.*)"
			pattern = re.compile(pattern)
			nick = pattern.search(nick).groups()
			if nick[0] == '@':
				self.users[nick[1]] = user.User(nick[1], True)
			elif nick[0] == '+':
				self.users[nick[1]] = user.User(nick[1])
				self.users[nick[1]].voice = True
			elif nick[0] in ('@+', '+@'):
				self.users[nick[1]] = user.User(nick[1], True)
				self.users[nick[1]].voice = True
			else:
				self.users[nick[1]] = user.User(nick[1])
		else:
			self.users[nick] = user.User(nick, True)

	def removeUser(self, nick):
		del self.users[nick]
			
	def setTopic(self, topic, settop = False):
		self.topic = topic
		if settop:
			self.bot.connection.sendmsg(message.compose('TOPIC', self.name, topic))
