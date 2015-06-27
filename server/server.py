import socket
import logging
import thread
import re
import os
import uuid
import time
import sys
from datetime import datetime
import hashlib
from user import User
import json

APP_NAME = "WyboServer"

# server information
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9003

# Users informations
DATA_FILE_LOCATION = "data/"
DATA_FILE_NAME = "users.json"

# Logger settings
LOG_FILE_LOCATION = "log/"
LOG_FILE_NAME = "server.log"

# Protocol code
CODE_STOP_WORKING = 0
CODE_START_WORKING = 1
CODE_DISCONNECTED = 2
CODE_AUTHENTIFICATION = 3


class Server(object):
    """
    Server
    """

    _socket = None
    _logger = None
    _listenner = None
    _running = None
    _listening = None

    def __init__(self):
        """
        Constructor
        """

        self._running = False
        self._listening = False
        # init log folder
        self._init_log_folder()
        # init data file
        self._init_data_file()
        # init logger (console and file)
        self._init_logger()

    def _init_logger(self):
        """
        Init logger
        """

        self._logger = logging.getLogger(APP_NAME)
        file_handler = logging.FileHandler(LOG_FILE_LOCATION + LOG_FILE_NAME)
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

    def start(self, PORT = SERVER_PORT):
        """
        Start server
        :param PORT:
        """

        if not self._running:
            self._running = True
            self._logger.info("Starting server...")
            # init socket
            # bind socket
            try:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self._socket.bind((SERVER_IP, PORT))
                self._socket.settimeout(10)
            except socket.error as msg:
                self._logger.debug("Bind failed : %s", msg)

            self._logger.info("Server started")
            # start listening in a thread
            thread.start_new_thread(self._listen, ())
            self._logger.debug("Listening on port: %d (UDP Protocol)", PORT)
        else:
            self._logger.info("Server already started")

    def _add_working_state(self, data, addr):
        """
        Add working state to json file and send confirmation to client
        :param data: data send by client
        :param addr: client address
        :return:
        """

        # get user uuid and user state
        uuid = data[:data.index(":")]
        state = int(data[data.index(":") + 1:])

        # if user exist
        if self._has_user_by_uuid(uuid):
            # read user working hour file
            with open(DATA_FILE_LOCATION + uuid + ".json") as file:
                user_working_hours = json.load(file)
                # change current state of user
                user_working_hours["currentState"] = state

                # get number of elements
                if len(user_working_hours["workingHours"]) > 0:
                    elem = len(user_working_hours["workingHours"]) - 1
                else:
                    elem = 0

                # check if user is currently working and hasn't already stopped
                if state == CODE_STOP_WORKING and user_working_hours["workingHours"][elem]["startDatetime"] != "" and user_working_hours["workingHours"][elem]["endDatetime"] == "":
                    # end current working hour
                    user_working_hours["workingHours"][elem]["endDatetime"] = datetime.now().strftime('%Y%m%d%H%M%S%f')
                    working_time = datetime.strptime(user_working_hours["workingHours"][elem]["endDatetime"], "%Y%m%d%H%M%S%f") - datetime.strptime(
                        user_working_hours["workingHours"][elem]["startDatetime"], "%Y%m%d%H%M%S%f")
                    user_working_hours["workingHours"][elem]["workingTime"] = str(working_time.microseconds / 100)
                    self._logger.debug("user (uuid : %s - ip : %s) stopped working", uuid, addr[0])
                elif state == CODE_START_WORKING:
                    # start a new working hour
                    new_working_hours = {
                        "startDatetime": datetime.now().strftime('%Y%m%d%H%M%S%f'),
                        "endDatetime": "",
                        "workingTime": ""
                    }

                    # add new working hours to the dict
                    user_working_hours["workingHours"].append(new_working_hours)
                    self._logger.debug("user (uuid : %s - ip : %s) started working", uuid, addr[0])
                elif state == CODE_DISCONNECTED:
                    # end current working hour if user had started a working hour
                    if user_working_hours["workingHours"][elem]["endDatetime"] == "":
                        user_working_hours["workingHours"][elem]["endDatetime"] = datetime.now().strftime('%Y%m%d%H%M%S%f')
                        working_time = datetime.strptime(user_working_hours["workingHours"][elem]["endDatetime"], "%Y%m%d%H%M%S%f") - datetime.strptime(
                            user_working_hours["workingHours"][elem]["startDatetime"], "%Y%m%d%H%M%S%f")
                        user_working_hours["workingHours"][elem]["workingTime"] = str(working_time.microseconds / 100)
                        self._logger.debug("user (uuid : %s - ip : %s) stopped working", uuid, addr[0])

                # add new working hours to the file
                with open(DATA_FILE_LOCATION + uuid + ".json", "w") as file:
                    json.dump(user_working_hours, file, indent = 4, encoding = 'utf-8')

                # send confirmation value to client
                self._socket.sendto(str(state), (addr[0], addr[1]))
                self._logger.debug("Send confirmation \"%s\" to %s", str(state), addr[0])
        else:
            self._logger.debug("Unknow user send \"%s\" from %s", data, addr[0])
            # send authentification code to ask authentification from client
            self._socket.sendto(str(CODE_AUTHENTIFICATION), (addr[0], addr[1]))
            self._logger.debug("Authentification asked to %s", addr[0])

    def _handle_data_received(self, data, addr):
        """
        Handle data received
        :param data: data send by client
        :param addr: client address

        """

        # format data
        data = data.replace("\n", "")
        self._logger.debug("Data received : \"%s\" from %s", data, addr[0])

        # analyze string sent and redirect to the right handlers
        if re.compile("^[0-9a-zA-Z\-]+:(" + str(CODE_STOP_WORKING) + "|" + str(CODE_START_WORKING) + "|" + str(CODE_DISCONNECTED) + "){1}$").match(data):
            self._add_working_state(data, addr)
        elif re.compile(".+:[0-9a-zA-Z\-]+:" + str(CODE_AUTHENTIFICATION) + "$") \
                .match(data):
            self._sync_user_credentials(data, addr)

    def _has_user(self, u):
        """
        Check if user exists
        :param u: user
        :return boolean:
        """

        # load all users from json file
        with open(DATA_FILE_LOCATION + DATA_FILE_NAME, "r") as file:
            users = json.load(file)
        # search user
        for user in users:
            if str(u._email) == user["email"] and u._password == user["password"]:
                return True

        return False

    def _has_user_by_uuid(self, uuid):
        """
        Check if user exists
        :param u: user
        :return boolean:
        """

        # load all users from json file
        with open(DATA_FILE_LOCATION + DATA_FILE_NAME, "r") as file:
            users = json.load(file)
        # search user
        for user in users:
            if uuid == user["uuid"]:
                return True

        return False

    def _find_user(self, u):
        """
        Search a user and return all his information
        :param u: user
        """

        # load all users from json file
        with open(DATA_FILE_LOCATION + DATA_FILE_NAME, "r") as file:
            users = json.load(file)

        # search user
        for user in users:
            if u._email == user["email"] and u._password == user["password"]:
                return User(user["id"], user["firstName"], user["lastName"], user["email"],
                            user["uuid"], user["password"])

        return None

    def _sync_user_credentials(self, data, addr):
        """
        Received user credentials and send its uuid
        :param data: data send by client
        :param addr: client address
        """

        self._logger.debug("User trying to login from %s", addr[0])
        self._logger.debug("Checking credentials...")
        # format user information received
        data.replace("\n", "")
        user = User()
        user._email = data.split(":")[0]
        user._password = data.split(":")[1]

        # search user
        user_found = self._find_user(user)

        if user_found != None:
            # send the generated uuid to client
            self._socket.sendto(user_found._uuid, (addr[0], addr[1]))
            self._logger.debug("User found")
            self._logger.debug("User (email: %s) is logged", user_found._email)
            self._logger.debug("UUID: \"%s\" sent to %s", user_found._uuid, addr[0])
        else:
            # send empty string to client
            self._socket.sendto("none", (addr[0], addr[1]))
            self._logger.debug("none string sent to %s", addr[0])
            self._logger.debug("User not found")
            self._logger.debug("User (email: %s) failed to login", user._email)

    def add_user(self):
        """
        Add user in data file
        """

        self._logger.info("Please enter user information")
        user = User()
        # ask user information
        sys.stdout.write("first name: ")
        user._first_name = sys.stdin.readline()
        sys.stdout.write("last name: ")
        user._last_name = sys.stdin.readline()
        sys.stdout.write("email: ")
        user._email = sys.stdin.readline()
        sys.stdout.write("password: ")
        password = sys.stdin.readline()

        # hash password
        user._password = hashlib.sha256(password).hexdigest()
        # read users file
        with open(DATA_FILE_LOCATION + DATA_FILE_NAME) as file:
            users = json.load(file)

        # increment id
        user._id = len(users) + 1
        # generate an unique uuid
        user._uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, user._email))

        # define the new user with data received
        new_user = {
            'id': user._id,
            'firstName': user._first_name.replace("\n", ""),
            'lastName': user._last_name.replace("\n", ""),
            'email': user._email.replace("\n", ""),
            'password': user._password,
            'uuid': user._uuid
        }

        # add user to the dict
        users.append(new_user)

        # save user settings in json file
        with open(DATA_FILE_LOCATION + DATA_FILE_NAME, "w") as file:
            json.dump(users, file, indent = 4, encoding = 'utf-8')

        # init user work data file
        with open(DATA_FILE_LOCATION + user._uuid + ".json", "w") as file:
            user_hours = {
                "uuid": user._uuid,
                "currentState": "",
                "workingHours": []
            }
            json.dump(user_hours, file, indent = 4, encoding = 'utf-8')

        self._logger.info("User successfully added ")
        self._logger.debug("New user added (id: %s - email: %s)", user._id, user._email)

    def _listen(self):
        """
        Listen incoming connections and handle received data
        """

        self._listening = True
        while self._running:
            try:
                data, addr = self._socket.recvfrom(1024)
                self._handle_data_received(data, addr)
            except socket.timeout:
                pass

    def reboot(self):
        """
        Stop and start server
        """

        if not self._running:
            self.stop()
        else:
            self.stop()
            self.start()

    def stop(self):
        """
        Stop server, close socket and end thread
        """

        if self._running:
            self._logger.info("Stopping server...")
            self._running = False
            self._listening = False
            time.sleep(self._socket.gettimeout() + 2)
            self._socket.close()
            self._socket = None
            self._logger.debug("Socket closed")
            self._logger.info("Server stopped")
        else:
            self._logger.info("Server not started")

    def _init_log_folder(self):
        """
        Create data file if it doesn't exist
        """

        # create folder if it doesn't exist
        if not os.path.isdir(LOG_FILE_LOCATION):
            os.makedirs(LOG_FILE_LOCATION)

    def _init_data_file(self):
        """
        Create data file if it doesn't exist
        """

        # create folder if it doesn't exist
        if not os.path.isdir(DATA_FILE_LOCATION):
            os.makedirs(DATA_FILE_LOCATION)

        # create folder if it doesn't exist
        if not os.path.isdir(DATA_FILE_LOCATION):
            os.makedirs(DATA_FILE_LOCATION)

        # create file if it doesn't exist
        if not os.path.exists(DATA_FILE_LOCATION + DATA_FILE_NAME):
            # init file with an array
            with open(DATA_FILE_LOCATION + DATA_FILE_NAME, "w") as file:
                array = []
                json.dump(array, file, indent = 4)
