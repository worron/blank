# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
from gi.repository import Gtk, Gdk
from .common import hex_from_rgba
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
	def __init__(self, config, gui):
		self.config = config
		self.gui = gui
		self.parser = ThemeParser(self.config)
		self.NO_PARENT = "Select parent"

		# Fill up GUI
		self.color_buttons = dict()
		self.parent_buttons = dict()
		self.pattern_checks = dict()
		self.button_signals = dict()
		self.gui["colors_box"].pack_start(Gtk.Separator(), False, False, 0)

		# colors list
		current_patterns = self.config.get_list("Pattern", "colors")
		for key, value in self.config.colors.items():
			box = Gtk.Box(spacing=8)
			label = Gtk.Label(key)

			# init row elements
			self.color_buttons[key] = Gtk.ColorButton()
			self.parent_buttons[key] = Gtk.Button()
			self.pattern_checks[key] = Gtk.CheckButton()

			# set color button
			self.set_color_button_state(key, value)
			self.button_signals[key] = self.color_buttons[key].connect("color_set", self.on_color_changed, key)

			# set pattern check
			self.pattern_checks[key].set_active(key in current_patterns)
			self.pattern_checks[key].connect("toggled", self.on_pattern_check_toggled, key)

			# set parent button
			self.parent_buttons[key].set_property("width-request", 300)
			self.set_parent_button_state(self.config["Colors"][key], key)
			self.parent_buttons[key].connect("clicked", self.on_parent_color_click, key)

			# built color settings row
			box.pack_start(label, False, False, 0)
			box.pack_end(self.pattern_checks[key], False, False, 0)
			box.pack_end(self.color_buttons[key], False, False, 0)
			box.pack_end(self.parent_buttons[key], False, False, 0)
			self.gui["colors_box"].pack_start(box, False, False, 0)
			self.gui["colors_box"].pack_start(Gtk.Separator(), False, False, 0)

		# Main page buttons handlers
		self.main_handlers = dict()
		self.main_handlers['build_button'] = self.rebuild_theme

	# noinspection PyUnusedLocal
	def rebuild_theme(self, widget):
		"""Full theme rebuild with current colors"""
		self.parser.write_colors()
		self.parser.update_scss()
		# self.parser.rebuild_images()

	def set_color_button_state(self, button_name, hex_color):
		"""Set button rgba form hex color"""
		color = Gdk.RGBA()
		color.parse(hex_color)
		self.color_buttons[button_name].set_rgba(color)

	def set_parent_button_state(self, parent_color, name):
		"""Set parent button label"""
		is_inherited = parent_color in self.config.colors.keys()
		self.color_buttons[name].set_sensitive(not is_inherited)
		self.parent_buttons[name].set_label("Parent: " + parent_color if is_inherited else self.NO_PARENT)

	# noinspection PyUnusedLocal
	def on_pattern_check_toggled(self, button, name):
		current_patterns = [key for key in self.pattern_checks if self.pattern_checks[key].get_active()]
		self.config.set_list("Pattern", "colors", current_patterns)

	# noinspection PyUnusedLocal
	def on_parent_color_click(self, button, name):
		# build list of parent color candidates
		ccd = self.config["Colors"]
		parent_colors = [k for k in ccd.keys() if ccd[k] not in ccd.keys() and k != name]

		# show dialog
		dialog = ParentColorDialog(self.gui["window"], parent_colors, ccd[name])
		response = dialog.run()

		if response == Gtk.ResponseType.OK:
			# set parent button state
			selected = dialog.combo.get_active_text()
			self.set_parent_button_state(selected, name)

			# write config
			if selected in self.config.colors.keys():
				ccd[name] = selected
				with self.color_buttons[name].handler_block(self.button_signals[name]):
					self.set_color_button_state(name, ccd[selected])
			else:
				ccd[name] = hex_from_rgba(self.color_buttons[name].get_rgba())

			self.config.load_colors()

		dialog.destroy()

	def on_color_changed(self, button, name):
		hex_color = hex_from_rgba(button.get_rgba())
		self.config["Colors"][name] = hex_color
		for color_name in self.config.colors.keys():
			if self.config["Colors"][color_name] == name:
				with self.color_buttons[color_name].handler_block(self.button_signals[color_name]):
					self.set_color_button_state(color_name, hex_color)
		self.config.load_colors()
