#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4:et

import os
import sys
import asyncio
import serial.aio
import RPi.GPIO as GPIO
import configparser
import json
import paho.mqtt.client as mqtt


DRUM_CONFIGS_DIR = os.path.join(os.path.dirname(__file__), 'drum_configs')
drums = []

client = mqtt.Client(client_id="piui_roll")
try:
    client.connect("msggwt1.service.deutschebahn.com", 1905, 60)
except:
    print("Sorry mqtt connection didn't work")

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(23, GPIO.OUT)#, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(24, GPIO.OUT)#, pull_up_down=GPIO.PUD_DOWN)
    GPIO.output(23, GPIO.HIGH)
    GPIO.output(24, GPIO.HIGH)

def shutdown():
    # Close the server
    socket_proto.close()
    loop.run_until_complete(socket_proto.wait_closed())
    loop.close()
    GPIO.output(23, GPIO.LOW)
    GPIO.output(24, GPIO.LOW)


def get_drum_by_address(addr):
    global drums
    for drum in drums:
        if drum.address == addr:
            return drum
    return None

class Drum(object):
    def __init__(self, name, address, pages, sensor_shift, strings):
        self.name = name
        self.address = int(address)
        self.pages = int(pages)
        self.strings = strings
        self.sensor_shift = sensor_shift
        if len(strings) < pages:
            self.strings = strings + ["n/a"] * (pages - len(strings))
        self.current_page = 0

    def get_current_page(self):
        """
        Get a tuple of current page number and page string
        """
        return self.current_page, strings[current_page]

    def set_current_page(self, page):
        """
        Change the current page of this drum
        """
        self.current_page = page
        #publsih page to mqtt 
        client.publish("PIUI/display"), payload = page, qos=0, retain=False)

    def get_available_pages(self):
        """
        Get a list of all available pages with their page numbers.
        Filter out the empty pages
        """
        ps = filter(lambda x: x != '', enumerate(self.strings))
        retval = []
        for p in ps:
            retval.append({"index": p[0], "label": p[1]})
        return retval

    def get_status(self):
        """
        Get a dict of the current state for JSON serilization.
        """
        return {
            'name': self.name,
            'address': self.address,
            'pages': self.pages,
            'current_page': self.current_page,
            'current_label': self.strings[self.current_page]
        }

    def advance_pages(self, num):
        self.current_page = (self.current_page + num) % self.pages

    def get_index_by_label(self, label):
        for index, bla in enumerate(self.strings):
            if bla == label:
                return index

        return None 

    
    def __repr__(self):
        return '<Drum name={} addr={} pages={}>'.format(self.name, self.address, self.pages)


def read_strings(filename):
    strings = []
    infh = open(filename, mode='r')
    for line in infh.readlines():
       strings.append(line.strip())
    return strings

def iterate_drum_configs():
    drums = []
    for root, dirs, files in os.walk(DRUM_CONFIGS_DIR, topdown=False):
        for name in files:
            full_path = os.path.join(root, name)
            basename, ext = os.path.splitext(name)
            if ext == '.conf':
                print('found {}'.format(name))
                config = configparser.ConfigParser()
                config.read(full_path)

                strings_path = os.path.join(root, '{}.strings'.format(basename))
                strings = read_strings(strings_path)

                d = Drum(config.get('Drum', 'name'), config.get('Drum', 'address'), 
                         config.getint('Drum', 'pages'), config.get('Drum', 'sensor_shift'), 
                         strings)
            
                drums.append(d)
    return sorted(drums, key=lambda x: x.address)


class RoloboxProtocol(asyncio.Protocol):

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from %s:%d' % peername)
        self.transport = transport

    def data_received(self, data):
        global drums
        print('{}: {!r}'.format(self.transport.get_extra_info('peername'), data.decode()))
        msg = data.decode().strip()
        if msg == 'status':
            status = [d.get_status() for d in drums]
            json_status = json.dumps(status) + '\n'
            self.transport.write(json_status.encode('utf-8'))
        elif msg.startswith('labels'):
            cmd, address = msg.split(' ', 1)
            drum = get_drum_by_address(int(address))
            json_status = json.dumps(drum.get_available_pages()) + "\n"
            self.transport.write(json_status.encode('utf-8'))
        elif msg.startswith('go'):
            cmd, address, index = msg.split(' ', 2)
            drum = get_drum_by_address(int(address))
            try:
                index = int(index)
            except ValueError:
                lbl = index
                index = drum.get_index_by_label(lbl)
                print("found {} as {}".format(lbl, index))
            drum.current_page = 0
            if index == 0:
                data = '{}/{}/0\n'.format(int(address), drum.sensor_shift)
            else:
                adv = index
                drum.advance_pages(adv)
                data = '{}/{}/0\n'.format(int(address), drum.sensor_shift)
                data += '{}/{}/adv\n'.format(int(address), drum.sensor_shift, adv)
            asyncio.async(self.send_message(data.encode('utf-8')))
        else:
            address, advance_pages = msg.split('/', 1)
            address = int(address)
            advance_pages = int(advance_pages)
            print('advance by {} on {}'.format(advance_pages, address))
            drum = get_drum_by_address(address)
            if drum is None:
                self.transport.write(b"error: wrong address\n")
                return
            if advance_pages > 100:
                self.transport.write(b"error: too many pages\n")
                return

            drum.advance_pages(advance_pages)
            asyncio.async(self.send_message(data))

    @asyncio.coroutine
    def send_message(self, message):
        print('Sending to serial: {!r}'.format(message))
        serial_proto[0].write(message)
        
    def connection_lost(self, exc):
        print('The server closed the connection')


class SerialProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        print('port opened', transport)

    def data_received(self, data):
        print('From serial: {!r}'.format(data.decode()))

    def connection_lost(self, exc):
        print('port closed')
        asyncio.get_event_loop().stop()


drums = iterate_drum_configs()
setup()
loop = asyncio.get_event_loop()
socket_coroutine = loop.create_server(RoloboxProtocol, '0.0.0.0', 8888)
socket_proto = loop.run_until_complete(socket_coroutine)
print('Serving on %s:%d' % socket_proto.sockets[0].getsockname())

try:
    serial_coroutine = serial.aio.create_serial_connection(loop, SerialProtocol, '/dev/ttyAMA0', baudrate=9600)
    serial_proto = loop.run_until_complete(serial_coroutine)
    loop.run_forever()
except serial.serialutil.SerialException as e:
    print(e)
except KeyboardInterrupt:
    pass
finally:
    shutdown()
