# Description

This plugin will try to open Sublime Text file paths found on selections/cursor when pressing "ALT+D".
It has support for .coffee/.js/.hbs/.jade files when no extension specified. Usefull when doing require style JavaScript modules.

Strings starting with HTTP will open with default browser (if binary), if not, we will read the file with urllib and open the result in a new view. By setting the `"open_http_in_browser"` setting in your user preferences to `true`, we will always open the default browser.

`use_strict` preference will control if the path should be complete and correct, if not the file will not open and the package will not attempt to find the file.

## Sources:

-   If in "Find Results" panel, current file and line number position

-   The exact selection(s)

-   Text between quotes under caret positions.

-   Selections expanded to full lines covered by caret positions or partial selections.

-   Current lines splitted by (){}'"

-   Current lines splitted by spaces or tabs

-   Current word

-   If nothing works, will check the Full text up to 10485760

## Resolving:

Will try to resolve to:

-   Absolute path to URL (eg https?://...)

-   Relative to current view

-   Relative to current view minus 1 folder

-   Relative to current view minus 2 folders

-   Relative to project folders

-   Relative to project folders minus 1 folder

-   Relative to project folders minus 2 folders

-   Absolute path

If everything else fails will also look into:

-   Relative to the folder of all opened views

-   Relative to all subfolders

-   Relative to all parent folders

## Reporting an error somewhere

Please, To report an error provide the following information:

1. Project path (ex: "c:/www/website")
2. Opened file path (ex: "c:/www/website/index.html")
3. Included file line code (ex: a href="../html/views/home/Content/base/t16.shtml" ....
4. Exact location of included file, in t16.shtml (ex "c:/www/website/views/home/Content/base/t16.shtml" )

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
