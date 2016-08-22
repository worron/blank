# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
from gi.repository import Gtk, Gdk
from .common import hex_from_rgba
from .parser import ThemeParser


class ColorsConfig:
	"Colors settings helper"
	def __init__(self, config, gui):
		self.config = config
		self.gui = gui
		self.parser = ThemeParser(self.config)

		# Fill up GUI
		self.color_buttons = dict()
		self.pattern_checks = dict()
		self.gui["colors_box"].pack_start(Gtk.Separator(), False, False, 0)

		# colors list
		current_pattents = self.config.get_list("Pattern", "colors")
		for key, value in self.config['Colors'].items():
			box = Gtk.Box(spacing=8)
			label = Gtk.Label(key)
			self.color_buttons[key] = Gtk.ColorButton()
			self.pattern_checks[key] = Gtk.CheckButton()

			color = Gdk.RGBA()
			color.parse(value)
			self.color_buttons[key].set_rgba(color)
			self.color_buttons[key].connect("color_set", self.on_color_changed)

			self.pattern_checks[key].set_active(key in current_pattents)
			self.pattern_checks[key].connect("toggled", self.on_pattern_check_toggled, key)

			box.pack_start(label, False, False, 0)
			box.pack_end(self.pattern_checks[key], False, False, 0)
			box.pack_end(self.color_buttons[key], False, False, 0)
			self.gui["colors_box"].pack_start(box, False, False, 0)
			self.gui["colors_box"].pack_start(Gtk.Separator(), False, False, 0)

		# Mainpage buttnons hanlers
		self.mhandlers = dict()
		self.mhandlers['build_button'] = self.rebuild_theme

	def rebuild_theme(self, widget):
		self.parser.write_colors()
		self.parser.update_scss()
		self.parser.rebuild_images()

	def on_pattern_check_toggled(self, button, name):
		current_pattents = [key for key in self.pattern_checks if self.pattern_checks[key].get_active()]
		self.config.set_list("Pattern", "colors", current_pattents)

	def on_color_changed(self, *args):
		for key, button in self.color_buttons.items():
			self.config['Colors'][key] = hex_from_rgba(button.get_rgba())
