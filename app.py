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
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('cug.log', maxBytes=1048576, backupCount=2)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)-5s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger.addHandler(handler)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('broadcast', namespace='/cyber')
def broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('response', {'data': bytes(message['data'], 'utf-8'), 'count': session['receive_count']}, broadcast=True)


@socketio.on('disconnect', namespace='/cyber')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('response', {'data': bytes('disconnected', 'utf-8'), 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/cyber')
def test_connect():
    emit('response', {'data': bytes('connected', 'utf-8'), 'count': 0})


@socketio.on('disconnect', namespace='/cyber')
def test_disconnect():
    print('disconnected')


if __name__ == '__main__':
    socketio.run(app)
