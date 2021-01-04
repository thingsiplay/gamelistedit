#!/usr/bin/python3

import sys
import os
import pathlib

from PyQt5 import QtWidgets, QtCore

import modules
from modules import settings as G
from modules.MainWindow import *
from modules.arguments import *
from modules.misc import *


if __name__ == '__main__':
    APP = QtWidgets.QApplication(sys.argv)
    check_version()
    arguments = get_arguments()
    if frozen():
        executable = sys.executable
    else:
        executable = os.path.abspath(__file__)
    executable = os.path.realpath(executable)
    G.set_settings(executable, arguments)
    set_window_style(APP)
    mainwin = MainWindow(arguments)
    if G.settings['no_gui']:
        mainwin.export_file()
        EOT_action()
        sys.exit(0)
    else:
        APP.setApplicationName(G.settings['app_title'])
        APP.setApplicationDisplayName(G.settings['app_title'])
        mainwin.show()
    sys.exit(APP.exec())
