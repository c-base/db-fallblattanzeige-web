#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4:et

import os
import sys
import asyncio
import serial.aio
import RPi.GPIO as GPIO

def setup():
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

class RoloboxProtocol(asyncio.Protocol):

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from %s:%d' % peername)
        self.transport = transport

    def data_received(self, data):
        print('{}: {!r}'.format(self.transport.get_extra_info('peername'), data.decode()))
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
