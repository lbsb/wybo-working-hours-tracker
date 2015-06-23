import serial
import socket
import re
import time
import logging

# client serial port settings
CLIENT_SERIAL_BAUDRATE = 9600
CLIENT_SERIAL_PORT = "/dev/cu.usbmodemfd121"
# waiting time between 2 tentatives of reconnection
CLIENT_SERIAL_RECONNECTION_DELAY = 5

# Server settings
SERVER_IP = "172.16.104.31"
SERVER_PORT = 9003

# Logger settings
LOG_FILE_LOCATION = "log/"
LOG_FILE_NAME = "client"


class Client(object):
    _serial_port = None
    _socket = None
    _logger = None

    def __init__(self):
        """
        Constructor
        """

        # init logger (console and file)
        self._logger = logging.getLogger(LOG_FILE_NAME)
        file_handler = logging.FileHandler(LOG_FILE_LOCATION + LOG_FILE_NAME + ".log")
        console_handler = logging.StreamHandler()
        file_handler.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.INFO)
        logger_formatter = logging.Formatter("%(asctime)s - %(name)s - "
                                             "%(levelname)s - %(message)s", "%m/%d/%Y %I:%M:%S %p")
        file_handler.setFormatter(logger_formatter)
        console_handler.setFormatter(logger_formatter)
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
        self._logger.setLevel(logging.DEBUG)

    def _init_serial_port(self):
        """
        Init serial port
        """

        while self._serial_port == None:
            try:
                self._serial_port = serial.Serial(port = CLIENT_SERIAL_PORT, baudrate = CLIENT_SERIAL_BAUDRATE)
                self._logger.info("Arduino connected")
            except OSError as msg:
                self._logger.debug("Connection failed : %s", msg)
            except serial.SerialException as msg:
                self._logger.debug("Connection failed : %s", msg)
            finally:

                # short delay between 2 tentatives
                time.sleep(CLIENT_SERIAL_RECONNECTION_DELAY)

    def _reconnect_serial_port(self):
        """
        Reconnect serial port
        """

        while not self._serial_port.isOpen():
            try:
                self._logger.debug("Try to reconnect serial port")
                # try to reconnect
                self._serial_port.open()
                self._logger.info("Arduino reconnected")
                self._send_message_to_server("01:01:0")
            except OSError as msg:
                self._logger.debug("Reconnection failed : %s", msg)
            except serial.SerialException as msg:
                self._logger.debug("Reconnection failed : %s", msg)
            finally:
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

        # init serial connection
        self._init_serial_port()

        # init socket connection
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as msg:
            self._logger.debug("Can't init socket : %s", msg)

        self._logger.debug("Listening on serial port : %s", CLIENT_SERIAL_PORT)
        # listening on the serial port..
        while (True):
            try:
                # get the sensor status on serial port
                sensor_status = self._serial_port.readline().replace('\r\n', '')
                self._logger.debug("Message : \"%s\" has been received on serial port", sensor_status)
                # send message to server only if protocol is respected
                if re.compile("[0-9]{2}:[0-9]{2}:[0-9]{1}").match(sensor_status):
                    self._send_message_to_server(sensor_status)

            # handle disconnection
            except IOError, e:
                self._logger.info("Arduino disconnected")
                self._logger.debug("Arduino seems to be disconnected. Impossible to received and send messages. Please check your serial connection.")
                self._serial_port.close()
                self._logger.debug("Serial port : \"%s\" has been closed", CLIENT_SERIAL_PORT)
                # send last message if the sensor is disconnected
                self._send_message_to_server("01:01:2")
                self._logger.debug("Disconnected status has been sent to the server")
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
        self._logger.debug("message : \"%s\" has been sent to %s:%d", message, SERVER_IP, SERVER_PORT)
