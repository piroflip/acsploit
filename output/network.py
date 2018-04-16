import os
import socket
from options import Options


class Network:

    OUTPUT_NAME = 'network'  # exploits can use this internally to whitelist/blacklist supported output formats

    _SEPARATORS = {  # as bytes because
        'newline': b'\n',
        'comma': b',',
        'space': b' ',
        'tab': b'\t',
        'os_newline': bytes(os.linesep.encode()),
        'CRLF': b'\r\n'
    }

    _VERSIONS = {
        'IPv4': socket.AF_INET,
        'IPv6': socket.AF_INET6
    }

    _BANNER_LENGTH = 1024

    def __init__(self):
        self.options = Options()
        self.options.add_option('host', '127.0.0.1', 'Host to connect to')
        self.options.add_option('port', 80, 'Port to connect to')
        self.options.add_option('ip_version', 'IPv4', 'Version of IP to use', ['IPv4', 'IPv6'])
        self.options.add_option('separator', 'newline', 'Separator between elements', ['newline', 'comma', 'space',
                                                                                       'tab', 'os_newline', 'CRLF'])
        self.options.add_option('final_separator', False, 'Whether to end output with an instance of the separator')
        self.options.add_option('await_banner', False, 'Receive a banner message from the server before sending data')
        self.options.add_option('number_format', 'decimal', 'Format for numbers', ['decimal', 'hexadecimal', 'octal'])

    def output(self, output_list):
        separator = Network._SEPARATORS[self.options['separator']]
        line = separator.join([self.convert_item(item) for item in output_list])
        if self.options['final_separator']:
            line += separator
        protocol = Network._VERSIONS[self.options['ip_version']]
        # TODO: handle exceptions?
        s = socket.socket(protocol, socket.SOCK_STREAM)
        s.connect((self.options['host'], self.options['port']))
        if self.options['await_banner']:
            s.recv(Network._BANNER_LENGTH)
        s.sendall(line)
        s.close()

    def convert_item(self, item):
        # NB: this doesn't recurse onto lists
        if type(item) is int:
            if self.options['number_format'] == 'hexadecimal':
                item = hex(item)
            elif self.options['number_format'] == 'octal':
                item = oct(item)
        if type(item) is not bytes:
            item = str(item).encode(encoding='utf-8')  # TODO: this is a bit of a hack, to put it mildly

        return item
