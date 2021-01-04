#!/usr/bin/python3

import pathlib
import glob
import urllib.parse


def get_path(file, useglob=True):
    """
        Expects a path str or a list of path str, which then the first
        entry will be used.  Globbing with wildcards works and its again
        its first entry will be used.  The "~" for home directory of the
        user is supported too.  In example '~/*.xml' would work fine.

        When a file was found, then a pathlib.Path with full path from
        disc will be returned.  Otherwise it still tries to resolve and
        build a full path with the original in place.

        Use isinstance(file, os.PathLike) to test if its a path.
    """
    if isinstance(file, list):
        file = file[0] if file else ''
    path = file
    if useglob and not path == '':
        # 1. NotImplementedError: Non-relative patterns are unsupported:
        #       path = list(pathlib.Path().glob(file))
        # 2. sorted() does not sort the same as commandline (ls -U).
        #       therefore results from commandline wildcards may differ.
        try:
            path = pathlib.Path(path).expanduser().resolve()
        except (KeyError, RuntimeError, PermissionError):
            path = file
        path = sorted(glob.glob(str(path)))
        path = path[0] if path else file
    try:
        path = pathlib.Path(path).expanduser().resolve() if path else path
    except (KeyError, RuntimeError, PermissionError):
        path = file
    return path


def normalize_path(path):
    """ Unquotes and normalizes drag and dropped paths.
    """
    if path.startswith('file://'):
        path = path[7:]
    return urllib.parse.unquote(path)  #.strip()
