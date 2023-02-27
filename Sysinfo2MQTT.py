"""
Skript to read Data from a server and publish it to MQTT
information to psutil to be found here:
https://www.thepythoncode.com/article/get-hardware-system-information-python

The information is published on a topic "server/{uname.node}/[info]/
the data is published as int or float
"""

__author__ = "Patrick Horbach"
__copyright__ = "Copyright 2022, Patrick Horbach"
__license__ = "Apache-2.0 License"
__version__ = "0.1.0"
__maintainer__ = "Patrick Horbach"
__email__ = ""
__status__ = "Production"

import os
import time
import paho.mqtt.client as mqtt
from queue import Queue
import psutil
import platform
from datetime import datetime

# enter MQTT Broker Data here, note, USER and PW are not supported at the moment
BROKER_IP = "192.168.10.100"
BROKER_PORT = 1883

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    client.subscribe(ctlTopic)  # Subscribe to the topic
    client.subscribe(ctlShutdown)  # Subscribe to the topic

def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    if msg.topic == ctlTopic:
        try:
            q.put(int(msg.payload.decode("utf-8")))
            print("Intervall vom MQTT: " + str(msg.payload.decode("utf-8")))
        except:
            print("not an int")
    if msg.topic == ctlShutdown:
        print("poweroff")
        os.system("sudo shutdown now")

#get Systemname
sysname = platform.uname().node
ctlTopic = "server/"+sysname+"/control/UpdateInterval"
ctlShutdown = "server/"+sysname+"/control/poweroff"
client =mqtt.Client(sysname)
client.on_connect = on_connect  # Define callback function for successful connection
client.on_message = on_message  # Define callback function for receipt of a message
client.connect(BROKER_IP, BROKER_PORT) #connect to broker
q=Queue() # we use a queue to get date from the on_message callback to the main

#standard value for update interval
interval = 60

#go on forever
client.loop_start()
while True:

    # get control interval data from queue and set it as sleeptime, limit between 5 and 120
    while not q.empty():
        interval = q.get()
        if interval <= 5: interval = 5
        if interval >= 120: interval = 120

    # Interval
    client.publish("server/"+sysname+"/UpdateInterval", interval)

    # publish boot time of system
    bt = datetime.fromtimestamp(psutil.boot_time())
    client.publish("server/"+sysname+"/bootTime", (f"{bt.year}-{bt.month:02d}-{bt.day:02d} {bt.hour}:{bt.minute}:{bt.second}"))

    # Disk Information
    # get all disk partitions
    partitions = psutil.disk_partitions()
    for partition in partitions:

        # linux systems use "/" in device, this can create strange topics since topics also use "/" so we catch that
        if "/" not in partition.device:
            topic = "server/" + sysname + "/" + partition.device
        else:
            topic = "server/" + sysname + partition.device

        # publish the partition type
        client.publish(topic + "/fstype", str(partition.fstype))

        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that isn't ready
            print("lesen der Daten nicht möglich!")
            continue

        client.publish(topic + "/totalSizeGB", (f"{partition_usage.total/1073741824:.2f}"))
        client.publish(topic + "/usedGB", (f"{partition_usage.used/1073741824:.2f}"))
        client.publish(topic + "/freeGB", (f"{partition_usage.free / 1073741824:.2f}"))
        client.publish(topic + "/usedPCT", (f"{partition_usage.percent}"))

    time.sleep(interval)
