# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
from gi.repository import Gtk, Gdk
from .common import hex_from_rgba
from .parser import ThemeParser


class ParentColorDialog(Gtk.Dialog):
	"""Choose parent color dialog"""
	def __init__(self, parent, clist, current):
		Gtk.Dialog.__init__(
			self, "Parent Color", parent, 0,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
		)
		self.set_default_size(300, 100)

		self.combo = Gtk.ComboBoxText()
		self.combo.set_entry_text_column(0)

		clist.insert(0, "None")
		for cname in clist:
			self.combo.append_text(cname)
		self.combo.set_active(clist.index(current) if current in clist else 0)

		box = self.get_content_area()
		box.add(self.combo)
		self.show_all()


class ColorsConfig:
	"Colors settings helper"
	def __init__(self, config, gui):
		self.config = config
		self.gui = gui
		self.parser = ThemeParser(self.config)
		self.NO_PARENT = "Select parent"

		# Fill up GUI
		self.color_buttons = dict()
		self.parent_buttons = dict()
		self.pattern_checks = dict()
		self.bsignals = dict()
		self.gui["colors_box"].pack_start(Gtk.Separator(), False, False, 0)

		# colors list
		current_pattents = self.config.get_list("Pattern", "colors")
		for key, value in self.config.colors.items():
			box = Gtk.Box(spacing=8)
			label = Gtk.Label(key)

			# init row elements
			self.color_buttons[key] = Gtk.ColorButton()
			self.parent_buttons[key] = Gtk.Button()
			self.pattern_checks[key] = Gtk.CheckButton()

			# set color button
			self.set_color_button_state(key, value)
			self.bsignals[key] = self.color_buttons[key].connect("color_set", self.on_color_changed, key)

			# set pattern check
			self.pattern_checks[key].set_active(key in current_pattents)
			self.pattern_checks[key].connect("toggled", self.on_pattern_check_toggled, key)

			# set parent button
			self.parent_buttons[key].set_property("width-request", 300)
			self.set_parent_button_state(self.config["Colors"][key], key)
			self.parent_buttons[key].connect("clicked", self.on_parent_color_click, key)

			# built color settins row
			box.pack_start(label, False, False, 0)
			box.pack_end(self.pattern_checks[key], False, False, 0)
			box.pack_end(self.color_buttons[key], False, False, 0)
			box.pack_end(self.parent_buttons[key], False, False, 0)
			self.gui["colors_box"].pack_start(box, False, False, 0)
			self.gui["colors_box"].pack_start(Gtk.Separator(), False, False, 0)

		# Mainpage buttnons hanlers
		self.mhandlers = dict()
		self.mhandlers['build_button'] = self.rebuild_theme

	def rebuild_theme(self, widget):
		"""Full theme rebuild with current colors"""
		self.parser.write_colors()
		self.parser.update_scss()
		self.parser.rebuild_images()

	def set_color_button_state(self, bname, hex_color):
		"""Set button rgba form hex color"""
		color = Gdk.RGBA()
		color.parse(hex_color)
		self.color_buttons[bname].set_rgba(color)

	def set_parent_button_state(self, pcolor, name):
		"""Set parent button label"""
		is_inherited = pcolor in self.config.colors.keys()
		self.color_buttons[name].set_sensitive(not is_inherited)
		self.parent_buttons[name].set_label("Parent: " + pcolor if is_inherited else self.NO_PARENT)

	def on_pattern_check_toggled(self, button, name):
		current_pattents = [key for key in self.pattern_checks if self.pattern_checks[key].get_active()]
		self.config.set_list("Pattern", "colors", current_pattents)

	def on_parent_color_click(self, button, name):
		# build list of parent color candidats
		ccd = self.config["Colors"]
		parent_colors = [k for k in ccd.keys() if ccd[k] not in ccd.keys() and k != name]

		# show dilaog
		dialog = ParentColorDialog(self.gui["window"], parent_colors, ccd[name])
		response = dialog.run()

		if response == Gtk.ResponseType.OK:
			# set parent button state
			selected = dialog.combo.get_active_text()
			self.set_parent_button_state(selected, name)

			# write config
			if selected in self.config.colors.keys():
				ccd[name] = selected
				with self.color_buttons[name].handler_block(self.bsignals[name]):
					self.set_color_button_state(name, ccd[selected])
			else:
				ccd[name] = hex_from_rgba(self.color_buttons[name].get_rgba())

			self.config.load_colors()

		dialog.destroy()

	def on_color_changed(self, button, name):
		hex_color = hex_from_rgba(button.get_rgba())
		self.config["Colors"][name] = hex_color
		for cname in self.config.colors.keys():
			if self.config["Colors"][cname] == name:
				with self.color_buttons[cname].handler_block(self.bsignals[cname]):
					self.set_color_button_state(cname, hex_color)
		self.config.load_colors()
