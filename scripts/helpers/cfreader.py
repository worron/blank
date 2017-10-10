# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
import configparser
import collections


def read_params(str_):
	"""Read list of parameters from string"""
	return [element.strip() for element in str_.split(";")]


def get_real_value(dict_, key):
	"""Get key from linked dictionary"""
	return get_real_value(dict_, dict_[key]) if dict_[key] in dict_ else dict_[key]


class ConfigReader(configparser.ConfigParser):
	def __init__(self, configfile):
		configparser.ConfigParser.__init__(self)

		self.configfile = configfile
		self.read(self.configfile)

		self.colors = collections.OrderedDict()
		self.load_colors()

	def load_colors(self):
		"""Read color scheme from config"""
		for color_name in (self["Colors"]):
			self.colors[color_name] = get_real_value(self["Colors"], color_name)

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
