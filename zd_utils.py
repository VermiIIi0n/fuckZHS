from Crypto.Cipher import AES
from base64 import b64encode, b64decode
from ObjDict import ObjDict
import json

IV = b"1g3qqdh4jvbskb9x"

HOME_KEY  = b"7q9oko0vqb3la20r"
VIDEO_KEY = b"qz632524n86i7fk9"
QA_KEY    = b"w1k5ntxecb8wmbc2"

class Cipher:
    def __init__(self, key:bytes=None, iv:bytes=None):
        self.key = key or VIDEO_KEY
        self.iv = iv or IV

    @staticmethod
    def pad(data):
        return (data+chr(16-len(data)%16)*(16-len(data)%16)).encode()
    
    @staticmethod
    def unpad(data):
        data = data.decode()
        return data[:-ord(data[-1])]

    def encrypt(self, data:str):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return b64encode(cipher.encrypt(self.pad(data))).decode()

    def decrypt(self, data:str):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return self.unpad(cipher.decrypt(b64decode(data)))

def getWP(start:int, end:int):
    wp = "0,1"
    for i in range(start, end)[::2]:
        wp += f",{i//5+2}"
    return wp

def getEv(data:list, key:str="zzpttjd"):
    """
    key: d26666->zzpttjd (default)
         d24444->zhihuishu
    """
    def gen():
        while True:
            for c in key:
                yield ord(c)
    gen = gen()
    data = ';'.join(map(str, data))
    ev = ""
    for c in data:
        tmp = hex(ord(c)^next(gen)).replace("0x", "")
        if len(tmp)<2:
            tmp = '0' + tmp
        ev += tmp[-4:] # actually -2 is fine, but their souce code said -4
    return ev

def revEv(ev:str, key:str="zzpttjd"):
    """
    key: d26666->zzpttjd (default)
         d24444->zhihuishu
    """
    def gen():
        while True:
            for c in key:
                yield ord(c)
    gen = gen()
    ev = list(ev)
    ls = []
    ret = ""
    while ev:
        d2,d1 = ev.pop(),ev.pop()
        c = int(d1+d2, 16)
        ls.append(c)
    for c in ls[::-1]:
        ret += chr(c^next(gen))
    return ret

if __name__ == "__main__":
    v = Cipher()
    h = Cipher(HOME_KEY)
    q = Cipher(QA_KEY)
    #print(getEv([1,2,3,4,'你']))
    d = ""
    r = ObjDict(json.loads(v.decrypt(d)))
    print(r)
    #print(r.watchPoint)
    print(revEv(r.ev))
    #print(getWP(61, 321))