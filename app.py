#!/usr/bin/env python3
# coding: utf-8

import os
import time
import logging
from logging.handlers import RotatingFileHandler

import serial
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

from config import LEAVES


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


# web stuff

@APP.route('/')
def index():
    LOGGER.debug('rendering index.html for %s' % request.remote_addr)
    return render_template('index.html')


# serial com

def send_command(target, command, response=None):
    if target in range(6):
        error = False
        try:
            with serial.Serial(SERIALDEV, SERIALBAUD, timeout=1) as ser:
                msg = '%d;%s\n' % (target, command)
                if not response:
                    response = '#%s' % msg
                LOGGER.info('sending command: %s' % msg)
                ser.write(msg)

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



def goto(leaf, position):
    if leaf in range(6) and type(position) == int and position >= 0:
        error = False
        try:
            with serial.Serial(SERIALDEV, SERIALBAUD, timeout=1) as ser:
                msg = '%d;move;%d\n' % (leaf, position)
                LOGGER.info('sending command: %s' % msg)
                ser.write(msg)
                ser.write(msg)

                LOGGER.info('waiting for answer..')
                timeout = time.time() + 5
                while True:
                    line = ser.readline()
                    if line == '#%s' % msg:
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



# socketio

@SOCKETIO.on('connected')
def handle_connect_event():
    LOGGER.info('client connected')

@SOCKETIO.on('home')
def handle_home_event(leaf):
    if leaf in (0, 1, 2, 3, 4, 5):
        send_command(leaf, 'home')
    elif leaf == 'all':
        for i in range(6):
            send_command(i, 'home')

@SOCKETIO.on('update')
def handle_update_event(json):
    LOGGER.info('update received, sending it to the others..')
    LOGGER.debug('content was: ' + str(json))
    emit('update', json, broadcast=True)
    # TODO: send it to leafes
    for leaf, value in json.items():
        send_command(leaf, 'move;%d' % value)

@SOCKETIO.on('reset')
def handle_reset_event():
    LOGGER.info('reset all the things!')
    emit('reset', LEAVES, broadcast=True)


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
