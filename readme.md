Description
------------------

This plugin will try to open Sublime Text file paths found on selections/cursor when pressing "ALT+D".
It has support for .coffee/.js/.hbs/.jade files when no extension specified. Usefull when doing require style javascript modules.

Strings starting with HTTP will open with default browser (if binary), if not, we will read the file with urllib and open the result in a new view. By setting the `"open_http_in_browser"` setting in your user preferences to `true`, we will always open the default browser.

`use_strict` preference will control if the path should be complete and correct, if not the file will not open and the package will not attempt to find the file.

Sources:
------------------

- Text between quotes under caret position.
- Selected text.
- Full lines covered by caret positions or selections.
- Current lines splitted by spaces or tabs

Resolving:
------------------

Will try to resolve to:

- Relative to current view
- Relative to current view minus 1 folder
- Relative to current view minus 2 folders
- Relative to project folders
- Relative to project folders minus 1 folder
- Relative to project folders minus 2 folders
- Absolute path
