#!/usr/bin/env python3
# coding: utf-8

import logging
import logging.handlers

from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler('cug.log', maxBytes=1048576, backupCount=2)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)-5s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger.addHandler(handler)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('my broadcast event', namespace='/cyber')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response', {'data': message['data'], 'count': session['receive_count']}, broadcast=True)


@socketio.on('disconnect request', namespace='/cyber')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response', {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
