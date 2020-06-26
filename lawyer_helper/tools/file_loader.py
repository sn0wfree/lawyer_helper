# coding=utf-8
import os
from glob import glob
from platform import system


def get_current_path():
    return os.getcwd()


def get_upper_path(path=None, deep=1):
    if path is None:
        current_path = get_current_path()
    else:
        current_path = path
    path2 = os.path.abspath(os.path.join(current_path, '..'))

    if deep == 1:
        return path2
    elif deep == 0:
        return current_path
    else:
        return get_upper_path(path=path2, deep=deep - 1)


def file_loader(conf_file: str = 'conn.ini', path: str = None):
    if system() == 'Windows':
        sep = '\\'
    else:
        sep = '/'

    path1 = get_current_path() if path is None else path
    path2 = get_upper_path(path=path1, deep=1)
    path3 = get_upper_path(path=path1, deep=2)

    if path1 + sep + conf_file in glob(path1 + sep + '*'):
        target_path = path1 + sep
    elif path2 + sep + conf_file in glob(path2 + sep + '*'):
        target_path = path2 + sep
    elif path3 + sep + conf_file in glob(path3 + sep + '*'):
        target_path = path3 + sep
    else:
        raise FileNotFoundError('cannot locate {} at {}'.format(conf_file, __file__))
    return target_path + conf_file


if __name__ == '__main__':
    print(get_upper_path(deep=0))

    pass
