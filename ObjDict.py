#!/usr/bin/env python3
# -*- coding: utf-8 -*-
class ObjDict(dict):

    @property
    def NotExist(self): # for default value
        return ObjDict.NotExist
    
    def __init__(self, d:dict=None, recursive=True, default=NotExist, *, antiloop_map = None):
        '''
        ## ObjDict is a subclass of dict that allows for object-like access
        #### Preserved:
        these preserved names are not allowed to be set using dot access, but you can access your version using `['name']` or `get`
        * `NotExist`: default value for missing key, will raise KeyError
        * `update`: just like dict.update(), but recursively converts nested dicts
        * `copy`: returns a shallow copy
        * Any attribute of the dict class
        * Any name starts with `_`

        #### Precedence: 
        * `.` : Attribute > Key > Default
        * `[]` & `get` : Key > Default

        #### Params:
        * `d`: dict
        * `default`: default value to return if key is not found, reset to ObjDict.NotExist to raise KeyError
        * `recursive`: recursively try to convert all sub-objects in `d`
        * `antiloop_map`: a dict to store the loop-detection, if you want to use the same ObjDict object in multiple places, you can pass a dict to `antiloop_map` to avoid infinite loop
        '''
        self.__dict__["_antiloop_map"] = {} if antiloop_map is None else antiloop_map # for reference loop safety
        self.__dict__["_default"] = default
        self.__dict__["_recursive"] = recursive
        d = d or {}
        self._antiloop_map[id(d)] = self
        self.update(d)

    def update(self, d, **kw):
        try:
            if not isinstance(d, dict) or kw:
                d = dict(d, **kw)
            else:
                self._convert(d) # create a dummy if not exist yet, prevent infinite-loop
            for k, v in d.items():
                self[k] = self._convert(v)
        finally:
            self.__dict__["_antiloop_map"] = {} # reset the map

    def _convert(self, v, recursive:bool=None):
        recursive = recursive if recursive is not None else self._recursive
        if not recursive:
            return v
        if isinstance(v, dict):
            if id(v) in self._antiloop_map:
                return self._antiloop_map[id(v)]
            elif isinstance(v, ObjDict):
                if v.default is not self.default:
                    v.default = self.default
                return v
            else:
                return ObjDict(v, default=self.default, antiloop_map=self._antiloop_map)
        elif isinstance(v, list):
            return [self._convert(i) for i in v]
        elif isinstance(v, tuple):
            return tuple(self._convert(i) for i in v)
        elif isinstance(v, set):
            return set(self._convert(i) for i in v)
        else:
            return v

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
        * set to mutable objects is *NOT RECOMMENDED*, since all references share the same object
        """
        self.__dict__["_default"] = value
        self.update(self)

    def copy(self):
        """### return a shallow copy"""
        return ObjDict(self, recursive=False, default=self.default)

    def __getattr__(self, name, default=NotExist):
        try:
            return self[name] if default is self.NotExist else self.get(name,default)
        except KeyError:
            raise AttributeError(f"{name} not found in {self}")

    def __setattr__(self, name, value):
        if name in {"NotExist", "update", "copy"} or name.startswith("_"):
            raise AttributeError(f"set '{name}' with dot access is not allowed, consider using ['{name}']")
        if name in self.__dict__: # cannot just call setattr(self, name, value), recursion error
            self.__dict__[name] = value
        elif hasattr(getattr(type(self), name, None), "__set__"):
            getattr(type(self), name).__set__(self, value)
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
    assert c.a is c.a.b.a
    assert c is c.a.b
    e.update(b)
    assert e is not e.a.b # dummy works fine
    assert e.a is e.a.b.a
    e.update(c)
    assert e.a is c.a

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
        print("successfully raised AttributeError for not_a_key")
    e.default = None
    assert e.not_a_key is None

    # default broadcast test
    e.c = c
    e.default = "dft"
    assert e.not_exist == "dft"
    assert e.default == e.c.default
    e.id = 114514
    assert c.id != e.id
    ecp = e.copy()
    assert e.default == ecp.default
    assert e.default is not ObjDict.NotExist

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
