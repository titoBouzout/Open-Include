import sublime, sublime_plugin
import os.path
import re

BINARY = re.compile('\.(apng|png|jpg|gif|jpeg|bmp|psd|ai|cdr|ico|cache|sublime-package|eot|svgz|ttf|woff|zip|tar|gz|rar|bz2|jar|xpi|mov|mpeg|avi|mpg|flv|wmv|mp3|wav|aif|aiff|snd|wma|asf|asx|pcm|pdf|doc|docx|xls|xlsx|ppt|pptx|rtf|sqlite|sqlitedb|fla|swf|exe)$', re.I);

class OpenInclude(sublime_plugin.TextCommand):

	# run and look for different sources of paths
	def run(self, edit):
		window = sublime.active_window()
		view = self.view
		for region in view.sel():
			opened = False

			# between quotes
			syntax = self.view.syntax_name(region.begin())
			if re.match(".*string.quoted.double", syntax) or re.match(".*string.quoted.single", syntax):
				opened = self.resolve_path(window, view, view.substr(view.extract_scope(region.begin())))

			# selected text
			if not opened:
				opened = self.resolve_path(window, view, view.substr(sublime.Region(region.begin(), region.end())))

			# current lines
			if not opened:
				opened = self.resolve_path(window, view, view.substr(sublime.Region(view.line(region.begin()).begin(), view.line(region.end()).end())))

			# current scope
			if not opened:
				opened = self.resolve_path(window, view, view.substr(view.extract_scope(region.begin())))

			# current line quotes and parenthesis
			if not opened:
				line = view.substr(sublime.Region(view.line(region.begin()).begin(), view.line(region.end()).end()))
				line = line.replace(')', '"').replace('(', '"').replace("'", '"')
				lines = line.split('"')
				for line in lines:
					line = line.strip()
					if line:
						opened = self.resolve_path(window, view, line)
						if opened:
							break;

			# current lines splitted by spaces or tabs
			if not opened:
				opened = self.resolve_path(window, view, view.substr(sublime.Region(view.line(region.begin()).begin(), view.line(region.end()).end())).replace('\t', '\n').replace(' ', '\n'))


	# resolve the path of these sources and send to try_open
	def resolve_path(self, window, view, paths):

		paths = paths.split('\n')
		paths.append(paths[0].replace('../', ''))
		paths = list(set(paths))

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
				opened = self.try_open(window, maybe_path)
				if opened:
					continue

			# relative to view dirname
			if view.file_name() != None and view.file_name() != '':
				maybe_path = self.resolve_relative(os.path.dirname(os.path.dirname(view.file_name())), path)
				opened = self.try_open(window, maybe_path)
				if opened:
					continue

			# relative to project folders
			for maybe_path in sublime.active_window().folders():
				maybe_path = self.resolve_relative(maybe_path, path)
				opened = self.try_open(window, maybe_path)
				if opened:
					break
			if opened:
				continue

			# absolute
			opened = self.try_open(window, path)
			if opened:
					continue

		return opened

	# try opening the resouce
	def try_open(self, window, maybe_path):
		if maybe_path[:4] == 'http':
			try:
				import webbrowser
				webbrowser.open_new_tab(maybe_path)
				return True
			except:
				pass
		if os.path.isfile(maybe_path):
			if BINARY.search(maybe_path):
				import sys
				path = os.path.join(sublime.packages_path(), 'Open-Include')
				if path not in sys.path:
					sys.path.append(path)
				import desktop
				desktop.open(maybe_path)
			else:
				window.open_file(maybe_path)
			sublime.status_message("Opening file " + maybe_path)
			return True
		else:
			return False

	# util
	def resolve_relative(self, absolute, path):
		subs = path.replace('\\', '/').split('/')
		for sub in subs:
			if sub != '':
				absolute = os.path.join(absolute, sub)
		return absolute