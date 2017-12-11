# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
import os
from gi.repository import GdkPixbuf


def get_file_list(path, ext='.svg', deep=False):
	"""Find all files in directories"""
	file_list = []
	for root, _, files in os.walk(path):
		for name in files:
			fullname = os.path.join(root, name)
			if name.endswith(ext) and not os.path.islink(fullname):
				file_list.append(fullname)
		if not deep:
			break
	return file_list


def pixbuf_from_hex(value, width=128, height=16):
	"""Create GDK pixbuf from color"""
	pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, False, 8, width, height)
	pixbuf.fill(int(value[1:] + "FF", 16))
	return pixbuf


def rewrite_file(file_, text):
	"""Rewrite opened file"""
	file_.seek(0)
	file_.write(text)
	file_.truncate()


def hex_from_rgba(rgba):
	"""Translate color from Gdk.RGBA to html hex format"""
	return "#%02X%02X%02X" % tuple([int(getattr(rgba, name) * 255) for name in ("red", "green", "blue")])
