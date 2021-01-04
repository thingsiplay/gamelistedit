#!/usr/bin/python3

import sys
import os
import pathlib
import urllib.parse
import xml.etree.ElementTree as ElementTree
import webbrowser

import PyQt5.uic
from PyQt5 import QtWidgets, QtCore, QtGui

from modules import settings as G
from modules.gamelistedit_ui import Ui_mainwindow
from modules.GamelistTable import *
from modules.dialogs import *
from modules.path import *
from modules.misc import *


class MainWindow(QtWidgets.QMainWindow, QtGui.QWindow):
    """    """
    def __init__(self, arguments):

        ##################################
        # START OF MainWindow.__init__() #
        super(MainWindow, self).__init__()
        self.ui = Ui_mainwindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(str(G.settings['app_icon_path'])))
        self.setWindowTitle(G.settings['app_title'])

        # Note: Gamelist, view and model are created after adding the Widgets.

        # ATTRIBUTES
        # gamelist will be created by GamelistTable() and contains view and
        # model.
        self.gamelist = None

        # is_fullscreen should not be set by itself without changing the
        # actual fullscreen of window.  Use set_fullscreen() or
        # toggle_fullscreen() instead.
        self.is_fullscreen = False

        # le_export_startswith_custom defines if the text in le_export starts
        # with a "custom-" in front of filename, the moment when button
        # CFG (custom-collection) is clicked the first time. This helps to
        # reset and remove the "custom-" portion again, if the user did not
        # have it prior the click.
        # Whenever the text is edited manually, it should reset to None and
        # get initialized by next button click again.

        # le_export_startswith_custom saves the state if le_export text include
        # "custom-" in front of filename. True for yes, False for no and None
        # for unspecified. Whenever the button Format button
        # CFG (custom-collection) is clicked, this variable gets initialized.
        # Editing the text manually should reset this variable to None again.
        # This variable helps to know if the original filename before clicking
        # the button included the portion of name, so it can be removed later.
        self.le_export_startswith_custom = None

        if not G.settings['no_gui']:
            # add SHORTCUTS
            self.shortcut_filterbar = QtWidgets.QShortcut(
                QtGui.QKeySequence('F9'), self)
            self.shortcut_filterbar.activated.connect(
                self.toggle_filterbar_activated)

            self.shortcut_toggle_weblinks = QtWidgets.QShortcut(
                QtGui.QKeySequence('F10'), self)
            self.shortcut_toggle_weblinks.activated.connect(
                self.toggle_weblinks_activated)

            self.shortcut_fullscreen = QtWidgets.QShortcut(
                QtGui.QKeySequence('F11'), self)
            self.shortcut_fullscreen.activated.connect(
                self.toggle_fullscreen)

            self.shortcut_editbox = QtWidgets.QShortcut(
                QtGui.QKeySequence('F12'), self)
            self.shortcut_editbox.activated.connect(
                self.tb_toggle_editbox_clicked)

            self.shortcut_firstgame = QtWidgets.QShortcut(
                QtGui.QKeySequence('Home'), self)
            self.shortcut_firstgame.activated.connect(
                self.select_table_row)

            self.shortcut_lastgame = QtWidgets.QShortcut(
                QtGui.QKeySequence('End'), self)
            self.shortcut_lastgame.activated.connect(
                self.select_last_table_row)

            self.shortcut_prevgame = QtWidgets.QShortcut(
                QtGui.QKeySequence('PgUp'), self)
            self.shortcut_prevgame.activated.connect(
                self.b_edit_prevgame_clicked)

            self.shortcut_nextgame = QtWidgets.QShortcut(
                QtGui.QKeySequence('PgDown'), self)
            self.shortcut_nextgame.activated.connect(
                self.b_edit_nextgame_clicked)

        # add WIDGETS
        self.l_current_file = self.findChild(
            QtWidgets.QLabel,
            'l_current_file')  # Remember to str() before .setText()

        self.t_tabs = self.findChild(
            QtWidgets.QTabWidget,
            't_tabs')
        self.t_tabs.currentChanged.connect(
            self.t_tabs_currentChanged)
        self.t_tabs_bar = self.t_tabs.tabBar()
        self.tabs_names = {'import': 0, 'edit': 1, 'export': 2, 'about': 3}

        self.pb_file_progress = self.findChild(
            QtWidgets.QProgressBar,
            'pb_file_progress')

        # add IMPORT TAB
        self.tb_import_filedialog = self.findChild(
            QtWidgets.QToolButton,
            'tb_import_filedialog')
        self.tb_import_filedialog.clicked.connect(
            self.tb_import_filedialog_clicked)

        self.le_import_file = self.findChild(
            QtWidgets.QLineEdit,
            'le_import_file')
        self.le_import_file.textChanged.connect(
            self.le_import_file_textChanged)  # Remember to .strip()
        self.le_import_file.returnPressed.connect(
            self.le_import_file_returnPressed)

        self.dbb_import_buttons = self.findChild(
            QtWidgets.QDialogButtonBox,
            'dbb_import_buttons')
        self.dbb_import_buttons.clicked.connect(
            self.dbb_import_buttons_clicked)

        # add EDIT TAB widgets
        self.w_filterbar = self.findChild(
            QtWidgets.QWidget,
            'w_filterbar')

        self.w_weblinks = self.findChild(
            QtWidgets.QWidget,
            'w_weblinks')

        if not G.settings['no_gui']:
        # add WEBLINK TOOLBUTTONS
            self.tb_search_source = self.findChild(
                QtWidgets.QWidget,
                'tb_search_source')
            self.tb_search_source.clicked.connect(
                self.tb_search_source_clicked)

            self.tb_search_web = self.findChild(
                QtWidgets.QWidget,
                'tb_search_web')
            self.tb_search_web.clicked.connect(
                self.tb_search_web_clicked)

            self.tb_search_video = self.findChild(
                QtWidgets.QWidget,
                'tb_search_video')
            self.tb_search_video.clicked.connect(
                self.tb_search_video_clicked)

            self.tb_search_wiki = self.findChild(
                QtWidgets.QWidget,
                'tb_search_wiki')
            self.tb_search_wiki.clicked.connect(
                self.tb_search_wiki_clicked)

            self.tb_search_games = self.findChild(
                QtWidgets.QWidget,
                'tb_search_games')
            self.tb_search_games.clicked.connect(
                self.tb_search_games_clicked)

            self.tb_search_emulation = self.findChild(
                QtWidgets.QWidget,
                'tb_search_emulation')
            self.tb_search_emulation.clicked.connect(
                self.tb_search_emulation_clicked)

            self.tb_search_romhacks = self.findChild(
                QtWidgets.QWidget,
                'tb_search_romhacks')
            self.tb_search_romhacks.clicked.connect(
                self.tb_search_romhacks_clicked)

        # add EDIT TAB
        self.cbb_filter_header = self.findChild(
            QtWidgets.QComboBox,
            'cbb_filter_header')
        self.cbb_filter_header.currentIndexChanged.connect(
            self.le_filter_textChanged)

        self.le_filter = self.findChild(
            QtWidgets.QLineEdit,
            'le_filter')
        self.le_filter.textChanged.connect(
            self.le_filter_textChanged)
        self.le_filter.editingFinished.connect(
            self.le_filter_editingFinished)

        self.cbb_filter_history = self.findChild(
            QtWidgets.QComboBox,
            'cbb_filter_history')
        self.cbb_filter_history.textActivated.connect(
            self.cbb_filter_history_textActivated)

        self.b_filter_rehelp = self.findChild(
            QtWidgets.QPushButton,
            'b_filter_rehelp')
        self.b_filter_rehelp.clicked.connect(
            self.b_filter_rehelp_clicked)

        self.cb_filter_regex = self.findChild(
            QtWidgets.QCheckBox,
            'cb_filter_regex')
        self.cb_filter_regex.stateChanged.connect(
            self.cb_filter_regex_stateChanged)

        self.cb_filter_case = self.findChild(
            QtWidgets.QCheckBox,
            'cb_filter_case')
        self.cb_filter_case.stateChanged.connect(
            self.le_filter_textChanged)

        self.b_filter_clear = self.findChild(
            QtWidgets.QPushButton,
            'b_filter_clear')
        self.b_filter_clear.clicked.connect(
            self.b_filter_clear_clicked)

        self.l_edit_icount = self.findChild(
            QtWidgets.QLabel,
            'l_edit_icount')

        # add EDIT TAB > editbox
        self.f_editbox = self.findChild(
            QtWidgets.QFrame,
            'f_editbox')

        self.tb_toggle_editbox = self.findChild(
            QtWidgets.QToolButton,
            'tb_toggle_editbox')
        self.tb_toggle_editbox.clicked.connect(
            self.tb_toggle_editbox_clicked)

        # EDITBOX BUTTONS
        if not G.settings['no_gui']:
            self.b_edit_delete = self.findChild(
                QtWidgets.QPushButton,
                'b_edit_delete')
            self.b_edit_delete.clicked.connect(
                self.b_edit_delete_clicked)

            self.b_edit_duplicate = self.findChild(
                QtWidgets.QPushButton,
                'b_edit_duplicate')
            self.b_edit_duplicate.clicked.connect(
                self.b_edit_duplicate_clicked)

            self.b_edit_new = self.findChild(
                QtWidgets.QPushButton,
                'b_edit_new')
            self.b_edit_new.clicked.connect(
                self.b_edit_new_clicked)

            self.b_edit_prevgame = self.findChild(
                QtWidgets.QPushButton,
                'b_edit_prevgame')
            self.b_edit_prevgame.clicked.connect(
                self.b_edit_prevgame_clicked)

            self.b_edit_nextgame = self.findChild(
                QtWidgets.QPushButton,
                'b_edit_nextgame')
            self.b_edit_nextgame.clicked.connect(
                self.b_edit_nextgame_clicked)

        # dict will be filled with adresses of all labels and edit fields.
        # It will be used later for hiding controls alongside the headers,
        # when using the --hide option.
        self.editbox_vars = dict()

        self.fl_editbox_left = self.findChild(
            QtWidgets.QFormLayout,
            'fl_editbox_left')

        self.fl_editbox_right = self.findChild(
            QtWidgets.QFormLayout,
            'fl_editbox_right')

        self.hbl_idsource = self.findChild(
            QtWidgets.QHBoxLayout,
            'hbl_idsource')

        self.hbl_devpub = self.findChild(
            QtWidgets.QHBoxLayout,
            'hbl_devpub')

        self.hbl_idsource = self.findChild(
            QtWidgets.QHBoxLayout,
            'hbl_idsource')

        self.hbl_relgen = self.findChild(
            QtWidgets.QHBoxLayout,
            'hbl_relgen')

        self.hbl_countlast = self.findChild(
            QtWidgets.QHBoxLayout,
            'hbl_countlast')

        self.hbl_playrating = self.findChild(
            QtWidgets.QHBoxLayout,
            'hbl_playrating')

        self.hbl_favhikid = self.findChild(
            QtWidgets.QHBoxLayout,
            'hbl_favhikid')

        self.vbl_favhikid = self.findChild(
            QtWidgets.QVBoxLayout,
            'vbl_favhikid')

        # EDIT BOX WITH VARS
        self.l_edit_id = self.findChild(
            QtWidgets.QLabel,
            'l_edit_id')
        self.le_edit_id = self.findChild(
            QtWidgets.QLineEdit,
            'le_edit_id')
        self.editbox_vars['id'] = [self.l_edit_id,
                                   self.le_edit_id]

        self.l_edit_source = self.findChild(
            QtWidgets.QLabel,
            'l_edit_source')
        self.le_edit_source = self.findChild(
            QtWidgets.QLineEdit,
            'le_edit_source')
        self.editbox_vars['source'] = [self.l_edit_source,
                                       self.le_edit_source]

        self.l_edit_name = self.findChild(
            QtWidgets.QLabel,
            'l_edit_name')
        self.le_edit_name = self.findChild(
            QtWidgets.QLineEdit,
            'le_edit_name')
        self.editbox_vars['name'] = [self.l_edit_name,
                                     self.le_edit_name]

        self.l_edit_sortname = self.findChild(
            QtWidgets.QLabel,
            'l_edit_sortname')
        self.le_edit_sortname = self.findChild(
            QtWidgets.QLineEdit,
            'le_edit_sortname')
        self.editbox_vars['sortname'] = [self.l_edit_sortname,
                                         self.le_edit_sortname]

        self.l_edit_desc = self.findChild(
            QtWidgets.QLabel,
            'l_edit_desc')
        self.pte_edit_desc = self.findChild(
            QtWidgets.QPlainTextEdit,
            'pte_edit_desc')
        self.editbox_vars['desc'] = [self.l_edit_desc,
                                     self.pte_edit_desc]

        self.l_edit_developer = self.findChild(
            QtWidgets.QLabel,
            'l_edit_developer')
        self.le_edit_developer = self.findChild(
            QtWidgets.QLineEdit,
            'le_edit_developer')
        self.editbox_vars['developer'] = [self.l_edit_developer,
                                          self.le_edit_developer]

        self.l_edit_publisher = self.findChild(
            QtWidgets.QLabel,
            'l_edit_publisher')
        self.le_edit_publisher = self.findChild(
            QtWidgets.QLineEdit,
            'le_edit_publisher')
        self.editbox_vars['publisher'] = [self.l_edit_publisher,
                                          self.le_edit_publisher]

        self.l_edit_releasedate = self.findChild(
            QtWidgets.QLabel,
            'l_edit_releasedate')
        self.le_edit_releasedate = self.findChild(
            QtWidgets.QLineEdit,
            'le_edit_releasedate')
        self.editbox_vars['releasedate'] = [self.l_edit_releasedate,
                                            self.le_edit_releasedate]

        self.l_edit_genre = self.findChild(
            QtWidgets.QLabel,
            'l_edit_genre')
        self.cbb_edit_genre = self.findChild(
            QtWidgets.QComboBox,
            'cbb_edit_genre')
        self.editbox_vars['genre'] = [self.l_edit_genre,
                                      self.cbb_edit_genre]

        self.l_edit_path = self.findChild(
            QtWidgets.QLabel,
            'l_edit_path')
        self.le_edit_path = self.findChild(
            QtWidgets.QLineEdit,
            'le_edit_path')
        self.editbox_vars['path'] = [self.l_edit_path,
                                     self.le_edit_path]

        self.l_edit_thumbnail = self.findChild(
            QtWidgets.QLabel,
            'l_edit_thumbnail')
        self.le_edit_thumbnail = self.findChild(
            QtWidgets.QLineEdit,
            'le_edit_thumbnail')
        self.editbox_vars['thumbnail'] = [self.l_edit_thumbnail,
                                          self.le_edit_thumbnail]

        self.l_edit_image = self.findChild(
            QtWidgets.QLabel,
            'l_edit_image')
        self.le_edit_image = self.findChild(
            QtWidgets.QLineEdit,
            'le_edit_image')
        self.editbox_vars['image'] = [self.l_edit_image,
                                      self.le_edit_image]

        self.l_edit_marquee = self.findChild(
            QtWidgets.QLabel,
            'l_edit_marquee')
        self.le_edit_marquee = self.findChild(
            QtWidgets.QLineEdit,
            'le_edit_marquee')
        self.editbox_vars['marquee'] = [self.l_edit_marquee,
                                        self.le_edit_marquee]

        self.l_edit_video = self.findChild(
            QtWidgets.QLabel,
            'l_edit_video')
        self.le_edit_video = self.findChild(
            QtWidgets.QLineEdit,
            'le_edit_video')
        self.editbox_vars['video'] = [self.l_edit_video,
                                      self.le_edit_video]

        self.l_edit_playcount = self.findChild(
            QtWidgets.QLabel,
            'l_edit_playcount')
        self.sp_edit_playcount = self.findChild(
            QtWidgets.QSpinBox,
            'sp_edit_playcount')
        self.editbox_vars['playcount'] = [self.l_edit_playcount,
                                          self.sp_edit_playcount]

        self.l_edit_lastplayed = self.findChild(
            QtWidgets.QLabel,
            'l_edit_lastplayed')
        self.le_edit_lastplayed = self.findChild(
            QtWidgets.QLineEdit,
            'le_edit_lastplayed')
        self.editbox_vars['lastplayed'] = [self.l_edit_lastplayed,
                                           self.le_edit_lastplayed]

        self.l_edit_players = self.findChild(
            QtWidgets.QLabel,
            'l_edit_players')
        self.sp_edit_players = self.findChild(
            QtWidgets.QSpinBox,
            'sp_edit_players')
        self.editbox_vars['sp_edit_players'] = [self.l_edit_players,
                                                self.sp_edit_players]

        self.l_edit_rating = self.findChild(
            QtWidgets.QLabel,
            'l_edit_rating')
        self.dsp_edit_rating = self.findChild(
            QtWidgets.QDoubleSpinBox,
            'dsp_edit_rating')
        self.editbox_vars['rating'] = [self.l_edit_rating,
                                       self.dsp_edit_rating]

        self.cb_edit_favorite = self.findChild(
            QtWidgets.QCheckBox,
            'cb_edit_favorite')
        self.editbox_vars['favorite'] = [self.cb_edit_favorite]

        self.cb_edit_hidden = self.findChild(
            QtWidgets.QCheckBox,
            'cb_edit_hidden')
        self.editbox_vars['hidden'] = [self.cb_edit_hidden]

        self.cb_edit_kidgame = self.findChild(
            QtWidgets.QCheckBox,
            'cb_edit_kidgame')
        self.editbox_vars['kidgame'] = [self.cb_edit_kidgame]
        # END OF EDIT BOX WITH VARS

        self.dbb_edit_buttons = self.findChild(
            QtWidgets.QDialogButtonBox,
            'dbb_edit_buttons')
        self.dbb_edit_buttons.clicked.connect(
            self.dbb_edit_buttons_clicked)

        # add EXPORT TAB
        self.tb_export_filedialog = self.findChild(
            QtWidgets.QToolButton,
            'tb_export_filedialog')
        self.tb_export_filedialog.clicked.connect(
            self.tb_export_filedialog_clicked)

        self.le_export_file = self.findChild(
            QtWidgets.QLineEdit,
            'le_export_file')
        self.le_export_file.textChanged.connect(
            self.le_export_file_textChanged)  # Remember to .strip()
        self.le_export_file.returnPressed.connect(
            self.le_export_file_returnPressed)
        self.le_export_file.editingFinished.connect(
            self.le_export_file_editingFinished)

        self.cb_export_sameasopen = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_sameasopen')
        self.cb_export_sameasopen.clicked.connect(
            self.cb_export_sameasopen_clicked)

        self.rb_export_format_xml = self.findChild(
            QtWidgets.QRadioButton,
            'rb_export_format_xml')
        self.rb_export_format_xml.clicked.connect(
            self.rb_export_format_clicked)
        self.rb_export_format_xml.toggled.connect(
            self.rb_export_format_toggled)

        self.rb_export_format_json = self.findChild(
            QtWidgets.QRadioButton,
            'rb_export_format_json')
        self.rb_export_format_json.clicked.connect(
            self.rb_export_format_clicked)
        self.rb_export_format_json.toggled.connect(
            self.rb_export_format_toggled)

        self.rb_export_format_csv = self.findChild(
            QtWidgets.QRadioButton,
            'rb_export_format_csv')
        self.rb_export_format_csv.clicked.connect(
            self.rb_export_format_clicked)
        self.rb_export_format_csv.toggled.connect(
            self.rb_export_format_toggled_csv)

        self.rb_export_format_cfg = self.findChild(
            QtWidgets.QRadioButton,
            'rb_export_format_cfg')
        self.rb_export_format_cfg.clicked.connect(
            self.rb_export_format_clicked)
        self.rb_export_format_cfg.toggled.connect(
            self.rb_export_format_toggled_cfg)

        self.rb_export_format_txt = self.findChild(
            QtWidgets.QRadioButton,
            'rb_export_format_txt')
        self.rb_export_format_txt.clicked.connect(
            self.rb_export_format_clicked)
        self.rb_export_format_txt.toggled.connect(
            self.rb_export_format_toggled)

        self.l_export_available_space = self.findChild(
            QtWidgets.QLabel,
            'l_export_available_space')

        self.l_export_available = self.findChild(
            QtWidgets.QLabel,
            'l_export_available')

        self.cb_export_applyfilter = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_applyfilter')

        self.cb_export_keep_empty = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_keep_empty')

        self.dbb_export_buttons = self.findChild(
            QtWidgets.QDialogButtonBox,
            'dbb_export_buttons')
        self.dbb_export_buttons.clicked.connect(
            self.dbb_export_buttons_clicked)

        # add EXCLUDE TAGS in EXPORT TAB
        self.cb_export_exclude = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude')
        self.cb_export_exclude.stateChanged.connect(
            self.cb_export_exclude_stateChanged)

        self.l_export_exclude_more = self.findChild(
            QtWidgets.QLabel,
            'l_export_exclude_more')

        self.f_export_exclude = self.findChild(
            QtWidgets.QFrame,
            'f_export_exclude')

        # list of all checkboxes for exclude tags.
        self.export_exclude_vars = []

        self.cb_export_exclude_id = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_id')
        self.cb_export_exclude_id.stateChanged.connect(
            self.cb_export_exclude_id_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_id)

        self.cb_export_exclude_source = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_source')
        self.cb_export_exclude_source.stateChanged.connect(
            self.cb_export_exclude_source_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_source)

        self.cb_export_exclude_name = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_name')
        self.cb_export_exclude_name.stateChanged.connect(
            self.cb_export_exclude_name_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_name)

        self.cb_export_exclude_sortname = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_sortname')
        self.cb_export_exclude_sortname.stateChanged.connect(
            self.cb_export_exclude_sortname_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_sortname)

        self.cb_export_exclude_desc = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_desc')
        self.cb_export_exclude_desc.stateChanged.connect(
            self.cb_export_exclude_desc_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_desc)

        self.cb_export_exclude_developer = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_developer')
        self.cb_export_exclude_developer.stateChanged.connect(
            self.cb_export_exclude_developer_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_developer)

        self.cb_export_exclude_publisher = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_publisher')
        self.cb_export_exclude_publisher.stateChanged.connect(
            self.cb_export_exclude_publisher_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_publisher)

        self.cb_export_exclude_releasedate = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_releasedate')
        self.cb_export_exclude_releasedate.stateChanged.connect(
            self.cb_export_exclude_releasedate_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_releasedate)

        self.cb_export_exclude_genre = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_genre')
        self.cb_export_exclude_genre.stateChanged.connect(
            self.cb_export_exclude_genre_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_genre)

        self.cb_export_exclude_path = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_path')
        self.cb_export_exclude_path.stateChanged.connect(
            self.cb_export_exclude_path_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_path)

        self.cb_export_exclude_thumbnail = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_thumbnail')
        self.cb_export_exclude_thumbnail.stateChanged.connect(
            self.cb_export_exclude_thumbnail_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_thumbnail)

        self.cb_export_exclude_image = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_image')
        self.cb_export_exclude_image.stateChanged.connect(
            self.cb_export_exclude_image_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_image)

        self.cb_export_exclude_marquee = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_marquee')
        self.cb_export_exclude_marquee.stateChanged.connect(
            self.cb_export_exclude_marquee_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_marquee)

        self.cb_export_exclude_video = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_video')
        self.cb_export_exclude_video.stateChanged.connect(
            self.cb_export_exclude_video_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_video)

        self.cb_export_exclude_players = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_players')
        self.cb_export_exclude_players.stateChanged.connect(
            self.cb_export_exclude_players_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_players)

        self.cb_export_exclude_rating = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_rating')
        self.cb_export_exclude_rating.stateChanged.connect(
            self.cb_export_exclude_rating_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_rating)

        self.cb_export_exclude_favorite = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_favorite')
        self.cb_export_exclude_favorite.stateChanged.connect(
            self.cb_export_exclude_favorite_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_favorite)

        self.cb_export_exclude_hidden = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_hidden')
        self.cb_export_exclude_hidden.stateChanged.connect(
            self.cb_export_exclude_hidden_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_hidden)

        self.cb_export_exclude_kidgame = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_kidgame')
        self.cb_export_exclude_kidgame.stateChanged.connect(
            self.cb_export_exclude_kidgame_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_kidgame)

        self.cb_export_exclude_lastplayed = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_lastplayed')
        self.cb_export_exclude_lastplayed.stateChanged.connect(
            self.cb_export_exclude_lastplayed_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_lastplayed)

        self.cb_export_exclude_playcount = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_playcount')
        self.cb_export_exclude_playcount.stateChanged.connect(
            self.cb_export_exclude_playcount_stateChanged)
        self.export_exclude_vars.append(self.cb_export_exclude_playcount)

        self.b_export_exclude_invert = self.findChild(
            QtWidgets.QPushButton,
            'b_export_exclude_invert')
        self.b_export_exclude_invert.clicked.connect(
            self.b_export_exclude_invert_clicked)

        self.b_export_exclude_none = self.findChild(
            QtWidgets.QPushButton,
            'b_export_exclude_none')
        self.b_export_exclude_none.clicked.connect(
            self.b_export_exclude_none_clicked)

        self.b_export_exclude_all = self.findChild(
            QtWidgets.QPushButton,
            'b_export_exclude_all')
        self.b_export_exclude_all.clicked.connect(
            self.b_export_exclude_all_clicked)

        # add EXCLUDE UNSUPPORTED TAGS
        self.cb_export_exclude_unsupptags = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_exclude_unsupptags')

        # add INDENT
        self.cb_export_indent = self.findChild(
            QtWidgets.QCheckBox,
            'cb_export_indent')
        self.cb_export_indent.stateChanged.connect(
            self.cb_export_indent_stateChanged)

        self.sb_export_indent = self.findChild(
            QtWidgets.QSpinBox,
            'sb_export_indent')

        self.l_export_indent_more = self.findChild(
            QtWidgets.QLabel,
            'l_export_indent_more')

        self.f_export_indent = self.findChild(
            QtWidgets.QFrame,
            'f_export_indent')

        self.b_export_indent_zero = self.findChild(
            QtWidgets.QPushButton,
            'b_export_indent_zero')
        self.b_export_indent_zero.clicked.connect(
            self.b_export_indent_zero_clicked)

        self.b_export_indent_four = self.findChild(
            QtWidgets.QPushButton,
            'b_export_indent_four')
        self.b_export_indent_four.clicked.connect(
            self.b_export_indent_four_clicked)

        # add ABOUT Tab
        if not G.settings['no_gui']:
            self.l_about_app_icon = self.findChild(
                QtWidgets.QLabel,
                'l_about_app_icon')

            self.l_about_app_title = self.findChild(
                QtWidgets.QLabel,
                'l_about_app_title')

            self.l_about_app_version = self.findChild(
                QtWidgets.QLabel,
                'l_about_app_version')

            self.l_about_app_path = self.findChild(
                QtWidgets.QLabel,
                'l_about_app_path')

            self.l_about_app_copyright = self.findChild(
                QtWidgets.QLabel,
                'l_about_app_copyright')

            self.l_about_app_readme = self.findChild(
                QtWidgets.QLabel,
                'l_about_app_readme')

            self.l_about_app_desc = self.findChild(
                QtWidgets.QLabel,
                'l_about_app_desc')

            self.l_about_app_name = self.findChild(
                QtWidgets.QLabel,
                'l_about_app_name')

            self.l_about_app_author = self.findChild(
                QtWidgets.QLabel,
                'l_about_app_author')

            self.l_about_app_license = self.findChild(
                QtWidgets.QLabel,
                'l_about_app_license')

            self.l_about_app_execpython = self.findChild(
                QtWidgets.QLabel,
                'l_about_app_execpython')

            self.l_about_app_execqt5 = self.findChild(
                QtWidgets.QLabel,
                'l_about_app_execqt5')

            self.l_about_app_ispyinstaller = self.findChild(
                QtWidgets.QLabel,
                'l_about_app_ispyinstaller')

            self.l_about_app_dir= self.findChild(
                QtWidgets.QLabel,
                'l_about_app_dir')

        # CREATE GAMELIST with, table view and model data
        self.new_gamelist(str(G.settings['import']), 'tv_gamelist')
        #self.gamelist.view.clicked.connect(self.gamelist_view_clicked)

        if (G.settings['import']
        and not os.path.exists(G.settings['import'])):
            msg = f'Error! File does not exist: {str(G.settings["import"])}'
            msg_show_error(msg, 'Critical')

        if G.settings['maximize']:
            self.setWindowState(QtCore.Qt.WindowMaximized)
        self.set_fullscreen(G.settings['fullscreen'])

        if self.gamelist.model.file:
            self.jump_to_tab('edit')
        else:
            self.jump_to_tab('import')

        if (G.settings['no_gui']
        and G.settings['open_editbox']):
            self.enable_editbox()
        else:
            self.disable_editbox()

        if G.settings['hide_weblinks']:
            self.w_weblinks.setHidden(True)

        # IMPORT and EXPORT TAB
        self.set_le_import_file(G.settings['import'])
        self.set_le_export_file(G.settings['export'])
        # Disable button if no text is available in line edit.
        self.dbb_import_buttons.setEnabled(bool(self.le_import_file.text()))
        self.dbb_export_buttons.setEnabled(self.allow_export())

        self.cb_export_applyfilter.setChecked(G.settings['export_apply_filter'])
        #self.cb_export_sameasopen.setChecked(bool(self.sameasopen(text)))
        if not G.settings['no_same'] is None:
            #self.cb_export_sameasopen_clicked(True)
            self.cb_export_sameasopen_clicked(False)

        self.cb_export_exclude.setChecked(True)
        self.cb_export_exclude.setChecked(not G.settings['export_exclude'] == [])
        self.export_exclude_init(G.settings['export_exclude'])
        self.cb_export_exclude_unsupptags.setChecked(G.settings['export_exclude_unsupptags'])
        self.cb_export_keep_empty.setChecked(G.settings['export_keep_empty'])
        self.pb_file_progress.setVisible(False)

        if G.settings['indent'] is not None:
            self.sb_export_indent.setValue(G.settings['indent'])
        self.set_export_indent()

        if pathlib.PurePath(self.le_export_file.text()).suffix == '':
            self.rb_export_format_xml.setChecked(True)
        self.set_export_format()
        if self.rb_export_format_cfg.isChecked():
            self.enable_widgets_cfg(False)
        elif self.rb_export_format_csv.isChecked():
            self.enable_widgets_csv(False)
        self.rb_export_format_clicked()

        if not G.settings['no_gui']:
            # EDIT TAB
            self.b_filter_rehelp.setEnabled(self.cb_filter_regex.isChecked())
            # ABOUT TAB
            picture = QtGui.QPixmap(str(G.settings['app_icon_path']))
            self.l_about_app_icon.setPixmap(picture)
            self.l_about_app_title.setText(G.settings['app_title'])
            self.l_about_app_version.setText(G.settings['app_version'])
            self.l_about_app_path.setText(str(G.settings['app_path']))
            text = G.settings['app_copyright_years']
            author = G.settings['app_author']
            self.l_about_app_copyright.setText(f'Copyright © {text} {author}')
            self.l_about_app_desc.setText(G.settings['app_desc'])
            self.l_about_app_name.setText(G.settings['app_name'])
            self.l_about_app_author.setText(G.settings['app_author'])
            text = G.settings['app_license']
            path = G.settings['app_license_path']
            self.l_about_app_license.setText(f'<a href="{path}">{text}</a>')
            text = f'{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}'
            self.l_about_app_execpython.setText(text)
            self.l_about_app_execqt5.setText(QtCore.qVersion())
            self.l_about_app_ispyinstaller.setText('yes' if frozen() else 'no')
            path = G.settings['app_readme_path']
            self.l_about_app_readme.setText(f'<a href="{path}">Open README</a>')
            text = 'Open AppFolder'
            path = G.settings['app_dir']
            self.l_about_app_dir.setText(f'<a href="{path}">{text}</a>')
        else:
            # Terminate program, if no files are set while in no-gui mode.
            if (self.le_import_file.text() == ''
            or (not self.le_export_file.text() == '/dev/null/'
                and self.le_export_file.text() == '')
            ):
                msg = ('Error! Missing import file. --no-gui option requires'
                      ' --import with a FILE argument.'
                      '\nProgram will terminate.')
                msg_show_error(msg, 'Critical')
                sys.exit(2)

        # END OF MainWindow.__init__()   #
        ##################################

    # GENERAL
    def new_gamelist(self, file, table):
        self.l_current_file.setVisible(False)
        self.pb_file_progress.reset()
        self.pb_file_progress.setVisible(True)

        try:
            del self.gamelist
        except AttributeError:
            pass

        self.tv_gamelist = self.findChild(
            QtWidgets.QTableView,
            table)

        self.gamelist = GamelistTable(
            file,
            self.tv_gamelist,
            self,
            G.settings['tag_order'],
            self.pb_file_progress)

        if self.gamelist.model.file:
            msg_stderr(f'File successfully imported: {str(file)}')
            wintitle = f'{os.path.basename(file)}[*] - {G.settings["app_title"]}'
            self.setWindowTitle(wintitle)
            self.l_current_file.setText(str(file))
            self.dbb_export_buttons.setEnabled(self.allow_export())
        self.gamelist.reset_unsaved()

        tabs = []
        tabs.append(self.t_tabs.widget(self.tabs_names['edit']))
        tabs.append(self.t_tabs.widget(self.tabs_names['export']))
        for tab in tabs:
            tab.setEnabled(bool(self.gamelist.model.file))

        if G.settings['no_table_edit']:
            self.gamelist.view.doubleClicked.connect(
                self.view_doubleClicked)
            self.gamelist.disable_edit()

        self.cbb_filter_header.currentIndexChanged.disconnect(
            self.le_filter_textChanged)

        if G.settings['mod_flag']:
            self.gamelist.model.mod_flag_role = QtGui.QColor('yellow')
        self.cbb_edit_genre.clear()
        self.cbb_edit_genre.addItems(
            self.gamelist.get_genres(G.settings['genre_groups']))
        self.le_filter_textChanged()

        self.selectionModel = self.gamelist.view.selectionModel()
        self.selectionModel.selectionChanged.connect(
            self.gamelist_selectionChanged)

        self.cbb_filter_header.clear()
        self.cbb_filter_header.addItems(['ALL'])
        self.cbb_filter_header.addItems(self.gamelist.get_header())
        self.set_filter_header(G.settings['filter_by'])

        self.cbb_filter_header.currentIndexChanged.connect(
            self.le_filter_textChanged)

        self.cb_filter_regex.setChecked(G.settings['filter_regex'])
        self.cb_filter_case.setChecked(G.settings['filter_case'])
        self.le_filter.setText(G.settings['filter'])

        self.gamelist.sort_header(G.settings['sort'])

        locked_header = self.gamelist.lock_columns(G.settings['lock'])
        self.lock_controls(locked_header)
        self.hide_header_and_controls(G.settings['turnoff'])
        self.set_header_sizes(G.settings['resize'])
        if self.gamelist.model.file:
            self.select_table_row(0)

        self.update_completer()

        self.item_delegate = self.gamelist.view.itemDelegate()
        self.item_delegate.commitData.connect(
            self.commitData)

        self.pb_file_progress.setVisible(False)
        self.l_current_file.setVisible(True)
        self.le_export_startswith_custom = None

    def update_completer(self):
        if (not G.settings['no_gui']
        and not G.settings['no_autocomplete']):
            self.gamelist.set_completer(self.le_filter,
                ['name', 'developer', 'publisher'], 'MatchContains')
            self.gamelist.set_completer(self.le_edit_source,
                'source')
            self.gamelist.set_completer(self.le_edit_name,
                'name')
            self.gamelist.set_completer(self.le_edit_sortname,
                'sortname')
            self.gamelist.set_completer(self.le_edit_developer,
                'developer')
            self.gamelist.set_completer(self.le_edit_publisher,
                'publisher')
            self.gamelist.set_completer(self.le_edit_releasedate,
                'releasedate')
            self.gamelist.set_completer(self.le_edit_path,
                'path')
            self.gamelist.set_completer(self.le_edit_thumbnail,
                'thumbnail')
            self.gamelist.set_completer(self.le_edit_image,
                'image')
            self.gamelist.set_completer(self.le_edit_marquee,
                'marquee')
            self.gamelist.set_completer(self.le_edit_video,
                'video')

    def commitData(self, editor):
        self.gamelist.view.commitData(editor)
        self.update_editbox()
        self.update_completer()

    def view_doubleClicked(self, mindex):
        self.tb_toggle_editbox_clicked()

    def select_table_row(self, row=0):
        self.gamelist.view.setFocus()
        try:
            model = self.gamelist.view.model()
            if row < 0:
                row = model.rowCount() + row
            mindex = model.index(row, 0, QtCore.QModelIndex())
            self.gamelist.view.selectRow(mindex.row())
        except Exception:
            self.gamelist.view.selectRow(0)

    def select_last_table_row(self):
        self.select_table_row(-1)

    def gamelist_selectionChanged(self, newSelection, oldSelection):
        self.update_editbox()

    def closeEvent(self, event):
        #and self.gamelist.model.is_edited()):
        close = True
        if self.gamelist.is_unsaved():
            msg = ('Attention, potential data loss!'
                  '\n\nYou have a modified and unsaved XML database open.'
                  ' Proceeding will discard the content and terminate the'
                  ' application.'
                  '\n\nDo you want continue?')
            if not msg_continue(msg, 'Warning', parent=self):
                close = False
        if close:
            EOT_action()
            event.accept()
        else:
            event.ignore()

    def update_icount_display(self, index):
        current = index + 1 if not index is None else '-'
        total_count = len(self.gamelist.model.data)
        if len(self.le_filter.text()) > 0:
            filtered_count = self.gamelist.view.model().rowCount()
            total = f'{filtered_count} / {total_count}'
        else:
            total = f'{total_count}'
        self.l_edit_icount.setText(f'Game No. {current} (Total: {total})')

    def enable_toolbox_source(self, source, id):
        if not G.settings['no_gui']:
            enable = bool((not source == '' and not id == '')
                          and self.w_weblinks.isEnabled())
            self.tb_search_source.setEnabled(enable)
            self.tb_search_source.setChecked(not enable)

    def enable_toolbox_weblinks(self, enable=True):
        if not G.settings['no_gui']:
            self.w_weblinks.setEnabled(enable)
            self.tb_search_source.setChecked(not enable)
            self.tb_search_web.setChecked(not enable)
            self.tb_search_video.setChecked(not enable)
            self.tb_search_wiki.setChecked(not enable)
            self.tb_search_games.setChecked(not enable)
            self.tb_search_emulation.setChecked(not enable)
            self.tb_search_romhacks.setChecked(not enable)

    def update_editbox(self, reset=False):
        mindex = self.gamelist.get_selected_mindex()
        index = self.gamelist.get_data_index(mindex) if mindex else None

        self.update_icount_display(index)

        id = ''  # will be set after reading data
        source = ''
        if index is None:
            self.enable_toolbox_weblinks(False)

            self.le_edit_source.clear()
            self.le_edit_id.clear()
            self.le_edit_name.clear()
            self.le_edit_sortname.clear()
            self.pte_edit_desc.clear()
            self.le_edit_path.clear()
            self.le_edit_thumbnail.clear()
            self.le_edit_image.clear()
            self.le_edit_marquee.clear()
            self.le_edit_video.clear()
            self.le_edit_developer.clear()
            self.le_edit_publisher.clear()
            self.le_edit_releasedate.clear()
            self.cbb_edit_genre.clearEditText()
            self.sp_edit_playcount.clear()
            self.le_edit_lastplayed.clear()
            self.sp_edit_players.clear()
            self.dsp_edit_rating.clear()
            self.cb_edit_favorite.setChecked(False)
            self.cb_edit_hidden.setChecked(False)
            self.cb_edit_kidgame.setChecked(False)
        else:
            self.enable_toolbox_weblinks(True)

            if reset:
                data = self.gamelist.model._original_data[index]
            else:
                data = self.gamelist.model.data[index]
            header = self.gamelist.model.header

            try:
                text = data[header['source']]
            except ValueError:
                text = ''
            if text:
                self.le_edit_source.setText(text)
            else:
                self.le_edit_source.clear()

            source = text

            try:
                text = data[header['id']]
            except ValueError:
                text = ''
            if text:
                self.le_edit_id.setText(text)
            else:
                self.le_edit_id.clear()

            id = text

            try:
                text = data[header['name']]
            except ValueError:
                text = ''
            if text:
                self.le_edit_name.setText(text)
            else:
                self.le_edit_name.clear()

            try:
                text = data[header['sortname']]
            except ValueError:
                text = ''
            if text:
                self.le_edit_sortname.setText(text)
            else:
                self.le_edit_sortname.clear()

            try:
                text = data[header['desc']]
            except ValueError:
                text = ''
            if text:
                self.pte_edit_desc.setPlainText(text)
            else:
                self.pte_edit_desc.clear()

            try:
                text = data[header['path']]
            except ValueError:
                text = ''
            if text:
                self.le_edit_path.setText(text)
            else:
                self.le_edit_path.clear()

            try:
                text = data[header['thumbnail']]
            except ValueError:
                text = ''
            if text:
                self.le_edit_thumbnail.setText(text)
            else:
                self.le_edit_thumbnail.clear()

            try:
                text = data[header['image']]
            except ValueError:
                text = ''
            if text:
                self.le_edit_image.setText(text)
            else:
                self.le_edit_image.clear()

            try:
                text = data[header['marquee']]
            except ValueError:
                text = ''
            if text:
                self.le_edit_marquee.setText(text)
            else:
                self.le_edit_marquee.clear()

            try:
                text = data[header['video']]
            except ValueError:
                text = ''
            if text:
                self.le_edit_video.setText(text)
            else:
                self.le_edit_video.clear()

            try:
                text = data[header['developer']]
            except ValueError:
                text = ''
            if text:
                self.le_edit_developer.setText(text)
            else:
                self.le_edit_developer.clear()

            try:
                text = data[header['publisher']]
            except ValueError:
                text = ''
            if text:
                self.le_edit_publisher.setText(text)
            else:
                self.le_edit_publisher.clear()

            try:
                text = data[header['releasedate']]
            except ValueError:
                text = ''
            if text:
                self.le_edit_releasedate.setText(text)
            else:
                self.le_edit_releasedate.clear()

            try:
                text = data[header['genre']]
            except ValueError:
                text = ''
            if text:
                self.cbb_edit_genre.setEditText(text)
            else:
                self.cbb_edit_genre.clearEditText()

            try:
                text = data[header['playcount']]
                text = int(text)
            except (ValueError, TypeError):
                text = ''
            if text:
                self.sp_edit_playcount.setValue(text)
            else:
                self.sp_edit_playcount.clear()

            try:
                text = data[header['lastplayed']]
            except ValueError:
                text = ''
            if text:
                self.le_edit_lastplayed.setText(text)
            else:
                self.le_edit_lastplayed.clear()

            try:
                text = data[header['players']]
                text = int(text)
            except (ValueError, TypeError):
                text = ''
            if not text == '':
                self.sp_edit_players.setValue(text)
            else:
                self.sp_edit_players.clear()

            try:
                text = data[header['rating']]
                text = float(text)
            except (ValueError, TypeError):
                text = ''
            if not text == '':
                self.dsp_edit_rating.setValue(text)
            else:
                self.dsp_edit_rating.clear()

            try:
                text = data[header['favorite']]
            except ValueError:
                text = ''
            self.cb_edit_favorite.setChecked(text == 'true')

            try:
                text = data[header['hidden']]
            except ValueError:
                text = ''
            self.cb_edit_hidden.setChecked(text == 'true')

            try:
                text = data[header['kidgame']]
            except ValueError:
                text = ''
            self.cb_edit_kidgame.setChecked(text == 'true')

        self.enable_toolbox_source(source, id)

    def apply_editbox_changes(self):
        mindex = self.gamelist.get_selected_mindex()
        if mindex:
            index = self.gamelist.get_data_index(mindex)
            header = self.gamelist.model.header

            if self.le_edit_id.isEnabled():
                text = self.le_edit_id.text()
                self.gamelist.model.data[index][header['id']] = text

            if self.le_edit_source.isEnabled():
                text = self.le_edit_source.text()
                self.gamelist.model.data[index][header['source']] = text

            if self.le_edit_name.isEnabled():
                text = self.le_edit_name.text()
                self.gamelist.model.data[index][header['name']] = text

            if self.le_edit_sortname.isEnabled():
                text = self.le_edit_sortname.text()
                self.gamelist.model.data[index][header['sortname']] = text

            if self.pte_edit_desc.isEnabled():
                text = self.pte_edit_desc.toPlainText()
                self.gamelist.model.data[index][header['desc']] = text

            if self.le_edit_developer.isEnabled():
                text = self.le_edit_developer.text()
                self.gamelist.model.data[index][header['developer']] = text

            if self.le_edit_publisher.isEnabled():
                text = self.le_edit_publisher.text()
                self.gamelist.model.data[index][header['publisher']] = text

            if self.le_edit_releasedate.isEnabled():
                text = self.le_edit_releasedate.text()
                self.gamelist.model.data[index][header['releasedate']] = text

            if self.cbb_edit_genre.isEnabled():
                text = self.cbb_edit_genre.currentText()
                self.gamelist.model.data[index][header['genre']] = text

            if self.le_edit_path.isEnabled():
                text = self.le_edit_path.text()
                self.gamelist.model.data[index][header['path']] = text

            if self.le_edit_thumbnail.isEnabled():
                text = self.le_edit_thumbnail.text()
                self.gamelist.model.data[index][header['thumbnail']] = text

            if self.le_edit_image.isEnabled():
                text = self.le_edit_image.text()
                self.gamelist.model.data[index][header['image']] = text

            if self.le_edit_marquee.isEnabled():
                text = self.le_edit_marquee.text()
                self.gamelist.model.data[index][header['marquee']] = text

            if self.le_edit_video.isEnabled():
                text = self.le_edit_video.text()
                self.gamelist.model.data[index][header['video']] = text

            if self.sp_edit_playcount.isEnabled():
                text = self.sp_edit_playcount.cleanText()
                self.gamelist.model.data[index][header['playcount']] = text

            if self.le_edit_lastplayed.isEnabled():
                text = self.le_edit_lastplayed.text()
                self.gamelist.model.data[index][header['lastplayed']] = text

            if self.sp_edit_players.isEnabled():
                text = self.sp_edit_players.cleanText()
                self.gamelist.model.data[index][header['players']] = text

            if self.dsp_edit_rating.isEnabled():
                text = self.dsp_edit_rating.cleanText().replace(',', '.')
                if not text == '1.00':
                    text = text.rstrip('0')
                self.gamelist.model.data[index][header['rating']] = text

            if self.cb_edit_favorite.isEnabled():
                if self.cb_edit_favorite.checkState():
                    text = 'true'
                else:
                    text = ''
                self.gamelist.model.data[index][header['favorite']] = text

            if self.cb_edit_hidden.isEnabled():
                if self.cb_edit_hidden.checkState():
                    text = 'true'
                else:
                    text = ''
                self.gamelist.model.data[index][header['hidden']] = text

            if self.cb_edit_kidgame.isEnabled():
                if self.cb_edit_kidgame.checkState():
                    text = 'true'
                else:
                    text = ''
                self.gamelist.model.data[index][header['kidgame']] = text

            self.gamelist.update_selected_row()
            self.gamelist.item_delegate.commitData.emit(self.f_editbox)

    def reset_row_data(self):
        self.update_editbox(reset=True)

    def dbb_edit_buttons_clicked(self, button):
        role = self.dbb_edit_buttons.buttonRole(button)
        if role == 8:  # ApplyRole
            self.apply_editbox_changes()
        elif role == 7:  # ResetRole
            self.reset_row_data()

    # SHORTCUTS
    def toggle_fullscreen(self):
        self.set_fullscreen(not self.is_fullscreen)
        return self.is_fullscreen

    def toggle_weblinks_activated(self):
        if not G.settings['no_gui']:
            self.w_weblinks.setHidden(not self.w_weblinks.isHidden())
            return self.w_weblinks.isHidden()
        else:
            return True

    def toggle_filterbar_activated(self):
        self.w_filterbar.setHidden(not self.w_filterbar.isHidden())
        return self.w_filterbar.isHidden()

    # Window
    def set_fullscreen(self, enable):
        if enable:
            self.t_tabs_bar.setHidden(True)
            self.l_current_file.setHidden(True)
            if not G.settings['no_gui']:
                self.w_weblinks.setHidden(True)
            self.is_fullscreen = True
            self.setWindowState(QtCore.Qt.WindowFullScreen)
        else:
            self.t_tabs_bar.setHidden(False)
            self.l_current_file.setHidden(False)
            if not G.settings['no_gui']:
                self.w_weblinks.setHidden(False)
            self.is_fullscreen = False
            self.setWindowState(QtCore.Qt.WindowNoState)
            if G.settings['maximize']:
                self.setWindowState(QtCore.Qt.WindowMaximized)
        return self.is_fullscreen

    def t_tabs_currentChanged(self, index):
        if self.tabs_names['export'] == index:
            self.set_l_export_available()

    def jump_to_tab(self, tab):
        self.t_tabs.setCurrentIndex(self.tabs_names[tab])

    # IMPORT TAB
    def tb_import_filedialog_clicked(self):
        file = dialog_choose_file('Choose a gamelist XML file',
                                  '*.xml', 'Load')
        if file:
            self.set_le_import_file(file)

    def set_le_import_file(self, text):
        self.le_import_file.setText(str(text))

    def le_import_file_textChanged(self, text):
        orig = text.strip()
        norm = normalize_path(orig)
        if norm != orig:
            self.le_import_file.setText(norm)
        self.dbb_import_buttons.setEnabled(norm != '')

    def le_import_file_returnPressed(self):
        self.import_file()

    def dbb_import_buttons_clicked(self, button):
        role = self.dbb_import_buttons.buttonRole(button)
        if role == 0:  # AcceptRole
            self.import_file()

    def import_file(self):
        if self.gamelist.is_unsaved():
        #and self.gamelist.model.is_edited()):
            msg = ('Attention, potential data loss!'
                  '\n\nYou have already open up and modified a XML database.'
                  ' Proceeding will discard and replace the entire content'
                  ' with the chosen file.'
                  '\n\nDo you want continue?')
            proceed = msg_continue(msg, 'Warning', parent=self)
        else:
            proceed = True

        if proceed:
            file = get_path(self.le_import_file.text().strip())
            try:
                if file and file.exists():
                    self.new_gamelist(file, 'tv_gamelist')
                    if self.gamelist.model.file:
                        self.jump_to_tab('edit')
                    else:
                        self.jump_to_tab('import')
                else:
                    msg_show_error(f'Error! File does not exist: {str(file)}',
                                   'Critical')
            except PermissionError:
                msg_show_error(f'Error! No permission to access: {str(file)}',
                               'Critical')
            except IsADirectoryError:
                msg_show_error(f'Error! Path is a directory: {str(file)}',
                               'Critical')
            except OSError:
                msg_show_error(f'Error! File cannot be opened: {str(file)}',
                               'Critical')

            self.cb_export_sameasopen_clicked(
                self.cb_export_sameasopen.isChecked())

    # EDIT TAB
    def le_filter_textChanged(self):
        if self.cbb_filter_header.currentIndex() == 0:
            head = None
        else:
            head = self.cbb_filter_header.currentText()
        self.gamelist.filter(head,
                             self.le_filter.text(),
                             self.cb_filter_regex.isChecked(),
                             self.cb_filter_case.isChecked(),
                             self.le_filter)
        self.update_editbox()

    def le_filter_editingFinished(self):
        text = self.le_filter.text()
        if (not text == ''
           and self.cbb_filter_history.findText(text) == -1):
            self.cbb_filter_history.insertItem(0, text)
            self.cbb_filter_history.setCurrentIndex(0)
        self.select_table_row(0)

    def cbb_filter_history_textActivated(self, text):
        self.le_filter.setText(text)

    def cb_filter_regex_stateChanged(self):
        self.b_filter_rehelp.setEnabled(self.cb_filter_regex.isChecked())
        self.le_filter_textChanged()

    def b_filter_rehelp_clicked(self):
        msg=('In Regular Expressions some characters have special meaning.\n'
            '\n^\tstart of line'
            '\n$\tend of line'
            '\n.\tmatch any character'
            '\nA*\t0 or more times of preceding char A'
            '\nB+\t1 or more times of preceding char B'
            '\nC?\tpreceding character C is optional'
            '\n[abc]\tmatch one of the chars from a set'
            '\nA|B\tmatch A or B'
            '\n\\d\tmatch any decimal digit'
            '\n\\w\tany alphanumeric char or underscore'
            '\n\\s\twhitespace char (space, tab, newline)'
            '\n(ABC)\tgroupig to use with other features'
            '\n\\.\tslash for literal char without effect'
            '\n\nThere are more rules and special characters to RegEx. This'
            ' is just a small subset. Enable RegEx first, otherwise the'
            ' filter will perform a literal text comparison only. Examples:'
            '\n\n^Super Mario'
            '\nStarts with "Super Mario".'
            '\n\n^$'
            '\nEmpty content.'
            '\n\nSuper M[ae].*\d?'
            '\nContains "Super M", followed by an "a" or "e" and optionally'
            ' a digit somewhere after.'
            '\n\n\./(Mods|Unreleased|Homebrew)/'
            '\nmatch literal "." dot character, followed by "/" and "Mods",'
            ' "Unreleased" or "Homebrew"'
            )
        msg_continue(msg, 'Information', 'RegEx Quick Help', None, True)

    def b_filter_clear_clicked(self):
        self.gamelist.clear_sort()
        self.cbb_filter_header.setCurrentIndex(0)
        self.le_filter.clear()
        self.cb_filter_regex.setChecked(False)
        self.cb_filter_case.setChecked(False)

    def set_filter_header(self, head):
        headid = self.gamelist.get_header(head)
        if headid > -1:
            self.cbb_filter_header.setCurrentIndex(headid + 1)

    def tb_toggle_editbox_clicked(self):
        if self.f_editbox.isVisible():
            self.disable_editbox()
        else:
            self.enable_editbox()

    def enable_editbox(self):
        self.f_editbox.setVisible(True)
        self.tb_toggle_editbox.setArrowType(QtCore.Qt.ArrowType.DownArrow)
        self.update_editbox()
        if G.settings['no_table_edit']:
            self.gamelist.disable_edit()  # edit in box only

    def disable_editbox(self):
        self.f_editbox.setVisible(False)
        self.tb_toggle_editbox.setArrowType(QtCore.Qt.ArrowType.UpArrow)
        if not G.settings['no_table_edit']:
            self.gamelist.enable_edit() # edit in table only

    def b_edit_delete_clicked(self):
        mindex = self.gamelist.get_selected_mindex()
        if mindex:
            row = self.gamelist.get_data_index(mindex)
            name = mindex.data(self.gamelist.get_header('name'))
            proceed = True
            if not self.gamelist.is_unsaved():
                msg = ('Delete game:'
                      f'\n\n{row + 1}. {name}'
                      '\n\nRemoving an entire game entry cannot be reverted.'
                      ' Proceed only, if you are 100% sure to discard the'
                      ' selected row.'
                      '\nIf you accept, this message will not appear again'
                      ' until next import or export.'
                      '\n\nDo you want continue?')
                if not msg_continue(msg, 'Warning', parent=self):
                    proceed = False
            if proceed:
                self.gamelist.remove(row)
                self.update_editbox()

    def b_edit_duplicate_clicked(self):
        mindex = self.gamelist.get_selected_mindex()
        if mindex:
            row = self.gamelist.get_data_index(mindex)
            if not self.gamelist.is_unsaved():
                msg = ('New copy of a game.'
                      f'\n\n{row + 1}. {mindex.data(0)[:48]}'
                      '\n\nActive sorting prevents automatic selection of new'
                      ' game entry. Therefore each time a new game is copied,'
                      ' the current tables sort order will be cleared.'
                      '\nThis message will not appear again until next import'
                      ' or export.')
                msg_continue(msg, 'Information', parent=self)
            new = self.gamelist.duplicate(row, G.settings['ignore_copy'])
            filter_backup = self.le_filter.text()
            self.le_filter.clear()
            self.gamelist.clear_sort()
            self.gamelist.view.selectRow(new.row())
            self.le_filter.setText(filter_backup)
            self.update_editbox()

    def b_edit_new_clicked(self):
        if not self.gamelist.is_unsaved():
            msg = ('New empty game added.'
                  f'\n\n{len(self.gamelist.model.data) + 1}.'
                  '\n\nActive filter and sorting prevents automatic selection'
                  ' of new game entry. Therefore each time a new game is'
                  ' added, the current tables filter pattern and sort order'
                  ' will be cleared.'
                  '\nThis message will not appear again until next import'
                  ' or export.')
            msg_continue(msg, 'Information', parent=self)
        new = self.gamelist.insert()
        self.le_filter.clear()
        self.gamelist.clear_sort()
        self.gamelist.view.selectRow(new.row())
        self.update_editbox()

    def b_edit_prevgame_clicked(self):
        mindex = self.gamelist.get_selected_mindex()
        if mindex:
            self.gamelist.view.selectRow(mindex.row() - 1)
        else:
            self.gamelist.view.selectRow(0)

    def b_edit_nextgame_clicked(self):
        mindex = self.gamelist.get_selected_mindex()
        if mindex:
            self.gamelist.view.selectRow(mindex.row() + 1)
        else:
            self.gamelist.view.selectRow(0)

    def lock_controls(self, locklist):
        for hidden in locklist:
            for control_var in self.editbox_vars[hidden]:
                if control_var:
                    control_var.setEnabled(False)

    def hide_header_and_controls(self, hidelist):
        # BUG  after making certain controls invisible, the vertical space is
        # wrong. setParent to None will solve the issue, but the code is ugly.
        for hidden in self.gamelist.hide_header(hidelist):
            for control_var in self.editbox_vars[hidden]:
                if control_var:
                    control_var.setParent(None)
                    control_var.setVisible(False)

        if ('id' in hidelist
        and 'source' in hidelist):
            self.hbl_idsource.setParent(None)

        elif ('developer' in hidelist
        and 'publisher' in hidelist):
            self.hbl_devpub.setParent(None)

        elif ('releasedate' in hidelist
        and 'genre' in hidelist):
            self.hbl_relgen.setParent(None)

        elif ('playcount' in hidelist
        and 'lastplayed' in hidelist):
            self.hbl_countlast.setParent(None)

        elif ('players' in hidelist
        and 'rating' in hidelist):
            self.hbl_playrating.setParent(None)

        elif ('favorite' in hidelist
        and 'hidden' in hidelist
        and 'kidgame' in hidelist):
            self.hbl_favhikid.setParent(None)

    def set_header_sizes(self, resizedict):
        for head, size in resizedict.items():
            headid = self.gamelist.get_header(head)
            if headid > -1:
                self.gamelist.resize_header(headid, size)

    def get_index_data_byselection(self):
        mindex = self.gamelist.get_selected_mindex()
        if mindex:
            index = self.gamelist.get_data_index(mindex)
            data = self.gamelist.model.data[index]
            return index, data
        else:
            return None, None

    def add_query(self, data, head, quote=True, maxlen=40):
        text = data[self.gamelist.model.header[head]]
        text = text.replace('"', '').strip()
        if head == 'image':
            # Get folder name of image file.
            path = pathlib.PurePath(text).parent.stem
            text = path if path else ''
        if not text == '':
            if len(text) > maxlen:
                text = text[:maxlen]
            text = text.replace('\n', ' ')
            return f' "{text}"' if quote else f' {text}'
        else:
            return ''

    def add_urlquery_source(self, data):
        url = ''
        query = ''
        id = data[self.gamelist.model.header['id']]
        source = data[self.gamelist.model.header['source']]
        if not id == '' and not source == '':
            if source == 'adb.arcadeitalia.net':
                url = 'http://adb.arcadeitalia.net/dettaglio_mame.php?'
                query = f'game_name={id}'
            elif (source == 'screenscraper.fr'
            or 'screenscraper' in source.lower()):
                url = 'https://www.screenscraper.fr/gameinfos.php?'
                query = 'action=changelangue&langue=en'
                query += '&gameid='
                query += id
        return url + query

    def tb_search_source_clicked(self):
        index, data = self.get_index_data_byselection()
        if index is not None:
            urlquery = self.add_urlquery_source(data)
            if not urlquery == '':
                webbrowser.open_new_tab(urlquery)
        self.tb_search_source.setChecked(False)

    def tb_search_web_clicked(self):
        url = 'https://duckduckgo.com/?q='
        index, data = self.get_index_data_byselection()
        if index is not None:
            query = ''
            query += self.add_query(data, 'image')
            query += self.add_query(data, 'name')
            query += self.add_query(data, 'developer')
            query += self.add_query(data, 'publisher')
            #query += self.add_query(data, 'desc', False)
            query = urllib.parse.quote(query.strip())
            webbrowser.open_new_tab(url + query)
        self.tb_search_web.setChecked(False)

    def tb_search_video_clicked(self):
        url = 'https://www.youtube.com/results?search_query='
        index, data = self.get_index_data_byselection()
        if index is not None:
            query = 'emulation'
            query += self.add_query(data, 'image')
            query += self.add_query(data, 'name')
            query = urllib.parse.quote(query.strip())
            webbrowser.open_new_tab(url + query)
        self.tb_search_video.setChecked(False)

    def tb_search_wiki_clicked(self):
        url = 'https://en.wikipedia.org/w/index.php?search='
        index, data = self.get_index_data_byselection()
        if index is not None:
            query = ''
            query += self.add_query(data, 'name')
            query = urllib.parse.quote(query.strip())
            webbrowser.open_new_tab(url + query)
        self.tb_search_wiki.setChecked(False)

    def tb_search_games_clicked(self):
        url = 'https://www.mobygames.com/search/quick?q='
        url_tail = '&search=Go&sFilter=1&sG=on'  # games only
        index, data = self.get_index_data_byselection()
        if index is not None:
            query = ''
            query += self.add_query(data, 'name')
            query = urllib.parse.quote(query.strip())
            webbrowser.open_new_tab(url + query + url_tail)
        self.tb_search_games.setChecked(False)

    def tb_search_emulation_clicked(self):
        url = 'https://retropie.org.uk/forum/search?term='
        url_tail =('&in=titlesposts&matchWords=all&sortBy=relevance'
                  '&sortDirection=desc&showAs=posts&categories[]=2')
        index, data = self.get_index_data_byselection()
        if index is not None:
            query = ''
            query += self.add_query(data, 'name')
            query = urllib.parse.quote(query.strip())
            webbrowser.open_new_tab(url + query + url_tail)
        self.tb_search_emulation.setChecked(False)

    def tb_search_romhacks_clicked(self):
        url = 'https://duckduckgo.com/?q='
        url_tail = ('+site=https://www.romhacking.net/games/'
                   ' +inurl:romhacking.net/games')
        index, data = self.get_index_data_byselection()
        if index is not None:
            query = ''
            query += self.add_query(data, 'image', False)
            query += self.add_query(data, 'name', False)
            query += self.add_query(data, 'developer', False)
            query = urllib.parse.quote(query.strip())
            webbrowser.open_new_tab(url + query + url_tail)
        self.tb_search_romhacks.setChecked(False)

    # EXPORT TAB
    def tb_export_filedialog_clicked(self):
        file = dialog_choose_file('Choose a gamelist XML file',
                                  '*.xml', 'Save')
        if file:
            self.set_le_export_file(file)

    def rename_le_export_file_ext(self, ext):
        file = self.le_export_file.text()
        if file == '/dev/null/':
            pass
        elif not file == '':
            try:
                path = pathlib.PurePath(file).with_suffix('')
                path = path.with_suffix(ext)
            except ValueError:
                path = pathlib.PurePath(file)
            if self.rb_export_format_cfg.isChecked():
                name = path.name
                startswith_custom = bool(name.startswith('custom-'))
                if not startswith_custom:
                    name = 'custom-' + name
                    path = path.with_name(name)
                if self.le_export_startswith_custom is None:
                    self.le_export_startswith_custom = startswith_custom
            elif self.le_export_startswith_custom == False:
                name = path.name
                startswith_custom = bool(name.startswith('custom-'))
                if startswith_custom:
                    name = name.replace('custom-', '')
                    path = path.with_name(name)
            self.le_export_file.setText(str(path))

    def rb_export_format_toggled(self):
        self.set_l_export_available()

    def rb_export_format_toggled_cfg(self):
        self.enable_widgets_cfg(not self.rb_export_format_cfg.isChecked())
        self.rb_export_format_toggled()

    def rb_export_format_toggled_csv(self):
        self.enable_widgets_csv(not self.rb_export_format_csv.isChecked())
        self.rb_export_format_toggled()

    def set_l_export_available(self):
        if self.rb_export_format_xml.isChecked():
            x = self.rb_export_format_xml.x()
            text = 'gamelist.xml: import and export (complete)'
        elif self.rb_export_format_json.isChecked():
            x = self.rb_export_format_json.x()
            text = 'universal data exchange: export only (complete)'
        elif self.rb_export_format_csv.isChecked():
            x = self.rb_export_format_csv.x()
            text = 'table database: export only (limited to game data)'
        elif self.rb_export_format_txt.isChecked():
            x = self.rb_export_format_txt.x()
            text = 'unstructured text: export only (limited to game data)'
        elif self.rb_export_format_cfg.isChecked():
            x = self.rb_export_format_cfg.x()
            text = 'custom-collection: export only (limited to path tag)'
        else:
            text = ''
        self.l_export_available_space.setFixedWidth(x - (16 if x > 0 else 0))
        self.l_export_available.setText(text)

    def rb_export_format_clicked(self):
        if self.rb_export_format_xml.isChecked():
            self.rename_le_export_file_ext('.xml')
            self.set_export_indent()
        elif self.rb_export_format_json.isChecked():
            self.rename_le_export_file_ext('.json')
            self.set_export_indent()
        elif self.rb_export_format_csv.isChecked():
            self.rename_le_export_file_ext('.csv')
            self.cb_export_indent.setChecked(False)
        elif self.rb_export_format_txt.isChecked():
            self.rename_le_export_file_ext('.txt')
            self.set_export_indent()
        elif self.rb_export_format_cfg.isChecked():
            self.rename_le_export_file_ext('.cfg')
            self.cb_export_exclude.setChecked(False)
            self.cb_export_exclude_unsupptags.setChecked(False)
            self.cb_export_indent.setChecked(False)

    def enable_widgets(self, enable):
        self.cb_export_exclude.setEnabled(enable)
        self.f_export_exclude.setEnabled(enable)
        self.cb_export_exclude_unsupptags.setEnabled(enable)
        self.cb_export_keep_empty.setEnabled(enable)
        self.cb_export_indent.setEnabled(enable)
        self.f_export_indent.setEnabled(enable)

    def enable_widgets_cfg(self, enable):
        self.cb_export_exclude.setEnabled(enable)
        self.f_export_exclude.setEnabled(enable)
        self.cb_export_exclude_unsupptags.setEnabled(enable)
        self.cb_export_keep_empty.setEnabled(enable)
        self.cb_export_indent.setEnabled(enable)
        self.f_export_indent.setEnabled(enable)

    def enable_widgets_csv(self, enable):
        self.cb_export_indent.setEnabled(enable)
        self.f_export_indent.setEnabled(enable)

    def set_export_indent(self):
        if G.settings['indent'] is not None:
            self.cb_export_indent.setChecked(True)
            self.cb_export_indent_stateChanged(True)
        else:
            self.cb_export_indent.setChecked(False)
            self.cb_export_indent_stateChanged(False)

    def set_export_format(self, file=None):
        if file is None:
            file = self.le_export_file.text()
        path = pathlib.PurePath(file)
        if G.settings['export_format']:
            format = G.settings['export_format']
        else:
            format = path.suffix.lower().replace('.', '')
        if format == 'xml':
            self.rb_export_format_xml.setChecked(True)
        elif format == 'json':
            self.rb_export_format_json.setChecked(True)
        elif format == 'csv':
            self.rb_export_format_csv.setChecked(True)
        elif format == 'txt':
            self.rb_export_format_txt.setChecked(True)
        elif format == 'cfg':
            self.rb_export_format_cfg.setChecked(True)

    def allow_export(self, file=None):
        if file is None:
            file = self.le_export_file.text()
        file = normalize_path(file.strip())
        allow = file != '' and self.l_current_file.text() != ''
        self.set_export_format(file)
        return allow

    def set_le_export_file(self, text):
        self.le_export_file.setText(str(text))

    def le_export_file_textChanged(self, text):
        self.dbb_export_buttons.setEnabled(self.allow_export(text))
        self.cb_export_sameasopen.setChecked(bool(self.sameasopen(text)))

    def le_export_file_returnPressed(self):
        self.export_file()

    def le_export_file_editingFinished(self):
        self.le_export_startswith_custom = None

    def build_export_exclude(self):
        export_exclude_list = []
        if self.cb_export_exclude.checkState():
            if self.cb_export_exclude_id.checkState():
                export_exclude_list.append('id')
            if self.cb_export_exclude_source.checkState():
                export_exclude_list.append('source')
            if self.cb_export_exclude_name.checkState():
                export_exclude_list.append('name')
            if self.cb_export_exclude_sortname.checkState():
                export_exclude_list.append('sortname')
            if self.cb_export_exclude_desc.checkState():
                export_exclude_list.append('desc')
            if self.cb_export_exclude_developer.checkState():
                export_exclude_list.append('developer')
            if self.cb_export_exclude_publisher.checkState():
                export_exclude_list.append('publisher')
            if self.cb_export_exclude_releasedate.checkState():
                export_exclude_list.append('releasedate')
            if self.cb_export_exclude_genre.checkState():
                export_exclude_list.append('genre')
            if self.cb_export_exclude_path.checkState():
                export_exclude_list.append('path')
            if self.cb_export_exclude_thumbnail.checkState():
                export_exclude_list.append('thumbnail')
            if self.cb_export_exclude_image.checkState():
                export_exclude_list.append('image')
            if self.cb_export_exclude_marquee.checkState():
                export_exclude_list.append('marquee')
            if self.cb_export_exclude_video.checkState():
                export_exclude_list.append('video')
            if self.cb_export_exclude_players.checkState():
                export_exclude_list.append('players')
            if self.cb_export_exclude_rating.checkState():
                export_exclude_list.append('rating')
            if self.cb_export_exclude_favorite.checkState():
                export_exclude_list.append('favorite')
            if self.cb_export_exclude_hidden.checkState():
                export_exclude_list.append('hidden')
            if self.cb_export_exclude_kidgame.checkState():
                export_exclude_list.append('kidgame')
            if self.cb_export_exclude_lastplayed.checkState():
                export_exclude_list.append('lastplayed')
            if self.cb_export_exclude_playcount.checkState():
                export_exclude_list.append('playcount')
        return export_exclude_list

    def b_export_indent_zero_clicked(self):
        self.sb_export_indent.setValue(0)

    def b_export_indent_four_clicked(self):
        self.sb_export_indent.setValue(4)

    def dbb_export_buttons_clicked(self, button):
        role = self.dbb_export_buttons.buttonRole(button)
        if role == 0:  # AcceptRole
            self.export_file()

    def get_remove_empty(self):
        return not self.cb_export_keep_empty.isChecked()

    def export_file(self):
        proceed = (bool(self.le_export_file.text())
                  and bool(self.l_current_file.text()))
        if proceed and self.cb_export_sameasopen.isChecked():
            if G.settings['no_same'] is not None:
                msg = ('Warning!'
                      '\n-E or --no-same option in effect, cannot overwrite'
                      ' same file from input, choose a different filename')
                msg_continue(msg, 'Information', parent=self)
                proceed = False
            else:
                msg = ('Attention, potential data loss!'
                      '\nThe export file is the same as currently open imported'
                      ' file. If you continue, the file on disk will be replaced'
                      ' and overwritten by the new edited file.'
                      '\n\nDo you want continue?')
                if msg_continue(msg, 'Warning', parent=self):
                    proceed = True
                else:
                    proceed = False

        if proceed:
            self.l_current_file.setVisible(False)
            self.pb_file_progress.reset()
            self.pb_file_progress.setVisible(True)
            self.dbb_export_buttons.setEnabled(False)

            if self.cb_export_applyfilter.isChecked():
                data = self.gamelist.get_filtered_tabledata()
            else:
                data = self.gamelist.get_data()
            file = get_path(self.le_export_file.text().strip())
            exclude = self.build_export_exclude()
            empty = self.get_remove_empty()
            exunsupptags = self.cb_export_exclude_unsupptags.isChecked()
            progress = self.pb_file_progress
            if self.cb_export_indent.isChecked():
                indent = int(self.sb_export_indent.cleanText())
            else:
                indent = None

            if self.rb_export_format_xml.isChecked():
                success = self.export_xml(
                                data, file, exclude, exunsupptags, empty,
                                progress, indent)
            elif self.rb_export_format_json.isChecked():
                success = self.export_json(
                                data, file, exclude, exunsupptags, empty,
                                progress, indent)
            elif self.rb_export_format_csv.isChecked():
                success = self.export_csv(
                                data, file, exclude, exunsupptags, empty,
                                progress)
            elif self.rb_export_format_txt.isChecked():
                success = self.export_txt(
                                data, file, exclude, exunsupptags, empty,
                                progress, indent)
            elif self.rb_export_format_cfg.isChecked():
                success = self.export_cfg(
                                data, file, progress)

            if success:
                self.gamelist.reset_unsaved()
                msg_stderr(f'File successfully exported: {str(file)}')
                G.settings['EOT_action_file'] = file
                if G.settings['export_open']:
                    run_with_default_app(G.settings['EOT_action_file'])

            self.pb_file_progress.setVisible(False)
            self.l_current_file.setVisible(True)
            self.dbb_export_buttons.setEnabled(True)

    def export_xml(self, data, file, export_exclude, exclude_unsupptags,
                   remove_empty, progress, indent):
        proceed = True
        try:
            ElementTree.parse(file)
        except ElementTree.ParseError:
            msg = ('You are about to overwrite and replace a non XML file:'
                  f' {str(file)}'
                  '\n\nDo you want continue?')
            if not msg_continue(msg, 'Warning', 'Export', self):
                proceed = False
        except Exception:
            pass

        if proceed:
            xml_data = self.gamelist.data_to_xml(data,
                                                 export_exclude,
                                                 exclude_unsupptags,
                                                 remove_empty,
                                                 progress,
                                                 indent=indent)
            try:
                if G.settings['export'] == '/dev/null/':
                    sys.stdout.write(
                        self.gamelist.xml_to_string(xml_data, indent))
                else:
                    self.gamelist.xml_write(xml_data, file)
            except PermissionError:
                msg_show_error(f'Error! No permission to access: {str(file)}',
                               'Critical')
            except IsADirectoryError:
                msg_show_error(f'Error! Path is a directory: {str(file)}',
                               'Critical')
            except OSError:
                msg_show_error(f'Error! File cannot be saved: {str(file)}',
                               'Critical')
            else:
                if file and file.exists():
                    return True
        return False

    def export_json(self, data, file, export_exclude, exclude_unsupptags,
                    remove_empty, progress, indent):
        json_data = self.gamelist.data_to_json(data,
                                               export_exclude,
                                               exclude_unsupptags,
                                               remove_empty,
                                               progress,
                                               indent=indent)
        try:
            if G.settings['export'] == '/dev/null/':
                sys.stdout.write(str(json_data) + '\n')
            else:
                self.gamelist.json_write(json_data, file)
        except PermissionError:
         msg_show_error(f'Error! No permission to access: {str(file)}',
                        'Critical')
        except IsADirectoryError:
            msg_show_error(f'Error! Path is a directory: {str(file)}',
                           'Critical')
        except OSError:
            msg_show_error(f'Error! File cannot be saved: {str(file)}',
                           'Critical')
        else:
            if file and file.exists():
                return True
        return False

    def export_csv(self, data, file, export_exclude, exclude_unsupptags,
                   remove_empty, progress):
        csv_data, header = self.gamelist.data_to_csv(data,
                                                     export_exclude,
                                                     exclude_unsupptags,
                                                     remove_empty,
                                                     progress)
        try:
            if G.settings['export'] == '/dev/null/':
                self.gamelist.csv_write_stdout(csv_data, header)
            else:
                self.gamelist.csv_write(csv_data, file, header)
        except PermissionError:
         msg_show_error(f'Error! No permission to access: {str(file)}',
                        'Critical')
        except IsADirectoryError:
            msg_show_error(f'Error! Path is a directory: {str(file)}',
                           'Critical')
        except OSError:
            msg_show_error(f'Error! File cannot be saved: {str(file)}',
                           'Critical')
        else:
            if file and file.exists():
                return True
        return False

    def export_txt(self, data, file, export_exclude, exclude_unsupptags,
                   remove_empty, progress, indent):
        txt_data= self.gamelist.data_to_txt(data,
                                            export_exclude,
                                            exclude_unsupptags,
                                            remove_empty,
                                            progress,
                                            indent=indent)
        try:
            if G.settings['export'] == '/dev/null/':
                sys.stdout.write('\n'.join(txt_data) + '\n')
            else:
                self.gamelist.txt_write(txt_data, file)
        except PermissionError:
         msg_show_error(f'Error! No permission to access: {str(file)}',
                        'Critical')
        except IsADirectoryError:
            msg_show_error(f'Error! Path is a directory: {str(file)}',
                           'Critical')
        except OSError:
            msg_show_error(f'Error! File cannot be saved: {str(file)}',
                           'Critical')
        else:
            if file and file.exists():
                return True
        return False

    def export_cfg(self, data, file, progress):
        cfg_data = self.gamelist.data_to_cfg(data,
                                             progress)
        try:
            if G.settings['export'] == '/dev/null/':
                sys.stdout.write('\n'.join(cfg_data) + '\n')
            else:
                self.gamelist.cfg_write(cfg_data, file)
        except PermissionError:
         msg_show_error(f'Error! No permission to access: {str(file)}',
                        'Critical')
        except IsADirectoryError:
            msg_show_error(f'Error! Path is a directory: {str(file)}',
                           'Critical')
        except OSError:
            msg_show_error(f'Error! File cannot be saved: {str(file)}',
                           'Critical')
        else:
            if file and file.exists():
                return True
        return False

    def cb_export_sameasopen_clicked(self, checked):
        export_file = self.sameasopen(self.le_export_file.text())
        same = bool(export_file)
        ext = G.settings['no_same']
        if ext is None or ext == '':
            file = pathlib.PurePath(G.settings['import'])
            ext = '_export' + file.suffix
        if checked:
            if same:
                text = str(export_file.with_suffix('')) + ext
            else:
                text = self.l_current_file.text()
            self.le_export_file.setText(text)
        else:
            if same:
                text = str(export_file.with_suffix('')) + ext
                self.le_export_file.setText(text)

    def sameasopen(self, file):
        open_file = get_path(self.l_current_file.text(), False)
        other_file = get_path(file)
        if type(other_file) is pathlib.PosixPath:
            try:
                same = other_file.samefile(open_file)
            except Exception:
                same = False
        else:
            same = False
        return other_file if same else None

    def set_export_exclude_checkbox(self, checkbox, state):
        checkbox.setChecked(state)
        if state:
            style = ('color: grey;'
                    'font-style: italic;'
                    'text-decoration: line-through;')
        else:
            style = ('font-style: normal;'
                    'text-decoration: none;')
        checkbox.setStyleSheet(style)

    def export_exclude_init(self, exclude_list):
        for checkbox in self.export_exclude_vars:
            if checkbox.text() in exclude_list:
                self.set_export_exclude_checkbox(checkbox, True)

    def cb_export_exclude_stateChanged(self, state):
        self.f_export_exclude.setVisible(state)
        self.l_export_exclude_more.setVisible(state)

    def b_export_exclude_invert_clicked(self):
        for checkbox in self.export_exclude_vars:
            self.set_export_exclude_checkbox(checkbox,
                                             not checkbox.checkState())

    def b_export_exclude_all_clicked(self):
        for checkbox in self.export_exclude_vars:
            self.set_export_exclude_checkbox(checkbox, True)

    def b_export_exclude_none_clicked(self):
        for checkbox in self.export_exclude_vars:
            self.set_export_exclude_checkbox(checkbox, False)

    def cb_export_exclude_id_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_id, button)

    def cb_export_exclude_source_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_source, button)

    def cb_export_exclude_name_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_name, button)

    def cb_export_exclude_sortname_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_sortname, button)

    def cb_export_exclude_desc_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_desc, button)

    def cb_export_exclude_developer_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_developer, button)

    def cb_export_exclude_publisher_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_publisher, button)

    def cb_export_exclude_releasedate_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_releasedate, button)

    def cb_export_exclude_genre_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_genre, button)

    def cb_export_exclude_path_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_path, button)

    def cb_export_exclude_thumbnail_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_thumbnail, button)

    def cb_export_exclude_image_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_image, button)

    def cb_export_exclude_marquee_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_marquee, button)

    def cb_export_exclude_video_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_video, button)

    def cb_export_exclude_players_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_players, button)

    def cb_export_exclude_rating_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_rating, button)

    def cb_export_exclude_favorite_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_favorite, button)

    def cb_export_exclude_hidden_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_hidden, button)

    def cb_export_exclude_kidgame_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_kidgame, button)

    def cb_export_exclude_lastplayed_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_lastplayed, button)

    def cb_export_exclude_playcount_stateChanged(self, button):
        self.set_export_exclude_checkbox(self.cb_export_exclude_playcount, button)

    def cb_export_indent_stateChanged(self, state):
        self.f_export_indent.setVisible(state)
        self.l_export_indent_more.setVisible(state)
