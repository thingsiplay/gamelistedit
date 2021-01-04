#!/usr/bin/python3

import argparse

from PyQt5 import QtWidgets

from modules import settings as G

def get_arguments():
    """
        Later in program all unspecified arguments and None values are
        replaced by default values when converting to settings
        dictionary.
    """
    b = '\033[1m'
    n = '\033[0m'
    parser = argparse.ArgumentParser(
        prog=G.settings['app_name'],
        description=G.settings['app_desc'],
        epilog=(
            f'Hotkeys: {b}HOME{n}, {b}END{n}, {b}PGUP{n}, {b}PGDOWN{n}='
            f'navigation, {b}F9{n}=toggle-filterbar, {b}F10{n}=toggle-weblinks'
            f' {b}F11{n}=toggle-fullscreen, {b}F12{n}=toggle-editbox'),
        allow_abbrev=False
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=G.settings['app_version']
    )
    parser.add_argument(
        '-i', '--import',
        dest='import',
        metavar='FILE',
        nargs='*',
        type=str,
        required=False,
        help=(f'┗ {b}import{n}: gamelist xml file for editing, wildcards'
             ' supported but only first match is used, only in GUI mode: if no'
             ' FILE is given then a file select dialog will popup, if FILE'
             ' points to a folder then file select dialog on that folder will'
             ' popup')
    )
    parser.add_argument(
        '-e', '--export',
        dest='export',
        metavar='FILE',
        nargs='*',
        type=str,
        required=False,
        help=(f'┗ {b}export{n}: location to output file, if --export is'
             ' specified without argument FILE then export becomes same as'
             ' import file, if --export option is omitted entirely and'
             ' --no-gui option is in use then output will be redirected to'
             ' stdout instead, the file format will be determined by file'
             ' extension but can be overwritten with --format option,'
             ' available formats:'
             f' {b}.xml{n}=XML, {b}.json{n}=JSON, {b}.csv{n}=CSV,'
             f' {b}.txt{n}=TXT, {b}.cfg{n}=custom-collection, default: XML')
    )
    parser.add_argument(
        '-E', '--no-same',
        dest='no_same',
        metavar='EXT',
        nargs='?',
        const='',
        default=None,
        type=str,
        required=False,
        help=(f'┗ {b}export{n}: prevents overwriting import file by extending'
             ' the filename, any extension in export filename will be replaced'
             f' with this, default: _export.xml')
    )
    parser.add_argument(
        '-F', '--format',
        dest='export_format',
        metavar='FORMAT',
        choices=['xml', 'json', 'csv', 'txt', 'cfg'],
        type=str,
        required=False,
        help=(f'┗ {b}export{n}: force file format for export regardless of its'
             ' file ending, can also be used if no export file is specified')
    )
    parser.add_argument(
        '-d', '--cd', '--dir',
        dest='dir',
        metavar='FOLDER',
        type=str,
        required=False,
        help=f'┗ {b}im/export{n}: change current working directory'
    )
    parser.add_argument(
        '-I', '--indent',
        dest='indent',
        metavar='LEVEL',
        nargs='?',
        const='4',
        default=4,
        type=int,
        required=False,
        help=(f'┗ {b}export{n}: overwrite count of spaces for every'
             ' indentation level of XML and JSON or add empty lines to'
             ' unstructured TXT, default LEVEL is 4 even if not specified')
    )
    parser.add_argument(
        '--no-indent',
        dest='no_indent',
        action='store_true',
        default=None,
        required=False,
        help=(f'┗ {b}export{n}: disable --indent and its default value, also'
             ' causes to strip any newline between the tags, but tag content'
             ' such as "desc" may still contain newlines')
    )
    parser.add_argument(
        '-O', '--export-open',
        dest='export_open',
        action='store_true',
        default=None,
        required=False,
        help=(f'┗ {b}export{n}: open each successful exported file with the'
             ' app associated to its filetype right after its creation')
    )
    parser.add_argument(
        '-a', '--apply-filter',
        dest='export_apply_filter',
        action='store_true',
        default=None,
        required=False,
        help=(f'┗ {b}export{n}: apply search filter and sorting when exporting'
             ' the data, only visible game data will be saved, but hidden'
             ' column tags are still included, without this option all data'
             ' will be exported in its original order')
    )
    parser.add_argument(
        '-x', '--exclude',
        dest='export_exclude',
        metavar='TAG',
        nargs='+',
        type=str,
        required=False,
        help=(f'┗ {b}export{n}: ignore all specified tags when exporting to'
             ' file, in example "rating id desc", has higher priority of tags'
             ' when combined with --exclude-whitelist')
    )
    parser.add_argument(
        '-X', '--exclude-whitelist',
        dest='export_exclude_whitelist',
        metavar='TAG',
        nargs='+',
        type=str,
        required=False,
        help=(f'┗ {b}export{n}: inverted logic of -x or --exclude, all tags'
             ' are blocked at default, except this list, -x option can still'
             ' blacklist over this list')
    )
    parser.add_argument(
        '--exclude-turnoff',
        dest='export_exclude_turnoff',
        action='store_true',
        default=None,
        required=False,
        help=(f'┗ {b}export{n}: add the list of tags from -t --turnoff option'
             ' into -x or --exclude option list')
    )
    parser.add_argument(
        '--exclude-lock',
        dest='export_exclude_lock',
        action='store_true',
        default=None,
        required=False,
        help=(f'┗ {b}export{n}: add the list of tags from -l --lock option'
             ' into -x or --exclude option list')
    )
    parser.add_argument(
        '-U', '--exclude-unsupported',
        dest='export_exclude_unsupptags',
        action='store_true',
        default=None,
        required=False,
        help=(f'┗ {b}export{n}: remove unsupported data, folder and other tags'
              ' when exporting, following the RetroPie GAMELISTS format,'
              ' unsupported tags are not visible in the editor and cannot be'
              ' edited, but are preserved at default for supported formats')
    )
    parser.add_argument(
        '-k', '--keep-empty',
        dest='export_keep_empty',
        action='store_true',
        default=None,
        required=False,
        help=(f'┗ {b}export{n}: do not remove empty tags or empty game'
              ' entries without tags, no effect on import')
    )
    parser.add_argument(
        '-f', '--filter',
        dest='filter',
        metavar='PATTERN',
        nargs='+',
        type=str,
        required=False,
        help=(f'┗ {b}edit/filter{n}: set the search field to a predefined text'
             ' or pattern to show matching results only')
    )
    parser.add_argument(
        '-b', '--by',
        dest='filter_by',
        metavar='TAG',
        type=str,
        required=False,
        help=(f'┗ {b}edit/filter{n}: preselect a tag name to apply the'
             ' --filter on specific columns only, such as "name" or "path"')
    )
    parser.add_argument(
        '-r', '--regex',
        dest='filter_regex',
        action='store_true',
        default=None,
        required=False,
        help=f'┗ {b}edit/filter{n}: enable regex algorithm for filter'
    )
    parser.add_argument(
        '-c', '--case',
        dest='filter_case',
        action='store_true',
        default=None,
        required=False,
        help=f'┗ {b}edit/filter{n}: enable case sensitivity for filter'
    )
    parser.add_argument(
        '--re',
        dest='re',
        metavar='PATTERN',
        nargs='+',
        type=str,
        required=False,
        help=(f'┗ {b}edit/filter{n}: a shortcut to overwrite multiple regular'
             ' expression related options, argument pattern is used as -f and'
             ' the options -a -r and -c are all activated')
    )
    parser.add_argument(
        '-s', '--sort',
        dest='sort',
        metavar='TAG',
        nargs='+',
        type=str,
        required=False,
        help=(f'┗ {b}edit/filter{n}: list of tag names to sort game rows by'
             ' table columns, multiple entries are supported,'
             f' default: name')
    )
    parser.add_argument(
        '-S', '--no-sort',
        dest='no_sort',
        action='store_true',
        required=False,
        help=f'┗ {b}edit/filter{n}: disable option -s or --sort and its default'
    )
    parser.add_argument(
        '-t', '--turnoff',
        dest='turnoff',
        metavar='TAG',
        nargs='+',
        type=str,
        required=False,
        help=(f'┗ {b}edit/ui{n}: list of tag names to hide columns from view'
             ' in table display, but are still able to export to file,'
             f' default: sortname thumbnail')
    )
    parser.add_argument(
        '-T', '--no-turnoff',
        dest='no_turnoff',
        action='store_true',
        required=False,
        help=f'┗ {b}edit/ui{n}: disable option -t or --turnoff and its default'
    )
    parser.add_argument(
        '-l', '--lock',
        dest='lock',
        metavar='TAG',
        nargs='+',
        type=str,
        required=False,
        help=(f'┗ {b}edit{n}: list of tag names to protect whole columns from'
             f' editing, default: lastplayed playcount id source')
    )
    parser.add_argument(
        '-L', '--no-lock',
        dest='no_lock',
        action='store_true',
        required=False,
        help=f'┗ {b}edit{n}: disable option -l or --lock and its default value'
    )
    parser.add_argument(
        '-p', '--ignore-copy',
        dest='ignore_copy',
        metavar='TAG',
        nargs='+',
        type=str,
        required=False,
        help=(f'┗ {b}edit{n}: list of tag names to ignore when duplicating a'
             ' game, defaults to same tags from -l or --lock option')
    )
    parser.add_argument(
        '-P', '--no-ignore-copy',
        dest='no_ignore_copy',
        action='store_true',
        required=False,
        help=f'┗ {b}edit{n}: disable option -p or --ignore-copy and its default'
    )
    parser.add_argument(
        '-R', '--no-resize',
        dest='no_resize',
        action='store_true',
        required=False,
        help=f'┗ {b}edit{n}: disable automatic resizing of columns at start'
    )
    parser.add_argument(
        '-o', '--tag-order',
        dest='tag_order',
        metavar='TAG',
        nargs='+',
        type=str,
        required=False,
        help=(f'┗ {b}edit/{n}: rearrange the order of tags for export file and'
             ' table view, unspecified tags will have default order')
    )
    parser.add_argument(
        '-D', '--no-direct-edit',
        dest='no_table_edit',
        action='store_true',
        default=None,
        required=False,
        help=(f'┗ {b}edit{n}: disable direct editing of table cells, turns'
             ' mouse double click into toggle editbox')
    )
    parser.add_argument(
        '-C', '--no-autocomplete',
        dest='no_autocomplete',
        action='store_true',
        default=None,
        required=False,
        help=f'┗ {b}edit{n}: disable auto completion'
    )
    parser.add_argument(
        '-g', '--genre-groups',
        dest='genre_groups',
        action='store_true',
        default=None,
        required=False,
        help=(f'┗ {b}edit{n}: list group of genres instead of extracting'
              ' individual genres in the editbox')
    )
    parser.add_argument(
        '-m', '--show-mod',
        dest='mod_flag',
        action='store_true',
        default=None,
        required=False,
        help=(f'┗ {b}edit/ui{n}: indicate modified cells in table with a'
             ' colored label')
    )
    parser.add_argument(
        '-n', '--open-editbox',
        dest='open_editbox',
        action='store_true',
        default=None,
        required=False,
        help=f' {b}ui{n}: extend the editbox at start'
    )
    parser.add_argument(
        '-W', '--hide-web',
        dest='hide_weblinks',
        action='store_true',
        default=None,
        required=False,
        help=f'┗ {b}ui{n}: hide weblinks toolbar at start'
    )
    parser.add_argument(
        '-z', '--max',
        dest='maximize',
        action='store_true',
        default=None,
        required=False,
        help=f'┗ {b}ui{n}: maximize window state at start'
    )
    parser.add_argument(
        '-Z', '--fullscreen',
        dest='fullscreen',
        action='store_true',
        default=None,
        required=False,
        help=f'┗ {b}ui{n}: start into fullscreen mode, toggle with F11'
    )
    parser.add_argument(
        '--window-style',
        dest='window_style',
        metavar='STYLE',
        type=str,
        required=False,
        help=(f'┗ {b}ui{n}: use alternative Qt window styling, available styles'
             f' on this system: {", ".join(QtWidgets.QStyleFactory.keys())}')
    )
    parser.add_argument(
        '-G', '--no-gui',
        dest='no_gui',
        action='store_true',
        default=None,
        required=False,
        help=(f'┗ {b}ui/terminal{n}: hides window for automation, exports file'
             ' and exits with an exitcode "0", supresses GUI messages and,'
             ' dialogs but still output them to stdout, assumes "continue" at'
             ' all user interactions, requires --import and --export files,'
             ' also will set --apply-filter if --filter or --sort is in use')
    )
    parser.add_argument(
        '-q', '--quiet',
        dest='quiet',
        action='store_true',
        default=None,
        required=False,
        help=(f'┗ {b}ui/terminal{n}: supresses almost all messages and dialogs,'
             ' except critical error messages')
    )
    parser.add_argument(
        '-Q', '--silence',
        dest='silence',
        action='store_true',
        default=None,
        required=False,
        help=(f'┗ {b}ui/terminal{n}: like --quiet, but with the addition to'
             ' supress critical error messages and output too')
    )
    parser.add_argument(
        '-1', '--stdout',
        dest='EOT_stdout',
        metavar='ACTION',
        nargs='+',
        action='append',
        choices=['open', 'file', 'settings'],
        default=None,
        type=str,
        required=False,
        help=(f'┗ {b}ui/terminal{n}: end of transmission, final action to do'
             ' when program exits, output will be printed to system stdout even'
             ' with --quiet or --silence option in effect, action is determined'
             ' by a predefined set of sub-options, multiple actions are'
             ' supported,'
             f' ACTION={b}open{n}: open last successful exported file with the'
             ' app associated to its filetype,'
             f' ACTION={b}file{n}: print full path of last successful exported'
             ' file,'
             f' ACTION={b}settings{n}: print a snapshot of programs settings'
             ' and meta information from initial launch state')
    )
    parser.add_argument(
        '-2', '--stderr',
        dest='EOT_stderr',
        metavar='ACTION',
        nargs='+',
        action='append',
        choices=['open', 'file', 'settings'],
        default=None,
        type=str,
        required=False,
        help=(f'┗ {b}ui/terminal{n}: same as -1 or --stdout, but printing to'
             ' system stderr instead')
    )
    return parser.parse_args()
