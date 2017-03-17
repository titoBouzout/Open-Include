import sublime, sublime_plugin
import os

# Note: This plugin uses 'Verbose' plugin available in 'Package Control' to log some messages for debug purpose but it works fine without.


PluginName = 'Open-Include'


def verbose(**kwargs):
    kwargs.update({'plugin_name': PluginName})
    sublime.run_command("verbose", kwargs)


class Prefs:
    @staticmethod
    def load():
        print('Load settings: ' + PluginName)
        settings = sublime.load_settings(PluginName + '.sublime-settings')
        os_specific_settings = {}
        if sublime.platform() == 'windows':
            os_specific_settings = sublime.load_settings(PluginName + ' (Windows).sublime-settings')
        elif sublime.platform() == 'osx':
            os_specific_settings = sublime.load_settings(PluginName + ' (OSX).sublime-settings')
        else:
            os_specific_settings = sublime.load_settings(PluginName + ' (Linux).sublime-settings')
        Prefs.environment = os_specific_settings.get('environment', settings.get('environment', []))
        Prefs.expand_alias = os_specific_settings.get('expand_alias', settings.get('expand_alias', True))

    @staticmethod
    def show():
        verbose(log="############################################################")
        for env in Prefs.environment:
            for key, values in env.items():
                verbose(log=key + ": " + ';'.join(values))
        verbose(log="############################################################")


def plugin_loaded():
    Prefs.load()


### OpenFileFromEnv ###

# Find root directory
# Get base directory with name
# foreach env test if file exit
class OpenFileFromEnvCommand(sublime_plugin.TextCommand):

    # Set by is_enabled()
    initial_env_name = ''
    base_name = ''

    # List of existing files in other environments
    env_files = []

    def run(self, edit):
        verbose(log="run()")

        verbose(log="initial_env_name: " + self.initial_env_name)
        verbose(log="base_name: " + self.base_name)

        if len(self.base_name) > 0:
            # Create a list of files which exist in other environment
            self.env_files = []
            for env in Prefs.environment:
                for env_name, root_alias in env.items():

                    # Bypass initial environment
                    if env_name == self.initial_env_name:
                        continue

                    # Loop in path alias of the current environment
                    available_file_names = []
                    for root in root_alias:
                        env_file_name = os.path.join(os.path.expandvars(root), self.base_name)
                        state = ' '
                        if os.path.exists(env_file_name):
                            state = 'X'
                            if Prefs.expand_alias:
                                self.env_files.append([env_name, env_file_name])
                            else:
                                available_file_names.append(env_file_name)
                        verbose(log='[%s] %15s %s' % (state, env_name, env_file_name))

                    if len(available_file_names) > 0:
                        # available_file_names used only with expand_alias = False
                        current_id = self.view.id()
                        is_file_opened = False
                        # Find the first file of the environment which is already opened in st
                        for v in self.view.window().views():
                            if v.id() == current_id or v.file_name() is None:
                                continue
                            for file_name in available_file_names:
                                if file_name.lower() == v.file_name().lower():
                                    self.env_files.append([env_name, file_name])
                                    is_file_opened = True
                                    break
                            if is_file_opened:
                                break
                        # Or choose the file of the environment of the main path
                        if not is_file_opened:
                            self.env_files.append([env_name, available_file_names[0]])

            if len(self.env_files) > 0:
                self.view.window().show_quick_panel(self.env_files, self.quick_panel_done)
            else:
                sublime.status_message("No file found in other environments")


    def quick_panel_done(self, index):
        if index > -1:
            # Open selected file in an another environment
            self.view.window().open_file(self.env_files[index][1])


    def is_filename_part_of_env(self, file_name, root_alias):
        for root in root_alias:
            # Remove trailing os.sep
            root = os.path.expandvars(root)
            root = os.path.normpath(root).lower()
            if file_name.startswith(root):
                base_name = file_name.replace(root.lower(), "")
                if base_name[0] == os.sep:
                    # Get back the original case
                    file_name = self.view.file_name()
                    # Remove first os.sep character and get base name
                    self.base_name = file_name[len(file_name)-len(base_name)+1:]
                    return True
        return False

    # Return True if the file is part of an environment
    def is_enabled(self):
        Prefs.show()
        verbose(log="is_enabled()")

        file_name = self.view.file_name()
        self.initial_env_name = ''
        base_name = ''
        if file_name is not None and len(file_name) > 0:
            file_name = file_name.lower()
            verbose(log="file_name: " + file_name)

            # Loop into registered environment
            for env in Prefs.environment:
                for env_name, root_alias in env.items():
                    # Test if file_name is part of an environment
                    if self.is_filename_part_of_env(file_name, root_alias):
                        self.initial_env_name = env_name
                        return True

        sublime.status_message("The current file is not part of an environment")
        return False

if int(sublime.version()) < 3000:
    plugin_loaded()
