import os


class DebugLogFileError(Exception):
	"""Exception used by DebugLogFile class to indicate failure."""
	pass


class DebugLogFile:
	"""This class was created to simplify debugging by providing easy
	handling of debug log file.

	This class was designed for developers only. It should not be part
	of any YAIB release.
	"""
	def __init__(self, file_name):
		"""This method initializes new DebugLogFile object.

		It tooks only one parameter name of debug log file.
		By default this file will be stored in $HOME directory,
		but this can be changed by setting file_path attribute.
		file_path should contain full path to file. This method
		does not create file on hard disk.
		"""
		self.file_path = os.path.join(os.environ['HOME'], file_name)

	def add_entry(self, entry):
		"""Adds entry to the debug log file.

		The only parameter is the entry string.
		"""
		if not self.check_path():
			raise DebugLogFileError, ('Path \'%s\' does not exist, '
				'is not readable or writable.') % self.file_path
		try:
			log_file = open(self.file_path, 'a')
			log_file.write('%s\n' % entry)
			log_file.close()
		except IOError:
			raise DebugLogFileError, ('Adding entry to \'%s\' '
				'debug log failed') % self.file_path

	def check_path(self, try_to_make_dirs=true):
		"""This method checks if the path to the file exists,
		is readable and writable.

		If the path does not exist, this method tries to create it.
		"""
		if os.access(self.file_path, os.F_OK):
			return os.access(self.file_path, os.R_OK | os.W_OK)
		else:
			directory = os.path.dirname(self.file_path)
			if os.access(directory, os.F_OK):
				return os.access(directory, os.R_OK | os.W_OK)
			else:
				if not try_to_make_dirs:
					return False
				try:
					os.makedirs(directory)
					return True
				except OSError:
					return False


	def clear_log(self):
		"""Clears debug log file."""
		if not self.check_path(False):
			raise DebugLogFileError, ('Path \'%s\' does not exist, '
				'is not readable or writable.') % self.file_path
		try:
			log_file = open(self.file_path, 'w')
			log_file.close()
		except IOError:
			raise DebugLogFileError, ('Removal of log content '
				'did not succeed')

	def print_var(self, var):
		"""This method writes the representation of variable
		to the debug log file.

		repr() function is used to get variable representation.
		"""
		self.add_entry('%s\n' % repr(var))
