#!/usr/bin/python3

import sys
import os

from PyQt5 import QtWidgets, QtCore, QtGui

from modules import settings as G


def msg_stderr(part1, part2=None, is_critical=False):
    if (is_critical
    or not G.settings['quiet']):
        sys.stderr.write(str(part1) + '\n')
        if part2 is not None:
            sys.stderr.write(str(part2) + '\n')


def msg_show_error(message, mode):
    """ Displays a standardized error message box. """
    msgBox = QtWidgets.QMessageBox()
    if mode == 'Warning':
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
    elif mode == 'Critical':
        msgBox.setIcon(QtWidgets.QMessageBox.Critical)
    elif mode == 'Information':
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
    else:
        raise ValueError('Invalid value for "mode" in msg_show_error().')
    msgBox.setWindowTitle(os.path.basename(__file__))
    msgBox.setText(message)
    msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)

    if not G.settings['silence']:
        msg_stderr(message, None, bool(mode == 'Critical'))

        if not G.settings['no_gui']:
            if mode == 'Critical' or not G.settings['quiet']:
                msgBox.exec()


def msg_continue(message, mode='Question', title=None, parent=None, force=False):
    """ Standard message box asking to continue with process.
    """
    if (G.settings['no_gui']
        or (not force and G.settings['quiet'])
    ):
        return True
    msgBox = QtWidgets.QMessageBox(parent) if parent else QtWidgets.QMessageBox()
    # Ask to proceed. Default is ok.
    if mode == 'Question':
        msgBox.setIcon(QtWidgets.QMessageBox.Question)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.No
                                 | QtWidgets.QMessageBox.Ok)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
        msgBox.setEscapeButton(QtWidgets.QMessageBox.No)
    # No question, just show an information.
    elif mode == 'Information':
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
        msgBox.setEscapeButton(QtWidgets.QMessageBox.Ok)
    # Important. Ask to proceed. Default is no.
    elif mode == 'Warning':
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.No
                                 | QtWidgets.QMessageBox.Ok)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.No)
        msgBox.setEscapeButton(QtWidgets.QMessageBox.No)
    # Like Information, but do not show any icon.
    elif mode is None:
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
        msgBox.setEscapeButton(QtWidgets.QMessageBox.Ok)
    else:
        raise ValueError('Wrong value for "mode" in msg_continue().')

    if title is None:
        title = os.path.basename(__file__)
    msgBox.setWindowTitle(title)

    msgBox.setText(message)
    return bool(msgBox.exec() == QtWidgets.QMessageBox.Ok)

def dialog_choose_file(title,
    filetype=None,
    mode=None,
    wdir=None,
    no_gui=None):
    """ Show a standardized dialog for selecting files. """
    dialog = QtWidgets.QFileDialog()
    dialog.setWindowTitle(title)
    if filetype is not None:
        dialog.setNameFilter(filetype)
    if wdir is None:
        wdir = os.getcwd()
    dialog.setDirectory(wdir)
    dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
    dialog.setOptions(QtWidgets.QFileDialog.DontUseNativeDialog
                      | QtWidgets.QFileDialog.DontConfirmOverwrite)
    if mode == 'Save':
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)

    # Helper argument, because settings does not exist when called from
    # set_settings()
    try:
        no_gui = G.settings['no_gui']
    except:
        pass

    if (not no_gui
    and dialog.exec_() == QtWidgets.QDialog.Accepted):
        file = str(dialog.selectedFiles()[0])
        if mode == 'Load' and not os.path.exists(file):
            file = None
    else:
        file = None
    return file
