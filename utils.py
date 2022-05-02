#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import copy
from multiprocessing import Lock

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
    if path == os.path.abspath(path):
        return os.path.realpath(path)
    return os.path.join(getDir(), path)

def progressBar (iteration, total, prefix = '', suffix = '', decimals = 1,
                      length = (os.get_terminal_size().columns-1), fill = '#'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
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

class ObjDict(dict):
    def __init__(self, d:dict, recursive=True, *, antiloop_map = None):
        self.antiloop_map = antiloop_map or {} # for reference loop safety
        self.antiloop_map[id(d)] = self
        for k, v in d.items():
            k = str(k)
            if   isinstance(v, dict)  and recursive:
                self.__dict__[k] = self._convert(v)
            elif isinstance(v, list)  and recursive:
                self.__dict__[k] = [self._convert(i) for i in v]
            elif isinstance(v, tuple) and recursive:
                self.__dict__[k] = tuple(self._convert(i) for i in v)
            elif isinstance(v, set)   and recursive:
                self.__dict__[k] = set(self._convert(i) for i in v)
            else:
                self.__dict__[k] = v
        self.__dict__.pop('antiloop_map')

    def _convert(self, d):
        if isinstance(d, dict):
            if id(d) in self.antiloop_map:
                return self.antiloop_map[id(d)]
            else:
                new = ObjDict(d, antiloop_map=self.antiloop_map)
                return new
        else:
            return d

    def items(self):
        return self.__dict__.items()
    def keys(self):
        return self.__dict__.keys()
    def values(self):
        return self.__dict__.values()
    def update(self, *args, **kw):
        for arg in args:
            for k, v in arg.items() if hasattr(arg, 'items') else arg:
                self.__dict__.update({str(k): self._convert(v)})
        for k, v in kw.items():
            self.__dict__.update({str(k): self._convert(v)})
    def pop(self, key, *args):
        return self.__dict__.pop(key, *args)
    def popitem(self):
        return self.__dict__.popitem()
    def clear(self):
        self.__dict__.clear()
    def copy(self):
        return copy.copy(self)
    def fromkeys(self, seq, value=None):
        return self.__dict__.fromkeys(seq, value)
    def get(self, key, default=None):
        return self.__dict__.get(key, default)
    def setdefault(self, key, default=None):
        return self.__dict__.setdefault(key, default)
    def __getitem__(self, key):
        return self.__dict__[key]
    def __setitem__(self, key, value):
        self.__dict__[key] = value
    def __delitem__(self, key):
        del self.__dict__[key]
    def __contains__(self, key):
        return key in self.__dict__
    def __len__(self):
        return len(self.__dict__)
    def __iter__(self):
        return iter(self.__dict__)
    def __repr__(self):
        return repr(self.__dict__)
    def __str__(self):
        return str(self.__dict__)

