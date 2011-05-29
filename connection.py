# -*- coding: utf-8 -*-
import socket
import configuration
import channel
import message


class NotConnectedToServerError(Exception):
	"""Occurs when there is no active connection ith IRC server.

	This exception is raised by many methods of IRCConnection class.
	"""
	pass


class ChannelNotJoinedError(Exception):
	"""Occurs when bot tries to leave channel that it did not join.

	This exception is raised by part() method.
	"""
	pass


class AlreadyConnected(Exception):
	"""Exception raised by connect() method when connection
	with IRC server is already established.
	"""
	pass


class ChannelJoinedError(Exception):
	"""Occurs when bot tries to join channel it already joined.

	This exception is raised by join() method.
	"""
	pass


class WrongChannelNameError(Exception):
	"""Occurs when the specified channel name does not begin with '#'
	character.

	This exception is raised by join() method.
	"""
	pass


class IRCConnectionError(Exception):
	"""General exception used by IRCConnection class."""
	pass


class IRCConnection(object):

	def __init__(self, bot):
		"""IRCConnection object initializer."""
		self.bot = bot
		self.channels = {}
		self.connected = False
		self.data = ''
		self.previous_data = ''

	def change_nick(self, nick, temporary=True):
		"""Changes nickname on IRC network.

		By default change of nickname is temporary. It means that
		after you will restart your bot, it will use nickname stored
		in configuration file again. If you want change to be
		persistent second parameter should be set to false value.
		In the previous versions this method was called nickchange().
		Now nickchange() is an alias of this one.
		"""
		self.send('NICK %s\r\n' % nick)
		if not temporary:
			self.bot.configuration['nick'] = nick

	def connect(self, alternate_nick=''):
		"""Connects bot to IRC server.

		If you want to use different nickname than this stored
		in configuration file you can specify alternate_nick parameter.
		This method can raise the following exceptions:

		AlreadyConnected
			Exception raised when bot is already connected to IRC
			server.

		IRCConnectionError
			General exception raised when there is a problem with
			communication over socket. It means that connection
			failed.
		"""
		self.bot.configuration.loadFile()
		if self.connected:
			raise AlreadyConnected, 'Already connected to IRC server.'
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.socket.connect((self.bot.configuration['host'],
					     int(self.bot.configuration['port'])))
		except (socket.error, socket.herror, socket.gaierror, socket.timeout):
			raise IRCConnectionError, 'Connection failed.'
		self.connected = True
		if self.bot.configuration['pass']:
			self.send('PASS %s\r\n' % self.bot.configuration['pass'])
		if alternate_nick:
			self.send('NICK %s\r\n' % alternate_nick)
		else:
			self.send('NICK %s\r\n' % self.bot.configuration['nick'])
		self.send('USER %s 0 * :%s\r\n' % (self.bot.configuration['username'],
						   self.bot.configuration['realname']))

	def join(self, chan, key=''):
		"""Joins specified IRC channel.

		If channel is protected by key, it can be specified
		as the second parameter. By default no key is used.
		Following exceptions can be raised by this method:

		WrongChannelNameError
			Exception raised when channel name does not begin with
			# character. Actually this is not correct because some
			servers accepts also different types of channel names.
			This issue will be fixed with the implementation
			of ISUPPORT.

		ChannelJoinedError
			Already joined channel.

		Important! See also send() method description!
		"""
		if chan[0] != '#':
			raise WrongChannelNameError, 'Wrong channel name.'
		if chan in self.channels:
			raise ChannelJoinedError, 'Already joined channel.'
		if key:
			self.send('JOIN %s %s\r\n' % (chan, key))
		else:
			self.send('JOIN %s\r\n' % chan)
		

	def nickchange(self, nick, temporary=True):
		"""Use change_nick() method instead of this one.

		This method is only an alias of change_nick() kept for
		backward compatibility.
		"""
		self.change_nick(nick, temporary)

	def part(self, channel, msg=''):
		"""Parts specified channel.

		Reason can be specified as the second parameter.

		Important! See also send() method description!
		"""
		if channel not in self.channels:
			raise ChannelNotJoinedError, 'Channel not joined.'
		self.send('PART %s :%s\r\n' % (channel, msg))
		del self.channels[channel]

	def pong(self, server):
		"""Sends reply to PING message to the specified server.

		Important! See also send() method description!
		"""
		self.send('PONG %s\r\n' % server)

	def quit(self, msg=''):
		"""Closes connection to the IRC server.

		Goodbye message can be specified as the second parameter.

		Important! See also send() method description!
		"""
		if msg:
			self.send('QUIT %s\r\n' % msg)
		else:
			self.send('QUIT\r\n')
		self.socket.close()
		self.channels = {}
		self.connected = False

	def receive(self):
		"""Receives data from IRC server.

		This method returns list of messages received from IRC server.
		receive() should be used only inside DataReceive class.
		It can raise the following exceptions:

		NotConnectedToServerError
			Connection to the server is not established.

		IRCConnectionError
			General exception raised when there is a problem with
			communication over socket. When this exception occurs,
			connection is closed.
		"""
		if not self.connected:
			raise NotConnectedToServerError, 'Not connected to IRC server.'
		try:
			while True:
				self.data = self.socket.recv(4096)
				if self.previous_data != '':
					self.data = '%s%s' % (self.previous_data, self.data)
					self.previous_data = ''
				messages = self.data.split('\r\n')
				if messages[-1] != '':
					self.previous_data = messages[-1]
				del messages[-1]
				if len(messages) > 0:
					return messages
		except (socket.error, socket.herror, socket.gaierror, socket.timeout):
			self.connected = False
			raise IRCConnectionError, 'Receiving data failed. Connection closed.'

	def send(self, data):
		"""Sends data (string) to the IRC server.

		send() is used by many other methods present in this class.
		It can raise the following exceptions:

		NotConnectedToServerError
			Connection to the server is not established.

		IRCConnectionError
			General exception raised when there is a problem with
			communication over socket. When this exception occurs,
			connection is closed.
		"""
		if not self.connected:
			raise NotConnectedToServerError, 'Not connected to IRC server.'
		try:
			self.socket.sendall(data)
		except (socket.error, socket.herror, socket.gaierror, socket.timeout):
			self.connected = False
			raise IRCConnectionError, 'Sending data failed. Connection closed.'

	def send_msgs(self, msgs):
		"""Sends on or more messages to the IRC server.

		This method gets as a parameter list of messages (list of strings)
		or just one message (string).

		Important! See also send() method description!
		"""
		if type(msgs) == str:
			msgs = [msgs]
		for msg in msgs:
			self.send(msg)
			msg = ':%s!%s@%s %s' % (self.bot.configuration['nick'],
						self.bot.configuration['username'],
						self.bot.configuration['hostname'],
						msg.rstrip('\r\n'))
			self.bot.currentMessage = message.parse(msg)

	def __getitem___(self, key):
		"""Returns channel object."""
		return self.channels[key]
