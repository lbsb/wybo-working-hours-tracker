import serial
import socket
import re
import time

# client serial port information
CLIENT_SERIAL_BAUDRATE = 9600
CLIENT_SERIAL_PORT = "/dev/cu.usbmodem2041"
# waiting time between 2 tentatives of reconnection
CLIENT_SERIAL_RECONNECTION_DELAY = 2

# Server information
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9003


class Client(object):
    _serial_port = None
    _socket = None

    def __init__(self):
        """
        Constructor
        """

        # init serial connection
        self._serial_port = serial.Serial(port = CLIENT_SERIAL_PORT, baudrate = CLIENT_SERIAL_BAUDRATE)
        # init socket connection
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _reconnect_serial_port(self):
        """
        Reconnect serial port
        """

        while not self._serial_port.isOpen():
            try:
                # try to reconnect
                self._serial_port.open()
            except OSError:
                # short delay between 2 tentatives
                time.sleep(CLIENT_SERIAL_RECONNECTION_DELAY)

    def start(self):
        """
        Receive data on serial port and send it on UDP to the server
        (protocol : XX:XX:X)
        XX: sensor id
        YY: sensor type
        Z : sensor value
        """

        # listen on the serial port..
        while (True):
            try:
                # get the sensor status on serial port
                sensor_status = self._serial_port.readline().replace('\r\n', '')
                # send message to server only if protocol is respected
                if re.compile("[0-9]{2}:[0-9]{2}:[0-9]{1}").match(sensor_status):
                    self._send_message_to_server(sensor_status)
            # handle disconnection
            except IOError, e:
                self._serial_port.close()
                # send last message if the sensor is disconnected
                self._send_message_to_server("01:01:2")
                self._reconnect_serial_port()

    def _send_message_to_server(self, message):
        """
        Send a message to server (protocol : XX:YY:Z)
        XX: sensor id
        YY: sensor type
        Z : sensor value
        :param message:
        """

        self._socket.sendto(message, (SERVER_IP, SERVER_PORT))
