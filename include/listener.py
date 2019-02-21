########################################################
############ COPYRIGHT (c) 2019 Tesla Works ############
########################################################
#################### listener.py #######################
########################################################

import os
import paho.mqtt.client as mqtt

class Listener:

    def __init__(self):
        self.name = "Nick Knudsen"

    def printName(self):
        print(self.name)

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))