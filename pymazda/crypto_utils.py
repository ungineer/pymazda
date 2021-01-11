import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad


def encrypt_aes128cbc_buffer_to_base64_str(data, key, iv):
    cipher = AES.new(key.encode("ascii"), AES.MODE_CBC, iv.encode("ascii"))
    return base64.b64encode(cipher.encrypt(pad(data, AES.block_size))).decode("utf-8")


def decrypt_aes128cbc_buffer_to_str(data, key, iv):
    cipher = AES.new(key.encode("ascii"), AES.MODE_CBC, iv.encode("ascii"))
    return unpad(cipher.decrypt(data), AES.block_size)


def encrypt_rsaecbpkcs1_padding(data, publicKey):
    key = RSA.importKey(base64.b64decode(publicKey))
    cipher = PKCS1_v1_5.new(key)
    return cipher.encrypt(data.encode("utf-8"))

def generate_uuid_from_seed(seed):
    hash = hashlib.sha256(seed.encode()).hexdigest().upper()
    return hash[0:8] + "-" + hash[8:12] + "-" + hash[12:16] + "-" + hash[16:20] + "-" + hash[20:32]

def generate_usher_device_id_from_seed(seed):
    hash = hashlib.sha256(seed.encode()).hexdigest().upper()
    id = int(hash[0:8], 16)
    return "ACCT" + str(id)