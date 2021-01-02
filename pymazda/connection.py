import aiohttp
import time
import hashlib
import base64
import json
from urllib.parse import urlencode
from pymazda.crypto_utils import encryptAES128CBCBufferToBase64String, decryptAES128CBCBufferToString, encryptRSAECBPKCS1Padding
from pymazda.exceptions import MazdaAuthenticationException, MazdaAccountLockedException, MazdaException


APP_CODE = "202007270941270111799"
IV = "0102030405060708"
SIGNATURE_MD5 = "C383D8C4D279B78130AD52DC71D95CAA"
APP_PACKAGE_ID = "com.interrait.mymazda"
DEVICE_ID = "D9E89AFC-BD3C-309F-A48C-A2A9466DFE9C"
USER_AGENT = "MyMazda-Android/7.1.0"
APP_OS = "Android"
APP_VERSION = "7.1.0"

BASE_URL = "https://0cxo7m58.mazda.com/prod/"


class Connection:
    """Main class for handling MyMazda API connection"""
    
    def __init__(self, email, password, websession=None):
        self.email = email
        self.password = password

        self.encKey = None
        self.signKey = None

        self.accessToken = None
        self.accessTokenExpirationTs = None

        if websession is None:
            self._session = aiohttp.ClientSession()
        else:
            self._session = websession

    def __getTimestampStrMs(self):
        return str(int(round(time.time() * 1000)))

    def __getTimestampStr(self):
        return str(int(round(time.time())))

    def __getDecryptionKeyFromAppCode(self):
        val1 = hashlib.md5((APP_CODE + APP_PACKAGE_ID).encode()).hexdigest().upper()
        val2 = hashlib.md5((val1 + SIGNATURE_MD5).encode()).hexdigest().lower()
        return val2[4:20]

    def __getTemporarySignKeyFromAppCode(self, appCode):
        val1 = hashlib.md5((appCode + APP_PACKAGE_ID).encode()).hexdigest().upper()
        val2 = hashlib.md5((val1 + SIGNATURE_MD5).encode()).hexdigest().lower()
        return val2[20:32] + val2[0:10] + val2[4:6]

    def __getSignFromTimestamp(self, timestamp):
        if timestamp is None or timestamp == "":
            return ""

        timestampExtended = (timestamp + timestamp[6:] + timestamp[3:]).upper()

        temporarySignKey = self.__getTemporarySignKeyFromAppCode(APP_CODE)

        return self.__getPayloadSign(timestampExtended, temporarySignKey).upper()

    def __getSignFromPayloadAndTimestamp(self, payload, timestamp):
        if timestamp is None or timestamp == "":
            return ""
        if self.signKey is None or self.signKey == "":
            raise MazdaException("Missing sign key")

        return self.__getPayloadSign(self.__encryptPayloadUsingKey(payload) + timestamp + timestamp[6:] + timestamp[3:], self.signKey)

    def __getPayloadSign(self, encryptedPayloadAndTimestamp, signKey):
        return hashlib.sha256((encryptedPayloadAndTimestamp + signKey).encode()).hexdigest().upper()

    def __encryptPayloadUsingKey(self, payload):
        if self.encKey is None or self.encKey == "":
            raise MazdaException("Missing encryption key")
        if payload is None or payload == "":
            return ""

        return encryptAES128CBCBufferToBase64String(payload.encode("utf-8"), self.encKey, IV)

    def __decryptPayloadUsingAppCode(self, payload):
        buf = base64.b64decode(payload)
        key = self.__getDecryptionKeyFromAppCode()
        decrypted = decryptAES128CBCBufferToString(buf, key, IV)
        return json.loads(decrypted)

    def __decryptPayloadUsingKey(self, payload):
        if self.encKey is None or self.encKey == "":
            raise MazdaException("Missing encryption key")

        buf = base64.b64decode(payload)
        decrypted = decryptAES128CBCBufferToString(buf, self.encKey, IV)
        return json.loads(decrypted)

    def __encryptPasswordWithPublicKey(self, password, publicKey):
        timestamp = self.__getTimestampStr()
        encryptedBuffer = encryptRSAECBPKCS1Padding(password + ":" + timestamp, publicKey)
        return base64.b64encode(encryptedBuffer).decode("utf-8")

    async def apiRequest(self, method, uri, queryDict={}, bodyDict={}, needsKeys=True, needsAuth=False):
        if needsKeys:
            await self.__ensureKeysPresent()
        if needsAuth:
            await self.__ensureTokenIsValid()

        timestamp = self.__getTimestampStrMs()

        originalQueryStr = ""
        encryptedQueryDict = {}

        if queryDict:
            originalQueryStr = urlencode(queryDict)
            encryptedQueryDict["params"] = self.__encryptPayloadUsingKey(originalQueryStr)

        originalBodyStr = ""
        encryptedBodyStr = ""
        if bodyDict:
            originalBodyStr = json.dumps(bodyDict)
            encryptedBodyStr = self.__encryptPayloadUsingKey(originalBodyStr)

        headers = {
            "device-id": DEVICE_ID,
            "app-code": APP_CODE,
            "app-os": APP_OS,
            "user-agent": USER_AGENT,
            "app-version": APP_VERSION,
            "app-unique-id": APP_PACKAGE_ID,
            "region": "us",
            "access-token": (self.accessToken if needsAuth else ""),
            "language": "en-US",
            "locale": "en-US",
            "X-acf-sensor-data": "",
            "req-id": "req_" + timestamp,
            "timestamp": timestamp
        }

        if "checkVersion" in uri:
            headers["sign"] = self.__getSignFromTimestamp(timestamp)
        elif method == "GET":
            headers["sign"] = self.__getSignFromPayloadAndTimestamp(originalQueryStr, timestamp)
        elif method == "POST":
            headers["sign"] = self.__getSignFromPayloadAndTimestamp(originalBodyStr, timestamp)

        response = await self._session.request(method, BASE_URL + uri, headers=headers, data=encryptedBodyStr)

        responseJson = await response.json()

        if responseJson["state"] == "S":
            if "checkVersion" in uri:
                return self.__decryptPayloadUsingAppCode(responseJson["payload"])
            else:
                return self.__decryptPayloadUsingKey(responseJson["payload"])
        elif responseJson["errorCode"] == 600001:
            raise MazdaException("Server rejected encrypted request")
        elif responseJson["errorCode"] == 600002:
            raise MazdaException("Token expired")
        else:
            raise MazdaException("Request failed for an unknown reason")

    async def __ensureKeysPresent(self):
        if self.encKey is None or self.signKey is None:
            await self.__retrieveKeys()

    async def __ensureTokenIsValid(self):
        if self.accessToken is None or self.accessTokenExpirationTs is None or self.accessTokenExpirationTs <= time.time():
            await self.login()

    async def __retrieveKeys(self):
        response = await self.apiRequest("POST", "service/checkVersion", needsKeys=False, needsAuth=False)

        self.encKey = response["encKey"]
        self.signKey = response["signKey"]

    async def login(self):
        encryptionKeyResponse = await self._session.request("GET", "https://ptznwbh8.mazda.com/appapi/v1/system/encryptionKey?appId=MazdaApp&locale=en-US&deviceId=ACCT1195961580&sdkVersion=11.2.0000.002", headers={"User-Agent": "MyMazda/7.0.1 (Google Pixel 3a; Android 11)"})

        encryptionKeyResponseJson = await encryptionKeyResponse.json()

        publicKey = encryptionKeyResponseJson["data"]["publicKey"]
        encryptedPassword = self.__encryptPasswordWithPublicKey(self.password, publicKey)
        versionPrefix = encryptionKeyResponseJson["data"]["versionPrefix"]

        loginResponse = await self._session.request(
            "POST",
            "https://ptznwbh8.mazda.com/appapi/v1/user/login",
            headers={"User-Agent": "MyMazda/7.0.1 (Google Pixel 3a; Android 11)"},
            json={
                "appId": "MazdaApp",
                "deviceId": "ACCT1195961580",
                "locale": "en-US",
                "password": versionPrefix + encryptedPassword,
                "sdkVersion": "11.2.0000.002",
                "userId": self.email,
                "userIdType": "email"
            })

        loginResponseJson = await loginResponse.json()

        if loginResponseJson["status"] == "INVALID_CREDENTIAL":
            raise MazdaAuthenticationException("Invalid email or password")
        if loginResponseJson["status"] == "USER_LOCKED":
            raise MazdaAccountLockedException("Account has been locked")
        if loginResponseJson["status"] != "OK":
            raise MazdaException("Login failed")

        self.accessToken = loginResponseJson["data"]["accessToken"]
        self.accessTokenExpirationTs = loginResponseJson["data"]["accessTokenExpirationTs"]

    async def __close(self) -> None:
        if self._session:
            await self._session.close()
