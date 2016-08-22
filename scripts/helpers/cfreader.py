# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
import configparser


def read_params(str_):
	"""Read list of parametrs from srtring"""
	return [element.strip() for element in str_.split(";")]


class ConfigReader(configparser.ConfigParser):
	def __init__(self, configfile):
		configparser.ConfigParser.__init__(self)

		self.configfile = configfile
		self.read(self.configfile)

	def get_list(self, section, option):
		"""Read list of values"""
		try:
			str_ = self.get(section, option)
			res = read_params(str_)
		except Exception:
			res = []

		return res

	def set_list(self, section, option, value):
		"""Write list of values"""
		self[section][option] = ";".join(value)

	def save(self):
		"""Save config"""
		with open(self.configfile, 'w') as configfile:
			self.write(configfile)
