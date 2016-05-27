#!/usr/bin/env python3
# coding: utf-8

import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit, disconnect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('cug.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)-5s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connected')
def handle_my_custom_event():
    logger.info('client connected')

@socketio.on('update')
def handle_update_event(json):
    logger.info('got an update. sending it to the others.')
    logger.debug('content was: ' + str(json))
    emit('update', json, broadcast=True)

@socketio.on('home')
def handle_update_event(target):
    logger.info('homing event received')
    logger.debug('content was: ' + target)


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
    socketio.run(app)
