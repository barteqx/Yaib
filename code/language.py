#*-* coding: utf-8

import configuration
import os

class BadLanguageName(Exception):
	pass

class Language(object):
	
	def __init__(self, language='en'):
		self.language = language
		try:
			self.openLanguageFile()
		except IOError:
			pass #raise BadLanguageName
			
	def openLanguageFile(self):
		self.langfile = open(os.path.join('languages', self.language), 'r')
		self.langfile = self.langfile.readlines()
		self.lang = {}
		for lang in self.langfile:
			lang = lang.rstrip(r"'\n'").lstrip("'").split("'='")
			self.lang[lang[0]] = lang[1]
			
	def __getitem__(self, key):
		try:
			return self.lang[key]
		except:
			return key
