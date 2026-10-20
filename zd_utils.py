from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from base64 import b64encode, b64decode
from Crypto.Util.number import bytes_to_long, long_to_bytes
import requests
import json
import time

IV = b"1g3qqdh4jvbskb9x"

HOME_KEY  = b"7q9oko0vqb3la20r"
AI_KEY=b"hw2fdlwcj4cs1mx7"
VIDEO_KEY = b"azp53h0kft7qi78q"
QA_KEY    = b"kcGOlISPkYKRksSK"
EXAM_KEY  = b"onbfhdyvz8x7otrp"

KEY_SERVICE = "https://appcomm-user.zhihuishu.com/app-commserv-user/c/has"
KEY_SERVICE_V2 = "https://appcomm-user.zhihuishu.com/app-commserv-user/c/hasV2"
KEY_SERVICE_PUBLIC_KEY = b"""-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCgfZmpLpPEpEFRKBe+ZjWJUjPe+7qg7pGqcfN3j2egJ8H2mrKwaEqZEnPnpi2O3hN8HRyaFozDOp8gwZiYfiIZjWy0Jr/FNAiiKYh5bq0GsEn+ieMmRyJg/+i1rqizhvCXvFdrdGhFTw5EBwTpsGdwe1utdlrvIJUAFWj9Yh4qbQIDAQAB
-----END PUBLIC KEY-----"""

class Cipher:
    def __init__(self, key:bytes=VIDEO_KEY, iv:bytes=IV):
        self.key = key.encode() if isinstance(key, str) else key
        self.iv = iv

    @staticmethod
    def pad(data):
        if isinstance(data, str):
            data = data.encode("utf-8")
        if not isinstance(data, bytes):
            raise TypeError("data must be str or bytes")
        padding = 16 - len(data) % 16
        return data + bytes([padding]) * padding
    
    @staticmethod
    def unpad(data):
        if not isinstance(data, bytes) or not data or len(data) % 16:
            raise ValueError("invalid AES block data")
        padding = data[-1]
        if not 1 <= padding <= 16 or data[-padding:] != bytes([padding]) * padding:
            raise ValueError("invalid PKCS#7 padding")
        return data[:-padding].decode("utf-8")

    def encrypt(self, data:str):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return b64encode(cipher.encrypt(self.pad(data))).decode()

    def decrypt(self, data:str):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return self.unpad(cipher.decrypt(b64decode(data)))


def _rsa_public_decrypt(value: str, public_key: bytes = KEY_SERVICE_PUBLIC_KEY) -> dict:
    """Decode the service response signed with its RSA private key.

    The browser calls this operation ``decrypt`` even though the response is
    produced with the server private exponent. Applying the public exponent
    and validating the PKCS#1 v1.5 block matches that behavior.
    """
    key = RSA.import_key(public_key)
    encrypted = b64decode(value, validate=True)
    if len(encrypted) != key.size_in_bytes():
        raise ValueError("invalid dynamic key response length")
    block = long_to_bytes(
        pow(bytes_to_long(encrypted), key.e, key.n),
        key.size_in_bytes(),
    )
    if not block.startswith(b"\x00\x01"):
        raise ValueError("invalid dynamic key response padding")
    separator = block.find(b"\x00", 2)
    if separator < 10 or any(byte != 0xFF for byte in block[2:separator]):
        raise ValueError("invalid dynamic key response padding")
    return json.loads(block[separator + 1:].decode("utf-8"))


def fetch_dynamic_key(module: int, session=None, proxies=None, timeout: float = 10) -> str:
    """Fetch the AES key used by the current Zhihuishu web client."""
    session = session or requests.Session()
    endpoint = KEY_SERVICE_V2 if int(module) == 10 else KEY_SERVICE
    public_key = RSA.import_key(KEY_SERVICE_PUBLIC_KEY)
    request_body = json.dumps({"module": int(module)}, separators=(",", ":")).encode()
    encrypted = PKCS1_v1_5.new(public_key).encrypt(request_body)
    response = session.get(
        endpoint,
        params={"uid": b64encode(encrypted).decode("ascii")},
        proxies=proxies,
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    try:
        decoded = _rsa_public_decrypt(payload["rt"]["sl"])
        # ``key`` is the protocol version's rotating value. The web client
        # assigns ``cKey`` to its AES key.
        key = decoded["cKey"]
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("invalid dynamic key service response") from exc
    if not isinstance(key, str) or not key:
        raise ValueError("dynamic key service returned an empty key")
    return key


class DynamicKeyCache:
    def __init__(self, session=None, proxies=None, ttl: float = 300):
        self.session = session
        self.proxies = proxies
        self.ttl = ttl
        self._values = {}

    def get(self, module: int) -> str:
        module = int(module)
        now = time.monotonic()
        cached = self._values.get(module)
        if cached and now - cached[0] < self.ttl:
            return cached[1]
        value = fetch_dynamic_key(module, self.session, self.proxies)
        self._values[module] = (now, value)
        return value

    def clear(self):
        self._values.clear()

class WatchPoint:
    def __init__(self, init:int=0):
        self.reset(init)

    def add(self, end:int, start:int=None):
        wp_interval = 2 # watch point record interval in seconds
        start = self.last if start is None else start
        end = int(end)
        self.last = end
        for i in range(start, end+1)[::wp_interval]:
            self.wp.append(self.gen(i))

    def get(self):
        return ','.join(map(str,self.wp))

    def reset(self, init:int=0):
        self.wp = [0,1]
        self.last = int(init) or 1
    
    @staticmethod
    def gen(time:int):
        return int(time//5+2)

def getEv(data:list, key:str="zzpttjd"):
    """
    * key:
      * d26666 -> "zzpttjd" (default)
      * d24444 -> "zhihuishu"
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
        ev += tmp[-4:] # actually -2 is fine, but their sauce code said -4
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
    e = Cipher(EXAM_KEY)
    a = Cipher(AI_KEY)
    
    #print(getEv([1,2,3,4,'你']))
    # d = "R8b5YgowBZhvyiaFlYAhdoTbupkjQBWiT2cwpDf275SvouM6xvxeAv9YdvdYw97tfmjBuqoXPcj7ptqnWJcFPwtWZMv6Ptld70F5yIl8R9Q="
    # r = ObjDict(json.loads(q.decrypt(d)))
    # print(r)
    # #print(r.watchPoint)
    # print(revEv(r.sdsew))

    encoded = a.encrypt(json.dumps({'courseId': '1839576198548688896', 'classId': 4239, 'dateFormate': 1729175218000}))
    print(encoded)

    decoded = e.decrypt("xI1pFlV/3UmvLdGDXuK0f2iiN+Po+oSemJWfhnvgzCu9/KU6P2vSWty3Qe2QIxtGJ/Ik+jvUrnNZJZEXvandQiv4039O/MevpN5QUEhDwNJ1Yep+dYhGjdBOgkzjUvxl")

    print(decoded)
