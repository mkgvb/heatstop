#!/usr/bin/env python

import asyncio
import websockets
import json
import requests
import time
import sys
import logging

logging.basicConfig(
    handlers=[logging.FileHandler("newlog.log"), logging.StreamHandler()],
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%D:%H:%M:%S',
    level=logging.INFO
)

logging.info("Starting heatstop")

HOT_T=77
COLD_T=71

async def hello(uri):
    attempts = 0
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                while True:
                    msgstr =  await websocket.recv()
                    msgobj = json.loads(msgstr)
                    if "temperature" in msgobj:
                        print(msgstr)
                        for therm in msgobj["temperature"]:
                            msg = ""
                            if therm["id"] == "0417c1ac2bff":
                                msg += "Water temp = {}f".format(therm["value"])
                                if therm["value"] >= HOT_T:
                                    msg += " TOO HOT"
                                    r = requests.get( url="http://localhost:8000/2/off")
                                    logging.warning(msg)
                                elif therm["value"] <= COLD_T:
                                    msg += " TOO COLD"
                                    r = requests.get( url="http://localhost:8000/2/on")
                                    logging.warning(msg)
                            else:
                                msg += "Room temp = {}f".format(therm["value"])
                            print(msg)
        except Exception as e:
            print("Wait 30: {}:".format(e))
            attempts += 1
            if attempts > 30:
                logging.critical("I AM GIVING UP")
                sys.exit(1)
            logging.warning("Attempts={}".format(attempts))
            time.sleep(30)
        

asyncio.get_event_loop().run_until_complete(
    hello('ws://pi:7999/chat/websocket'))
