#!/usr/bin/env python3
# coding: utf-8

import os
import time
import logging
from logging.handlers import RotatingFileHandler

import serial
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, disconnect

from config import LEAFS


APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'secret!'
SOCKETIO = SocketIO(APP)

SERIALDEV = '/dev/ttyUSB0'
SERIALBAUD = 9600

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
fh = RotatingFileHandler('cug.log', maxBytes=1024*1024*1024, backupCount=3)
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)-5s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
LOGGER.addHandler(fh)
LOGGER.addHandler(ch)


@APP.route('/')
def index():
    """
    Renders the index page.

    :return: rendered page
    :rtype: str
    """
    LOGGER.debug('rendering index.html for %s' % request.remote_addr)
    return render_template('index.html')


def send_command(target, command, response=None):
    """
    Sends a command to the leaf controller bus. The target leaf should parse the command send a response and then
    execute it.

    :param target: id of the leaf to send the command to
    :type target: int
    :param command: the command and it's parameters
    :type command: str
    :param response: the expected response
    :type response: str
    :return: False or error message
    :rtype: str
    """
    if target in range(6):
        error = False
        try:
            with serial.Serial(SERIALDEV, SERIALBAUD, timeout=1) as ser:
                msg = '%d;%s\n' % (target, command)
                if not response:
                    response = '#%s' % msg
                LOGGER.info('sending command: %s' % msg)
                ser.write(bytes(msg, encoding='utf-8'))

                LOGGER.info('waiting for answer..')
                timeout = time.time() + 5
                while True:
                    line = ser.readline()
                    if line ==  response:
                        LOGGER.info('command execution successful')
                        break
                    elif time.time() > timeout:
                        error = 'timeout'
                        LOGGER.error('timeout while sending command: %s' % msg)
                        break
            return error
        except Exception as e:
            LOGGER.error('unexpected error while sending command: %s' % e.with_traceback())
            return e
    LOGGER.warn('invalid leaf id given')
    return 'invalid leave id'


@SOCKETIO.on('connect')
def handle_connect_event():
    """
    A new web client established a connection.
    """
    LOGGER.info('[%s] client connected' % request.remote_addr)
    emit('connected')

@SOCKETIO.on('disconnect')
def handle_connect_event():
    """
    A web client closed a connection.
    """
    LOGGER.info('[%s] client disconnected' % request.remote_addr)
    # TODO: how do we disconnect? is this even necessary?
    #disconnect()

@SOCKETIO.on('home')
def handle_home_event(leaf):
    """
    Home a leaf or all of them.

    :param leaf: id of the leaf controller to home or 'all' to home all
    :type leaf: int | 'all'
    """
    LOGGER.info('[%s] home command received' % request.remote_addr)
    if leaf in (0, 1, 2, 3, 4, 5):
        send_command(leaf, 'home')
    elif leaf == 'all':
        for i in range(6):
            send_command(i, 'home')

@SOCKETIO.on('update')
def handle_update_event(json):
    """
    A client changed something. Now push the update to the leafes.

    :param json: A JSON string with all values
    :type json: str
    """
    LOGGER.info('[%s] update received, sending it to the others..') % request.remote_addr
    LOGGER.debug('content was: ' + str(json))
    emit('update', json, broadcast=True)
    # TODO: send it to leafes
    for leaf, value in json.items():
        send_command(leaf, 'move;%d' % value)

@SOCKETIO.on('resetme')
def handle_reset_event():
    """
    Resets the content of all web clients.
    """
    LOGGER.info('[%s] reset event received. sending fresh leafes' % request.remote_addr)
    data = {}
    for leaf, leafdata in LEAFS.items():
        data[leaf] = {}
        for k, v in leafdata.items():
            if v is not None:
                data[leaf][k] = v
    emit('reset', data)


#@socketio.on('broadcast', namespace='/cyber')
#def broadcast_message(message):
#    session['receive_count'] = session.get('receive_count', 0) + 1
#    emit('response', {'data': bytes(message['data'], 'utf-8'), 'count': session['receive_count']}, broadcast=True)


#@socketio.on('disconnect', namespace='/cyber')
#def disconnect_request():
#    session['receive_count'] = session.get('receive_count', 0) + 1
#    emit('response', {'data': bytes('disconnected', 'utf-8'), 'count': session['receive_count']})
#    disconnect()


#@socketio.on('connect', namespace='/cyber')
#def test_connect():
#    emit('response', {'data': bytes('connected', 'utf-8'), 'count': 0})


#@socketio.on('disconnect', namespace='/cyber')
#def test_disconnect():
#    print('disconnected')


if __name__ == '__main__':
    SOCKETIO.run(APP)
