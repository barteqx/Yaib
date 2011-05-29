#*-* coding: utf-8 *-*
#simple user class
class User(object):
	
	def __init__(self, nick, isop = False):
		self.lastMessage = {}
		self.nick = nick
		self.opchannels = []
		self.isOp = isop
		self.voice = False
		
	def __getitem__(self, key):
		return self.lastMessage[key]
		
	def setLastMsg(self, msg):
		self.lastMessage = msg
		if self.lastMessage['nick'] != self.nick:
			self.nick = self.lastMessage['nick']
			
	def op(self):
		self.isOp = True
		
	def deop(self):
		self.isOp = False
