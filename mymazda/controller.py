from mymazda.connection import Connection


class Controller:
    def __init__(self, email, password):
        self.connection = Connection(email, password)

    async def getTac(self):
        return await self.connection.apiRequest("GET", "content/getTac/v4", needsKeys=True, needsAuth=False)

    async def getLanguagePkg(self):
        postBody = {"platformType": "ANDROID", "region": "MNAO", "version": "2.0.4"}
        return await self.connection.apiRequest("POST", "junction/getLanguagePkg/v4", bodyDict=postBody, needsKeys=True, needsAuth=False)

    async def getVecBaseInfos(self):
        return await self.connection.apiRequest("POST", "remoteServices/getVecBaseInfos/v4", bodyDict={"internaluserid": "__INTERNAL_ID__"}, needsKeys=True, needsAuth=True)

    async def getVehicleStatus(self, internalVin):
        postBody = {
            "internaluserid": "__INTERNAL_ID__",
            "internalvin": internalVin,
            "limit": 1,
            "offset": 0,
            "vecinfotype": "0"
        }
        response = await self.connection.apiRequest("POST", "remoteServices/getVehicleStatus/v4", bodyDict=postBody, needsKeys=True, needsAuth=True)

        if response["resultCode"] != "200S00":
            raise Exception("Failed to get vehicle status")

        return response

    async def getHealthReport(self, internalVin):
        postBody = {
            "internaluserid": "__INTERNAL_ID__",
            "internalvin": internalVin,
            "limit": 1,
            "offset": 0
        }

        response = await self.connection.apiRequest("POST", "remoteServices/getHealthReport/v4", bodyDict=postBody, needsKeys=True, needsAuth=True)

        if response["resultCode"] != "200S00":
            raise Exception("Failed to get health report")

        return response

    async def doorUnlock(self, internalVin):
        postBody = {
            "internaluserid": "__INTERNAL_ID__",
            "internalvin": internalVin
        }

        response = await self.connection.apiRequest("POST", "remoteServices/doorUnlock/v4", bodyDict=postBody, needsKeys=True, needsAuth=True)

        if response["resultCode"] != "200S00":
            raise Exception("Failed to unlock door")

        return response

    async def doorLock(self, internalVin):
        postBody = {
            "internaluserid": "__INTERNAL_ID__",
            "internalvin": internalVin
        }

        response = await self.connection.apiRequest("POST", "remoteServices/doorLock/v4", bodyDict=postBody, needsKeys=True, needsAuth=True)

        if response["resultCode"] != "200S00":
            raise Exception("Failed to lock door")

        return response

    async def lightOn(self, internalVin):
        postBody = {
            "internaluserid": "__INTERNAL_ID__",
            "internalvin": internalVin
        }

        response = await self.connection.apiRequest("POST", "remoteServices/lightOn/v4", bodyDict=postBody, needsKeys=True, needsAuth=True)

        if response["resultCode"] != "200S00":
            raise Exception("Failed to turn light on")

        return response

    async def lightOff(self, internalVin):
        postBody = {
            "internaluserid": "__INTERNAL_ID__",
            "internalvin": internalVin
        }

        response = await self.connection.apiRequest("POST", "remoteServices/lightOff/v4", bodyDict=postBody, needsKeys=True, needsAuth=True)

        if response["resultCode"] != "200S00":
            raise Exception("Failed to turn light off")

        return response

    async def engineStart(self, internalVin):
        postBody = {
            "internaluserid": "__INTERNAL_ID__",
            "internalvin": internalVin
        }

        response = await self.connection.apiRequest("POST", "remoteServices/engineStart/v4", bodyDict=postBody, needsKeys=True, needsAuth=True)

        if response["resultCode"] != "200S00":
            raise Exception("Failed to start engine")

        return response

    async def engineStop(self, internalVin):
        postBody = {
            "internaluserid": "__INTERNAL_ID__",
            "internalvin": internalVin
        }

        response = await self.connection.apiRequest("POST", "remoteServices/engineStop/v4", bodyDict=postBody, needsKeys=True, needsAuth=True)

        if response["resultCode"] != "200S00":
            raise Exception("Failed to stop engine")

        return response
