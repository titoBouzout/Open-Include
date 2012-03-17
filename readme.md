Description
------------------

This plugin will try to open on Sublime Text file paths found on selections when pressing "ALT+D"
Binary included files such images, videos, etc will open with default application. http starting strings will open with default browser.

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
- Absolute path
