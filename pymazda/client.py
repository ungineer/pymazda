import json

from pymazda.controller import Controller


class Client:
    def __init__(self, email, password):
        self.controller = Controller(email, password)

    async def getVehicles(self):
        vecBaseInfos = await self.controller.getVecBaseInfos()

        vehicles = []

        for vecBaseInfo in vecBaseInfos["vecBaseInfos"]:
            otherVehInfo = json.loads(vecBaseInfo["Vehicle"]["vehicleInformation"])

            vehicle = {
                "vin": vecBaseInfo["vin"],
                "id": vecBaseInfo["Vehicle"]["CvInformation"]["internalVin"],
                "carlineCode": otherVehInfo["OtherInformation"]["carlineCode"],
                "carlineName": otherVehInfo["OtherInformation"]["carlineName"],
                "modelYear": otherVehInfo["OtherInformation"]["modelYear"],
                "modelCode": otherVehInfo["OtherInformation"]["modelCode"],
                "modelName": otherVehInfo["OtherInformation"]["modelName"],
                "automaticTransmission": otherVehInfo["OtherInformation"]["transmissionType"] == "A",
                "interiorColorCode": otherVehInfo["OtherInformation"]["interiorColorCode"],
                "interiorColorName": otherVehInfo["OtherInformation"]["interiorColorName"],
                "exteriorColorCode": otherVehInfo["OtherInformation"]["exteriorColorCode"],
                "exteriorColorName": otherVehInfo["OtherInformation"]["exteriorColorName"],
            }

            vehicles.append(vehicle)

        return vehicles

    async def getVehicleStatus(self, vehicleId):
        vehicleStatusResponse = await self.controller.getVehicleStatus(vehicleId)

        alertInfo = vehicleStatusResponse["alertInfos"][0]
        remoteInfo = vehicleStatusResponse["remoteInfos"][0]

        vehicleStatus = {
            "lastUpdatedTimestamp": remoteInfo["OccurrenceDate"],
            "latitude": remoteInfo["PositionInfo"]["Latitude"] * (-1 if remoteInfo["PositionInfo"]["LatitudeFlag"] == 1 else 1),
            "longitude": remoteInfo["PositionInfo"]["Longitude"] * (-1 if remoteInfo["PositionInfo"]["LongitudeFlag"] == 0 else 1),
            "positionTimestamp": remoteInfo["PositionInfo"]["AcquisitionDatetime"],
            "fuelRemainingPercent": remoteInfo["ResidualFuel"]["FuelSegementDActl"],
            "fuelDistanceRemainingKm": remoteInfo["ResidualFuel"]["RemDrvDistDActlKm"],
            "odometerKm": remoteInfo["DriveInformation"]["OdoDispValue"],
            "doors": {
                "driverDoorOpen": alertInfo["Door"]["DrStatDrv"] == 1,
                "passengerDoorOpen": alertInfo["Door"]["DrStatPsngr"] == 1,
                "rearLeftDoorOpen": alertInfo["Door"]["DrStatRl"] == 1,
                "rearRightDoorOpen": alertInfo["Door"]["DrStatRr"] == 1,
                "trunkOpen": alertInfo["Door"]["DrStatTrnkLg"] == 1,
                "hoodOpen": alertInfo["Door"]["DrStatHood"] == 1,
                "fuelLidOpen": alertInfo["Door"]["FuelLidOpenStatus"] == 1
            },
            "doorLocks": {
                "driverDoorUnlocked": alertInfo["Door"]["LockLinkSwDrv"] == 1,
                "passengerDoorUnlocked": alertInfo["Door"]["LockLinkSwPsngr"] == 1,
                "rearLeftDoorUnlocked": alertInfo["Door"]["LockLinkSwRl"] == 1,
                "rearRightDoorUnlocked": alertInfo["Door"]["LockLinkSwRr"] == 1,
            },
            "windows": {
                "driverWindowOpen": alertInfo["Pw"]["PwPosDrv"] == 1,
                "passengerWindowOpen": alertInfo["Pw"]["PwPosPsngr"] == 1,
                "rearLeftWindowOpen": alertInfo["Pw"]["PwPosRl"] == 1,
                "rearRightWindowOpen": alertInfo["Pw"]["PwPosRr"] == 1
            },
            "hazardLightsOn": alertInfo["HazardLamp"]["HazardSw"] == 1,
            "tirePressure": {
                "frontLeftTirePressurePsi": remoteInfo["TPMSInformation"]["FLTPrsDispPsi"],
                "frontRightTirePressurePsi": remoteInfo["TPMSInformation"]["FRTPrsDispPsi"],
                "rearLeftTirePressurePsi": remoteInfo["TPMSInformation"]["RLTPrsDispPsi"],
                "rearRightTirePressurePsi": remoteInfo["TPMSInformation"]["RRTPrsDispPsi"]
            }
        }

        return vehicleStatus

    async def turnHazardLightsOn(self, vehicleId):
        await self.controller.lightOn(vehicleId)

    async def turnHazardLightsOff(self, vehicleId):
        await self.controller.lightOff(vehicleId)

    async def unlockDoors(self, vehicleId):
        await self.controller.doorUnlock(vehicleId)

    async def lockDoors(self, vehicleId):
        await self.controller.lockDoors(vehicleId)

    async def startEngine(self, vehicleId):
        await self.controller.engineStart(vehicleId)

    async def stopEngine(self, vehicleId):
        await self.controller.engineStop(vehicleId)
