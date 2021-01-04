#!/usr/bin/python3

import sys
import os
import pathlib
import inspect

from modules.meta import *
from modules.dialogs import *
from modules.path import *


# Global: import settings as G
# Usage: G.settings['key']
settings = dict()
extend_settings_meta(settings)

def set_settings(main_path, arguments):
    arguments = vars(arguments)
    #print(arguments)
    # Defaults
    settings['app_path'] = get_path(main_path, False)
    settings['app_dir'] = settings['app_path'].parent
    settings['app_license_path'] = settings['app_dir'] / 'LICENSE'
    settings['app_readme_path'] = settings['app_dir'] / 'README.html'
    settings['app_icon_path'] = settings['app_dir'] / 'img' / 'icon.svg'
    settings['import'] = ''
    settings['export'] = ''
    settings['export_format'] = ''
    settings['no_same'] = None  # default will be set later
    settings['dir'] = ''
    settings['indent'] = None
    settings['no_indent'] = False
    settings['sort'] = ['name']
    settings['no_sort'] = False
    settings['turnoff'] = ['sortname', 'thumbnail']
    settings['no_turnoff'] = False
    settings['lock'] = ['lastplayed', 'playcount', 'id', 'source']
    settings['no_lock'] = False
    settings['tag_order'] = []
    # resize is also used as a list in export_exclude_whitelist
    settings['resize'] = {
        'name': 260, 'sortname': 120,
        'desc': 260,
        'developer': 120, 'publisher': 120,
        'releasedate': 160, 'genre': 160,
        'path': 120, 'thumbnail': 120, 'image': 120,
        'marquee': 120, 'video': 120,
        'id': 80, 'source': 80,
        'favorite': 80, 'hidden': 80, 'kidgame': 80,
        'players': 80, 'rating': 80,
        'lastplayed': 160, 'playcount': 80}
    settings['no_resize'] = False
    settings['no_table_edit'] = False
    settings['no_autocomplete'] = False
    settings['ignore_copy'] = []
    settings['no_ignore_copy'] = False
    settings['mod_flag'] = False
    settings['open_editbox'] = False
    settings['hide_weblinks'] = False
    settings['genre_groups'] = False
    settings['filter'] = ''
    settings['filter_by'] = ''
    settings['filter_regex'] = False
    settings['filter_case'] = False
    settings['re'] = False
    settings['export_open'] = False
    settings['export_apply_filter'] = False
    settings['export_keep_empty'] = False
    settings['export_exclude'] = []
    settings['export_exclude_whitelist'] = []
    settings['export_exclude_turnoff'] = False
    settings['export_exclude_lock'] = False
    settings['export_exclude_unsupptags'] = False
    settings['maximize'] = False
    settings['fullscreen'] = False
    settings['window_style'] = ''
    settings['no_gui'] = False
    settings['quiet'] = False
    settings['silence'] = False
    settings['EOT_stdout'] = []
    settings['EOT_stderr'] = []
    # ACTION=file at option --EOT
    # Important: Must be set to full file path string, whenever a successful
    # export happened.
    settings['EOT_action_file'] = None

    # Overwrite current settings by arguments.
    for key, value in arguments.items():
        #if value: # is not None:
        if value is not None:
            settings[key] = value

    if settings['silence']:
        settings['quiet'] = True

    # DIR change current working directory first
    if not settings['dir'] == '':
        dir = get_path(settings['dir'])
        try:
            os.chdir(dir)
        except PermissionError:
            msg_show_error(f'Error! No permission to access: {str(file)}',
                           'Warning')
        except FileNotFoundError:
            msg_show_error(f'Error! Directory not found: {str(dir)}',
                           'Warning')
        except NotADirectoryError:
            msg_show_error(f'Error! Path is not a directory: {str(dir)}',
                           'Warning')
        except OSError:
            msg_show_error(f'Error! Cannot change to directory: {str(dir)}',
                           'Warning')
        else:
            msg_stderr('Current working directory changed:', dir)

    input = arguments['import']
    # no --import
    if input is None:
        input = ''
    # --import
    elif input == []:
        file = dialog_choose_file('Import: Choose a gamelist XML file',
                                  '*.xml',
                                  'Load',
                                  no_gui=settings['no_gui'])
        input = get_path(file) if file else ''
    # --import FILE
    elif len(input) > 0:
        input = get_path(arguments['import'][0])
        if input.is_dir():
            file = dialog_choose_file('Import: Choose a gamelist XML file',
                                      '*.xml',
                                      'Load',
                                      wdir=str(input),
                                      no_gui=settings['no_gui'])
            input = get_path(file) if file else ''
    settings['import'] = input

    output = arguments['export']
    # no --export
    if output is None:
        output = ''
    # --export
    elif output == []:
        output = settings['import']
    # --export FILE
    elif len(output) > 0:
        output = get_path(arguments['export'][0])
    settings['export'] = output

    # -E
    if settings['no_same'] == '':
        file = pathlib.PurePath(settings['import'])
        settings['no_same'] = '_export' + file.suffix

    # Replace extension of output file, if input and output are identical
    # and -E option is in use.

    if (not output == ''
    and input == output
    and settings['no_same'] is not None):
        output = str(output.with_suffix('')) + settings['no_same']
        output = pathlib.Path(output)

    if settings['re']:
        settings['filter'] = ' '.join(settings['re'])
        settings['filter_regex'] = True
        settings['filter_case'] = True
        settings['export_apply_filter'] = True
    else:
        if settings['filter']:
            settings['filter'] = ' '.join(settings['filter'])
        else:
            settings['filter'] = ''

    if settings['no_indent']:
        settings['indent'] = None
    if settings['no_lock']:
        settings['lock'] = []
    if settings['no_turnoff']:
        settings['turnoff'] = []
    if settings['no_sort']:
        settings['sort'] = []
    if settings['no_resize']:
        settings['resize'] = {}
    if settings['export_exclude_turnoff']:
        settings['export_exclude'] += settings['turnoff']
    if settings['export_exclude_lock']:
        settings['export_exclude'] += settings['lock']

    if settings['export_exclude_whitelist']:
        blacklist = list(settings['resize'].keys())
        for tag in settings['export_exclude_whitelist']:
            try:
                blacklist.remove(tag)
            except ValueError:
                pass
        for tag in settings['export_exclude']:
            blacklist.append(tag)
        settings['export_exclude'] = blacklist
    settings['export_exclude'] = list(set(settings['export_exclude']))

    if settings['no_ignore_copy']:
        settings['ignore_copy'] = []
    elif settings['ignore_copy'] == []:
        settings['ignore_copy'] = settings['lock']

    if settings['no_gui']:
        if settings['export'] == '':
            settings['export'] = '/dev/null/'
        if (not settings['filter'] == ''
        or len(settings['sort']) > 0):
            settings['export_apply_filter'] = True

    #print(settings)
    return
