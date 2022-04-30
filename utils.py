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

class ObjDict(dict):
    lock = Lock() # for thread safety
    antiloop_map = {} # for loop safety
    def __init__(self, d, *, root: bool = True):
        try:
            if root:
                ObjDict.lock.acquire()
                ObjDict.antiloop_map.update({id(d): self})
            for k, v in d.items() if hasattr(d, 'items') else d:
                k = str(k)
                if isinstance(v, dict):
                    self.__dict__.update({k: self.autoDict(v)})
                elif isinstance(v, list):
                    self.__dict__.update({k: [self.autoDict(i) for i in v]})
                elif isinstance(v, tuple):
                    self.__dict__.update({k: (self.autoDict(i) for i in v)})
                else:
                    self.__dict__.update({k: v})
        except AttributeError:
            raise ValueError("Invalid type of argument")
        finally:
            if root:
                ObjDict.antiloop_map.clear()
                ObjDict.lock.release()

    @staticmethod
    def autoDict(d):
        if isinstance(d, dict):
            if id(d) in ObjDict.antiloop_map:
                return ObjDict.antiloop_map[id(d)]
            else:
                new = ObjDict(d, root=False)
                ObjDict.antiloop_map[id(d)] = new
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
                self.__dict__.update({str(k): self.autoDict(v)})
        for k, v in kw.items():
            self.__dict__.update({str(k): self.autoDict(v)})
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