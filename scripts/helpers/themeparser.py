# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
import os
import subprocess

from .cfreader import read_params


def get_file_list(*dirlist, ext='.svg'):
	"""Find all files in directories"""
	filelist = []
	for path in dirlist:
		for root, _, files in os.walk(path):
			filelist.extend([os.path.join(root, name) for name in files if name.endswith(ext)])
	return filelist


def rewrite_file(file_, text):
	"""Rewrite opened file"""
	file_.seek(0)
	file_.write(text)
	file_.truncate()


class ThemeParser:
	"Config files parser"
	def __init__(self, config):
		self.config = config
		self.scss_dir = config["SCSS"]["directory"]
		self.scss_command = self.config.get_list("SCSS", "command")
		self.images = []

		theme_sections = ["GTK2", "GTK3"]
		self.themes = []

		for theme in theme_sections:
			td = {
				"files": self.config.get_list(theme, "files"),
				"separator": self.config.get(theme, "separator"),
				"pattern": self.config.get(theme, "pattern") + '\n'
			}
			self.themes.append(td)

		for directories in self.config['Images'].values():
			self.images.append(dict(zip(("source", "dest"), read_params(directories))))

	def write_colors(self):
		"""Rewrite colors in theme files"""
		for theme in self.themes:
			for file_ in theme["files"]:
				with open(file_, 'r+') as themefile:
					text = themefile.read()
					old_colors = text.split(theme["separator"])[0]
					new_colors = "".join([theme["pattern"] % (n, c) for n, c in self.config['Colors'].items()])
					rewrite_file(themefile, text.replace(old_colors, new_colors))

	def update_scss(self):
		"""Build css files from scss"""
		try:
			subprocess.call(self.scss_command, cwd=self.scss_dir)
		except Exception as e:
			print("Fail to update scss\n", e)

	def make_image_from_pattern(self):
		"""Build theme svg images from patterns"""
		for images in self.images:
			for file_ in get_file_list(images["source"], ext=".pat"):
				filename = os.path.basename(file_)

				with open(file_, 'r') as imagefile:
					text = imagefile.read()

				for key, value in self.config['Colors'].items():
					text = text.replace("@" + key, value)

				with open(os.path.join(images["dest"], filename.split(".")[0] + ".svg"), 'w') as imagefile:
					rewrite_file(imagefile, text)

	def make_pattern_from_image(self):
		image_color_names = self.config.get_list("Pattern", "colors")
		image_colors = {k: self.config['Colors'][k] for k in image_color_names}
		filelist = get_file_list(self.config["Pattern"]["directory"])

		for file_ in filelist:
			with open(file_, 'r+') as imagefile:
				text = imagefile.read()

				for key, value in image_colors.items():
					text = text.replace(value, "@" + key)
					text = text.replace(value.lower(), "@" + key)

				rewrite_file(imagefile, text)

			os.rename(file_, file_.split(".")[0] + ".pat")
