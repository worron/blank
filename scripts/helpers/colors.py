# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
from gi.repository import Gtk, GdkPixbuf, Gdk
from .common import hex_from_rgba, pixbuf_from_hex
from .parser import ThemeParser


class ParentColorDialog(Gtk.Dialog):
	"""Choose parent color dialog"""
	def __init__(self, parent, color_list, current):
		Gtk.Dialog.__init__(
			self, "Parent Color", parent, 0,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
		)
		self.set_default_size(300, 100)

		self.combo = Gtk.ComboBoxText()
		self.combo.set_entry_text_column(0)

		color_list.insert(0, "None")
		for color_name in color_list:
			self.combo.append_text(color_name)
		self.combo.set_active(color_list.index(current) if current in color_list else 0)

		box = self.get_content_area()
		box.add(self.combo)
		self.show_all()


class ColorsConfig:
	"""Colors settings helper"""
	def __init__(self, mainapp):
		self._mainapp = mainapp
		self.config = mainapp.config
		self.gui = mainapp.gui

		self.parser = ThemeParser(self.config)
		self.NO_PARENT = "None"
		self.PIXBUF_PATTERN_WIDTH = 128

		# build color list store
		self.colors_store = Gtk.ListStore(str, str, GdkPixbuf.Pixbuf, str)
		self.gui["colors_treeview"].set_model(self.colors_store)

		# treeview columns
		columns = (
			Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=0),
			Gtk.TreeViewColumn("Hex", Gtk.CellRendererText(), text=1),
			Gtk.TreeViewColumn("Color", Gtk.CellRendererPixbuf().new(), pixbuf=2),
			Gtk.TreeViewColumn("Parent", Gtk.CellRendererText(), text=3),
		)

		for column in columns:
			self.gui["colors_treeview"].append_column(column)

			# column width tweaks
			if column.get_title() == "Color":
				column.set_fixed_width(self.PIXBUF_PATTERN_WIDTH + 20)
			if column.get_title() == "Name":
				column.set_fixed_width(200)

		# signals
		self.gui["colors_treeview"].connect("cursor_changed", self.on_color_selected)
		self.gui["colors_treeview"].connect("row_activated", self._on_row_activated)
		self.gui["build_button"].connect("clicked", self.rebuild_theme)
		self.gui["color_button"].connect("color_set", self.on_color_changed)
		self.gui["parent_button"].connect("clicked", self.on_parent_color_click)

		# GUI setup
		self.fill_color_list()

	# noinspection PyUnusedLocal
	def _on_row_activated(self, *args):
		if self.gui["color_button"].get_sensitive():
			self.gui["color_button"].emit("clicked")

	def fill_color_list(self, last_position=0):
		"""Fill up color data"""
		self.colors_store.clear()

		for key, value in self.config.colors.items():
			raw = self.config["Colors"][key]
			parent = raw if raw in self.config.colors.keys() else self.NO_PARENT
			pixbuf = pixbuf_from_hex(value, width=self.PIXBUF_PATTERN_WIDTH)
			self.colors_store.append([key, value, pixbuf, parent])

		self.gui["colors_treeview"].set_cursor(last_position)

	def on_color_selected(self, tree):
		"""GUI handler"""
		path = tree.get_cursor()[0]
		if path is not None:
			treeiter = self.colors_store.get_iter(path)
			hex_color = self.colors_store[treeiter][1]
			parent = self.colors_store[treeiter][3]

			self.gui["color_button"].set_sensitive(parent == self.NO_PARENT)

			color = Gdk.RGBA()
			color.parse(hex_color)
			self.gui["color_button"].set_rgba(color)

	# noinspection PyUnusedLocal
	def rebuild_theme(self, widget):
		"""Full theme rebuild with current colors"""
		self.parser.write_colors()
		self.parser.update_scss()
		self.parser.rebuild_images()

		self._mainapp.emit("rebuild", None)  # FIXME: make signal without args

	# noinspection PyUnusedLocal
	def on_parent_color_click(self, button):
		path = self.gui["colors_treeview"].get_cursor()[0]
		treeiter = self.colors_store.get_iter(path)
		name = self.colors_store[treeiter][0]

		# build list of parent color candidates
		ccd = self.config["Colors"]
		parent_colors = [k for k in ccd.keys() if ccd[k] not in ccd.keys() and k != name]

		# show dialog
		dialog = ParentColorDialog(self.gui["window"], parent_colors, ccd[name])
		response = dialog.run()

		if response == Gtk.ResponseType.OK:
			selected = dialog.combo.get_active_text()

			# write config
			if selected in self.config.colors.keys():
				ccd[name] = selected
			else:
				ccd[name] = hex_from_rgba(self.gui["color_button"].get_rgba())

			# reload colors
			self.config.load_colors()
			self.fill_color_list(last_position=path)

		dialog.destroy()

	def on_color_changed(self, button):
		path = self.gui["colors_treeview"].get_cursor()[0]
		treeiter = self.colors_store.get_iter(path)
		name = self.colors_store[treeiter][0]

		hex_color = hex_from_rgba(button.get_rgba())

		self.config["Colors"][name] = hex_color
		self.config.load_colors()
		self.fill_color_list(last_position=path)
