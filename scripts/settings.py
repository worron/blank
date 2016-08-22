#!/usr/bin/env python3
# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
import os

from helpers.cfreader import ConfigReader
from helpers.themeparser import ThemeParser

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


# Support functions
def hex_from_rgba(rgba):
	"""Translate color from Gdk.RGBA to html hex format"""
	return "#%02X%02X%02X" % tuple([int(getattr(rgba, name) * 255) for name in ("red", "green", "blue")])


class MainWindow:
	"""Main program"""
	def __init__(self):
		# Read config
		self.config = ConfigReader("scripts/settings.ini")

		# Load parser
		self.parser = ThemeParser(self.config)

		# Load GUI
		self.builder = Gtk.Builder()
		self.builder.add_from_file('scripts/gui/main.glade')

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
