#!/usr/bin/python3

import sys
import subprocess
import os

from PyQt5 import QtWidgets

from modules import settings as G
from modules.dialogs import *


def frozen():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def check_version():
    error = 0
    app_minpython = G.settings['app_minpython'].split('.')
    if (sys.version_info[0] < int(app_minpython[0])
    or  sys.version_info[1] < int(app_minpython[1])):
        print('ERROR! At least Python 3.6 is required.')
        error += 1

    qt5version = QtCore.qVersion().split('.')
    app_minqt5 = G.settings['app_minqt5'].split('.')
    if (int(qt5version[0]) < int(app_minqt5[0])
    or  int(qt5version[1]) < int(app_minqt5[1])):
        print('ERROR! At least Qt5 5.9 is required.')
        error += 1

    if error:
        print('\nYour system does not meet the minimum requirements.')
        print('Program terminates.')
        sys.exit(1)
    return error


def EOT_action():

    def EOT(action, std, file):
        if action == 'open' and file:
            run_with_default_app(file)
        elif action == 'file':
            std.write('\n' if file is None else str(file) + '\n')
        elif action == 'settings':
            std.write('[settings]\n')
            for key, value in sorted(G.settings.items()):
                std.write(f"{key}={value}\n")

    file = G.settings['EOT_action_file']
    for action_list in G.settings['EOT_stdout']:
        for action in action_list:
            EOT(action, sys.stdout, file)
    for action_list in G.settings['EOT_stderr']:
        for action in action_list:
            EOT(action, sys.stderr, file)


def run_with_default_app(file):
    try:
        if str(file) == '/dev/null':
            pass
        elif file.exists() and file.is_file():
            if sys.platform.startswith('linux'):
                subprocess.call(["xdg-open", file])
            else:
                os.startfile(file)  # pylint: disable=E1101
        else:
            msg = f'Error! Could not find file: {str(file)}'
            msg_show_error(msg, 'Warning')
    except Exception:
        msg = f'Error! Could not run file with associated app: {str(file)}'
        msg_show_error(msg, 'Warning')


def set_window_style(app):
    style = G.settings['window_style']
    if style:
        all_styles = QtWidgets.QStyleFactory.keys()
        if style.lower() in [key.lower() for key in all_styles]:
            app.setStyle(style)
        else:
            msg_stdout(f'WARNING! Unsupported window style selected: {style}'
                      f'\nAvailable styles: {", ".join(all_styles)}'
                      '\nProgram defaults to current system setting.')
