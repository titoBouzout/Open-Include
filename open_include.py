import sublime, sublime_plugin
import os.path
import re

class OpenInclude(sublime_plugin.TextCommand):
	def run(self, edit):
		window = sublime.active_window()
		view = self.view
		for region in view.sel():
			opened = False

			# between quotes
			syntax = self.view.syntax_name(region.begin())
			if re.match(".*string.quoted.double", syntax) or re.match(".*string.quoted.single", syntax):
				opened = self.do_open(window, view, view.substr(view.extract_scope(region.begin())))

			# selected text
			if not opened:
				opened = self.do_open(window, view, view.substr(sublime.Region(region.begin(), region.end())))

			# current lines
			if not opened:
				opened = self.do_open(window, view, view.substr(sublime.Region(view.line(region.begin()).begin(), view.line(region.end()).end())))

	def do_open(self, window, view, paths):

		paths = paths.split('\n')
		opened = False
		for path in paths:
			# remove quotes
			path = re.sub('^"|\'', '',  re.sub('"|\'$', '', path.strip()))

			# remove :row:col
			path = re.sub('(\:[0-9]*)+$', '', path.strip()).strip()

			if path == '':
				continue

			# relative to view
			if view.file_name() != None and view.file_name() != '':
				maybe_path = self.resolve_relative(os.path.dirname(view.file_name()), path)
				if os.path.isfile(maybe_path):
					window.open_file(maybe_path)
					sublime.status_message("Opening file " + maybe_path)
					opened = True
					continue

			# relative to project folders
			for maybe_path in sublime.active_window().folders():
				maybe_path = self.resolve_relative(maybe_path, path)
				if os.path.isfile(maybe_path):
					window.open_file(maybe_path)
					sublime.status_message("Opening file " + maybe_path)
					opened = True
					break

			#absolute
			if os.path.isfile(path):
				window.open_file(path)
				sublime.status_message("Opening file " + path)
				opened = True
				continue

		return opened

	def resolve_relative(self, absolute, path):
		subs = path.replace('\\', '/').split('/')
		for sub in subs:
			if sub != '':
				absolute = os.path.join(absolute, sub)
		return absolute