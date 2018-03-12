#!/usr/bin/env python3
# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
import os

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject

from helpers.cfreader import ConfigReader
from helpers.viewer import IconView
from helpers.colors import ColorsConfig


class MainWindow(GObject.GObject):
	"""Main program"""
	__gsignals__ = {
		"rebuild": (GObject.SIGNAL_RUN_FIRST, None, (object,))
	}

	def __init__(self):
		super().__init__()

		# Read config
		self.config = ConfigReader("scripts/settings.ini")

		# Load GUI
		self.builder = Gtk.Builder()
		self.builder.add_from_file('scripts/gui/settings.ui')

		gui_elements = (
			"window", "stack", "colors_box", "icons_box", "parent_button", "color_button", "images_iconview",
			"build_button", "colors_treeview", "images_iconview", "images_location_label", "images_directory_button",
			"images_size_spinbutton", "save-load-menu-button",
		)
		self.gui = {element: self.builder.get_object(element) for element in gui_elements}

		# Pages
		self.gui["stack"].add_titled(self.gui["colors_box"], "colors", "Colors")
		self.gui["stack"].add_titled(self.gui["icons_box"], "icons", "Icons")

		self.colors_page = ColorsConfig(self)
		self.icons_page = IconView(self)

		# Connect signals
		self.signals = dict()
		self.gui['window'].connect("delete-event", self.on_close_window)

		# Application init
		self.gui['window'].show_all()
		self.icons_page.reload_images()

	def on_close_window(self, *args):
		self.icons_page.clean_up()
		self.config.save()
		Gtk.main_quit(*args)


if __name__ == "__main__":
	os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
	MainWindow()
	Gtk.main()
