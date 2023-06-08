##################################################################################
##############################@A29S###############################################
###########install mqtt.simple module#################### 
#import network
#import mip
#import time

# update with your Wi-Fi network's configuration
#WIFI_SSID = "MEO-4E5AA3"
#WIFI_PASSWORD = "55EBFB2419"

#wlan = network.WLAN(network.STA_IF)

#print(f"Connecting to Wi-Fi SSID: {WIFI_SSID}")

#wlan.active(True)
#wlan.connect(WIFI_SSID, WIFI_PASSWORD)

#while not wlan.isconnected():
 #   time.sleep(0.5)

#print(f"Connected to Wi-Fi SSID: {WIFI_SSID}")

#mip.install("https://raw.githubusercontent.com/micropython/micropython-lib/master/micropython/umqtt.simple/umqtt/simple.py")


# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, PATH_TO_AMAZON_ROOT_CA_1, TOPIC, and RANGE
ENDPOINT = "a1mcj6srl638fo-ats.iot.eu-west-2.amazonaws.com"
CLIENT_ID = "testDevice"
PATH_TO_CERTIFICATE = "31115e61c1c7f1de2b86d19b401cf3654ae605476d124b406a8703b7c19d9bf1-certificate.pem.crt"
PATH_TO_PRIVATE_KEY = "31115e61c1c7f1de2b86d19b401cf3654ae605476d124b406a8703b7c19d9bf1-private.pem.key"
PATH_TO_AMAZON_ROOT_CA_1 = "AmazonRootCA1.pem"
TOPIC = "Lusita/DataBase"
RANGE = 1

# Define the message callback function
def on_message_received(topic, payload, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))

# Spin up resources
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT,
    cert_filepath=PATH_TO_CERTIFICATE,
    pri_key_filepath=PATH_TO_PRIVATE_KEY,
    client_bootstrap=client_bootstrap,
    ca_filepath=PATH_TO_AMAZON_ROOT_CA_1,
    client_id=CLIENT_ID,
    clean_session=False,
    keep_alive_secs=6
)

print("Connecting to {} with client ID '{}'...".format(ENDPOINT, CLIENT_ID))
# Make the connect() call
connect_future = mqtt_connection.connect()
# Future.result() waits until a result is available
connect_future.result()
print("Connected!")

# Subscribe to the desired topic
mqtt_connection.subscribe(topic=TOPIC, qos=mqtt.QoS.AT_LEAST_ONCE, callback=on_message_received)
print("Subscribed to topic: '{}'".format(TOPIC))

# Publish message to server desired number of times
print('Begin Publish')
#for i in range(RANGE):
    
message = {"message": "Hello World {}".format(1)}
mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
print("Published: '{}' to the topic: '{}'".format(json.dumps(message), TOPIC))
t.sleep(0.1)
print('Publish End')

# Keep the program running to receive messages
while True:
    t.sleep(1)

# Disconnect from the MQTT broker
disconnect_future = mqtt_connection.disconnect()
disconnect_future.result()