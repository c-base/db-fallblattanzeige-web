#!/usr/bin/env python3
# coding: utf-8

import time
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, disconnect


APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'secret!'
SOCKETIO = SocketIO(APP)

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
fh = RotatingFileHandler('fia.log', maxBytes=1024*1024*1024, backupCount=3)
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


def send_command(command):
    """
    Sends a command to the socket of the control daemon.

    :param command: the command and it's parameters
    :type command: str
    :return: False or error message
    :rtype: str
    """
    pass

@SOCKETIO.on('connect')
def handle_connect_event():
    """
    A new web client established a connection.
    """
    LOGGER.info('[%s] connected' % request.remote_addr)
    emit('connected')


@SOCKETIO.on('disconnect')
def handle_connect_event():
    """
    A web client closed a connection.
    """
    LOGGER.info('[%s] disconnected' % request.remote_addr)


@SOCKETIO.on('home')
def handle_home_event(drum):
    """
    Home a leaf or all of them.

    :param drum: id of the leaf controller to home or 'all' to home all
    :type drum: int | 'all'
    """
    LOGGER.info('[%s] requested homing' % request.remote_addr)
    send_command('home')


@SOCKETIO.on('resetme')
def handle_resetme_event():
    """
    Resets the content of a web client.
    """
    LOGGER.info('[%s] wants fresh content' % request.remote_addr)
    data = send_command('status')
    emit('reset', data)


@SOCKETIO.on('go')
def handle_update_event(json):
    """
    A client changed something. Now push the update to the leafes.

    :param json: A JSON dict with the drum and the value it should be set to
    :type json: dict
    """
    LOGGER.info('[%s] wants to switch drum %d to %d' % (request.remote_addr, json['drum'], json['index']))
    send_command('go %d %d' % (json['drum'], json['index']))


def get_update_from_drums():
    # TODO: get update
    #if update:
    #    emit('update', json, broadcast=True)
    pass


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
