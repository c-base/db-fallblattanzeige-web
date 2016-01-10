# coding: utf-8

import sys
import serial
import logging


class Leave:
    def __init__(self, content, serial_dev, leave_id):
        self.leave_id = leave_id
        self.lines = content
        self.index = 0

        self.logger = logging.getLogger(__name__)

        try:
            self.ser = serial.Serial(serial_dev, 9600)
        except IOError as e:
            self.logger.fatal('Fatal error while establishing tty connection: %s' % e)
            sys.exit(e)

    def home(self):
        self.logger.info('Homing leave %d' % self.leave_id)

        try:
            self.ser.write('/leave/%d/home\n' % self.leave_id)
        except IOError as e:
            self.logger.error('Error while trying to home leave %d: %s' % (self.leave_id, e))

    def goto(self, index):
        self.logger.info('Changing the index of leave %d to %d' % (self.leave_id, index))
        try:
            self.ser.write('/leave/%d/goto/%d\n' % (self.leave_id, index))
            self.index = index
        except IOError as e:
            self.logger.error('Error while trying to change index of leave %d to %d: %s' % (self.leave_id, index, e))
