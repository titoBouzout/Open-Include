import os.path
import re
import threading
import urllib

import sublime
import sublime_plugin

try:
    from .Edit import Edit as Edit
except:
    from Edit import Edit as Edit

BINARY = re.compile('\.(psd|ai|cdr|ico|cache|sublime-package|eot|svgz|ttf|woff|zip|tar|gz|rar|bz2|jar|xpi|mov|mpeg|avi|mpg|flv|wmv|mp3|wav|aif|aiff|snd|wma|asf|asx|pcm|pdf|doc|docx|xls|xlsx|ppt|pptx|rtf|sqlite|sqlitedb|fla|swf|exe)$', re.I)
IMAGE = re.compile('\.(apng|png|jpg|gif|jpeg|bmp)$', re.I)

# global settings container
s = None


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
            if view.score_selector(region.begin(), "parameter.url, string.quoted"):
                file_to_open = view.substr(view.extract_scope(region.begin()))
                opened = self.resolve_path(window, view, file_to_open)

                if not opened:
                    opened = self.resolve_path(window, view, file_to_open)
                    if opened:
                        break

                if not opened and s.get('create_if_not_exists') and view.file_name():
                    file_name = view.substr(view.extract_scope(region.begin())).replace("'", '').replace('"', '')
                    path = self.resolve_relative(os.path.dirname(view.file_name()), file_name)
                    branch, leaf = os.path.split(path)
                    try:
                        os.makedirs(branch)
                    except:
                        pass
                    window.open_file(path)
                    opened = True

            # selected text
            if not opened:
                opened = self.resolve_path(window, view, view.substr(region))

            # current line quotes and parenthesis
            if not opened:
                line = view.substr(view.line(region.begin()))
                for line in re.split(r"[()'\"]", line):
                    line = line.strip()
                    if line:
                        opened = self.resolve_path(window, view, line)
                        if opened:
                            break

            # selection expanded to full lines
            if not opened:
                expanded_lines = view.substr(sublime.Region(view.line(region.begin()).begin(), view.line(region.end()).end()))
                opened = self.resolve_path(window, view, expanded_lines)

                # split by spaces and tabs
                if not opened:
                    words = re.sub(r"\s+", "\n", expanded_lines)  # expanded_lines.replace('\t', '\n').replace(' ', '\n'))
                    opened = self.resolve_path(window, view, words)

            if opened:
                something_opened = True

        # Nothing in a selected region could be opened
        if not something_opened:
            # This rarely helps and only creates a huge load of overload
            # self.resolve_path(window, view, view.substr(sublime.Region(0, view.size())).replace('\t', '\n'))
            sublime.status_message("Unable to find a file in the current selection")

    def expand_paths_with_extensions(self, window, view, paths):

        # Special file naming conventions, e.g. '_'+name+'.scss' + current extension
        extensions = s.get('auto_extension', [])
        if view.file_name():
            file_ext = os.path.splitext(view.file_name())[1]
            extensions.append(dict(extension=file_ext))

        path_add = []
        for path in paths:
            if os.path.splitext(path)[1]:
                continue
            for extension in extensions:
                subs = path.replace('\\', '/').split('/')
                subs[-1] = re.sub('("|\')', '', subs[-1]);
                subs[-1] = extension.get('prefix', '') + subs[-1] + extension.get('extension', '')
                path_add.append(os.path.join(*subs))
        return paths + path_add

    # resolve the path of these sources and send to try_open
    def resolve_path(self, window, view, paths):
        try:
            paths_decoded = urllib.unquote(paths.encode('utf8'))
            paths_decoded = unicode(paths_decoded.decode('utf8'))
            paths += '\n' + paths_decoded
        except:
            pass

        paths = paths.split('\n')

        if s.get('use_strict'):
            return self.try_open(window, self.resolve_relative(os.path.dirname(view.file_name()), paths[0]))

        paths = self.expand_paths_with_extensions(window, view, paths)

        something_opened = False

        for path in paths:
            path = path.strip()
            if path == '':
                continue

            # remove quotes
            path = path.strip('"\'<>')  # re.sub(r'^("|\'|<)|("|\'|>)$', '', path)

            # remove :row:col
            path = re.sub('(\:[0-9]*)+$', '', path).strip()

            folder_structure = ["../" * i for i in range(s.get('maximum_folder_up', 5))]

            # relative to view & view dir name
            opened = False
            if view.file_name():
                for new_path_prefix in folder_structure:
                    maybe_path = os.path.dirname(view.file_name())
                    opened = self.create_path_relative_to_folder(window, view, maybe_path, new_path_prefix + path)
                    if not opened:
                        maybe_path = os.path.dirname(maybe_path)
                        opened = self.create_path_relative_to_folder(window, view, maybe_path, new_path_prefix + path)

                    if opened:
                        break

            # relative to project folders
            if not opened:
                for maybe_path in sublime.active_window().folders():
                    for new_path_prefix in folder_structure:
                        if self.create_path_relative_to_folder(window, view, maybe_path, new_path_prefix + path):
                            opened = True
                            break
                    if opened:
                        break

            # absolute
            if not opened:
                opened = self.try_open(window, path)
                if opened:
                    opened = True

            if opened:
                something_opened = True

        return something_opened

    def create_path_relative_to_folder(self, window, view, maybe_path, path):
        maybe_path_tpm = self.resolve_relative(maybe_path, path)
        return self.try_open(window, maybe_path_tpm)

    # try opening the resouce
    def try_open(self, window, maybe_path):
        # TODO: Add this somewhere WAY earlier since we are doing so much data
        # processing regarding paths prior to this
        if re.match(r'https?://', maybe_path):
            # HTTP URL
            if BINARY.search(maybe_path) or s.get("open_http_in_browser", False):
                sublime.status_message("Opening in browser " + maybe_path)

                import webbrowser
                webbrowser.open_new_tab(maybe_path)
            else:
                sublime.status_message("Opening URL " + maybe_path)
                # Create thread to download url in background
                threading.Thread(target=self.read_url, args=(maybe_path,)).start()

        elif os.path.isfile(maybe_path):
            if IMAGE.search(maybe_path):
                window.open_file(maybe_path)
            elif BINARY.search(maybe_path):
                try:
                    import desktop
                except:
                    from . import desktop
                desktop.open(maybe_path)
            else:
                # Open within ST
                window.open_file(maybe_path)
            sublime.status_message("Opening file " + maybe_path)
        else:
            return False

        return True

    # util
    def resolve_relative(self, absolute, path):
        subs = path.replace('\\', '/').split('/')
        for sub in subs:
            if sub != '':
                absolute = os.path.join(absolute, sub)
        return absolute

    def read_url(self, url):
        try:
            if url.startswith('https'):
                url = 'http' + url[5:]

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
            # ST3 is thread-safe, but ST2 is not so we use set_timeout to get to the main thread again
            sublime.set_timeout(lambda: self.read_url_on_done(content, content_type), 0)
        except:
            pass

    def read_url_on_done(self, content, content_type):
        if content:
            window = sublime.active_window()
            view = window.new_file()
            with Edit(view) as edit:
                edit.insert(0, content)

            # TODO: convert to a dict and include in settings
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

if int(sublime.version()) < 3000:
    plugin_loaded()
