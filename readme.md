# Description

This plugin will try to open Sublime Text file paths found on caret positions or partial selections when pressing <kbd>ALT+D</kbd>.
It has support for custom prefixes and subfixes. Usefull when doing require style JavaScript modules when no extension specified.

Strings starting with HTTP will open with default browser (if binary, ie ends with png), if not, we will read the file with urllib and open the result in a new view/tab. By setting the `"open_http_in_browser"` setting in your user preferences to `true`, we will always open the default browser.

`use_strict` preference will control if the path should be complete and correct, if not the file will not open and the package will not attempt to find the source file.

## In theory this package should work like this:

-   If in "Find Results" panel, current file and line number position
-   The exact selection(s)
-   Text between quotes under caret positions.
-   Selections expanded to full lines covered by caret positions or partial selections.
-   Current lines split by `(){}[]'"`
-   Current lines split by spaces or tabs
-   Current word
-   If nothing works, will check the Full text up to 10485760

## Resolving:

Will try to resolve to:

-   Absolute path to URL (e.g. `https?://...`)
-   Relative to current view
-   Relative to current view minus 1 folder
-   Relative to current view minus 2 folders
-   Relative to project folders
-   Relative to project folders minus 1 folder
-   Relative to project folders minus 2 folders
-   Absolute path

If everything else fails will also look into:

-   Relative to the folder of all opened views
-   Relative to all sub-folders
-   Relative to all parent folders

It supports:

-   A generic setting `Open-Include.sublime-settings` which could be overloaded for each parameter in a platform specific configuration `Open-Include ($platform).sublime-settings`
-   Environment variable expansions both for paths in the settings and under the caret

## Reporting an error somewhere

Please, To report an error provide the following information:

1. Project path (ex: `c:/www/website`)
2. Opened file path (ex: `c:/www/website/index.html`)
3. Included file line code (ex: `a href="../html/views/home/Content/base/t16.shtml"` ....
4. Exact location of included file, in `t16.shtml` (ex `c:/www/website/views/home/Content/base/t16.shtml`)
5. The setting file of this package

## notes

### create_if_not_exists

 1. create if not exists work only in scope "parameter.url, string.quoted"

## Installation

Download or clone the contents of this repository to a folder named exactly as the package name into the Packages/ folder of ST.

## Contributors:

-   [titoBouzout][]
-   [vip32][]
-   [FichteFoll][]
-   [kizu][]
-   [i-akhmadullin][]
-   [hoest][]
-   [Raine][]
-   [jacobo-diaz][]
-   [iamntz][]
-   [Starli0n][]
-   [jbrooksuk][]
-   [xHN35RQ][]

  [titoBouzout]: https://github.com/titoBouzout
  [vip32]: https://github.com/vip32
  [FichteFoll]: https://github.com/FichteFoll
  [kizu]: https://github.com/kizu
  [i-akhmadullin]: https://github.com/i-akhmadullin
  [hoest]: https://github.com/hoest
  [Raine]: https://github.com/metaraine
  [jacobo-diaz]: https://github.com/jacobo-diaz
  [iamntz]: https://github.com/iamntz
  [Starli0n]: https://github.com/Starli0n
  [jbrooksuk]: https://github.com/jbrooksuk
  [xHN35RQ]: https://github.com/xHN35RQ
