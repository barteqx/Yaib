# -*- coding: utf-8 -*-
import json
import os
import pickle


class LoadingError(Exception):
	"""Exception raised by ConfigFile.loadFile() method to signal failure."""
	pass


class SavingError(Exception):
	"""Exception raised by ConfigFile.saveFile() method to signal failure."""
	pass


class ConfigFile(object):
	"""This class simplifies handling of configuration files."""

	def __init__(self, name, path=os.path.join(os.environ['HOME'], '.yaib')):
		"""Creates a new ConfigFile object.

		This method takes two arguments: filename and directory path.
		The second argument can be omitted, its default value is
		$HOME/.yaib. Further configuration can be done by setting
		appropriate values of the following attributes:

		module
			Module responsible for loading and saving data.
			Currently two modules are supported:
			'json' - JSON module (default)
			'pickle' - Pickle module

		updatesBetweenSaves
			Every change in configuration (setting/deleting value)
			is called an update. ConfigFile class automatically
			saves configuration to file every N updates.
			N can be specified by setting this attribute.
			Default value is 50. Auto saving functionality
			can be disabled by setting value of 0.

		Important! This method does not create file on hard disk.
		"""
		self.configuration = {}
		self.module = 'json'
		self.name = name
		self.path = path
		self.updatesCounter = 0
		self.updatesBetweenSaves = 50

	def autoSaveFile(self):
		"""Automatically saves file every N updates.

		N can be specified by setting self.updatesBetweenSaves.
		Value 0 disables automatic saving.
		"""
		if self.updatesBetweenSaves == 0:
			return
		if (self.updatesCounter < 0 or
		    self.updatesCounter > self.updatesBetweenSaves):
			self.updatesCounter = 0
		self.updatesCounter += 1
		if self.updatesCounter == self.updatesBetweenSaves:
			self.updatesCounter = 0
			try:
				self.saveFile()
			except SavingError:
				pass

	def checkPath(self):
		"""Checks whether config path exists, is readable and writable.

		This method returns True on success or False otherwise.
		If specified configuration path does not exist checkPath()
		will try to create it.
		"""
		if os.path.isdir(self.path):
			if os.access(self.path, os.R_OK | os.W_OK):
				return True
			else:
				return False
		try:
			os.makedirs(self.path)
			return True
		except OSError:
			return False

	def loadFile(self):
		"""Loads configuration from file.

		This method raises LoadingError exception on failure.
		"""
		if not self.checkPath():
			raise LoadingError
		try:
			configFile = open(os.path.join(self.path, self.name), 'r')
			self.configFileContent = configFile.read()
			configFile.close()
		except IOError:
			raise LoadingError
		try:
			self.configuration = json.loads(self.configFileContent)
			return
		except (TypeError, ValueError):
			pass
		# I do not like the fact that we need to handle StandardError
		# exception here, but I could not find a list of exceptions
		# that can be raised by pickle module.
		try:
			self.configuration = pickle.loads(self.configFileContent)
		except (pickle.UnpicklingError, StandardError):
			raise LoadingError

	def saveFile(self):
		"""Saves configuration to file.

		This method raises SavingError exception on failure.
		"""
		if not self.checkPath():
			raise SavingError
		try:
			self.configFile = open(os.path.join(self.path, self.name), 'w')
			if self.module == 'json':
				json.dump(self.configuration, self.configFile)
			elif self.module == 'pickle':
				pickle.dump(self.configuration, self.configFile)
			else:
				self.configFile.close()
				raise SavingError
			self.configFile.close()
		except (IOError, OverflowError, TypeError, ValueError):
			raise SavingError

	def __contains__(self, key):
		"""Returns True if configuration contains item with key 'key'.

		Example (assume 'cfo' is ConfigFile object):
			key in cfo
		"""
		return key in self.configuration

	def __delitem__(self, key):
		"""Deletes item with key 'key' if configuration contains it.

		Example (assume 'cfo' is ConfigFile object):
			del cfo[key]
		"""
		if key in self.configuration:
			del self.configuration[key]
			self.autoSaveFile()

	def __getitem__(self, key):
		"""Returns value of item with key 'key'.

		Example (assume 'cfo' is ConfigFile object):
			cfo[key]
		"""
		return self.configuration[key]

	def __setitem__(self, key, value):
		"""Sets value of item with key 'key'.

		Example (assume 'cfo' is ConfigFile object):
			cfo[key] = value
		"""
		self.configuration[key] = value
		self.autoSaveFile()
