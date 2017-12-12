# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
import os

from gi.repository import Gtk, GdkPixbuf
from .common import get_file_list


class IconView:
	"""Images viewer"""
	def __init__(self, mainapp):
		self._mainapp = mainapp
		self.config = mainapp.config
		self.gui = mainapp.gui

		self.current_dir = list(self.config['Images'].values())[0]
		self.isize = int(self.config.get("GUI", "icon_size"))

		# Images location dialog
		self.location_dialog = Gtk.FileChooserDialog(
			"Choose images directory", self.gui["window"], Gtk.FileChooserAction.SELECT_FOLDER,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
		)

		# Icon size
		self.gui["images_size_spinbutton"].set_value(self.isize)
		self.gui['images_size_spinbutton'].connect("value_changed", self.on_image_size_changed)

		# Create icon stores
		self.images_store = Gtk.ListStore(GdkPixbuf.Pixbuf)
		self.gui['images_iconview'].set_model(self.images_store)
		self.gui['images_iconview'].set_pixbuf_column(0)

		# signals
		self._mainapp.connect("rebuild", self.reload_images)
		self.gui['images_directory_button'].connect("clicked", self.on_change_directory_click)

		# Fill up GUI
		self.update_location_label()

	@staticmethod
	def load_images(path, store, size):
		"""Show svg images"""
		images = get_file_list(path, ".svg")

		store.clear()
		for image in images:
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(image, size, size)
			store.append([pixbuf])

	# noinspection PyUnusedLocal
	def reload_images(self, *args):
		"""Notebook handler"""
		self.load_images(self.current_dir, self.images_store, self.isize)

	def on_image_size_changed(self, button):
		self.isize = int(button.get_value())
		self.load_images(self.current_dir, self.images_store, self.isize)

	# noinspection PyUnusedLocal
	def on_change_directory_click(self, *args):
		self.location_dialog.set_current_folder(self.current_dir)

		response = self.location_dialog.run()
		if response == Gtk.ResponseType.OK:
			self.current_dir = self.location_dialog.get_current_folder()
			self.update_location_label()

			self.load_images(self.current_dir, self.images_store, self.isize)

		self.location_dialog.hide()

	def update_location_label(self):
		self.gui["images_location_label"].set_text(os.path.abspath(self.current_dir))

	def clean_up(self):
		self.location_dialog.destroy()
