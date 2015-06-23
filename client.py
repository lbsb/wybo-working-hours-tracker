import os
import serial
import socket
import re
import time
import logging
import json
import sys
import cPickle as pickle
from user import User

# User settings
USER_FILE_LOCATION = "user/"
USER_FILE_NAME = "user.json"

# Client serial port settings
CLIENT_SERIAL_BAUDRATE = 9600
CLIENT_SERIAL_PORT = "/dev/cu.usbmodem2041"
# waiting time between 2 tentatives of reconnection
CLIENT_SERIAL_RECONNECTION_DELAY = 1

# Server settings
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9003
# Delay between 2 pings
SERVER_PING_DELAY = 3

# Logger settings
LOG_FILE_LOCATION = "log/"
LOG_FILE_NAME = "client"


class Client(object):
    _serial_port = None
    _socket = None
    _logger = None
    _user = None

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
        # init user
        self._read_user_settings()
        # init serial connection
        self._init_serial_port()
        # init socket connection
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as msg:
            self._logger.debug("Can't init socket : %s", msg)

    def _read_user_settings(self):
        """
        Get user settings from file (JSON)
        :param path:
        :return:
        """

        user_file = None
        # open file
        try:
            user_file = open(USER_FILE_LOCATION + USER_FILE_NAME)
            # read file
            user_json = json.load(user_file)
            # set user information in current user
            self._user = User(user_json["id"], user_json["first_name"], user_json["last_name"], user_json["email"])
        except IOError:
            self._init_user_settings()

    def _init_user_settings(self):
        """
        Init user settings by asking to user enter his information
        """

        user = User()
        self._logger.info("Create new user")
        self._logger.info("Please enter your information.")
        sys.stdout.write("first name: ")
        user._first_name = sys.stdin.readline()
        sys.stdout.write("last name: ")
        user._last_name = sys.stdin.readline()
        sys.stdout.write("email: ")
        user._email = sys.stdin.readline()
        # sync user settings and get back generated id
        user._id = self._sync_user_settings(user)
        # save user settings
        self._save_user_settings(user)

    def _sync_user_settings(self, user):
        """
        Send user settings to server and get back a generated id
        """

        # serialize user object
        data_user = pickle.dumps(user, -1)

        # send user to server
        self._socket.sendto(data_user, (SERVER_IP, SERVER_PORT))
        # receive id
        data = self._socket.recv(1024)
        print "%s" % data

        return data.replace("\n", "")

    def _save_user_settings(self, user):
        """
        Save user settings in JSON file
        """

        # save user settings in json file
        with open(USER_FILE_LOCATION + USER_FILE_NAME, "w") as outfile:
            json.dump({
                'id': user._id,
                'first_name': user._first_name.replace("\n", ""),
                'last_name': user._last_name.replace("\n", ""),
                'email': user._email.replace("\n", "")
            }, outfile, indent = 4)

        # set user information in current user
        self._user = user

    def _init_serial_port(self):
        """
        Init serial port
        """
        self._logger.info("Arduino disconnected. Please connect it on USB port : %s", CLIENT_SERIAL_PORT)
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
                self._send_sensor_status_to_server("01:0")
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

        self._logger.debug("Listening on serial port : %s", CLIENT_SERIAL_PORT)
        # listening on the serial port..
        while (True):
            try:
                # get the sensor status on serial port
                sensor_status = self._serial_port.readline().replace('\r\n', '')
                self._logger.debug("Message : \"%s\" has been received on serial port", sensor_status)
                # send message to server only if protocol is respected
                if re.compile("[0-9]{1}").match(sensor_status):
                    self._send_sensor_status_to_server(sensor_status)

            # handle disconnection
            except IOError, e:
                self._logger.info("Arduino disconnected")
                self._logger.debug("Arduino seems to be disconnected. Impossible to received and send messages. Please check your serial connection.")
                self._serial_port.close()
                self._logger.debug("Serial port : \"%s\" has been closed", CLIENT_SERIAL_PORT)
                # send last message if the sensor is disconnected
                self._send_sensor_status_to_server("01:2")
                self._logger.debug("Disconnected status has been sent to the server")
                self._reconnect_serial_port()

    def _send_sensor_status_to_server(self, sensor_value):
        """
        Send sensor status to server (protocol : XX:Z)
        XX: user id
        Z : sensor value
        :param message:
        """
    
        self._socket.sendto(sensor_value, (SERVER_IP, SERVER_PORT))
        self._logger.debug("message : \"%s\" has been sent to %s:%d", sensor_value, SERVER_IP, SERVER_PORT)


def _check_server_connection(self):
    """
    Ping server to check if it's available
    :return:
    """

    if os.system("ping -c 1 " + SERVER_IP) == 0:
        self._logger.debug("server is online")
    else:
        self._logger.debug("server is offline")

    # short delay between two tentatives
    time.sleep(SERVER_PING_DELAY)
