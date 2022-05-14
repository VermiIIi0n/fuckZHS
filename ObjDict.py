#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from copy import copy

class ObjDict(dict):

    NotExist = object() # for default value
    
    def __init__(self, d:dict=None, recursive=True, default=NotExist, *, antiloop_map = None):
        '''
        ## ObjDict is a subclass of dict that allows for object-like access
        #### Precedence: 
        * `.` : Attribute > Key > Default
        * `[]` & `get` : Key > Default

        #### params:
        * `d`: dict
        * `default`: default value to return if key is not found, reset to ObjDict.NotExist to raise KeyError
        '''
        self.__dict__["antiloop_map"] = antiloop_map or {} # for reference loop safety
        self.__dict__["_default"] = default
        self.update(d or {}, recursive=recursive)

    def update(self, *args, recursive:bool=True, **kw):
        for arg in args:
            self.antiloop_map[id(arg)] = self
            try:
                for k, v in arg.items():
                    self[k] = self._convert(v) if recursive else v
            except AttributeError:
                raise ValueError('update() takes either a dict or kwargs')
        for k, v in kw.items():
            self[k] = self._convert(v) if recursive else v
        self.antiloop_map = {}

    def _convert(self, d):
        if isinstance(d, ObjDict):
            d.default = self.default
            return d
        elif isinstance(d, dict):
            if id(d) in self.antiloop_map:
                return self.antiloop_map[id(d)]
            else:
                return ObjDict(d, default=self.default, antiloop_map=self.antiloop_map)
        elif isinstance(d, list):
            return [self._convert(i) for i in d]
        elif isinstance(d, tuple):
            return tuple(self._convert(i) for i in d)
        elif isinstance(d, set):
            return set(self._convert(i) for i in d)
        else:
            try:
                for k,v in d.__dict__.items():
                    d.__dict__[k] = self._convert(v)
            except Exception:
                pass
            return d

    @property
    def default(self):
        return self.__dict__["_default"]

    @default.setter
    def default(self, value):
        """
        ### default property
        * set value to return when key is not found
        * set to `ObjDict.NotExist` to raise KeyError when key is not found
        """
        self.__dict__["_default"] = value
        self.update(self)

    def copy(self):
        return copy(self)

    def __getattr__(self, name, default=NotExist):
        try:
            return self[name]
        except KeyError:
            if default is not ObjDict.NotExist:
                return default
            raise AttributeError

    def __setattr__(self, name, value):
        if hasattr(self, name):
            if name in self.__dict__: # cannot just call setattr(self, name, value), recursion error
                self.__dict__[name] = value
            else:
                setattr(type(self), name, value)
        else:
            self[name] = value

    def __getitem__(self, name):
        if name in self:
            return self.get(name)
        elif self.default is ObjDict.NotExist:
            raise KeyError(f"{name} not found in {self}")
        else:
            return self.default
