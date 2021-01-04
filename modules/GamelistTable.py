#!/usr/bin/python3

import sys
import os
import xml.etree.ElementTree as ElementTree
import html
import json
import csv
import copy

from PyQt5 import QtWidgets, QtCore, QtGui
import xmltodict

from modules.dialogs import *


class GamelistTableModel(QtCore.QAbstractTableModel):
    """    """
    def __init__(self, file, tags, progress):
        super(GamelistTableModel, self).__init__()
        # data structure from parsed XML file or ElementTree object,
        # header dict with fullset of name:id pairs,
        # file path of parsed XML from filesystem
        (self.data,
         self.header,
         self.unsupptags,
         self.otherdata,
         self.folders,
         self.file) = self.load(file, tags, progress)
        # original data is the unaltered copy of data, for quick and easy
        # revert possibility
        self._original_data = copy.deepcopy(self.data)
        # name of protected headers
        self.locked_columns = []
        # mod_flag_role is used in data as DecorationRole, should be updated
        # later to something like QtGui.QColor('yellow'), None to disable
        self.mod_flag_role = None

    def removeRows(self, position, rows=1, index=QtCore.QModelIndex()):
        self.beginRemoveRows(index, position, position + rows - 1)
        self.data.pop(position)
        self._original_data.pop(position)
        self.unsupptags.pop(position)
        self.endRemoveRows()
        #return True
        return position

    def duplicateRows(self, source_row, ignore,
                      position, rows=1, index=QtCore.QModelIndex()):
        self.beginInsertRows(index, position, position + rows - 1)
        new_row = copy.deepcopy(self.data[source_row])
        orig_row = copy.deepcopy(new_row)
        unsupptags_row = copy.deepcopy(self.unsupptags[source_row])

        header_keys = self.header.keys()
        for head in ignore:
            if head in header_keys:
                head_id = self.header[head]
                new_row[head_id] = ''
                orig_row[head_id] = ''

        self.data.append(new_row)
        self._original_data.append(orig_row)
        self.unsupptags.append(unsupptags_row)
        self.endInsertRows()
        #return True
        return QtCore.QVariant(len(self.data) - 1)

    def insertRows(self, position, rows=1, index=QtCore.QModelIndex()):
        self.beginInsertRows(index, position, position + rows - 1)
        empty_game = []
        for _ in self.header.keys():
            empty_game.append('')
        self.data.append(empty_game)
        self._original_data.append(empty_game)
        self.unsupptags.append(empty_game)
        self.endInsertRows()
        #return True
        return QtCore.QVariant(len(self.data) - 1)

    def rowCount(self, index):
        return len(self.data)

    def columnCount(self, index):
        try:
            return len(self.data[0])
        except IndexError:
            return 0

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if (orientation == QtCore.Qt.Horizontal
        and role == QtCore.Qt.DisplayRole):
            keys = self.header.keys()
            return list(keys)[section]

        if (orientation == QtCore.Qt.Vertical
        and role == QtCore.Qt.DisplayRole):
            return section + 1

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            row = self.data[index.row()]
            return row[index.column()]

        if role == QtCore.Qt.EditRole:
            row = self.data[index.row()]
            return row[index.column()]

        if role == QtCore.Qt.FontRole:
            row = index.row()
            column = index.column()
            if not self.data[row][column] == self._original_data[row][column]:
                font = QtGui.QFont()
                font.setItalic(True)
                return font
            else:
                return None

        if role == QtCore.Qt.DecorationRole:
            if self.mod_flag_role:
                row = index.row()
                column = index.column()
                if not self.data[row][column] == self._original_data[row][column]:
                    return self.mod_flag_role
                else:
                    return None

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            row = index.row()
            column = index.column()
            self.data[row][column] = value
            return True

        if role == QtCore.Qt.DecorationRole:
            row = index.row()
            column = index.column()
            if self.data[row][column] == self._original_data[row][column]:
                return QtGui.QColor('black')
            else:
                return QtGui.QColor('red')

    def is_edited(self):
        return not self.data == self._original_data

    def is_edited_row(self, index):
        return not self.data[index] == self._original_data[index]

    def is_edited_cell(self, index, hindex):
        return not self.data[index][hindex] == self._original_data[index][hindex]

    def append_locked_columns(self, head):
        if not head in self.locked_columns:
            self.locked_columns.append(head)

    def remove_locked_columns(self, head):
        if head in self.locked_columns:
            self.locked_columns.remove(head)

    def flags(self, index):
        if index.column() in self.locked_columns:
            return QtCore.Qt.ItemIsSelectable
        else:
            return (QtCore.Qt.ItemIsEditable
                    | QtCore.Qt.ItemIsEnabled
                    | QtCore.Qt.ItemIsSelectable)

    def load(self,
             xml,
             tags,
             progress):

        data = []
        unsupptags = []
        header_list = [
            'name', 'sortname', 'desc',
            'developer', 'publisher', 'releasedate', 'players',
            'path', 'thumbnail', 'image', 'marquee', 'video',
            'genre', 'rating',
            'favorite', 'hidden', 'kidgame',
            'lastplayed', 'playcount',
            'id', 'source'
        ]
        if tags:
            new_order = []
            # Validate user tag.
            for tag in tags:
                if (tag in header_list
                and tag not in new_order):
                    new_order.append(tag)
            # Remove from default list, so user list can appear in front.
            for tag in new_order:
                if tag in header_list:
                    header_list.remove(tag)
            header_list = new_order + header_list
        header = {key: val for val, key in enumerate(header_list)}
        folders = None
        otherdata = []

        # Path file to open
        if (isinstance(xml, os.PathLike)
        or os.path.exists(xml)):  # and xml.exists():
            try:
                file = xml
                xml = ElementTree.parse(xml).getroot()
            except FileNotFoundError as error:
                msg = f'Error! Could not find file: {str(file)}'
                msg_show_error(msg, 'Critical')
                xml = file = None
            except IsADirectoryError as error:
                msg = f'Error! Path is a directory: {str(file)}'
                msg_show_error(msg, 'Critical')
                xml = file = None
            except ElementTree.ParseError as error:
                msg = ('Error! Could not parse gamelist XML file '
                       f'{str(error.position)}: {str(file)}')
                msg_show_error(msg, 'Critical')
                xml = file = None
        else:
            file = None
        # Continue loading data if its a XML root element
        if isinstance(xml, ElementTree.Element):
            for tag in xml.iterfind('*'):
                if (not tag.tag == 'game'
                and not tag.tag == 'folder'):
                    otherdata.append(tag)
            folders = xml.findall('folder')
            all_games = xml.findall('game')
            progress.setRange(0, len(all_games))
            for count, game in enumerate(all_games, 1):
                game_data = {key: '' for key in header.keys()}
                game_data['id'] = html.unescape(game.get('id', ''))
                game_data['source'] = html.unescape(game.get('source', ''))
                unsupp = []
                for tagname in game.iter():
                    if not tagname.tag == 'game':
                        text = game.find(tagname.tag)
                        if text is None:
                            game_data[tagname.tag] = ''
                        elif tagname.tag not in header_list:
                            unsupp.append(text)
                        else:
                            text = text.text
                            if text is not None:
                                text = html.unescape(text)
                            game_data[tagname.tag] = text
                data.append(list(game_data.values()))
                unsupptags.append(unsupp)
                progress.setValue(count)
        return data, header, unsupptags, otherdata, folders, file

class GamelistTable():
    """    """
    instances = 0

    def __init__(self, file, table, parent, tags, progress):
        # Keep track of how many gamelists exist.
        self.__class__.instances += 1
        # Create the actual object.
        self.parent = parent
        self.model = GamelistTableModel(file, tags, progress)
        self.view = table
        self.proxy = QtCore.QSortFilterProxyModel()
        self.proxy.setSourceModel(self.model)
        self.view.setSortingEnabled(True)
        self.view.setModel(self.proxy)

        # self.view.horizontalHeader().setSectionsMovable(True)
        # self.view.horizontalHeader().setDragEnabled(True)
        # self.view.horizontalHeader().setDragDropMode(
        #        QtWidgets.QAbstractItemView.InternalMove)

        #self.model.rowsInserted.connect(
        #    self.model_rowsInserted)

        # commitData should be called whenever data is edited, which itself
        # will set self.unsaved to True.
        self.item_delegate = self.view.itemDelegate()
        self.item_delegate.commitData.connect(
            self.commitData)

        # unsaved should be set to True whenever data is changed,
        # set it back to False, when the file is successfully exported
        #   False=nothing changed, True=data changed and is unsaved
        self.unsaved = False

    def __del__(self):
        if self.__class__.instances:
            self.__class__.instances -= 1
            del self.model
            del self.view
            del self.proxy

    def commitData(self, editor):
        self.set_unsaved()
        self.view.model().layoutChanged.emit()

    def set_completer(self, widget, wordlist, FilterMode='MatchStartsWith'):
        completer = QtWidgets.QCompleter()
        completer.setCompletionMode(QtWidgets.QCompleter.UnfilteredPopupCompletion)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        completer.setCompletionRole(QtCore.Qt.DisplayRole)
        completer.setModelSorting(QtWidgets.QCompleter.CaseInsensitivelySortedModel)
        if FilterMode == 'MatchStartsWith':
            completer.setFilterMode(QtCore.Qt.MatchStartsWith)
        elif FilterMode == 'MatchContains':
            completer.setFilterMode(QtCore.Qt.MatchContains)
        elif FilterMode == 'MatchEndsWith':
            completer.setFilterMode(QtCore.Qt.MatchEndsWith)
        #completer.setModelSorting(QtWidgets.QCompleter.CaseInsensitivelySortedModel)
        if isinstance(wordlist, list):
            newwordlist = []
            for listinlist in wordlist:
                newwordlist.extend(self.get_wordlist(listinlist))
            wordlist = newwordlist
        if isinstance(wordlist, str):
            wordlist = self.get_wordlist(wordlist)
            completer.setCompletionMode(QtWidgets.QCompleter.InlineCompletion)
        wordlist = sorted(list(set(wordlist)))
        model = QtCore.QStringListModel(wordlist, completer)
        completer.setModel(model)
        widget.setCompleter(completer)

    def get_wordlist(self, header):
        head = self.model.header[header]
        wordlist = [row[head] for row in self.model.data]
        return filter(None, list(set(wordlist)))

    #def model_rowsInserted(self, parent, first, last):
    #    pass

    def get_display_row(self, index):
        """ Get header row of current filtered view row number in table.
            Example:
                index = self.gamelist.get_selected_mindex().row()
        """
        model = self.view.model()
        return model.headerData(index, QtCore.Qt.Vertical)

    def remove(self, row):
        self.model.removeRows(row, 1)
        self.commitData(self)
        return row

    def duplicate(self, row, ignore_header=[]):
        count = self.model.rowCount(QtCore.QModelIndex())
        new = self.model.duplicateRows(row, ignore_header, count)
        self.commitData(self)
        return self.model.index(new.value(), 0, QtCore.QModelIndex())

    def insert(self):
        count = self.model.rowCount(QtCore.QModelIndex())
        new = self.model.insertRows(count, 1)
        self.commitData(self)
        return self.model.index(new.value(), 0, QtCore.QModelIndex())

    def update_selected_row(self):
        for mindex in self.view.selectedIndexes():
            self.view.update(mindex)

    def get_data(self, index=None):
        if index is None:
            return self.model.data
        else:
            return self.model.data[index]

    def get_selected_mindex(self):
        QModelIndexes = self.view.selectedIndexes()
        return QModelIndexes[0] if QModelIndexes else None

    def get_all_selected_mindex(self):
        return self.view.selectedIndexes()

    def get_data_index(self, mindex):
        """ Get real index from data by QModelIndex."""
        return mindex.model().headerData(mindex.row(), QtCore.Qt.Vertical) - 1

    def get_filtered_tabledata(self):
        # Get model from current view.  Everything filtered in this model
        # is exactly what is filtered too.  Hidden columns are missing and
        # index numbers for rows does not match the real data from real model.
        table_model = self.view.model()

        filtered_data = []
        rowcount = table_model.rowCount(QtCore.QModelIndex())
        # Iterate over all rows from current filtered table view.  Catch the
        # index and get the data from real data.
        for rownum in range(rowcount):
            # Get QModelIndex of current filtered row.
            tableindex = table_model.index(rownum, 0, QtCore.QModelIndex())
            # Get QModelIndex of real data, including all hidden columns.
            dataindex = self.get_data_index(tableindex)
            # Get games list data from real data.
            filtered_data.append(self.model.data[dataindex])
        return filtered_data

    def xmltag_to_dict(self, tag):
        return xmltodict.parse(ElementTree.tostring(tag, encoding='unicode'))

    def xml_write(self, data, file):
        data.write(file, encoding='UTF-8', xml_declaration=True, method='xml')
        return file

    def xml_to_string(self, data, indent):
        xml_root = data.getroot()
        if indent is not None:
            self.xml_indent_root(xml_root, 0, indent)
            newline = ''
        else:
            newline = '\n'
        xml_root = ElementTree.tostring(xml_root, encoding='unicode')
        return xml_root + newline

    def xml_indent_root(self, element, level=0, indent=4):
        """
            https://effbot.org/zone/element-lib.htm#prettyprint
            2004 by Fredrik Lundh
        """
        spaces = indent * ' '
        i = '\n' + level * spaces
        if element:
            if not element.text or not element.text.strip():
                element.text = i + spaces
            if not element.tail or not element.tail.strip():
                element.tail = i
            for element in element:
                self.xml_indent_root(element, level + 1, indent)
            if not element.tail or not element.tail.strip():
                element.tail = i
        else:
            if level and (not element.tail or not element.tail.strip()):
                element.tail = i
        return element

    def data_to_xml(self,
                    data,
                    export_exclude,
                    exclude_unsupptags,
                    remove_empty,
                    progress,
                    indent):

        if not isinstance(data, list):
            raise TypeError('Invalid data in data_to_xml()', type(data))
        if data:
            progress.setRange(0, len(data))
        header_items = self.model.header.items()
        header_list = list(self.model.header.keys())
        unsupptags = [] if exclude_unsupptags else self.model.unsupptags
        folders = self.model.folders
        otherdata = self.model.otherdata

        root = '<gameList></gameList>'
        root = ElementTree.fromstring(root)
        for count, row in enumerate(data, 1):
            game_dict = {}

            for head, headid in header_items:
                if head in export_exclude:
                    continue
                cell = row[headid]
                if cell is None:
                    cell = ''
                if head in ['id', 'source']:
                    if not cell == '':
                        game_dict[head] = html.escape(cell)
                elif head in ['favorite', 'hidden', 'kidgame']:
                    if cell in ['true', 'false']:
                        game_dict[head] = cell
                elif not cell == '':
                    game_dict[head] = html.escape(cell)
                else:
                    game_dict[head] = ''

            if remove_empty is False:
                game = ElementTree.SubElement(root, 'game')
            elif remove_empty and game_dict:
                game = ElementTree.SubElement(root, 'game')
            elif unsupptags or folders:
                game = ElementTree.SubElement(root, 'game')

            if game_dict:
                for tag in header_list:
                    try:
                        cell = game_dict[tag]
                    except KeyError:
                        if remove_empty:
                            continue
                        elif tag in ['id', 'source']:
                            game.set(tag, '')
                        else:
                            ElementTree.SubElement(game, tag).text = ''
                    else:
                        if remove_empty and cell == '':
                            continue
                        elif tag in ['id', 'source']:
                            game.set(tag, cell)
                        else:
                            ElementTree.SubElement(game, tag).text = cell

            if unsupptags:
                for tag in unsupptags[count - 1]:
                    game.append(tag)
            progress.setValue(count)

        if not exclude_unsupptags:
            if folders:
                root.extend(folders)
            if otherdata:
                root.extend(otherdata)
        if indent is not None:
            self.xml_indent_root(root, 0, indent)
        return ElementTree.ElementTree(root)

    def json_write(self, data, file):
        with open(file, 'w') as jsonfile:
            jsonfile.write(data)
        return file

    def data_to_json(self,
                     data,
                     export_exclude,
                     exclude_unsupptags,
                     remove_empty,
                     progress,
                     indent):
        if not isinstance(data, list):
            raise TypeError('Invalid data in data_to_json()', type(data))
        if data:
            progress.setRange(0, len(data))
        header_items = self.model.header.items()
        header_list = list(self.model.header.keys())
        unsupptags = [] if exclude_unsupptags else self.model.unsupptags
        folders = self.model.folders
        otherdata = self.model.otherdata

        root = {'gameList': []}
        for count, row in enumerate(data, 1):
            game_dict = {}

            for head, headid in header_items:
                if head in export_exclude:
                    continue
                cell = row[headid]
                if cell is None:
                    cell = ''
                if head == 'id':
                    if not cell == '':
                        try:
                            cell = int(cell)
                        except ValueError:
                            pass
                        game_dict[head] = cell
                elif head == 'source':
                    if not cell == '':
                        game_dict[head] = cell
                elif head in ['favorite', 'hidden', 'kidgame']:
                    if cell == 'true':
                        game_dict[head] = True
                    elif cell == 'false':
                        game_dict[head] = False
                elif head in ['players', 'playcount']:
                    if not cell == '':
                        try:
                            cell = int(cell)
                        except ValueError:
                            pass
                        game_dict[head] = cell
                elif head == 'genre':
                    if not cell == '':
                        if '/' in cell:
                            cell = cell.split('/')
                            cell = [cell.strip() for cell in cell]
                        elif ',' in cell:
                            cell = cell.split(',')
                            cell = [cell.strip() for cell in cell]
                        game_dict[head] = cell
                elif head == 'rating':
                    if not cell == '':
                        try:
                            cell = float(cell)
                        except ValueError:
                            pass
                        game_dict[head] = cell
                elif cell is None:
                    game_dict[head] = ''
                elif not cell == '':
                    game_dict[head] = cell

            if (remove_empty
            and game_dict == {}
            and unsupptags == []
            and folders is None):
                progress.setValue(count)
                continue

            game = {}
            if game_dict:
                for tag in header_list:
                    try:
                        cell = game_dict[tag]
                    except KeyError:
                        if remove_empty:
                            continue
                        else:
                            game[tag] = ''
                    else:
                        if remove_empty and cell == '':
                            continue
                        else:
                            game[tag] = cell

            if unsupptags:
                for tag in unsupptags[count - 1]:
                    game.update(self.xmltag_to_dict(tag))

            root['gameList'].append(game)
            progress.setValue(count)

        if not exclude_unsupptags:
            if folders:
                for tag in folders:
                    root['gameList'].append(self.xmltag_to_dict(tag))
            if otherdata:
                for tag in otherdata:
                    root['gameList'].append(self.xmltag_to_dict(tag))
        return json.dumps(root, sort_keys=False, indent=indent)

    def csv_write(self, data, file, header):
        with open(file, 'w', newline='') as csvfile:
            csvwriter = csv.DictWriter(csvfile,
                                       fieldnames=header,
                                       restval='',
                                       extrasaction='ignore',
                                       dialect='excel')
            csvwriter.writeheader()
            csvwriter.writerows(data)
        return file

    def csv_write_stdout(self, data, header):
        csvwriter = csv.DictWriter(sys.stdout,
                                   fieldnames=header,
                                   restval='',
                                   extrasaction='ignore',
                                   dialect='excel')
        csvwriter.writeheader()
        csvwriter.writerows(data)
        return sys.stdout

    def data_to_csv(self,
                    data,
                    export_exclude,
                    exclude_unsupptags,
                    remove_empty,
                    progress):
        if not isinstance(data, list):
            raise TypeError('Invalid data in data_to_csv()', type(data))
        if data:
            progress.setRange(0, len(data))
        header_items = self.model.header.items()
        header_list = list(self.model.header.keys())
        unsupptags = [] if exclude_unsupptags else self.model.unsupptags

        root = []
        for count, row in enumerate(data, 1):
            game_dict = {}

            for head, headid in header_items:
                if head in export_exclude:
                    continue
                cell = row[headid]
                if cell is None:
                    game_dict[head] = ''
                elif not cell == '':
                    game_dict[head] = cell

            if unsupptags:
                for tag in unsupptags[count - 1]:
                    if tag.tag not in header_list:
                        header_list.append(tag.tag)
                    game_dict.update(self.xmltag_to_dict(tag))

            progress.setValue(count)
            if (remove_empty
            and game_dict == {}
            and unsupptags == []):
                continue

            root.append(game_dict)
        return root, header_list

    def txt_write(self, data, file):
        data = [str(line) + '\n' for line in data]
        with open(file, 'w', newline='') as txtfile:
            txtfile.writelines(data)
        return file

    def data_to_txt(self,
                    data,
                    export_exclude,
                    exclude_unsupptags,
                    remove_empty,
                    progress,
                    indent):
        if not isinstance(data, list):
            raise TypeError('Invalid data in data_to_txt()', type(data))
        if data:
            progress.setRange(0, len(data))
        header_items = self.model.header.items()
        header_list = list(self.model.header.keys())
        unsupptags = [] if exclude_unsupptags else self.model.unsupptags
        folders = self.model.folders

        if indent:
            indent = str(indent * '\n')
        else:
            indent = ''

        root = []
        for count, row in enumerate(data, 1):
            game_dict = {}

            for head, headid in header_items:
                if head in export_exclude:
                    continue

                cell = row[headid]
                if cell is None or cell == '':
                    game_dict[head] = ''
                else:
                    game_dict[head] = cell

            if (remove_empty
            and game_dict == {}
            and not unsupptags == {}):
                progress.setValue(count)
                continue

            if unsupptags:
                for tag in unsupptags[count - 1]:
                    if tag.tag not in header_list:
                        header_list.append(tag.tag)
                    game_dict.update(self.xmltag_to_dict(tag))

            game = []
            if game_dict:
                for tag in header_list:
                    try:
                        cell = game_dict[tag]
                    except KeyError:
                        if remove_empty:
                            continue
                        else:
                            game.append('')
                    else:
                        if remove_empty and cell == '':
                            continue
                        else:
                            game.append(str(cell))

            if indent and root and game:
                game[0] = indent + game[0]
            root.extend(game)
            progress.setValue(count)
        return root

    def cfg_write(self, data, file):
        data = [str(line) + '\n' for line in data]
        with open(file, 'w', newline='') as cfgfile:
            cfgfile.writelines(data)
        return file

    def data_to_cfg(self,
                    data,
                    progress):
        if not isinstance(data, list):
            raise TypeError('Invalid data in data_to_cfg()', type(data))
        if data:
            progress.setRange(0, len(data))
        headid = self.get_header('path')

        root = []
        for count, row in enumerate(data, 1):
            if not row[headid] == '' and not row[headid] is None:
                root.append(row[headid])
            progress.setValue(count)
        return root

    def is_unsaved(self):
        return self.unsaved

    def set_unsaved(self):
        self.unsaved = True
        self.parent.setWindowModified(True)

    def reset_unsaved(self):
        self.unsaved = False
        self.parent.setWindowModified(False)

    def get_instances(self):
        return self.__class__.instances

    def has_data(self):
        return len(self.model.data) > 0

    def get_genres(self, groups=False):
        headid = self.model.header['genre']
        genres = []
        for game in self.model.data:
            if (not game[headid] == ''
            and not game[headid] is None):
                if groups:
                    genres.append(game[headid])
                elif '/' in game[headid]:
                    genres.extend(game[headid].split('/'))
                else:
                    genres.append(game[headid])
        if genres:
            genres = [entry.strip() for entry in genres]
            genres = list(set(genres))
            genres.sort()
        return genres

    def get_header(self, head=None):
        if head is None:
            return self.model.header.keys()
        else:
            try:
                return self.model.header[head]
            except KeyError:
                return -1

    def lock_columns(self, locklist):
        locked_header = []
        for head in locklist:
            headid = self.get_header(head)
            if headid > -1:
                self.model.append_locked_columns(headid)
                locked_header.append(head)
        return locked_header

    def unlock_columns(self, unlocklist):
        unlocked_header = []
        for head in unlocklist:
            headid = self.get_header(head)
            if headid > -1:
                self.model.remove_locked_columns(headid)
                unlocked_header.append(head)
        return unlocked_header

    def get_locked_header(self):
        reverse_header = {v: k for k, v in self.model.header.items()}
        return [reverse_header[head] for head in self.model.locked_columns]

    def filter(self, head, filter, regex=False, case=False, widget=None):
        try:
            if head is None:
                self.proxy.setFilterKeyColumn(-1)
            else:
                self.proxy.setFilterKeyColumn(self.get_header(head))
        except KeyError:
            pass
        else:
            if regex:
                filter = QtCore.QRegularExpression(filter)
                if filter.isValid():
                    if widget:
                        widget.setStyleSheet('')
                    if case:
                        filter.setPatternOptions(
                            QtCore.QRegularExpression.UseUnicodePropertiesOption
                            | QtCore.QRegularExpression.DotMatchesEverythingOption
                        )
                    else:
                        filter.setPatternOptions(
                            QtCore.QRegularExpression.CaseInsensitiveOption
                            | QtCore.QRegularExpression.UseUnicodePropertiesOption
                            | QtCore.QRegularExpression.DotMatchesEverythingOption
                        )
                    self.proxy.setFilterRegularExpression(filter)
                else:
                    if widget:
                        widget.setStyleSheet('color: #8B0000;')  # DarkRed
            else:
                #self.proxy.setFilterWildcard(filter)
                self.proxy.setFilterFixedString(filter)
                self.proxy.setFilterCaseSensitivity(case)

    def clear_sort(self):
        self.view.clearSelection()
        self.view.sortByColumn(-1, QtCore.Qt.AscendingOrder)

    def sort_header(self, sortlist):
        self.view.sortByColumn(-1, QtCore.Qt.AscendingOrder)
        for head in sortlist:
            if head in self.get_header():
                self.view.sortByColumn(self.get_header(head),
                                       QtCore.Qt.AscendingOrder)

    def hide_header(self, hidelist):
        hidden = []
        tableheads = self.view.horizontalHeader()
        for head in hidelist:
            headid = self.get_header(head)
            if headid > -1:
                tableheads.hideSection(headid)
                hidden.append(head)
        return hidden

    def resize_header(self, index, size):
        self.view.setColumnWidth(index, size)

    def enable_edit(self):
        self.view.setEditTriggers(
            QtWidgets.QAbstractItemView.DoubleClicked
            | QtWidgets.QAbstractItemView.EditKeyPressed
            | QtWidgets.QAbstractItemView.AnyKeyPressed)

    def disable_edit(self):
        self.view.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
