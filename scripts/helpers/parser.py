# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
import os
import subprocess

from .common import get_file_list, rewrite_file


def make_pattern_from_image(dir_, image_colors):
	"""Build pattern from svg image"""
	file_list = get_file_list(dir_)

	for file_ in file_list:
		with open(file_, 'r+') as image_file:
			text = image_file.read()

		for key, value in image_colors.items():
			text = text.replace(value, "@" + key)
			text = text.replace(value.lower(), "@" + key)

		with open(file_[:-3] + "pat", 'w') as pattern_file:  # FIX THIS
			rewrite_file(pattern_file, text)


def make_image_from_pattern(source_dir, destination_dir, image_colors):
	"""Build image from pattern"""
	for file_ in get_file_list(source_dir, ext=".pat"):
		filename = os.path.basename(file_)

		with open(file_, 'r') as image_file:
			text = image_file.read()

		for key, value in image_colors.items():
			text = text.replace("@" + key, value)

			# noinspection PyTypeChecker
			with open(os.path.join(destination_dir, filename.split(".")[0] + ".svg"), 'w') as image_file:
				rewrite_file(image_file, text)


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
		"""Build theme svg images from patterns"""
		for image_dir in self.config['Images'].values():
			make_image_from_pattern(image_dir, image_dir, self.config.colors)
