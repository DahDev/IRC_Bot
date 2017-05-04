import socket
import sys
import telnetlib


def get_parameter(arg_list, value):
    if arg_list.count(value) > 0:
        index_host = arg_list.index(value)
        return arg_list[index_host + 1]
    else:
        return None


def read_parameters_from_arg(arg_list):
    host = get_parameter(arg_list, "-h")
    port = int(get_parameter(arg_list, "-p"))
    user = get_parameter(arg_list, "-u")
    mode = int(get_parameter(arg_list, "-m"))
    if host is None:
        pass  # throw error
    if port is None:
        port = 6667  # default port
    if user is None:
        user = "bot"  # default bot name
    if mode is None:
        mode = 0
    return host, port, user, mode


def debug(socket_to_debug):
    t = telnetlib.Telnet()
    t.sock = socket_to_debug
    t.interact()


def make_mess(message):
    print(message)
    return bytes(message + "\r\n", "utf-8")


(HOST, PORT, USERNAME, MODE) = read_parameters_from_arg(sys.argv)
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect((HOST, PORT))
my_socket.sendall(make_mess("NICK %s" % USERNAME))
my_socket.sendall(make_mess("USER %s %i * :%s" % (USERNAME, MODE, USERNAME)))
debug(my_socket)
