#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4:et

import json
import paho.mqtt.client as mqtt
import socket 
import time

client = mqtt.Client(client_id="piui_roll2")
client.connect("msggwt1.service.deutschebahn.com", 1905, 60)



def status_sender(host, port, content):

    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(content.encode('utf-8'))
    data=s.recv(1024)
    s.close
    data = str(data, 'utf-8')
    client.publish("PIUI/rollerin", payload=data, qos=0, retain=False)

if __name__ == "__main__":
    print("trying")
    while True:
        status_sender("127.0.0.1", 8888, "status")
        time.sleep(10)
