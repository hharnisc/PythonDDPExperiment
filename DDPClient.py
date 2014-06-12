import json
import thread
import traceback

from ws4py.client.threadedclient import WebSocketClient
from pyee import EventEmitter
from srp import _pysrp as srp

DDP_VERSIONS = ["pre1"]

class DDPClient(WebSocketClient, EventEmitter):
    """simple wrapper around Websockets for DDP connections"""
    def __init__(self, url):
        WebSocketClient.__init__(self, url)
        EventEmitter.__init__(self)
        self._session = None
        self._uniq_id = 0
        self._callbacks = {}

    def _next_id(self):
        """Get the next id that will be sent to the server"""
        self._uniq_id += 1
        return str(self._uniq_id)

    def opened(self):
        """Set the connect flag to true and send the connect message to
        the server."""
        self.send({
            "msg": "connect",
            "version": DDP_VERSIONS[0],
            "support": DDP_VERSIONS
        })

    def closed(self, code, reason=None):
        """Called when the connection is closed"""
        self.emit('socket_closed', code, reason)
        # TODO: retry here if not intended to close

    def send(self, msg_dict):
        """Send a message through the websocket client and wait for the
        answer if the message being sent contains an id attribute."""
        message = json.dumps(msg_dict)
        super(DDPClient, self).send(message)

    def received_message(self, data):
        """Incomming messages"""
        data = json.loads(str(data))
        if not data.get('msg'):
            return

        elif data['msg'] == 'failed':
            self.emit('failed', data)

        elif data['msg'] == 'connected':
            self._session = data.get('session')
            self.emit('connected')

        # method result
        elif data['msg'] == 'result':
            # call the optional callback
            callback = self._callbacks.get(data['id'])
            if callback:
                callback(data.get('error'), data.get('result'))
                self._callbacks.pop(data['id'])

        # missing subscription
        elif data['msg'] == 'nosub':
            callback = self._callbacks.get(data['id'])
            if callback:
                callback(data.get('error'), data['id'])
                self._callbacks.pop(data['id'])

        # document added to collection
        elif data['msg'] == 'added':
            self.emit('added', data['collection'],
                      data['id'], data.get('fields', {}))

        # document changed in collection
        elif data['msg'] == 'changed':
            self.emit('changed', data['collection'], data['id'],
                       data.get('fields', {}), data.get('cleared', {}))

        # document removed from collection
        elif data['msg'] == 'removed':
            self.emit('removed', data['collection'], data['id'])

        # subcription ready
        elif data['msg'] == 'ready':
            for sub_id in data.get('subs', []):
                callback = self._callbacks.get(sub_id)
                if callback:
                    callback(data.get('error'), sub_id)
                    self._callbacks.pop(sub_id)
        else:
            pass
            #print data

    def call(self, method, params, callback=None):
        """Call a method on the server"""
        cur_id = self._next_id()
        if callback:
            self._callbacks[cur_id] = callback
        self.send({'msg': 'method', 'id': cur_id, 'method': method, 'params': params})

    def subscribe(self, name, params, callback=None):
        """Subcribe to add/change/remove events for a collection"""
        cur_id = self._next_id()
        if callback:
            self._callbacks[cur_id] = callback
        self.send({'msg': 'sub', 'id': cur_id, 'name': name, 'params': params})
        return cur_id

    def unsubscribe(self, sub_id):
        """Unsubscribe from a collection"""
        self.send({'msg': 'unsub', 'id': sub_id})

    def _login(self, login_params, password, callback=None):
        """Login a user"""
        request = {'user': login_params}

        # python implementation expects that user is set here (I in SRP variables)
        # NOT 100% sure about the hash_alg and ng_type - what they look like from the
        # Meteor source 
        srp_usr = srp.User('', password, hash_alg=srp.SHA256, ng_type=srp.NG_1024)

        _, A = srp_usr.start_authentication() # A seems good here
    
        def _password_exchange_cb(error, result):
            """Password exchange callback"""
            if error:
                print error
                return
            print result
            # set `I` here direcly -- not sure about this though
            srp_usr.I = result['identity']
    
            M = srp_usr.process_challenge(result['salt'], result['B'])
            request = {'srp': {'M': M.encode('hex')}}
            print request
            self.call('login', [request], _login_cb)

        def _login_cb(error, result):
            """login callback"""
            if error:
                print error
                return
            print result

        request.update({'A': A.encode('hex')})
        self.call('beginPasswordExchange', [request], _password_exchange_cb)

    def run(self):
        try:
            super(DDPClient, self).run()
        except:
            traceback.print_exc()
        finally:
            thread.interrupt_main()
