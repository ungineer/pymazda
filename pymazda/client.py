import json

from pymazda.controller import Controller
from pymazda.exceptions import MazdaConfigException

class Client:
    def __init__(self, email, password, region, websession=None):
        if email is None or len(email) == 0:
            raise MazdaConfigException("Invalid or missing email address")
        if password is None or len(password) == 0:
            raise MazdaConfigException("Invalid or missing password")

        self.controller = Controller(email, password, region, websession)

    async def validate_credentials(self):
        await self.controller.login()
    
    async def get_vehicles(self):
        vec_base_infos_response = await self.controller.get_vec_base_infos()

        vehicles = []
        for i, current_vec_base_info in enumerate(vec_base_infos_response["vecBaseInfos"]):
            current_vehicle_flags = vec_base_infos_response["vehicleFlags"][i]

            # Ignore vehicles which are not enrolled in Mazda Connected Services
            if current_vehicle_flags["vinRegistStatus"] != 3:
                continue

            other_veh_info = json.loads(current_vec_base_info["Vehicle"]["vehicleInformation"])

            nickname = await self.controller.get_nickname(current_vec_base_info["vin"])
            
            vehicle = {
                "vin": current_vec_base_info["vin"],
                "id": current_vec_base_info["Vehicle"]["CvInformation"]["internalVin"],
                "nickname": nickname,
                "carlineCode": other_veh_info["OtherInformation"]["carlineCode"],
                "carlineName": other_veh_info["OtherInformation"]["carlineName"],
                "modelYear": other_veh_info["OtherInformation"]["modelYear"],
                "modelCode": other_veh_info["OtherInformation"]["modelCode"],
                "modelName": other_veh_info["OtherInformation"]["modelName"],
                "automaticTransmission": other_veh_info["OtherInformation"]["transmissionType"] == "A",
                "interiorColorCode": other_veh_info["OtherInformation"]["interiorColorCode"],
                "interiorColorName": other_veh_info["OtherInformation"]["interiorColorName"],
                "exteriorColorCode": other_veh_info["OtherInformation"]["exteriorColorCode"],
                "exteriorColorName": other_veh_info["OtherInformation"]["exteriorColorName"]
            }

            vehicles.append(vehicle)

        return vehicles

    async def get_vehicle_status(self, vehicle_id):
        vehicle_status_response = await self.controller.get_vehicle_status(vehicle_id)

        alert_info = vehicle_status_response["alertInfos"][0]
        remote_info = vehicle_status_response["remoteInfos"][0]

        vehicle_status = {
            "lastUpdatedTimestamp": remote_info["OccurrenceDate"],
            "latitude": remote_info["PositionInfo"]["Latitude"] * (-1 if remote_info["PositionInfo"]["LatitudeFlag"] == 1 else 1),
            "longitude": remote_info["PositionInfo"]["Longitude"] * (-1 if remote_info["PositionInfo"]["LongitudeFlag"] == 0 else 1),
            "positionTimestamp": remote_info["PositionInfo"]["AcquisitionDatetime"],
            "fuelRemainingPercent": remote_info["ResidualFuel"]["FuelSegementDActl"],
            "fuelDistanceRemainingKm": remote_info["ResidualFuel"]["RemDrvDistDActlKm"],
            "odometerKm": remote_info["DriveInformation"]["OdoDispValue"],
            "doors": {
                "driverDoorOpen": alert_info["Door"]["DrStatDrv"] == 1,
                "passengerDoorOpen": alert_info["Door"]["DrStatPsngr"] == 1,
                "rearLeftDoorOpen": alert_info["Door"]["DrStatRl"] == 1,
                "rearRightDoorOpen": alert_info["Door"]["DrStatRr"] == 1,
                "trunkOpen": alert_info["Door"]["DrStatTrnkLg"] == 1,
                "hoodOpen": alert_info["Door"]["DrStatHood"] == 1,
                "fuelLidOpen": alert_info["Door"]["FuelLidOpenStatus"] == 1
            },
            "doorLocks": {
                "driverDoorUnlocked": alert_info["Door"]["LockLinkSwDrv"] == 1,
                "passengerDoorUnlocked": alert_info["Door"]["LockLinkSwPsngr"] == 1,
                "rearLeftDoorUnlocked": alert_info["Door"]["LockLinkSwRl"] == 1,
                "rearRightDoorUnlocked": alert_info["Door"]["LockLinkSwRr"] == 1,
            },
            "windows": {
                "driverWindowOpen": alert_info["Pw"]["PwPosDrv"] == 1,
                "passengerWindowOpen": alert_info["Pw"]["PwPosPsngr"] == 1,
                "rearLeftWindowOpen": alert_info["Pw"]["PwPosRl"] == 1,
                "rearRightWindowOpen": alert_info["Pw"]["PwPosRr"] == 1
            },
            "hazardLightsOn": alert_info["HazardLamp"]["HazardSw"] == 1,
            "tirePressure": {
                "frontLeftTirePressurePsi": remote_info["TPMSInformation"]["FLTPrsDispPsi"],
                "frontRightTirePressurePsi": remote_info["TPMSInformation"]["FRTPrsDispPsi"],
                "rearLeftTirePressurePsi": remote_info["TPMSInformation"]["RLTPrsDispPsi"],
                "rearRightTirePressurePsi": remote_info["TPMSInformation"]["RRTPrsDispPsi"]
            }
        }

        return vehicle_status

    async def turn_on_hazard_lights(self, vehicle_id):
        await self.controller.light_on(vehicle_id)

    async def turn_off_hazard_lights(self, vehicle_id):
        await self.controller.light_off(vehicle_id)

    async def unlock_doors(self, vehicle_id):
        await self.controller.door_unlock(vehicle_id)

    async def lock_doors(self, vehicle_id):
        await self.controller.door_lock(vehicle_id)

    async def start_engine(self, vehicle_id):
        await self.controller.engine_start(vehicle_id)

    async def stop_engine(self, vehicle_id):
        await self.controller.engine_stop(vehicle_id)
