#!/usr/bin/python3

def extend_settings_meta(settings):
    settings['app_title'] = 'Gamelist XML Editor'
    settings['app_license'] = 'GNU GPL v3'
    settings['app_name'] = 'gamelistedit'
    settings['app_author'] = 'Tuncay D.'
    settings['app_copyright_years'] = '2021'
    settings['app_version'] = '0.1.0'
    settings['app_minpython'] = '3.6'
    settings['app_minqt5'] = '5.15'
    settings['app_desc'] = (
        'GUI operation and commandline automation to edit, filter'
        ' and export gamelist.xml files from EmulationStation.')
    return settings

def get_meta(key=None):
    meta = extend_settings_meta({})
    return meta if key is None else meta[key]

# python3 -m modules.meta name version
if __name__ == '__main__':
    import sys

    meta = get_meta()
    if len(sys.argv) > 1:
        for key in sys.argv[1:]:
            print(meta[f'app_{key}'])
    else:
        for key, value in meta.items():
            print(f'{key[4:]}={value}')
