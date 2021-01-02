import base64
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad


def encryptAES128CBCBufferToBase64String(data, key, iv):
    cipher = AES.new(key.encode("ascii"), AES.MODE_CBC, iv.encode("ascii"))
    return base64.b64encode(cipher.encrypt(pad(data, AES.block_size))).decode("utf-8")


def decryptAES128CBCBufferToString(data, key, iv):
    cipher = AES.new(key.encode("ascii"), AES.MODE_CBC, iv.encode("ascii"))
    return unpad(cipher.decrypt(data), AES.block_size)


def encryptRSAECBPKCS1Padding(data, publicKey):
    key = RSA.importKey(base64.b64decode(publicKey))
    cipher = PKCS1_v1_5.new(key)
    return cipher.encrypt(data.encode("utf-8"))
