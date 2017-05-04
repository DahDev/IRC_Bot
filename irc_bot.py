import socket
import sys


def get_parameter(arg_list, value):
    if value in arg_list:
        index_host = arg_list.index(value)
        return arg_list[index_host + 1]
    else:
        return None


def read_parameters_from_arg(arg_list):
    host = get_parameter(arg_list, "-h")
    port = get_parameter(arg_list, "-p")
    channel = get_parameter(arg_list, "-c")
    user = get_parameter(arg_list, "-u")
    mode = get_parameter(arg_list, "-m")
    if host is None:
        raise ValueError("Host undefined!")
    if port is None:
        port = 6667  # default port
    else:
        port = int(port)
    if channel is None:
        raise ValueError("Channel undefined!")
    if user is None:
        user = "bot"  # default bot name
    if mode is None:
        mode = 0
    else:
        mode = int(mode)
    return host, port, channel, user, mode


def make_mess(message):
    print(message)
    return bytes(message + "\r\n", "utf-8")


def receive_line(sock):
    line = b''
    character = b''
    while line.find(b'\n') == -1:
        try:
            character = sock.recv(1)
        except socket.error as msg:
            print(msg, file=sys.stderr)
        line += character
    return line


def get_username(prefix):
    if prefix.find("!") != -1 or prefix.find("@") != -1:
        start = prefix.index("!") + 2
        end = prefix.index("@")
        return prefix[start:end]
    else:
        return False


if __name__ == '__main__':
    commands = ['!alert', 'Found']
    users = set()

    (HOST, PORT, CHANNEL, USERNAME, MODE) = read_parameters_from_arg(sys.argv)
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((HOST, PORT))
    my_socket.sendall(make_mess("NICK %s" % USERNAME))
    my_socket.sendall(make_mess("USER %s %i * :%s" % (USERNAME, MODE, USERNAME)))
    my_socket.sendall(make_mess("JOIN %s" % CHANNEL))

    while True:
        line = str(receive_line(my_socket).strip(), "utf-8")
        print(line)
        split_line = line.split(" ", 2)
        length = len(split_line)
        if length == 2:  # PING case
            command, parameter = split_line
            if command == "PING":
                my_socket.sendall(make_mess("PONG %s" % parameter))
        elif length == 3:
            prefix, command, parameters = split_line
            if command == "PRIVMSG":
                parameters_list = parameters.split(" ")
                if len(parameters_list) == 2 and parameters_list[1][1:] == "!alert":
                    username = get_username(prefix)
                    if username:
                        if parameters_list[2] == "enabled":
                            users.add(username)
                        elif parameters_list[2] == "disabled":
                            users.pop(username)
