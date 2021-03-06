#!/usr/bin/env python3
# coding: utf-8
# vim: ts=4:et

import os
import time
import json
import logging
import socket
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, disconnect
import random
from colors import colors

APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'secret!'
SOCKETIO = SocketIO(APP)

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
fh = RotatingFileHandler('fia.log', maxBytes=1024*1024*1024, backupCount=3)
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)-5s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
LOGGER.addHandler(fh)
LOGGER.addHandler(ch)

# Global storage for a background thread
thread = None

HOSTS = {
        'alice': "127.0.0.1",
        'bob': "10.0.0.155",
        }        

PLAYLIST = [] # will be filled from playlist.txt at bootup
LABELS = None
PLAYLIST_FILE = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'playlist.txt')

MODE_WORKSHOP = 'workshop'
MODE_SHUFFLE= 'shuffle'
MODE_PARTY = 'party'
MODE_NORMAL = 'normal'
MODE = MODE_NORMAL

POS = 0

@APP.route('/')
def index():
    """
    Renders the index page.

    :return: rendered page
    :rtype: str
    """
    LOGGER.debug('rendering index.html for %s' % request.remote_addr)
    return render_template('index.html')

def ack():
    """
    Background thread that is activated when the first user connects and
    used to do random stuff during party mode.
    """
    i = 0
    while True:
        if MODE == MODE_PARTY:
            LOGGER.info('PARTEY!')
            host = random.choice(list(HOSTS.keys()))
            color = random.choice(colors)
            ww = random.randint(0, 100)
            bla = {'rgb': '#{}'.format(color), 'ww': ww, 'hostname': host}
            changeme(bla)
            LOGGER.info("BLA:" + repr(bla))
            if i % 20 == 0:
                blub = {'hostname': host}
                labels = get_labels()
                key = random.choice(list(labels.keys()))
                while True:
                    selected = random.choice(labels[key])
                    if selected['label'] != '':
                        break
                blub[key] = selected['index']
                LOGGER.info("BLUB:" + repr(blub))
                changeme(blub)
        else:
            # do nothing
            pass
        SOCKETIO.sleep(1.0)
        i += 1


@APP.route('/button')
def button():
    """
    Reacts to someone pressing THE BUTTON.
    """
    LOGGER.debug('Someone pressed the button.')
    global POS
    global APP
    global SOCKETIO
    global PLAYLIST
    global MODE
    if MODE == MODE_WORKSHOP:
        POS += 1
        if POS >= len(PLAYLIST):
            POS = 0
        entry = PLAYLIST[POS] 
        LOGGER.debug("entry {}".format(entry))
        for data in entry:
            LOGGER.debug("emit {} ".format(data))
            changeme(data)
    elif MODE == MODE_SHUFFLE:
        new_pos = random.randint(0, len(PLAYLIST) - 1)
        while new_pos == POS:
            new_pos = random.randint(0, len(PLAYLIST) - 1)
        POS = new_pos
        entry = PLAYLIST[POS] 
        for data in entry:
            changeme(data)
    else:
        #do nothing
        pass
    return render_template('button.html')


def send_command(hostname, command, wait=True):
    """
    Sends a command to the socket of the control daemon.

    :param command: the command and it's parameters
    :type command: str
    :return: False or error message
    :rtype: str
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = HOSTS[hostname]
    sock.connect((ip, 8888))
    sock.send('{}\n'.format(command).encode('utf-8'))
    if wait == False:
        return ''
    buffer = b''
    while True:
        data = sock.recv(8192)
        buffer = buffer + data
        if data.endswith(b'\n'):
            break
    sock.close()
    # print('Socket-Response: {}'.format(data))
    LOGGER.debug("=== DATA {}".format(repr(buffer)))
    decoded = json.loads(buffer.decode('utf-8'))
    return decoded

def select_random_label(hostname):
    pass    

@SOCKETIO.on('connect')
def handle_connect_event():
    """
    A new web client established a connection.
    """
    LOGGER.info('[%s] connected' % request.remote_addr)
    global thread
    if thread == None:
        thread = SOCKETIO.start_background_task(target=ack)
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
def handle_resetme_event(jsonr):
    """
    Resets the content of a web client.
    """
    LOGGER.info('[%s] wants resetme ' % request.remote_addr)
    emit('reset', ({'labels': get_labels()}, jsonr))

def get_labels():
    global LABELS
    if LABELS != None:
        return LABELS

    labels = {}
    for hostname, addr in HOSTS.items():
        status = send_command(hostname, 'status', True)
        LOGGER.debug('status {}: {}'.format(hostname, repr(status)))
        drum_nums = []
        for i in status:
            try:
                if isinstance(i['address'], int):
                    drum_nums.append(i['address']) 
            except KeyError:
                pass
        LOGGER.debug('drum nums: ' + repr(drum_nums))
        # TODO: Make {"hostname": "alice", "address": 1} and {"hostname": "bob", "address": 1}
        # Currently the address number may only occur once, even if the drum is at different hosts.
        for i in drum_nums:
            drum = send_command(hostname, 'labels {}'.format(i), True)
            labels[i] = drum
    LOGGER.debug('labels: ' + repr(labels))
    LABELS = labels
    return LABELS

@SOCKETIO.on('updateme')
def handle_updateme_event(jsonr):
    """
    Resets the content of a web client.
    """
    global HOSTS
    global PLAYLIST
    global POS
    for host, addr in HOSTS.items():
        print("{} -> {}".format(host, addr))
        print("Getting status from {}".format(host))
        status = send_command(host, 'status')
        emit('update', ({'hostname': host, 'status': status, 'playlist': PLAYLIST, 
            'position': POS, 'mode': MODE}, jsonr))
    LOGGER.info('[%s] wants fresh content' % request.remote_addr)


@SOCKETIO.on('changeme')
def handle_changeme_event(jsonr):
    """
    Resets the content of a web client.
    """
    LOGGER.info('[%s] wants changeme' % request.remote_addr)
    changeme(jsonr)
  
def changeme(jsonr):
    # light: R, G, B, WW 
    light = [None, None, None, None]
    hostname = jsonr['hostname']
    for address, value in jsonr.items():
        drum = address
        print("DRUM {}\n".format(drum))
        if drum == 'rgb':
            # decode the color string light "#ffeecc" in to integer components
            light[0:3] = int(value[1:3],16), int(value[3:5], 16), int(value[5:7], 16)
            print("HORST", hostname)
        elif drum == 'ww':
            # warm-white is given in percent. Convert to 0-255 range.
            light[3] = int(round(255 * (float(value) / 100.0)))
            print("HORST", hostname)
        else:
            send_command(hostname, 'go {} {}'.format(address, value), wait=False)
    cmd = 'light ' + ' '.join([str(x) for x in light])
    print("CMD: {}".format(cmd))
    send_command(hostname, cmd, wait=False)
    status = send_command(hostname, 'status')
    global PLAYLIST
    global POS
    SOCKETIO.emit('update', ({'hostname': hostname, 'status': status, 'mode': MODE,
        'playlist': PLAYLIST, 'position': POS}, jsonr), broadcast=True)


@SOCKETIO.on('go')
def handle_update_event(json):
    """
    A client changed something. Now push the update to the leafes.

    :param json: A JSON dict with the drum and the value it should be set to
    :type json: dict
    """
    LOGGER.info('[%s] wants to switch drum %d to %d' % (request.remote_addr, json['drum'], json['index']))
    send_command('go %d %d' % (json['drum'], json['index']))

@SOCKETIO.on('playlist')
def handle_playlist_event(jsonr):
    """
    Handle events that overwrite the current playlist with a new one.
    """
    global PLAYLIST
    global POS
    new_playlist = jsonr['playlist']
    PLAYLIST = new_playlist
    with open(PLAYLIST_FILE, mode="w") as fh:
        for i in new_playlist:
            fh.write(json.dumps(i) + '\n')
    POS = -1
    for hostname, addr in HOSTS.items():
        status = send_command(hostname, 'status')
        SOCKETIO.emit('update', ({'hostname': hostname, 'status': status, 'mode': MODE,
            'playlist': PLAYLIST, 'position': POS}, jsonr), broadcast=True)
            

@SOCKETIO.on('mode')
def handle_mode_event(jsonr):
    global MODE
    MODE = jsonr['mode']
    LOGGER.info('wants to switch mode, %s' % json)
    emit('connected', broadcast=True)
    #for hostname, addr in HOSTS.items():
    #    emit('update', {'hostname': hostname, 'status': status, 'mode': MODE, 
    #        'playlist': PLAYLIST, 'position': POS}, broadcast=True)
        

def get_update_from_drums():
    # TODO: get update
    #if update:
    #    emit('update', json, broadcast=True)
    pass


if __name__ == '__main__':
    LOGGER.info("Reading {}".format(PLAYLIST_FILE))
    get_labels()
    get_labels()
    get_labels()
    get_labels()
    get_labels()
    with open(PLAYLIST_FILE, mode="r") as infh:
        for line in infh.readlines():
            PLAYLIST.append(json.loads(line))

    SOCKETIO.run(APP, debug=True)
