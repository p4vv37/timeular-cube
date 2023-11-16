import simplepyble
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


import sys
from PyQt5 import QtGui
from PyQt5 import QtWidgets


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        menu = QtWidgets.QMenu(parent)
        exitAction = menu.addAction("Exit")
        self.setContextMenu(menu)


import asyncio
import logging
import threading
from functools import partial
import pystray

from PIL import Image
# After putting the computer to sleep, the cube will not reconnect

from bleak import BleakClient

logging.basicConfig()
logger = logging.getLogger("hackaru_timular")
logger.setLevel(logging.INFO)


MODEL_NUMBER_UUID = "00002a24-0000-1000-8000-00805f9b34fb"
MANUFACTURER_UUID = "00002a29-0000-1000-8000-00805f9b34fb"
SERIAL_NUMBER_UUID = "00002a25-0000-1000-8000-00805f9b34fb"
HARDWARE_REVISION_UUID = "00002a27-0000-1000-8000-00805f9b34fb"
SOFTWARE_REVISION_UUID = "00002a28-0000-1000-8000-00805f9b34fb"
FIRMWARE_REVISION_UUID = "00002a26-0000-1000-8000-00805f9b34fb"
ORIENTATION_UUID = "c7e70012-c847-11e6-8175-8c89a55d403c"

async def print_device_information(client):
    """Print device information about the connected Timular cube"""

    model_number = await client.read_gatt_char(MODEL_NUMBER_UUID)
    logger.info("Model Number: %s", "".join(map(chr, model_number)))

    manufacturer = await client.read_gatt_char(MANUFACTURER_UUID)
    logger.info("Manufacturer: %s", "".join(map(chr, manufacturer)))

    serial_number = await client.read_gatt_char(SERIAL_NUMBER_UUID)
    logger.info("Serial Number: %s", "".join(map(chr, serial_number)))

    hardware_revision = await client.read_gatt_char(HARDWARE_REVISION_UUID)
    logger.info("Hardware Revision: %s", "".join(map(chr, hardware_revision)))

    software_revision = await client.read_gatt_char(SOFTWARE_REVISION_UUID)
    logger.info("Software Revision: %s", "".join(map(chr, software_revision)))

    firmware_revision = await client.read_gatt_char(FIRMWARE_REVISION_UUID)
    logger.info("Firmware Revision: %s", "".join(map(chr, firmware_revision)))

DEVICE_ADDRESS = "DA:B5:2A:B7:08:CC"

SIDES = [
    "Side A",
    "Side B",
    "Side C",
    "Side D",
    "Side E",
    "Side F",
    "Side G",
    "Side H",
]

def callback(*args):
    side_id = int.from_bytes(args[-1], byteorder='big')
    print(SIDES[side_id])

from bleak import BleakScanner
import time
async def BLELoop():
    """Main loop listening for orientation changes"""
    print("Listing devices...")
    t0 = time.time()
    devices = await BleakScanner.discover()
    print("Done in %.3f seconds" % (time.time() - t0))
    for d in devices:
        print(d)
    print("Connecting to device...")
    t0 = time.time()
    try:
        async with BleakClient(DEVICE_ADDRESS, timeout=60) as client:
            print("Connected!")
            print("Done in %.3f seconds" % (time.time() - t0))
            await print_device_information(client)

            await client.start_notify(ORIENTATION_UUID, callback)
            while not False:
                await asyncio.sleep(1)
            await asyncio.sleep(1)
    except Exception as e:
        print("!", e)

loop = asyncio.new_event_loop()
threading.Thread(target=loop.run_forever).start()
asyncio.run_coroutine_threadsafe(BLELoop(), loop)


def main():
    app = QtWidgets.QApplication(sys.argv)

    w = QtWidgets.QWidget()
    trayIcon = SystemTrayIcon(QtGui.QIcon("icon.svg"), w)

    trayIcon.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
