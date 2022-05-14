#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from datetime import timedelta

def HMS(*args, **kw):
    return str(timedelta(*args, **kw))

def strToClass(class_name: str, module: str):
    return getattr(sys.modules[module], class_name)

def getDir():
    return os.path.dirname(os.path.realpath(__file__))

def getConfigPath():
    return os.path.join(getDir(), 'config.json')

def getRealPath(path: str):
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.normpath(path)
    if path != os.path.abspath(path):
        path = os.path.join(getDir(), path)
    return os.path.realpath(path)

def versionCmp(v1:str, v2:str):
    v1 = v1.split('.')
    v2 = v2.split('.')
    for i in range(min(len(v1), len(v2))):
        dt = int(v1[i]) - int(v2[i])
        if dt:
            return dt
    return 0 if len(v1) == len(v2) else (v1[-1] if len(v1) > len(v2) else -v2[-1])


def progressBar (iteration, total, prefix = '', suffix = '', decimals = 1,
                      length = (os.get_terminal_size().columns-4), fill = '#'):
    """
    ### Call in a loop to create terminal progress bar
    * `iteration`   - Required  : current iteration (Int)
    * `total`       - Required  : total iterations (Int)
    * `prefix`      - Optional  : prefix string (Str)
    * `suffix`      - Optional  : suffix string (Str)
    * `decimals`    - Optional  : positive number of decimals in percent complete (Int)
    * `length`      - Optional  : character length of bar (Int)
    * `fill`        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    prefix = f"{prefix} |"
    suffix = f"| {percent}% {suffix}"
    bar_len = length - len(prefix) - len(suffix)
    filled_len = int(bar_len * iteration // total)
    bar = fill * filled_len + ' ' * (bar_len - filled_len)
    print(f"\r{prefix}{bar}{suffix}", end = '\r')
    if iteration >= total:
        print('\r' + ' ' * (os.get_terminal_size().columns), end = '\r')
