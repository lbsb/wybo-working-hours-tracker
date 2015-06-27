from server import Server
import sys


def main():
    server = Server()

    while True:
        # create server
        sys.stdout.write("WYBO server> ")
        cmd = sys.stdin.readline()

        if cmd == "start\n":
            server.start(9003)
        elif cmd == "stop\n":
            server.stop()
        elif cmd == "restart\n" or cmd == "reboot\n":
            server.reboot()
        elif cmd == "adduser\n":
            server.add_user()
        elif cmd == "exit\n":
            server.stop()
            exit()


if __name__ == "__main__":
    main()
