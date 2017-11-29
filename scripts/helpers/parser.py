# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
import subprocess

from lxml import etree
from .common import get_file_list, rewrite_file

PARSER = etree.XMLParser(remove_blank_text=True)


def recolor_images(_dir, colors):
	"""Recolor all svg images in directory"""
	for file_ in get_file_list(_dir):
		tree = etree.parse(file_, PARSER)
		root = tree.getroot()

		for child in root:
			id_ = child.get("id")
			if id_ in colors.keys():
				child.set("fill", colors[id_])

		tree.write(file_, pretty_print=True)


class ThemeParser:
	"""Config files parser"""
	def __init__(self, config):
		self.config = config
		self.scss_dir = config["SCSS"]["directory"]
		self.scss_command = self.config.get_list("SCSS", "command")

		theme_sections = ["GTK2", "GTK3"]
		self.themes = []

		for theme in theme_sections:
			td = {
				"files": self.config.get_list(theme, "files"),
				"separator": self.config.get(theme, "separator"),
				"pattern": self.config.get(theme, "pattern") + '\n'
			}
			self.themes.append(td)

	def write_colors(self):
		"""Rewrite colors in theme files"""
		for theme in self.themes:
			for file_ in theme["files"]:
				with open(file_, 'r+') as theme_file:
					text = theme_file.read()
					old_colors = text.split(theme["separator"])[0]
					new_colors = "".join([theme["pattern"] % (n, c) for n, c in self.config.colors.items()])
					rewrite_file(theme_file, text.replace(old_colors, new_colors))

	def update_scss(self):
		"""Build css files from scss"""
		try:
			subprocess.call(self.scss_command, cwd=self.scss_dir)
		except Exception as e:
			print("Fail to update scss\n", e)

	def rebuild_images(self):
		"""Rebuild image according current colors"""
		for image_dir in self.config['Images'].values():
			recolor_images(image_dir, self.config.colors)
