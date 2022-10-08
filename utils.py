#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import os
import sys
from PIL import Image, ImageOps
from datetime import timedelta

def HMS(*args, **kw):
    return str(timedelta(*args, **kw))

def strToClass(class_name: str, module: str="__main__"):
    return getattr(sys.modules[module], class_name)

def showImage(img, show_in_terminal=False, ensure_unicode=False):
    if show_in_terminal:
        if ensure_unicode:
            terminalShowImage_unicode(img)
        else:
            terminalShowImage_tty(img)
    else:
        import threading
        img = Image.open(io.BytesIO(img))
        threading.Thread(target=img.show).run()
    print("Scan QR code")

def terminalShowImage_unicode(img):
    img = Image.open(io.BytesIO(img))
    qr = img.resize((47,47), Image.Resampling.NEAREST)
    qr = ImageOps.grayscale(qr)
    chars = [bytes((code,)).decode("cp437") for code in (255, 223, 220, 219)]
    new_line = '\n'
    col, row = qr.size
    def getPos(x, y):
        below = (y+1 < row) and qr.getpixel((x, y+1)) < 128
        return (qr.getpixel((x, y)) < 128) + below*2
    qr_str = ""
    for i in range(0, row, 2):
        qr_str += chars[0]
        for j in range(col):
            qr_str += chars[getPos(j, i)]
        qr_str += chars[0] + new_line
    print(chars[0]*49)
    print(qr_str, end='')
    print(chars[0]*49)

def terminalShowImage_tty(img):
    img = Image.open(io.BytesIO(img))
    qr = img.resize((47,47), Image.Resampling.NEAREST)
    qr = ImageOps.grayscale(qr)
    white = '\033[0;37;47m  '
    black = '\033[0;37;40m  '
    new_line = '\033[0m\n'
    col, row = qr.size
    qr_str = white * 49 + new_line
    for i in range(row):
        qr_str += white
        for j in range(col):
            qr_str += white if qr.getpixel((j, i)) > 128 else black
        qr_str += white + new_line
    qr_str += white * 49 + new_line
    print(qr_str)

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

def wipeLine():
    print('\r' + ' ' * (os.get_terminal_size().columns), end = '\r')

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
        wipeLine()
