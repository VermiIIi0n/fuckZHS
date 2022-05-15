#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
        self.__dict__["_antiloop_map"] = antiloop_map or {} # for reference loop safety
        self.__dict__["_default"] = default
        self.update(d or {}, recursive=recursive)

    def update(self, *args, recursive:bool=True, **kw):
        try:
            for arg in args:
                self._antiloop_map[id(arg)] = self
                try:
                    for k, v in arg.items():
                        self[k] = self._convert(v) if recursive else v
                except AttributeError:
                    raise ValueError('update() takes either a dict or kwargs')
            for k, v in kw.items():
                self[k] = self._convert(v) if recursive else v
        finally:
            self.__dict__["_antiloop_map"] = {}

    def _convert(self, d):
        if isinstance(d, dict):
            if id(d) in self._antiloop_map:
                return self._antiloop_map[id(d)]
            elif isinstance(d, ObjDict):
                d.default = self.default
                return d
            else:
                return ObjDict(d, default=self.default, antiloop_map=self._antiloop_map)
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
        NOTICE: will also set default value for all sub-dicts
        * set value to return when key is not found
        * set to `ObjDict.NotExist` to raise KeyError when key is not found
        * set to values other than `None` or `ObjDict.NotExist` is not recommended though
        """
        self.__dict__["_default"] = value
        self.update(self)

    def copy(self):
        """### return a shallow copy"""
        return ObjDict(self, recursive=False, default=self.default)

    def __getattr__(self, name, default=NotExist):
        try:
            return self[name]
        except KeyError:
            if default is not ObjDict.NotExist:
                return default
            raise AttributeError(f"{name} not found in {self}")

    def __setattr__(self, name, value):
        if name in {"_antiloop_map", "_default", "_convert", "NotExist",
                    "update", "copy", "__getattr__", "__getitem__", "__setattr__"}:
            raise AttributeError(f"set {name} is not allowed")
        if name in self.__dict__: # cannot just call setattr(self, name, value), recursion error
            self.__dict__[name] = value
        elif hasattr(type(self), name):
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

if __name__ == "__main__":
    # dict method test
    a = {}
    b = {'a':a}
    a['b'] = b
    c = ObjDict(b) # loop reference test
    print(c)
    d = {'a':1, 'b':2}
    e = ObjDict(d)
    assert isinstance(e, dict)
    e.update({'c':3}, g=4)
    ec = e.copy()
    assert e == ec
    assert e is not ec
    assert e['a'] == 1
    assert e.get('not_exist', None) is None

    # ObjDict method test
    e.a = 5
    assert e.a == 5
    e.ar = ObjDict({'ls':[{'name':'d1', 'value':1}, {'name':'d2', 'value':2}]}).ls
    assert e.ar[0].name == 'd1'
    assert e.ar[1].value == 2
    try:
        print(f"not a key: {e.not_a_key}")
        raise Exception("should not reach here")
    except AttributeError:
        print("successfully raised AttributeError")
    e.default = None
    assert e.not_a_key is None

    # default broadcast test
    e.c = c
    e.default = "dft"
    assert e.not_exist == "dft"
    assert e.default == e.c.default
    e.id = 114514
    assert c.id != e.id

    # extreme usage test
    f = ObjDict({'a':{'b':{'c':1}}})
    try:
        f.NotExist = 1
        raise Exception("should not reach here")
    except AttributeError:
        print("successfully raised AttributeError for NotExist")
    try:
        f._default = 1
        raise Exception("should not reach here")
    except AttributeError:
        print("successfully raised AttributeError for _default")