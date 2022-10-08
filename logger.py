#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
from utils import getRealPath

class MonoLogger:
    _logger_map = {}
    def __init__(self, name: str = "root", level: str | int = "WARNING", path: str = None,
                 formatter: logging.Formatter | str = None, to_console: bool = True):
        MonoLogger._logger_map.update({name: self})
        self._name = name
        if not path:
            path = os.path.join(os.getcwd(), name + ".logs")
        self.path = path
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        elif not os.path.isdir(self.path):
            raise ValueError("log path should be a directory")
        self._debug = logging.getLogger(self.name + "-debug")
        self._info = logging.getLogger(self.name + "-info")
        self._warning = logging.getLogger(self.name + "-warning")
        self._error = logging.getLogger(self.name + "-error")
        self._critical = logging.getLogger(self.name + "-critical")
        self.setLevel(level)

        self._console_hdlr = logging.StreamHandler()
        self._debug_hdlr = logging.FileHandler(os.path.join(self.path, "debug.log"), mode='w', encoding="utf-8")
        self._debug.addHandler(self._debug_hdlr)
        self._info_hdlr = logging.FileHandler(os.path.join(self.path, "info.log"), mode='w', encoding="utf-8")
        self._info.addHandler(self._info_hdlr)
        self._warning_hdlr = logging.FileHandler(os.path.join(self.path, "warning.log"), mode='w', encoding="utf-8")
        self._warning.addHandler(self._warning_hdlr)
        self._error_hdlr = logging.FileHandler(os.path.join(self.path, "error.log"), mode='w', encoding="utf-8")
        self._error.addHandler(self._error_hdlr)
        self._critical_hdlr = logging.FileHandler(os.path.join(self.path, "critical.log"), mode='w', encoding="utf-8")
        self._critical.addHandler(self._critical_hdlr)
        self.setFormatter(formatter)
        self.toConsole(to_console)

    @property
    def name(self):
        return self._name
    @property
    def path(self):
        return self._path
    @path.setter
    def path(self, path: str):
        self._path = getRealPath(path)
    @property
    def debug(self):
        return self._debug.debug
    @property
    def info(self):
        return self._info.info
    @property
    def warning(self):
        return self._warning.warning
    @property
    def error(self):
        return self._error.error
    @property
    def critical(self):
        return self._critical.critical
    @property
    def exception(self):
        return self._error.exception
    
    def toConsole(self, to_console: bool):
        if to_console:
            self.addHandler(self._console_hdlr)
        else:
            self.removeHandler(self._console_hdlr)

    def addHandler(self, handler: logging.Handler):
        self._debug.addHandler(handler)
        self._info.addHandler(handler)
        self._warning.addHandler(handler)
        self._error.addHandler(handler)
        self._critical.addHandler(handler)

    def removeHandler(self, handler: logging.Handler):
        self._debug.removeHandler(handler)
        self._info.removeHandler(handler)
        self._warning.removeHandler(handler)
        self._error.removeHandler(handler)
        self._critical.removeHandler(handler)

    def setFormatter(self, formatter: logging.Formatter|str = None):
        if not formatter:
            formatter = logging.Formatter("%(asctime)s:  %(message)s")
        elif isinstance(formatter, str):
            formatter = logging.Formatter(formatter)
        self._formatter = formatter
        self._console_hdlr.setFormatter(formatter)
        self._debug_hdlr.setFormatter(formatter)
        self._info_hdlr.setFormatter(formatter)
        self._warning_hdlr.setFormatter(formatter)
        self._error_hdlr.setFormatter(formatter)
        self._critical_hdlr.setFormatter(formatter)

    def setLevel(self, level: str|int):
        level = str.upper(level)
        self._level = level
        self._debug.setLevel(level)
        self._info.setLevel(level)
        self._warning.setLevel(level)
        self._error.setLevel(level)
        self._critical.setLevel(level)

    def getLevel(self):
        return self._level

    @property
    def formatter(self):
        return self._formatter
    @formatter.setter
    def formatter(self, formatter: logging.Formatter|str):
        self.setFormatter(formatter)

    @property
    def level(self):
        return self._level
    @level.setter
    def level(self, level: str|int):
        self.setLevel(level)

    @staticmethod
    def getLogger(name: str):
        if name in MonoLogger._logger_map:
            return MonoLogger._logger_map[name]
        else:
            return MonoLogger(name)

    def __del__(self):
        self._debug_hdlr.close()
        self._info_hdlr.close()
        self._warning_hdlr.close()
        self._error_hdlr.close()
        self._critical_hdlr.close()
        MonoLogger._logger_map.pop(self.name)

logger = MonoLogger(name="root",path="./logs",to_console=False, level="DEBUG")
