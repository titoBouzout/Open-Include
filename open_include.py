import sublime, sublime_plugin
import os.path
import re

class OpenInclude(sublime_plugin.TextCommand):
	def run(self, view):
		for region in self.view.sel():
			syntax = self.view.syntax_name(region.begin())
			if re.match(".*string.quoted.double", syntax): self.doOpen(self.view, region, '"') # Match & Select Doubles
			if re.match(".*string.quoted.single", syntax): self.doOpen(self.view, region, "'") # Match & Select Singles

	def doOpen(self, view, region, char):
		begin = region.begin() - 1
		end = region.begin()
		while view.substr(begin) != char or view.substr(begin - 1) == '\\': begin -= 1
		while view.substr(end) != char or view.substr(end - 1) == '\\': end += 1
		view.sel().subtract(region)
		view.sel().add(sublime.Region(begin + 1, end))

		for region in self.view.sel():
			if region.empty():
				line = self.view.line(region)
				filepath = self.view.substr(line).strip()
			else:
				filepath = self.view.substr(region).strip()

			filepath = os.path.dirname(self.view.file_name().strip()) + '\\' + filepath.strip()
			
			if os.path.exists(filepath):
				self.view.window().open_file(filepath)
				sublime.status_message("Opening file " + filepath)

		view.sel().clear()