import json
import socket
import sys
from urllib import request, error


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
    # print(message)
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


def get_json_from_request(url):
    try:
        req = request.Request(url, method="GET")
        res = request.urlopen(req)
        return json.load(res)
    except error.HTTPError:
        return False


def get_foreign_exchange(base):
    base = base.upper()
    url = 'http://api.fixer.io/latest'
    result = get_json_from_request(url)
    if result and base in result['rates']:
        return result['rates'][base]
    else:
        return False


def get_country_ip(ip_address):
    url = 'https://api.ip2country.info/ip?' + ip_address
    result = get_json_from_request(url)
    if result:
        return result['countryName']


def response_for_ping(line):
    command, parameter = line
    if command == "PING":
        my_socket.sendall(make_mess("PONG %s" % parameter))


def recognize_command(commands, user_command):
    if user_command == commands[0]:
        return get_foreign_exchange
    elif user_command == commands[1]:
        return get_country_ip


if __name__ == '__main__':

    (HOST, PORT, CHANNEL, USERNAME, MODE) = read_parameters_from_arg(sys.argv)
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((HOST, PORT))
    my_socket.sendall(make_mess("NICK %s" % USERNAME))
    my_socket.sendall(make_mess("USER %s %i * :%s" % (USERNAME, MODE, USERNAME)))
    my_socket.sendall(make_mess("JOIN %s" % CHANNEL))

    commands = ['!foreign_exchange', '!ip_country']
    priv_msg = "PRIVMSG"
    while True:
        line = str(receive_line(my_socket).strip(), "utf-8")
        print(line)
        split_line = line.split(" ", 2)
        length = len(split_line)
        if length == 2:
            response_for_ping(split_line)
        elif length == 3:
            prefix, command, parameters = split_line
            if command == priv_msg:
                _, user_command, data = parameters.split(" ", 2)
                user_command = user_command[1:]
                if user_command in commands:
                    func = recognize_command(commands, user_command)
                    response = func(data)
                    if response:
                        my_socket.sendall(make_mess("%s %s :%s" % (priv_msg, CHANNEL, response)))
