import sys
import json
import socket
from cmd import Cmd

from DDPClient import DDPClient

class App(Cmd):
    """Main input loop"""
    def __init__(self, ddp_endpoint):
        Cmd.__init__(self)
        self.ddp_client = DDPClient(
            'ws://' + ddp_endpoint + '/websocket'
        )

        self.subscriptions = {}
        self.pending_results = {}

        # Showing a fancy prompt string if we're interactive
        if sys.stdin.isatty():
            self.prompt = ddp_endpoint + '> '
        else:
            self.prompt = ''

        self.ddp_client.on('connected', self.connected)
        self.ddp_client.on('socket_closed', self.closed)
        self.ddp_client.on('failed', self.failed)
        self.ddp_client.on('added', self.added)
        self.ddp_client.on('changed', self.changed)
        self.ddp_client.on('removed', self.removed)
        self.ddp_client.connect()

    def subscribe(self, name, params):
        if name in self.subscriptions:
            self._log('* ALREADY SUBSCRIBED - {}'.format(name))
            return
        sub_id = self.ddp_client.subscribe(name, params, self.subscribed)
        self.subscriptions[name] = sub_id

    def unsubscribe(self, name):
        if name not in self.subscriptions:
            self._log('* NOT SUBSCRIBED - {}'.format(name))
            return
        self.ddp_client.unsubscribe(self.subscriptions[name])
        del self.subscriptions[name]
        self._log('* UNSUBSCRIBED - {}'.format(name))

    def call(self, method_name, params):
        self.ddp_client.call(method_name, params, self.result)

    #
    # Callbacks
    #

    def added(self, collection, id, fields):
        self._log('* ADDED {} {}'.format(collection, id), True)
        for key, value in fields.items():
            self._log('  - FIELD {} {}'.format(key, value))


    def changed(self, collection, id, fields, cleared):
        self._log('* CHANGED {} {}'.format(collection, id), True)
        for key, value in fields.items():
            self._log('  - FIELD {} {}'.format(key, value))
        for key, value in cleared.items():
            self._log('  - CLEARED {} {}'.format(key, value))

    def removed(self, collection, id):
        self._log('* REMOVED {} {}'.format(collection, id), True)

    def subscribed(self, error, sub_id):
        if error:
            self._remove_sub_by_id(sub_id)
            self._log('* SUBSCRIPTION FAILED - {}'.format(error.get('reason')), True)
            return
        self._log('* READY', True)

    def result(self, error, result):
        if error:
            self._log('* METHOD FAILED - {}'.format(error.get('reason')), True)
            return
        self._log('* METHOD RESULT - {}'.format(str(result)), True)

    def connected(self):
        self._log('* CONNECTED', True)

    def closed(self, code, reason):
        """Called when the connection is closed"""
        self._log('* CONNECTION CLOSED {} {}'.format(code, reason))

    def failed(self, data):
        self._log('* FAILED - data: {}'.format(str(data)))

    #
    # Commands 
    #

    def do_sub(self, params):
        """The `sub` command"""
        try:
            sub_name, sub_params = self._parse_command(params)
        except ValueError:
            self._log('Error parsing parameter list - try `help sub`')
            return

        self.subscribe(sub_name, sub_params)

    def do_unsub(self, params):
        """The `unsub` command"""
        try:
            sub_name, sub_params = self._parse_command(params)
        except ValueError:
            self._log('Error parsing parameter list - try `help unsub`')
            return

        self.unsubscribe(sub_name)

    def do_call(self, params):
        """The `call` command"""
        try:
            method, params = self._parse_command(params)
        except ValueError:
            self._log('Error parsing parameter list - try `help call`')
            return

        self.call(method, params)

    def do_login(self, params):
        """The `login` command"""
        self._log('Not Implemented Yet -- SRP is in progress')
        self._log('However you can still calling the method `login` (WARNING: password sent in plaintext)')
        #self.ddp_client._login({'username': 'alice'}, 'password123')

    def do_EOF(self, line):
        """The `EOF` "command"

        It's here to support `cat file | python ddpclient.py`
        """
        return True

    def do_help(self, line):
        """The `help` command"""

        msgs = {
            'call': (
                'call <method name> <json array of parameters>\n'
                '  Calls a remote method\n'
                '  Example: call vote ["foo.meteor.com"]'),
            'sub': (
                'sub <subscription name> [<json array of parameters>]\n'
                '  Subscribes to a remote dataset\n'
                '  Examples: `sub allApps` or `sub myApp '
                '["foo.meteor.com"]`'),
            'unsub': (
                'unsub <subscription name>\n'
                '  Unsubscribes from a remote dataset\n'
                '  Examples: `unsub allApps` or `unsub myApp '
                '["foo.meteor.com"]`'),
        }

        line = line.strip()
        if line and line in msgs:
            return self._log('\n' + msgs[line])

        for msg in msgs.values():
            self._log('\n' + msg)

    #
    # Utils
    #

    def _log(self, msg, server_msg=False):
        if server_msg:
            sys.stderr.write('\n')
        sys.stderr.write('{}\n'.format(msg))
        if server_msg:
            sys.stderr.write('{}'.format(self.prompt))

    def _parse_command(self, params):
        """Parses a command with a first string param and a second
        json-encoded param"""
        name, args = (params + ' ').split(' ', 1)
        return name, args and json.loads(args) or []

    def _remove_sub_by_id(self, sub_id):
        for name, cur_sub_id in self.subscriptions.items():
            if cur_sub_id == sub_id:
                del self.subscriptions[name]

if __name__ == '__main__':
    ws_conn = '127.0.0.1:3000'
    if len(sys.argv) > 1:
        ws_conn = sys.argv[1]
    sys.stderr.write('Connecting to {}\n'.format(ws_conn))
    try:
        app = App(ws_conn)
    except socket.error:
        sys.stderr.write('###Error connecting to {}###\n'.format(ws_conn))
        sys.exit(-1)
    try:
        app.cmdloop()
    except KeyboardInterrupt:
        pass 
