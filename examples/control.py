import asyncio
from mymazda import MyMazda


async def main(loop):
    client = MyMazda("brandonrothweiler@gmail.com", "password1")
    print(client)
    return True

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
