import sublime, sublime_plugin
import os.path
import re

class OpenInclude(sublime_plugin.TextCommand):
	def run(self, edit):
		for region in self.view.sel():
			opened = False

			# between quotes
			syntax = self.view.syntax_name(region.begin())
			if re.match(".*string.quoted.double", syntax) or re.match(".*string.quoted.single", syntax):
				opened = self.do_open(self.view.substr(self.view.extract_scope(region.begin())))

			# selected text
			if not opened:
				opened = self.do_open(self.view.substr(sublime.Region(region.begin(), region.end())))

			# current line
			if not opened:
				opened = self.do_open(self.view.substr(sublime.Region(self.view.line(region.begin()).begin(), self.view.line(region.begin()).end())))

	def do_open(self, path):
		# remove quotes
		path = re.sub('^"|\'', '', re.sub('^"|\'', '', path.strip()))
		path = re.sub('"|\'$', '', re.sub('^"|\'$', '', path.strip()))

		# remove :row:col
		path = re.sub('(\:[0-9]*)+$', '', path.strip()).strip()
		print path

		if path == '':
			return False

		# relative to view
		if self.view.file_name() != None and self.view.file_name() != '':
			maybe_path = self.resolve_relative(os.path.dirname(self.view.file_name()), path)
			if os.path.isfile(maybe_path):
				self.view.window().open_file(maybe_path)
				sublime.status_message("Opening file " + maybe_path)
				return True

		# relative to project folders
		for maybe_path in sublime.active_window().folders():
			maybe_path = self.resolve_relative(maybe_path, path)
			if os.path.isfile(maybe_path):
				self.view.window().open_file(maybe_path)
				sublime.status_message("Opening file " + maybe_path)
				return True

		#absolute
		if os.path.isfile(path):
			self.view.window().open_file(path)
			sublime.status_message("Opening file " + path)
			return True

		return False

	def resolve_relative(self, absolute, path):
		subs = path.replace('\\', '/').split('/')
		for sub in subs:
			if sub != '':
				absolute = os.path.join(absolute, sub)
		return absolute