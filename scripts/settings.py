#!/usr/bin/env python3
# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
import os
import subprocess

from helpers.cfreader import ConfigReader, read_params

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


# Support functions
def hex_from_rgba(rgba):
	"""Translate color from Gdk.RGBA to html hex format"""
	return "#%02X%02X%02X" % tuple([int(getattr(rgba, name) * 255) for name in ("red", "green", "blue")])


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


# Main classes
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


class MainWindow:
	"""Main program"""
	def __init__(self):
		# Read config
		self.config = ConfigReader("scripts/settings.ini")

		# Load parser
		self.parser = ThemeParser(self.config)

		# Load GUI
		self.builder = Gtk.Builder()
		self.builder.add_from_file('scripts/gui.glade')

		gui_elements = ('window', "colors_box", "build_button", "exit_button", "pattern_button")
		self.gui = {element: self.builder.get_object(element) for element in gui_elements}

		# Fill up GUI
		self.color_buttons = dict()
		self.pattern_checks = dict()
		self.gui["colors_box"].pack_start(Gtk.Separator(), False, False, 0)

		current_pattents = self.config.get_list("Pattern", "colors")
		for key, value in self.config['Colors'].items():
			box = Gtk.Box(spacing=8)
			label = Gtk.Label(key)
			self.color_buttons[key] = Gtk.ColorButton()
			self.pattern_checks[key] = Gtk.CheckButton()

			color = Gdk.RGBA()
			color.parse(value)
			self.color_buttons[key].set_rgba(color)

			self.pattern_checks[key].set_active(key in current_pattents)

			box.pack_start(label, False, False, 0)
			box.pack_end(self.pattern_checks[key], False, False, 0)
			box.pack_end(self.color_buttons[key], False, False, 0)
			self.gui["colors_box"].pack_start(box, False, False, 0)
			self.gui["colors_box"].pack_start(Gtk.Separator(), False, False, 0)

		# Connect signals
		self.signals = dict()
		self.gui['window'].connect("delete-event", self.on_close_window)
		self.gui['build_button'].connect("clicked", self.on_rebuild_click)
		self.gui['pattern_button'].connect("clicked", self.on_pattern_click)
		self.gui['exit_button'].connect("clicked", self.on_close_window)

		# Application init
		self.gui['window'].show_all()

	def on_rebuild_click(self, widget):
		for key, button in self.color_buttons.items():
			self.config['Colors'][key] = hex_from_rgba(button.get_rgba())

		self.parser.write_colors()
		self.parser.update_scss()

		self.parser.make_image_from_pattern()

	def on_pattern_click(self, widget):
		current_pattents = [key for key in self.pattern_checks if self.pattern_checks[key].get_active()]
		self.config.set_list("Pattern", "colors", current_pattents)

		self.parser.make_pattern_from_image()

	def on_close_window(self, *args):
		self.config.save()
		Gtk.main_quit(*args)


if __name__ == "__main__":
	os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
	MainWindow()
	Gtk.main()
