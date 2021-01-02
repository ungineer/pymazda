# pymazda

This is an API client for the MyMazda (Mazda Connected Services) API.

Note: There is no official API, and this library may stop working at any time without warning.

## Usage
```python
import pymazda

async def test() -> None:
    # Initialize API client
    client = pymazda.Client("myemail", "mypassword")

    # Get list of vehicles from the API
    vehicles = await client.getVehicles()

    # Loop through the registered vehicles
    for vehicle in vehicles:
        # Get vehicle status
        status = await client.getVehicleStatus(vehicle["id"])
        print(status)

        # Turn on hazard lights
        await client.turnHazardLightsOn(vehicle["id"])

        # Start engine
        await client.startEngine(vehicle["id"])

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
```