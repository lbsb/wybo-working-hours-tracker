import serial
import socket
import re

CLIENT_SERIAL_BAUDRATE = 9600
CLIENT_SERIAL_PORT = "/dev/cu.usbmodemfd121"

SERVER_IP = "127.0.0.1"
SERVER_PORT = 9003


class Client(object):
    _serial_port = None
    _socket = None

    def __init__(self):
        self._serial_port = serial.Serial(port = CLIENT_SERIAL_PORT, baudrate = CLIENT_SERIAL_BAUDRATE)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        """
        Listen and send message to the server
        """

        # listen on the serial port..
        while (True):
            # clean the buffer
            self._serial_port.flush()
            # get the sensor state
            sensor_status = self._serial_port.readline().replace('\r\n', '')
            # apply regex to check if portocol is respected
            if re.compile("[0-9]{2}:[0-9]{2}:[0-9]{1}").match(sensor_status):
                # send message to the server
                self._send_message_to_server(sensor_status)

    def _send_message_to_server(self, message):
        """
        Send a message to server
        :param message:
        :return:
        """

        # send message to the server
        self._socket.sendto(message, (SERVER_IP, SERVER_PORT))

    def capturePhoto(self):
        pass
