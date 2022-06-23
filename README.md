# pymazda

This is an API client for the MyMazda (Mazda Connected Services) API. This is the API used by the MyMazda mobile app ([iOS](https://apps.apple.com/us/app/mymazda/id451886367)/[Android](https://play.google.com/store/apps/details?id=com.interrait.mymazda)).

Note: There is no official API, and this library may stop working at any time without warning.

There is also a JavaScript version of this library called [node-mymazda](https://github.com/bdr99/node-mymazda).

# Installation

To install the latest release from [PyPI](https://pypi.org/project/pymazda/), run `pip3 install pymazda`.

# Quick Start

This example initializes the API client and gets a list of vehicles linked to the account. Then, for each vehicle, it gets and outputs the vehicle status and starts the engine.

```python
import asyncio
import pymazda

async def test() -> None:
    # Initialize API client (MNAO = North America)
    client = pymazda.Client("myemail", "mypassword", "MNAO")

    # Get list of vehicles from the API (returns a list)
    vehicles = await client.get_vehicles()

    # Loop through the registered vehicles
    for vehicle in vehicles:
        # Get vehicle ID (you will need this in order to perform any other actions with the vehicle)
        vehicle_id = vehicle["id"]

        # Get and output vehicle status
        status = await client.get_vehicle_status(vehicle_id)
        print(status)

        # Start engine
        await client.start_engine(vehicle_id)
    
    # Close the session
    await client.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
```

You will need the email address and password that you use to sign into the MyMazda mobile app. Before using this library, you will need to link your vehicle to your MyMazda account using the app. You will also need the region code for your region. See below for a list of region codes.

When calling these methods, it may take some time for the vehicle to respond accordingly. This is dependent on the quality of the car's connection to the mobile network. It is best to avoid making too many API calls in a short time period of time, as this may result in rate limiting.

# API Documentation

## Initialize API Client

```python
client = pymazda.Client(email, password, region, websession)
```

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `email`   | The email address you use to log into the MyMazda mobile app |
| `password` | The password you use to log into the MyMazda mobile app |
| `region` | The code for the region in which your account was registered<br>Supported regions include:<ul><li>North America (`MNAO`)</li><li>Europe (`MME`)</li><li>Japan (`MJO`)</li></ul> |
| `websession` | Optional. An instance of `aiohttp.ClientSession` to be used for the API requests. If omitted, the library will instantiate its own instance. |
| `use_cached_vehicle_list` | Optional. Set to `True` to enable caching for the `get_vehicles()` call. When `get_vehicles()` is called for the first time, the vehicle list will be fetched from the API and cached in memory. Subsequent calls will return the value from the cache. This may help to avoid rate limiting. |

### Return value

Returns an instance of `pymazda.Client` which can be used to invoke the below methods.

## Get List of Vehicles

```python
await client.get_vehicles()
```

Gets a list of vehicles linked with the MyMazda account. **Only includes vehicles which are compatible with and enrolled in Mazda Connected Services.**

### Parameters

None

### Return value

```jsonc
[
   {
      "vin": "JMXXXXXXXXXXXXXXX",
      "id": 12345,
      "nickname": "My Mazda3",
      "carlineCode": "M3S",
      "carlineName": "MAZDA3 2.5 S SE AWD",
      "modelYear": "2021",
      "modelCode": "M3S  SE XA",
      "modelName": "W/ SELECT PKG AWD SDN",
      "automaticTransmission": true,
      "interiorColorCode": "BY3",
      "interiorColorName": "BLACK",
      "exteriorColorCode": "42M",
      "exteriorColorName": "DEEP CRYSTAL BLUE MICA",
      "isElectric": false
   },
   {
      // Other vehicles registered to your account
   }
]
```

## Get vehicle status

```python
await client.get_vehicle_status(vehicle_id)
```

Get information about the current status of the vehicle. In my experience, this info is usually current as of the last time the vehicle was used.

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `vehicle_id` | Vehicle ID (obtained from `get_vehicles()`) |

### Return value

```jsonc
{
   "lastUpdatedTimestamp": "20210227145504",
   "latitude": 0.000000,
   "longitude": 0.000000,
   "positionTimestamp": "20210227145503",
   "fuelRemainingPercent": 18.0,
   "fuelDistanceRemainingKm": 79.15,
   "odometerKm": 3105.8,
   "doors": {
      "driverDoorOpen": false,
      "passengerDoorOpen": false,
      "rearLeftDoorOpen": false,
      "rearRightDoorOpen": false,
      "trunkOpen": false,
      "hoodOpen": false,
      "fuelLidOpen": false
   },
   "doorLocks":{
      "driverDoorUnlocked": false,
      "passengerDoorUnlocked": false,
      "rearLeftDoorUnlocked": false,
      "rearRightDoorUnlocked": false
   },
   "windows":{
      "driverWindowOpen": false,
      "passengerWindowOpen": false,
      "rearLeftWindowOpen": false,
      "rearRightWindowOpen": false
   },
   "hazardLightsOn": false,
   "tirePressure": {
      "frontLeftTirePressurePsi": 33.0,
      "frontRightTirePressurePsi": 35.0,
      "rearLeftTirePressurePsi": 33.0,
      "rearRightTirePressurePsi": 33.0
   }
}
```

## Get EV vehicle status

```python
await client.get_ev_vehicle_status(vehicle_id)
```

Get additional status information which is specific to electric vehicles. This method should only be called for electric vehicles. To determine if the vehicle is electric, use the `isElectric` attribute from the `get_vehicles()` response.

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `vehicle_id` | Vehicle ID (obtained from `get_vehicles()`) |

### Return value

```jsonc
{
    "lastUpdatedTimestamp": "20210807083956",
    "chargeInfo": {
        "batteryLevelPercentage": 10,
        "drivingRangeKm": 218,
        "pluggedIn": false,
        "charging": true,
        "basicChargeTimeMinutes": 3, // Estimated time in minutes to fully charge using AC charging
        "quickChargeTimeMinutes": 0, // Estimated time in minutes to fully charge using DC charging
        "batteryHeaterAuto": true, // Current battery heater mode (true = auto, false = off)
        "batteryHeaterOn": true // Whether the battery heater is currently running
    },
    "hvacInfo": {
        "hvacOn": true,
        "frontDefroster": false,
        "rearDefroster": false,
        "interiorTemperatureCelsius": 15.1 // Current interior temperature of the car (actual temperature, not the HVAC setting)
    }
}
```

## Start Engine

```python
await client.start_engine(vehicle_id)
```

Starts the engine. May take some time for the engine to start.

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `vehicle_id` | Vehicle ID (obtained from `get_vehicles()`) |

### Return value

None

## Stop Engine

```python
await client.stop_engine(vehicle_id)
```

Stops the engine. I believe this only works if the engine was started remotely (using Mazda Connected Services).

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `vehicle_id` | Vehicle ID (obtained from `get_vehicles()`) |

### Return value

None

## Lock Doors

```python
await client.lock_doors(vehicle_id)
```

Locks the doors.

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `vehicle_id` | Vehicle ID (obtained from `get_vehicles()`) |

### Return value

None

## Unlock Doors

```python
await client.unlock_doors(vehicle_id)
```

Unlocks the doors.

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `vehicle_id` | Vehicle ID (obtained from `get_vehicles()`) |

### Return value

None

## Turn On Hazard Lights

```python
await client.turn_on_hazard_lights(vehicle_id)
```

Turns on the vehicle hazard lights.

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `vehicle_id` | Vehicle ID (obtained from `get_vehicles()`) |

### Return value

None

## Turn Off Hazard Lights

```python
await client.turn_off_hazard_lights(vehicle_id)
```

Turns off the vehicle hazard lights.

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `vehicle_id` | Vehicle ID (obtained from `get_vehicles()`) |

### Return value

None

## Send POI

```python
await client.send_poi(vehicle_id, latitude, longitude, poi_name)
```

Send a GPS location to the vehicle's navigation. Requires a navigation SD card in the vehicle.

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `vehicle_id` | Vehicle ID (obtained from `get_vehicles()`) |
| `latitude` | Latitude of the POI location |
| `longitude` | Longitude of the POI location|
| `poi_name` | A friendly name for the location (e.g. "Work") |

### Return value

None

## Start Charging

```python
await client.start_charging(vehicle_id)
```

Starts charging the battery (only for electric vehicles).

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `vehicle_id` | Vehicle ID (obtained from `get_vehicles()`) |

### Return value

None

## Stop Charging

```python
await client.stop_charging(vehicle_id)
```

Stops charging the battery (only for electric vehicles).

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `vehicle_id` | Vehicle ID (obtained from `get_vehicles()`) |

### Return value

None

## Get HVAC Setting

```python
await client.get_hvac_setting(vehicle_id)
```

Get the current settings for the vehicle's HVAC system. Only for electric vehicles.

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `vehicle_id` | Vehicle ID (obtained from `get_vehicles()`) |

### Return value

```jsonc
{
    "temperature": 20, // Current target temperature (NOT the current interior temperature reading)
    "temperatureUnit": "C",
    "frontDefroster": true,
    "rearDefroster": false
}
```

## Set HVAC Setting

```python
await client.set_hvac_setting(vehicle_id, temperature, temperature_unit, front_defroster, rear_defroster)
```

Set the HVAC settings for the vehicle's HVAC system. Only for electric vehicles.

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `vehicle_id` | Vehicle ID (obtained from `get_vehicles()`) |
| `temperature` | Desired target temperature |
| `temperature_unit` | Temperature unit - `"F"` or `"C"` |
| `front_defroster` | Whether to use the front defroster - `True` or `False` |
| `rear_defroster` | Whether to use the rear defroster - `True` or `False` |

### Return value

None

## Turn On HVAC

```python
await client.turn_on_hvac(vehicle_id)
```

Turn on the vehicle's HVAC system. Only for electric vehicles.

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `vehicle_id` | Vehicle ID (obtained from `get_vehicles()`) |

### Return value

None

## Turn Off HVAC

```python
await client.turn_off_hvac(vehicle_id)
```

Turn off the vehicle's HVAC system. Only for electric vehicles.

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `vehicle_id` | Vehicle ID (obtained from `get_vehicles()`) |

### Return value

None

## Refresh Vehicle Status

```python
await client.refresh_vehicle_status(vehicle_id)
```

Request a new status update from the vehicle. This is only for electric vehicles, and it only updates the info returned by `get_ev_vehicle_status()`, not `get_vehicle_status()`.

### Parameters

| Parameter | Description |
| --------- | ----------- |
| `vehicle_id` | Vehicle ID (obtained from `get_vehicles()`) |

### Return value

None

## Close Session

```python
await client.close()
```

This releases the `ClientSession` used by `aiohttp` to make the API requests. You should close the session when you are finished making requests.

### Parameters

None

### Return value

None