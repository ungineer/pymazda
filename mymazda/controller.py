import aiohttp
import time
import hashlib
import base64
import json
from urllib.parse import urlencode
from mymazda.crypto_utils import encryptAES128CBCBufferToBase64String, decryptAES128CBCBufferToString, encryptRSAECBPKCS1Padding

APP_CODE_406 = "201904042256322230255"
APP_CODE_701 = "202007270941270111799"
IV = "0102030405060708"
SIGNATURE_MD5 = "C383D8C4D279B78130AD52DC71D95CAA"
APP_PACKAGE_ID = "com.interrait.mymazda"
DEVICE_ID = "D9E89AFC-BD3C-309F-A48C-A2A9466DFE9C"
USER_AGENT = "MyMazda-Android/7.0.1"
APP_OS = "Android"
APP_VERSION = "7.0.1"

BASE_URL_406 = "https://b6nvzc7s.mazda.com/prod/"
BASE_URL_701 = "https://0cxo7m58.mazda.com/prod/"


class Controller:
    """Main class for handling MyMazda API connection"""

    def __init__(self, email, password):
        self.email = email
        self.password = password

        self.encKey = None
        self.signKey = None

        self.accessToken = None
        self.accessTokenExpirationTs = None

        self._session = aiohttp.ClientSession()

    def getTimestampStrMs(self):
        return str(int(round(time.time() * 1000)))

    def getTimestampStr(self):
        return str(int(round(time.time())))

    def getDecryptionKeyFromAppCode(self):
        val1 = hashlib.md5((APP_CODE_701 + APP_PACKAGE_ID).encode()).hexdigest().upper()
        val2 = hashlib.md5((val1 + SIGNATURE_MD5).encode()).hexdigest().lower()
        return val2[4:20]

    def getTemporarySignKeyFromAppCode(self, appCode):
        val1 = hashlib.md5((appCode + APP_PACKAGE_ID).encode()).hexdigest().upper()
        val2 = hashlib.md5((val1 + SIGNATURE_MD5).encode()).hexdigest().lower()
        return val2[20:32] + val2[0:10] + val2[4:6]

    def getSignFromTimestamp(self, timestamp):
        if timestamp is None or timestamp == "":
            return ""

        timestampExtended = (timestamp + timestamp[6:] + timestamp[3:]).upper()

        temporarySignKey = self.getTemporarySignKeyFromAppCode(APP_CODE_701)

        return self.getPayloadSign(timestampExtended, temporarySignKey).upper()

    def getSignFromPayloadAndTimestamp(self, payload, timestamp):
        if timestamp is None or timestamp == "":
            return ""
        if self.signKey is None or self.signKey == "":
            raise Exception("Missing sign key")

        return self.getPayloadSign(self.encryptPayloadUsingKey(payload) + timestamp + timestamp[6:] + timestamp[3:], self.signKey)

    def getPayloadSign(self, encryptedPayloadAndTimestamp, signKey):
        return hashlib.sha256((encryptedPayloadAndTimestamp + signKey).encode()).hexdigest().upper()

    def encryptPayloadUsingKey(self, payload):
        if self.encKey is None or self.encKey == "":
            raise Exception("Missing enc key")
        if payload is None or payload == "":
            return ""

        return encryptAES128CBCBufferToBase64String(payload.encode("utf-8"), self.encKey, IV)

    def decryptPayloadUsingAppCode(self, payload):
        buf = base64.b64decode(payload)
        key = self.getDecryptionKeyFromAppCode()
        decrypted = decryptAES128CBCBufferToString(buf, key, IV)
        return json.loads(decrypted)

    def decryptPayloadUsingKey(self, payload):
        if self.encKey is None or self.encKey == "":
            raise Exception("Missing enc key")

        buf = base64.b64decode(payload)
        decrypted = decryptAES128CBCBufferToString(buf, self.encKey, IV)
        return json.loads(decrypted)

    def encryptPasswordWithPublicKey(self, password, publicKey):
        timestamp = self.getTimestampStr()
        encryptedBuffer = encryptRSAECBPKCS1Padding(password + ":" + timestamp, publicKey)
        return base64.b64encode(encryptedBuffer).decode("utf-8")

    async def apiRequest(self, method, uri, queryDict={}, bodyDict={}, needsKeys=True, needsAuth=False):
        if needsKeys:
            await self.ensureKeysPresent()
        if needsAuth:
            await self.ensureTokenIsValid()

        timestamp = self.getTimestampStrMs()

        originalQueryStr = ""
        encryptedQueryDict = {}

        if queryDict:
            originalQueryStr = urlencode(queryDict)
            encryptedQueryDict["params"] = self.encryptPayloadUsingKey(originalQueryStr)

        originalBodyStr = ""
        encryptedBodyStr = ""
        if bodyDict:
            originalBodyStr = json.dumps(bodyDict)
            encryptedBodyStr = self.encryptPayloadUsingKey(originalBodyStr)

        headers = {
            "device-id": DEVICE_ID,
            "app-code": APP_CODE_701,
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
            headers["sign"] = self.getSignFromTimestamp(timestamp)
        elif method == "GET":
            headers["sign"] = self.getSignFromPayloadAndTimestamp(originalQueryStr, timestamp)
        elif method == "POST":
            headers["sign"] = self.getSignFromPayloadAndTimestamp(originalBodyStr, timestamp)

        response = await self._session.request(method, uri, headers=headers, data=encryptedBodyStr)

        responseJson = await response.json()

        if responseJson["state"] == "S":
            if "checkVersion" in uri:
                return self.decryptPayloadUsingAppCode(responseJson["payload"])
            else:
                return self.decryptPayloadUsingKey(responseJson["payload"])
        elif responseJson["errorCode"] == 600001:
            raise Exception("Server rejected encrypted request")
        elif responseJson["errorCode"] == 600002:
            raise Exception("Token expired")
        else:
            raise Exception("Request failed")

    async def ensureKeysPresent(self):
        if self.encKey is None or self.signKey is None:
            await self.retrieveKeys()

    async def ensureTokenIsValid(self):
        if self.accessToken is None or self.accessTokenExpirationTs is None or self.accessTokenExpirationTs <= time.time():
            await self.login()

    async def retrieveKeys(self):
        response = await self.apiRequest("POST", "https://0cxo7m58.mazda.com/prod/service/checkVersion", needsKeys=False, needsAuth=False)

        self.encKey = response["encKey"]
        self.signKey = response["signKey"]

    async def login(self):
        print("login")
        encryptionKeyResponse = await self._session.request("GET", "https://ptznwbh8.mazda.com/appapi/v1/system/encryptionKey?appId=MazdaApp&locale=en-US&deviceId=ACCT1195961580&sdkVersion=11.2.0000.002", headers={"User-Agent": "MyMazda/7.0.1 (Google Pixel 3a; Android 11)"})

        encryptionKeyResponseJson = await encryptionKeyResponse.json()

        publicKey = encryptionKeyResponseJson["data"]["publicKey"]
        encryptedPassword = self.encryptPasswordWithPublicKey(self.password, publicKey)
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

        if loginResponseJson["status"] == "USER_LOCKED":
            raise Exception("Account has been locked")
        if loginResponseJson["status"] != "OK":
            raise Exception("Login failed")

        self.accessToken = loginResponseJson["data"]["accessToken"]
        self.accessTokenExpirationTs = loginResponseJson["data"]["accessTokenExpirationTs"]

    async def getTac(self):
        return await self.apiRequest("GET", "https://0cxo7m58.mazda.com/prod/content/getTac/v4", needsKeys=True, needsAuth=False)

    async def getLanguagePkg(self):
        body = {"platformType": "ANDROID", "region": "MNAO", "version": "2.0.4"}
        return await self.apiRequest("POST", "https://0cxo7m58.mazda.com/prod/junction/getLanguagePkg/v4", bodyDict=body, needsKeys=True, needsAuth=False)

    async def getVehBaseInfos(self):
        return await self.apiRequest("POST", "https://0cxo7m58.mazda.com/prod/remoteServices/getVecBaseInfos/v4", bodyDict={"internaluserid": "__INTERNAL_ID__"}, needsKeys=True, needsAuth=True)

    async def close(self) -> None:
        if self._session:
            await self._session.close()
