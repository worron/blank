# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
import os
import tempfile

from gi.repository import Gtk, GdkPixbuf
from .common import get_file_list
from .parser import make_pattern_from_image, make_image_from_pattern


class IconView:
	"Images and patterns viewer"
	def __init__(self, config, gui):
		self.config = config
		self.gui = gui
		self.curdir = self.config.get("Pattern", "directory")
		self.ISIZE = int(self.config.get("GUI", "icon_size"))
		self.tempdir = tempfile.TemporaryDirectory()

		# Cleate icon stores
		self.images_store = Gtk.ListStore(GdkPixbuf.Pixbuf)
		self.gui['images_iconview'].set_model(self.images_store)
		self.gui['images_iconview'].set_pixbuf_column(0)

		self.pattern_store = Gtk.ListStore(GdkPixbuf.Pixbuf)
		self.gui['patterns_iconview'].set_model(self.pattern_store)
		self.gui['patterns_iconview'].set_pixbuf_column(0)

		# Mainpage buttnons hanlers
		self.mhandlers = dict()
		self.mhandlers['build_button'] = self.make_pattern

		# Connect local page signals
		self.signals = dict()
		self.gui['patterns_delete_button'].connect("clicked", self.on_patterns_delete_click)
		self.gui['images_delete_button'].connect("clicked", self.on_images_delete_click)

	def make_pattern(self, widget):
		"""Make patterns form images"""
		image_color_names = self.config.get_list("Pattern", "colors")
		image_colors = {k: self.config['Colors'][k] for k in image_color_names}
		make_pattern_from_image(self.curdir, image_colors)

		self.update_patterns_view()

	def load_images(self, path, store):
		"""Show svg images"""
		images = get_file_list(path, ".svg")

		store.clear()
		for image in images:
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(image, self.ISIZE, self.ISIZE)
			store.append([pixbuf])

	def on_page_switch(self):
		"""Notebook handler"""
		# show images
		self.load_images(self.curdir, self.images_store)

		# show patterns
		self.update_patterns_view()

	def update_patterns_view(self):
		"""Update patterns"""
		for oldfile in get_file_list(self.tempdir.name, ".svg"): os.remove(oldfile)
		make_image_from_pattern(self.curdir, self.tempdir.name, self.config['Colors'])
		self.load_images(self.tempdir.name, self.pattern_store)

	def on_patterns_delete_click(self, *args):
		for patfile in get_file_list(self.curdir, ".pat"): os.remove(patfile)
		self.update_patterns_view()

	def on_images_delete_click(self, *args):
		for imagefile in get_file_list(self.curdir, ".svg"): os.remove(imagefile)
		self.load_images(self.curdir, self.images_store)

	def on_exit(self):
		self.tempdir.cleanup()
