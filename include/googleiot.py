#!/usr/bin/env python3

import argparse
import datetime
import logging
import os
import random
import ssl
import time
import json

import jwt
import paho.mqtt.client as mqtt

logging.getLogger('munchi.logger').setLevel(logging.WARNING)

def create_jwt(project_id, private_key_file, algorithm):
    token = {
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        'aud': project_id
    }

    with open(private_key_file, 'r') as f:
        private_key = f.read()

    print('Creating JWT using {} from private key file {}'.format(algorithm, private_key_file))

    return jwt.encode(token, private_key, algorithm=algorithm)

def error_str(rc):
    return '{}: {}'.format(rc, mqtt.error_string(rc))

class Device(object):
    """Represents the state of a Device Object"""

    def __init__(self):
        self.project_id = 'munchi'
        self.cloud_region = 'us-central1'
        self.registry_id = 'munchis'
        self.device_id = 'dev_munchi'
        self.private_key_file = 'include/rsa_private.pem'
        self.algorithm = 'RS256'
        self.ca_certs = 'include/roots.pem'

        self.temperature = 0
        self.cooking = False
        self.connected = False
        self.recipeId = 0

    def update_sensor_data(self):
        """Read Sensor Data"""
        if self.cooking == True:
            self.temperature += 1
        else:
            if self.temperature > 0:
                self.temperature -= 1

    def wait_for_connection(self, timeout):
        total_time = 0
        while not self.connected and total_time < timeout:
            time.sleep(1)
            total_time += 1

        if not self.connected:
            raise RuntimeError('Could not connect to MQTT bridge.')

    def on_connect(self, unused_client, unused_userdata, unused_flags, rc):
        print('Connection Result:', error_str(rc))
        self.connected = True

    def on_disconnect(self, unused_client, unused_userdata, rc):
        print('Disconnected:', error_str(rc))
        self.connected = False

    def on_publish(self, unused_client, unused_userdata, unused_mid):
        print('Published message acked.')

    def on_subscribe(self, unused_client, unused_userdata, unused_mid, granted_qos):
        print('Subscribed: ', granted_qos)
        if granted_qos[0] == 128:
            print('Subscription failed.')

    def on_message(self, unused_client, unused_userdata, message):
        payload = message.payload.decode('utf-8')
        print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(payload, message.topic, str(message.qos)))

        if not payload:
            return

        data = json.loads(payload)
        if data['cooking'] != self.cooking:
            self.cooking = data['cooking']
            if self.cooking:
                print('Started cooking')
            else:
                print('Ended cooking')

class Client(object):

    def __init__(self, deviceID):
        self.project_id = 'munchi'
        self.cloud_region = 'us-central1'
        self.registry_id = 'munchis'
        self.device_id = deviceID
        self.private_key_file = 'include/rsa_private.pem'
        self.algorithm = 'RS256'
        self.ca_certs = 'include/roots.pem'
        self.mqtt_bridge_hostname = 'mqtt.googleapis.com'
        self.mqtt_bridge_port = 8883
        self.num_messages = 25

        self.run()

    def run(self):

        client = mqtt.Client(
            client_id='projects/{}/locations/{}/registries/{}/devices/{}'.format(
                self.project_id,
                self.cloud_region,
                self.registry_id,
                self.device_id))
        client.username_pw_set(
            username='unused',
            password=create_jwt(
                self.project_id,
                self.private_key_file,
                self.algorithm))
        client.tls_set(ca_certs=self.ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

        device = Device()

        client.on_connect = device.on_connect
        client.on_publish = device.on_publish
        client.on_disconnect = device.on_disconnect
        client.on_subscribe = device.on_subscribe
        client.on_message = device.on_message

        client.connect(self.mqtt_bridge_hostname, self.mqtt_bridge_port)

        client.loop_start()

        mqtt_telemetry_topic = '/devices/{}/events'.format(self.device_id)

        mqtt_config_topic = '/devices/{}/config'.format(self.device_id)

        device.wait_for_connection(5)

        client.subscribe(mqtt_config_topic, qos=1)

        for _ in range(self.num_messages):
            device.update_sensor_data()

            payload = json.dumps({'temperature': device.temperature})
            print('Publishing payload', payload)
            client.publish(mqtt_telemetry_topic, payload, qos=1)
            time.sleep(1)

        client.disconnect()
        client.loop_stop()
        print('Finished loop successfully. Goodbye!')