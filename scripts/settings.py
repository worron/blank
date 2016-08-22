#!/usr/bin/env python3
# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
import os

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from helpers.cfreader import ConfigReader
from helpers.viewer import IconView
from helpers.colors import ColorsConfig


class MainWindow:
	"""Main program"""
	def __init__(self):
		# Read config
		self.config = ConfigReader("scripts/settings.ini")

		# Load GUI
		self.builder = Gtk.Builder()
		self.builder.add_from_file('scripts/gui/main.glade')

		gui_elements = (
			'window', "colors_box", "build_button", "exit_button", "images_iconview", "notebook",
			"colors_scrolledwindow"
		)
		self.gui = {element: self.builder.get_object(element) for element in gui_elements}

		# Pages

		self.pages = [ColorsConfig(self.config, self.gui), IconView(self.config, self.gui)]
		self.last_handlers = dict()

		# Connect signals
		self.signals = dict()
		self.gui['window'].connect("delete-event", self.on_close_window)
		self.gui['exit_button'].connect("clicked", self.on_close_window)
		self.gui['notebook'].connect("switch_page", self.on_page_changed)

		# Application init
		self.gui['window'].show_all()
		self.gui['notebook'].emit("switch_page", self.gui['colors_scrolledwindow'], 0)

	def on_page_changed(self, nb, page, index):
		for button in ['build_button']:
			if button in self.last_handlers:
				self.gui[button].disconnect_by_func(self.last_handlers[button])
			if button in self.pages[index].mhandlers:
				self.gui[button].connect("clicked", self.pages[index].mhandlers[button])
			# self.gui[button].set_sensitive(button in self.pages[index].mhandlers)

		self.last_handlers = self.pages[index].mhandlers

		if hasattr(self.pages[index], 'on_page_switch'):
			self.pages[index].on_page_switch()

	def on_close_window(self, *args):
		self.config.save()
		Gtk.main_quit(*args)


if __name__ == "__main__":
	os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
	MainWindow()
	Gtk.main()
