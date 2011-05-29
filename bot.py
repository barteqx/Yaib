# -*- coding: utf-8 -*-
import connection
import threading
import message
import console
import configuration
import os
import time
import sys


class IRCBot(threading.Thread): #main IRCBot class

	def __init__(self):
		threading.Thread.__init__(self)
		self.mainpath = os.path.abspath('.')
		self.path = '%s/.yaib' % os.environ['HOME'] #set configuration path to ~/.yaib
		self.version = '0.1'
		self.connection = connection.IRCConnection(self) #creates instance for IRCConnection() - main connection class
		self.console = console.Console(self) #creates instance for Console() - class for control bot through intractive command line
		self.receiveData = ReceiveData(self) #receive data thread
		self.working = False
		self.currentMessage = {'msgtype': None, 'hostname': None, 'params': None} #current message stored as dictionary
		self.lastMessage = {'msgtype': None}
		self.messagesMgmt = message.MessageMgmt(self)

	def run(self):
		self.working = True
		self.console.start()
		while self.working:
			time.sleep(0.01)
			for key in self.connection.channels.keys():
				try:
					if self.lastMessage['target'] == key:
						self.connection.channels[key].currentMessage = self.lastMessage
				except KeyError:
					pass
		#self.ircListen = irclisten.IRCListem(self)

	def exit(self): #don't have to explain, right?
		self.working = False
		sys.exit()


class ReceiveData(threading.Thread): #data receive class

	def __init__(self, bot):
		threading.Thread.__init__(self)
		self.bot = bot
		self.working = True
		self.writing = False

	def run(self):
		while self.working:
			time.sleep(0.01)
			try:
				self.currentMessage = self.bot.connection.receive()
				for element in self.currentMessage:
					self.bot.currentMessage = message.parse(element)
					for elem in self.bot.connection.channels.values():
						elem.getMessage(self.bot.currentMessage)
					self.bot.messagesMgmt.manage(self.bot.currentMessage)
					self.bot.console.pluginApi.getMessage(self.bot.currentMessage)

					if self.writing == True:
						try:
							print "%s: %s: %s" % (self.bot.currentMessage['hostname'], self.bot.currentMessage['msgtype'], self.bot.currentMessage['params'])
						except:
							print "%s: %s" % (self.bot.currentMessage['msgtype'], self.bot.currentMessage['params'])
					if self.bot.currentMessage['msgtype'] in ('372', 'ERROR'):
						self.writing = False

			except (connection.NotConnectedToServerError, connection.IRCConnectionError):
				pass
			self.bot.lastMessage = self.bot.currentMessage


if __name__ == '__main__':
	bot = IRCBot()
	bot.start()
