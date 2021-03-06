# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
import os


def read_params(str_):
	"""Read list of parametrs from srtring"""
	return [element.strip() for element in str_.split(";")]


def get_file_list(path, ext='.svg', deep=False):
	"""Find all files in directories"""
	filelist = []
	for root, _, files in os.walk(path):
		for name in files:
			fullname = os.path.join(root, name)
			if (name.endswith(ext) and not os.path.islink(fullname)):
				filelist.append(fullname)
		if not deep: break
	return filelist


def rewrite_file(file_, text):
	"""Rewrite opened file"""
	file_.seek(0)
	file_.write(text)
	file_.truncate()


def hex_from_rgba(rgba):
	"""Translate color from Gdk.RGBA to html hex format"""
	return "#%02X%02X%02X" % tuple([int(getattr(rgba, name) * 255) for name in ("red", "green", "blue")])
