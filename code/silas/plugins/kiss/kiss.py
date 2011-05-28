#*-* coding: utf-8 *-*

def load(bot):
	return IRCKiss(bot)
	
class IRCKiss(object):

	def __init__(self, bot):
		self.bot = bot
		
	def getMessage(self, message):
		if message['params'] == '!kiss':
			self.bot.connection.sendmsg('PRIVMSG %s ::*\r\n' % message['nick'])
			
	def getCommand(self, command):
		pass
		
	def exit(self):
		pass
