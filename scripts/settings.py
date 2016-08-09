#!/usr/bin/env python3
# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
import os
import configparser

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


# Theme files settings
THEME_SETTINGS = {
	"gtk2": {
		"files": ["gtk-2.0/gtkrc"],
		"separator": "# === Autogenerated part end here =============================================",
		"pattern": 'gtk-color-scheme = "%s:%s"\n'
	}
}


# Support functions
def hex_from_rgba(rgba):
	"""Translate color from Gdk.RGBA to html hex format"""
	return "#%02X%02X%02X" % tuple([int(getattr(rgba, name) * 255) for name in ("red", "green", "blue")])


# Main classes
class ThemeParser:
	"Config files parser"
	def __init__(self):
		pass

	def write_colors(self, colors):
		for theme in THEME_SETTINGS:
			for file_ in THEME_SETTINGS[theme]["files"]:
				with open(file_, 'r+') as themefile:
					text = themefile.read()
					old_colors = text.split(THEME_SETTINGS[theme]["separator"])[0]
					new_colors = "".join([THEME_SETTINGS[theme]["pattern"] % (n, c) for n, c in colors.items()])

					themefile.seek(0)
					themefile.write(text.replace(old_colors, new_colors))
					themefile.truncate()


class MainWindow:
	"""Main program"""
	def __init__(self):
		# Read config
		self.configfile = "scripts/settings.ini"
		self.config = configparser.ConfigParser()
		self.config.read(self.configfile)

		# Load parser
		self.parser = ThemeParser()

		# Load GUI
		self.builder = Gtk.Builder()
		self.builder.add_from_file('scripts/gui.glade')

		gui_elements = ('window', "colors_box", "build_button", "exit_button")
		self.gui = {element: self.builder.get_object(element) for element in gui_elements}

		# Fill up GUI
		self.color_buttons = dict()
		for key, value in self.config['Colors'].items():
			box = Gtk.Box(spacing=8)
			label = Gtk.Label(key)
			self.color_buttons[key] = Gtk.ColorButton()

			color = Gdk.RGBA()
			color.parse(value)
			self.color_buttons[key].set_rgba(color)

			box.pack_start(label, False, False, 0)
			box.pack_end(self.color_buttons[key], False, False, 0)
			self.gui["colors_box"].pack_start(box, False, False, 0)
			self.gui["colors_box"].pack_start(Gtk.Separator(), False, False, 0)

		# Connect signals
		self.signals = dict()
		self.gui['window'].connect("delete-event", self.on_close_window)
		self.gui['build_button'].connect("clicked", self.on_rebuild_click)
		self.gui['exit_button'].connect("clicked", self.on_close_window)

		self.gui['window'].show_all()

	def on_rebuild_click(self, widget):
		for key, button in self.color_buttons.items():
			self.config['Colors'][key] = hex_from_rgba(button.get_rgba())
		with open(self.configfile, 'w') as configfile:
			self.config.write(configfile)

		self.parser.write_colors(self.config['Colors'])

	def on_close_window(self, *args):
		Gtk.main_quit(*args)


if __name__ == "__main__":
	os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
	MainWindow()
	Gtk.main()
