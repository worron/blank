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
		self.tempdir = tempfile.TemporaryDirectory()

		self.isize = int(self.config.get("GUI", "icon_size"))
		self.psize = int(self.config.get("GUI", "pattern_size"))

		# Pattern location dialog
		self.location_dialog = Gtk.FileChooserDialog(
			"Choose pattern directory", self.gui["window"], Gtk.FileChooserAction.SELECT_FOLDER,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
		)

		# Icon sizes
		self.gui["images_size_spinbutton"].set_value(self.isize)
		self.gui["patterns_size_spinbutton"].set_value(self.psize)
		self.gui['images_size_spinbutton'].connect("value_changed", self.on_image_size_changed)
		self.gui['patterns_size_spinbutton'].connect("value_changed", self.on_patterns_size_changed)

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
		self.gui['pattern_directory_button'].connect("clicked", self.on_change_directory_click)

		# Fill up GUI
		self.update_location_label()

	def make_pattern(self, widget):
		"""Make patterns form images"""
		image_color_names = self.config.get_list("Pattern", "colors")
		image_colors = {k: self.config.colors[k] for k in image_color_names}
		make_pattern_from_image(self.curdir, image_colors)

		self.update_patterns_view()

	@staticmethod
	def load_images(path, store, size):
		"""Show svg images"""
		images = get_file_list(path, ".svg")

		store.clear()
		for image in images:
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(image, size, size)
			store.append([pixbuf])

	def on_page_switch(self):
		"""Notebook handler"""
		self.load_images(self.curdir, self.images_store, self.isize)
		self.update_patterns_view()

	def update_patterns_view(self):
		"""Update patterns"""
		for oldfile in get_file_list(self.tempdir.name, ".svg"): os.remove(oldfile)
		make_image_from_pattern(self.curdir, self.tempdir.name, self.config.colors)
		self.load_images(self.tempdir.name, self.pattern_store, self.psize)

	def on_image_size_changed(self, button):
		self.isize = int(button.get_value())
		self.load_images(self.curdir, self.images_store, self.isize)

	def on_patterns_size_changed(self, button):
		self.psize = int(button.get_value())
		self.update_patterns_view()

	def on_patterns_delete_click(self, *args):
		for patfile in get_file_list(self.curdir, ".pat"): os.remove(patfile)
		self.update_patterns_view()

	def on_images_delete_click(self, *args):
		for imagefile in get_file_list(self.curdir, ".svg"): os.remove(imagefile)
		self.load_images(self.curdir, self.images_store, self.isize)

	def on_change_directory_click(self, *args):
		self.location_dialog.set_current_folder(self.curdir)

		response = self.location_dialog.run()
		if response == Gtk.ResponseType.OK:
			self.curdir = self.location_dialog.get_current_folder()
			self.update_location_label()

			self.load_images(self.curdir, self.images_store, self.isize)
			self.update_patterns_view()

		self.location_dialog.hide()

	def update_location_label(self):
		self.gui["pattern_location_label"].set_text(os.path.abspath(self.curdir))

	def on_exit(self):
		self.tempdir.cleanup()
		self.location_dialog.destroy()
