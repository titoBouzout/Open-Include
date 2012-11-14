import sublime, sublime_plugin
import os.path
import re
import thread

BINARY = re.compile('\.(apng|png|jpg|gif|jpeg|bmp|psd|ai|cdr|ico|cache|sublime-package|eot|svgz|ttf|woff|zip|tar|gz|rar|bz2|jar|xpi|mov|mpeg|avi|mpg|flv|wmv|mp3|wav|aif|aiff|snd|wma|asf|asx|pcm|pdf|doc|docx|xls|xlsx|ppt|pptx|rtf|sqlite|sqlitedb|fla|swf|exe)$', re.I);

s = sublime.load_settings('Open-Include.sublime-settings')


class OpenInclude(sublime_plugin.TextCommand):

	# run and look for different sources of paths
	def run(self, edit):
		window = sublime.active_window()
		view = self.view
		something_opened = False
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

			if opened:
				something_opened = True
		if not something_opened:
			self.resolve_path(window, view, view.substr(sublime.Region(0, view.size())).replace('\t', '\n'))

	# resolve the path of these sources and send to try_open
	def resolve_path(self, window, view, paths):
		import urllib
		try:
			paths_decoded = urllib.unquote(paths.encode('utf8'))
			paths_decoded = unicode(paths_decoded.decode('utf8'));
			paths += '\n'+paths_decoded
		except:
			pass

		paths = paths.split('\n')

		if s.get('use_strict'):
			return self.try_open(window, self.resolve_relative(os.path.dirname(view.file_name()), paths[0]))

		paths.append(paths[0].replace('../', ''))
		paths.append(paths[0].replace('/', '/_'))
		paths = list(set(paths))

		something_opened = False
		opened = False

		for path in paths:
			path = path
			if path.strip() == '':
				continue

			extensions = ["", ".coffee", ".hbs", ".jade", ".js", ".scss", ".sass", ".styl", ".less"];
			for extension in extensions:
				# remove quotes
				path = re.sub('^"|\'', '',  re.sub('"|\'$', '', path.strip()))

				# remove :row:col
				path = re.sub('(\:[0-9]*)+$', '', path.strip()).strip()


				newpath = path + extension

				# relative to view
				if not opened and view.file_name() != None and view.file_name() != '':
					maybe_path = self.resolve_relative(os.path.dirname(view.file_name()), newpath)
					opened = self.try_open(window, maybe_path)
					if opened:
						something_opened = True

				# relative to view dirname
				if not opened and view.file_name() != None and view.file_name() != '':
					maybe_path = self.resolve_relative(os.path.dirname(os.path.dirname(view.file_name())), newpath)
					opened = self.try_open(window, maybe_path)
					if opened:
						something_opened = True

				# relative to view dirname minus one folder
				if not opened and view.file_name() != None and view.file_name() != '':
					maybe_path = self.resolve_relative(os.path.dirname(os.path.dirname(view.file_name())), "../" + newpath)
					opened = self.try_open(window, maybe_path)
					if opened:
						something_opened = True

				# relative to view dirname minus two folders
				if not opened and view.file_name() != None and view.file_name() != '':
					maybe_path = self.resolve_relative(os.path.dirname(os.path.dirname(view.file_name())), "../../" + newpath)
					opened = self.try_open(window, maybe_path)
					if opened:
						something_opened = True

				# relative to project folders
				if not opened:
					for maybe_path in sublime.active_window().folders():
						maybe_path_tpm = self.resolve_relative(maybe_path, newpath)
						opened = self.try_open(window, maybe_path_tpm)
						if opened:
							something_opened = True
							break
						# relative to project folders minus one folder.
						maybe_path_tpm = self.resolve_relative(maybe_path, '../'+ newpath)
						opened = self.try_open(window, maybe_path_tpm)
						if opened:
							something_opened = True
							break
						# relative to project folders minus two folder.
						maybe_path_tpm = self.resolve_relative(maybe_path, '../../'+ newpath)
						opened = self.try_open(window, maybe_path_tpm)
						if opened:
							something_opened = True
							break

				# absolute
				if not opened:
					opened = self.try_open(window, newpath)
					if opened:
						something_opened = True

		return something_opened

	# try opening the resouce
	def try_open(self, window, maybe_path):
		if maybe_path[:4] == 'http':
			if BINARY.search(maybe_path) or s.get("open_http_in_browser", False):
				try:
					sublime.status_message("Opening in browser " + maybe_path)
					import webbrowser
					webbrowser.open_new_tab(maybe_path)
					return True
				except:
					return False
			else:
				sublime.status_message("Opening URL " + maybe_path)
				thread.start_new_thread(self.read_url, (maybe_path, maybe_path))
				return True

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

	def read_url(self, url, so):
		try:
			if url[:5] == 'https':
				url = re.sub('^https', 'http', url)
			import urllib2
			req = urllib2.urlopen(url)
			content = req.read()
			encoding=req.headers['content-type'].split('charset=')[-1]
			try:
				content = unicode(content, encoding)
			except:
				try:
					content = content.encode('utf-8')
				except:
					content = ''
			content_type = req.headers['content-type'].split(';')[0]
			sublime.set_timeout(lambda:self.read_url_on_done(content, content_type), 0)
		except:
			pass

	def read_url_on_done(self, content, content_type):
		if content:
			window = sublime.active_window()
			view = window.new_file()
			edit = view.begin_edit()
			try:
				view.insert(edit, 0, content)
			finally:
				view.end_edit(edit)
			if content_type == 'text/html':
				view.settings().set('syntax', 'Packages/HTML/HTML.tmLanguage')
			elif content_type == 'text/css':
				view.settings().set('syntax', 'Packages/CSS/CSS.tmLanguage')
			elif content_type == 'text/javascript' or content_type == 'application/javascript' or content_type == 'application/x-javascript':
				view.settings().set('syntax', 'Packages/JavaScript/JavaScript.tmLanguage')
			elif content_type == 'application/json' or content_type == 'text/json':
				view.settings().set('syntax', 'Packages/JavaScript/JSON.tmLanguage')
			elif content_type == 'text/xml' or content_type == 'application/xml':
				view.settings().set('syntax', 'Packages/XML/XML.tmLanguage')
