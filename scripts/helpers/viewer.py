# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
from gi.repository import Gtk, GdkPixbuf
from .common import get_file_list
from .parser import make_pattern_from_image


class IconView:
	"Images and patterns viewer"
	def __init__(self, config, gui):
		self.config = config
		self.gui = gui
		self.curdir = self.config.get("Pattern", "directory")

		self.images_store = Gtk.ListStore(GdkPixbuf.Pixbuf)
		self.gui['images_iconview'].set_model(self.images_store)
		self.gui['images_iconview'].set_pixbuf_column(0)

		# Mainpage buttnons hanlers
		self.mhandlers = dict()
		self.mhandlers['build_button'] = self.make_pattern

	def make_pattern(self, widget):
		"""Make patterns form images"""
		image_color_names = self.config.get_list("Pattern", "colors")
		image_colors = {k: self.config['Colors'][k] for k in image_color_names}
		make_pattern_from_image(self.config["Pattern"]["directory"], image_colors)

	def show_images(self):
		"""Show svg images"""
		images = get_file_list(self.curdir, ".svg")

		self.images_store.clear()
		for image in images:
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(image, 48, 48)
			self.images_store.append([pixbuf])

	def on_page_switch(self):
		self.show_images()
