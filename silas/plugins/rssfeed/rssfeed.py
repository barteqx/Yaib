#*-* coding: utf-8 *-*
import urllib
import os
import sys
sys.path.append('../..')
import configuration
import connection
import multiprocessing
import time
import re

def load(bot):
	rssfeed = RSSFeed(bot)
	rssfeed.start()
	return rssfeed
	
def getFeed(rssfeed):
	try:
		feed = urllib.urlopen(url=rssfeed['url'])
		feed = feed.read()
		rsschannel = feed.split('<channel', 1)[1].split('</channel>',1)[0]
		if not rsschannel:
			raise WrongRSSFeed
		rssfeed['title'] = rsschannel.split('<title>', 1)[1].split('</title>', 1)[0]
		item = feed.split('<item', 1)[1].split('</item>', 1)[0]
		itemTitle = item.split('<title>', 1)[1].split('</title>', 1)[0]
		itemLink = item.split('<link>', 1)[1].split('</link>', 1)[0]
		return {'title': itemTitle, 'link': itemLink, 'rssfeed': rssfeed}
	except Exception, msg:
		raise WrongRSSFeed, msg

class WrongRSSFeed(Exception):
	pass
	
class RSSFeed(multiprocessing.Process):
	def __init__(self, bot):
		self.process = multiprocessing.Process.__init__(self)
		self.bot = bot
		self.config = configuration.ConfigFile('rssfeed.cfg')
		try:
			self.config.loadFile()
		except configuration.ConfigFileNotFound:
			self.config['channels'] = {}
			self.config['timeout'] = 60
			self.config.saveFile()
		self.working = False
	
	def run(self):
		self.working = True
		while self.working:
			for element in self.config['channels'].values():
				for feed in element.values():
					try:
						news = getFeed(feed)
						if news['link'] != feed['lastNews'] and self.bot.connection.connected:
							message = feed['newsstring']
							try:
								message = message.replace('*feedtitle*', news['rssfeed']['title'])
							except Exception, msg:
								print msg
							try:
								message = message.replace('*newslink*', news['link'])
							except Exception, msg:
								print msg	
							try:
								message = message.replace('*newstitle*', news['title'])
							except Exception, msg:
								print msg
							try:
								self.bot.connection.sendmsg('NOTICE %s :%s\r\n' % (feed['channame'], message))						
							except Exception, msg:
								print msg
							feed['lastNews'] = news['link']
					except WrongRSSFeed, msg:
						print msg
					except connection.NotConnectedToServerError:
						print msg
			time.sleep(self.config['timeout'])
			self.config.saveFile()
			
	def getMessage(self, message):
		try:
			msg = message['params'].split(' ')[0]
		except:
			msg = ' '
		try:
			if msg == '!news':
					for feed in self.config['channels'][message['target'].rstrip(' ')].values():
						news = getFeed(feed)
						messagex = feed['newsstring']
						try:
							messagex = messagex.replace('*feedtitle*', news['rssfeed']['title'])
						except Exception, msg:
								print msg
						try:
							messagex = messagex.replace('*newslink*', news['link'])
						except Exception, msg:
								print msg	
						try:
							messagex = messagex.replace('*newstitle*', news['title'])
						except Exception, msg:
								print msg
						try:
							self.bot.connection.sendmsg('NOTICE %s :%s\r\n' % (message['nick'], messagex))
						except connection.NotConnectedToServerError:
							pass
				#except Exception, msg:
					#raise
		except Exception, msg:
			print msg

	def getCommand(self, command):	
		if command['command'] == 'rssfeed':
			self.bot.console.pluginApi.lock = True
			self.bot.console.lock = True
			params = command['params'].split(' ', 1)
			try:
				if params[0] == 'add':
					data = params[1].split(' ', 3)
					try:
						self.add(data[0], data[1], data[2])
					except WrongRSSFeed:
						print 'Wrong RSS feed address'
				elif params[0] == 'list':
					self.list()
				elif params[0] == 'remove':
					try:
						data = params[1].split(' ', 2)
						self.remove(data[1], data[2])
					except IndexError:
						try:
							data = params[1].split(' ')
							self.remove(data[0])
						except KeyError:
							print "No RSS feeds on this channel"
					except KeyError:
						print "No RSS feeds on this channel"
				elif params[0] == 'message':
					try:
						data = params[1].split(' ', 2)
						self.message(data[0], data[1], data[2])
					except IndexError:
						print "No feed set on this channel or feed unknown"
					except KeyError:
						print "No feed set on this channel or feed unknown"
					
			except IndexError:
				print "Not enough data"
		self.config.saveFile()
		self.bot.console.lock = False
				
	
	def add(self, channel, name, link):
		try:
			a = self.config['channels'][channel]
		except KeyError:
			self.config['channels'][channel] = {}
		print "Checking..."
		try:
			feed = getFeed({'url': link})
			self.config['channels'][channel][name] = {'lastNews': None, 'url':link, 'title': feed['rssfeed']['title'], 'newsstring': '*feedtitle* news! *newstitle*. link: *newslink*', 'channame': channel}
		except WrongRSSFeed:
			print "Wrong feed URL"
			
	def list(self):
			for elem in self.config['channels'].keys():
				print elem 
				for feed in self.config['channels'][elem].keys():
					print	'	%s %s %s' % (feed.ljust(10), self.config['channels'][elem][feed]['title'].ljust(20), self.config['channels'][elem][feed]['url'].ljust(30))
					
	def remove(self, channel, feed=''):
		if not feed:
			del self.config['channels'][channel]
		else:
			del self.config['channels'][channel][feed]
			
	def message(self, channel, feed, msg):
		self.config['channels'][channel][feed]['newsstring'] = msg
	
	def exit(self):
		self.config.saveFile()
		self.working = False
		self.terminate()
