Description
------------------

This plugin will try to open on Sublime Text file paths found on selections when pressing "ALT+D"

Binary included files such images, videos, etc will open with default application.

HTTP starting strings will open with default browser if binary, if not, we will read the file with urllib and open the result in a new view.

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
- Relative to parent of current view
- Relative to project folders
- Relative to project folders minus 1 folder
- Relative to project folders minus 2 folders
- Absolute path
