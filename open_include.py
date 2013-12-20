import os.path
import re
import sublime
import sublime_plugin
import threading
from .Edit import Edit as Edit

BINARY = re.compile('\.(apng|png|jpg|gif|jpeg|bmp|psd|ai|cdr|ico|cache|sublime-package|eot|svgz|ttf|woff|zip|tar|gz|rar|bz2|jar|xpi|mov|mpeg|avi|mpg|flv|wmv|mp3|wav|aif|aiff|snd|wma|asf|asx|pcm|pdf|doc|docx|xls|xlsx|ppt|pptx|rtf|sqlite|sqlitedb|fla|swf|exe)$', re.I)


def plugin_loaded():
  global s
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
      syntax = self.view.scope_name(region.begin())
      if re.match(".*(parameter.url|string.quoted.(double|single))", syntax):
        file_to_open = view.substr(view.extract_scope(region.begin()))
        opened = self.resolve_path(window, view, file_to_open)

        if not opened:
          for extension in s.get('auto_extension'):
            file_to_open = file_to_open.split('/')
            file_to_open[-1] = extension.get('prefix') + file_to_open[-1] + extension.get('extension')
            file_to_open = '/'.join(file_to_open)

            opened = self.resolve_path(window, view, file_to_open)
            if opened:
              break

        if not opened and s.get('create_if_not_exists') and view.file_name() is not None and view.file_name() != '':
          path = self.resolve_relative(os.path.dirname(view.file_name()), view.substr(view.extract_scope(region.begin())).replace("'", '').replace('"', ''))
          branch, leaf = os.path.split(path)
          try:
            os.makedirs(branch)
          except:
            pass
          window.open_file(path)
          return True

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
              break

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
      paths_decoded = unicode(paths_decoded.decode('utf8'))
      paths += '\n' + paths_decoded
    except:
      pass

    paths = paths.split('\n')

    if s.get('use_strict'):
      return self.try_open(window, self.resolve_relative(os.path.dirname(view.file_name()), paths[0]))

    # paths.append(paths[0].replace('../', ''))
    # paths.append(paths[0].replace('/', '/_'))
    # paths = list(set(paths))

    something_opened = False
    opened = False

    for path in paths:
      path = path.strip()
      if path == '':
        continue

      # extensions = ["", ".coffee", ".hbs", ".jade", ".js", ".scss", ".sass", ".styl", ".less"]
      # for extension in extensions:
      # remove quotes
      path = re.sub('^"|\'', '', re.sub('"|\'$', '', path))

      # remove :row:col
      path = re.sub('(\:[0-9]*)+$', '', path).strip()

      relative_paths = {
        "toView": view.file_name() if view.file_name() is not None and view.file_name() != '' else '',
        "toViewDirname": os.path.dirname(view.file_name()) if view.file_name() != None and view.file_name() != '' else ''
      }

      folder_structure = []
      for i in range(s.get('maximum_folder_up')):
        folder_structure.append("../" * i)

      # relative to view & view dir name
      something_opened = False
      for new_path_prefix in folder_structure:
        something_opened = self.create_path_relative_to_view(window, view, relative_paths['toView'], new_path_prefix + path)
        if not something_opened:
          something_opened = self.create_path_relative_to_view(window, view, relative_paths['toViewDirname'], new_path_prefix + path)
        else:
          break

      # relative to project folders
      if not something_opened:
        for maybe_path in sublime.active_window().folders():
          something_opened = False
          for new_path_prefix in folder_structure:
            if self.create_path_relative_to_project(window, maybe_path, new_path_prefix + path):
              something_opened = True
              break
          if something_opened:
            break

      # absolute
      if not something_opened:
        something_opened = self.try_open(window, path)
        if something_opened:
          something_opened = True

    return something_opened

  def create_path_relative_to_project(self, window, maybe_path, path):
    something_opened = False

    maybe_path_tpm = self.resolve_relative(maybe_path, path)
    opened = self.try_open(window, maybe_path_tpm)
    if opened:
      something_opened = True

    return something_opened

  def create_path_relative_to_view(self, window, view, relative_path, path):
    something_opened = False
    if not something_opened and view.file_name() is not None and view.file_name() != '':
      maybe_path = self.resolve_relative(os.path.dirname(relative_path), path)
      something_opened = self.try_open(window, maybe_path)
    return something_opened

  # try opening the resouce
  def try_open(self, window, maybe_path):
    if maybe_path[:7] == 'http://' or maybe_path[:8] == 'https://':
      if BINARY.search(maybe_path) or s.get("open_http_in_browser", False):
        sublime.status_message("Opening in browser " + maybe_path)
        import webbrowser
        webbrowser.open_new_tab(maybe_path)
        return True
      else:
        sublime.status_message("Opening URL " + maybe_path)
        threading.Thread(target=self.read_url, args=(maybe_path, maybe_path)).start()
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
      import urllib.request
      req = urllib.request.urlopen(url)
      content = req.read()
      encoding = req.headers['content-type'].split('charset=')[-1]
      try:
        content = str(content, encoding)
      except:
        try:
          content = str(content, 'utf-8')
        except:
          content = str(content, 'utf8', errors="replace")

      content_type = req.headers['content-type'].split(';')[0]
      sublime.set_timeout(lambda: self.read_url_on_done(content, content_type), 0)
    except:
      pass

  def read_url_on_done(self, content, content_type):
    if content:
      window = sublime.active_window()
      view = window.new_file()
      with Edit(view) as edit:
        try:
          edit.insert(0, content)
        except:
          pass
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
