# -*- coding: utf-8 -*-
import os
import serial
import socket
import re
import time
import logging
import json
import hashlib
import sys
import cPickle as pickle
from user import User

# User settings
DATA_FILE_LOCATION = "data/"
DATA_FILE_NAME = "user.json"

# Client serial port settings
CLIENT_SERIAL_BAUDRATE = 9600
CLIENT_SERIAL_PORT = "/dev/cu.usbmodemfd121"
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

        # init log folder
        self._init_log_folder()
        # init data folder
        self._init_data_folder()
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
        # init socket connection
        self._init_socket()
        # init serial connection
        self._init_serial_port()
        # read user settings
        self._read_user_settings()

    def _is_user_logged(self):
        """
        Check if user is logged
        """

        try:
            with open(DATA_FILE_LOCATION + DATA_FILE_NAME) as file:
                user = json.load(file)
                # set user information in current user
                if user["uuid"] != "":
                    return True

            return False
        except IOError:
            return False

    def _read_user_settings(self):
        """
        Get user settings from file (JSON)
        :param path:
        :return:
        """

        user_file = None
        # open file
        try:
            user_file = open(DATA_FILE_LOCATION + DATA_FILE_NAME)
            # read file
            user_json = json.load(user_file)
            # set user information in current user
            self._user = User()
            self._user._uuid = user_json["uuid"]
        except IOError:
            while not self._is_user_logged():
                self._login_user()

    def _login_user(self):
        """
        Ask user login
        """

        # send message to arduino to bling the LED
        self._send_message_to_arduino("3")
        self._logger.info("Please enter your email and password to login")
        user = User()
        sys.stdout.write("email: ")
        user._email = sys.stdin.readline()
        sys.stdout.write("password: ")
        password = sys.stdin.readline()

        # hash password
        user._password = hashlib.sha256(password).hexdigest()
        # sync user settings and get back generated id
        user._uuid = self._sync_user_settings(user)
        # save user settings
        if user._uuid != "":
            self._save_user_settings(user)
            self._logger.info("Login successful")
        elif user._uuid == "":
            self._logger.info("Login failed")
            self._login_user()
        elif user._uuid == 0:
            self._logger.info("Login failed. Please check your internet and/or serial connection and retry")
            self._login_user()

        # send message to arduino to put off LED
        self._send_message_to_arduino("4")

    def _send_message_to_arduino(self, message):
        """
        Send message to arduino
        """

        self._serial_port.write(message)
        self._logger.debug("Message : \"%s\" has been sent to arduino", message)

    def _sync_user_settings(self, user):
        """
        Send user settings to server and get back a generated id
        """

        self._logger.debug("Sending credentials to server...")
        # send user credentials
        message = user._email + ":" + user._password + ":3"
        self._socket.sendto(message, (SERVER_IP, SERVER_PORT))
        self._logger.debug("Message : \"%s\" has been sent to server (%s:%d)", message, SERVER_IP, SERVER_PORT)

        # received user_uuid
        user_uuid, addr = self._socket.recvfrom(1024)
        # format data
        user_uuid.replace("\n", "")

        if re.compile("[0-9a-zA-Z\-]+").match(user_uuid):
            self._logger.debug("valid UUID (%s) has been received from server (%s:%d)", user_uuid, SERVER_IP, SERVER_PORT)
            return user_uuid
        elif user_uuid == "":
            self._logger.debug("empty UUID (%s) has been received from server (%s:%d)", user_uuid, SERVER_IP, SERVER_PORT)
            return ""

        return 0

    def _save_user_settings(self, user):
        """
        Save user settings in JSON file
        """

        # save user settings in json file
        with open(DATA_FILE_LOCATION + DATA_FILE_NAME, "w") as outfile:
            json.dump({
                'uuid': user._uuid
            }, outfile, indent = 4, encoding = 'utf-8')

        self._logger.debug("User settings has been saved in \"%s\"", (DATA_FILE_LOCATION + DATA_FILE_NAME))

        # set user information in current user
        self._user = user

    def _init_socket(self):
        """
        Init socket
        """

        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as msg:
            self._logger.debug("Can't init socket : %s", msg)

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

        # short delay before (read/write) on serial port
        time.sleep(1)

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
                self._send_sensor_status_to_server("0")
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
                if re.compile("[0-1]{1}").match(sensor_status):
                    self._send_sensor_status_to_server(sensor_status)
                elif re.compile("[3]{1}").match(sensor_status):
                    self._login_user()

            # handle disconnection
            except IOError, e:
                self._logger.info("Arduino disconnected")
                self._logger.debug("Arduino seems to be disconnected. Impossible to received and send messages. Please check your serial connection.")
                self._serial_port.close()
                self._logger.debug("Serial port : \"%s\" has been closed", CLIENT_SERIAL_PORT)
                # send last message if the sensor is disconnected
                self._send_sensor_status_to_server("2")
                self._logger.debug("Disconnected status has been sent to the server")
                self._reconnect_serial_port()

    def _send_sensor_status_to_server(self, sensor_value):
        """
        Send sensor status to server (protocol : uuid:sensor_value)
        :param sensor_value:
        """

        # concat uuid with sensor value to be identified on server
        data_sensor = self._user._uuid + ":" + sensor_value
        self._socket.sendto(data_sensor, (SERVER_IP, SERVER_PORT))
        self._logger.debug("message : \"%s\" has been sent to %s:%d", data_sensor, SERVER_IP, SERVER_PORT)

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

    def _init_log_folder(self):
        """
        Create log folder if it doesn't exist
        """

        # create folder if it doesn't exist
        if not os.path.isdir(LOG_FILE_LOCATION):
            os.makedirs(LOG_FILE_LOCATION)

    def _init_data_folder(self):
        """
        Create data folder if it doesn't exist
        """

        # create folder if it doesn't exist
        if not os.path.isdir(DATA_FILE_LOCATION):
            os.makedirs(DATA_FILE_LOCATION)
