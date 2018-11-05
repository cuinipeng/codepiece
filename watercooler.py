import logging
import signal
import time

from urllib.parse import urlparse
from collections import defaultdict

from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.options import define, parse_command_line, options
from tornado.websocket import WebSocketHandler, WebSocketClosedError


define('debug', default=False, type=bool, help='Run in debug mode')
define('port', default=8080, type=int, help='Server port')
define('allowed_hosts', default='localhost:8080', multiple=True,
    help='Allowed hosts for cross doamin connections')


class ScrumApplication(Application):
    def __init__(self, **kwargs):
        routes = [
            (r'/(?P<sprint>[0-9]+)', SprintHandler),
        ]
        super().__init__(routes, **kwargs)
        self.subscriptions = defaultdict(list)

    def add_subscriber(self, channel, subscriber):
        self.subscriptions[channel].append(subscriber)

    def remove_subscriber(self, channel, subscriber):
        self.subscriptions[channel].remove(subscriber)

    def get_subscribers(self, channel):
        return self.subscriptions[channel]

    def broadcast(self, message, channel=None, sender=None):
        if channel is None:
            for c in self.subscriptions.keys():
                self.broadcast(message, channel=c, sender=sender)
        else:
            peers = self.get_subscribers(channel)
            for peer in peers:
                if peer != sender:
                    try:
                        peer.write_message(message)
                    except WebSocketClosedError:
                        self.remove_subscriber(channel, sender)

def shutdown(server):
    ioloop = IOLoop.instance()
    logging.info('Stopping server.')
    server.stop()

    def finalize():
        ioloop.stop()
        logging.info('Stopped.')

    ioloop.add_timeout(time.time() + 1.5, finalize)


# 定义 websocket 连接处理器
class SprintHandler(WebSocketHandler):
    """
    Handles real-time updates to the board
    """
    def check_origin(self, origin):
        allowed = super().check_origin(origin)
        parsed = urlparse(origin.lower())
        matched = any(parsed.netloc == host for host in options.allowed_hosts)
        return options.debug or allowed or matched

    def open(self, sprint):
        """
        Subscribe to sprint updates on a new connection
        """
        self.sprint = sprint
        self.application.add_subscriber(self.sprint, self)
        # print(self.application.subscriptions)

    def on_message(self, message):
        """
        Broadcast updates to other interested clients
        """
        # message <class 'str'>
        self.application.broadcast(message, channel=self.sprint, sender=self)

    def on_close(self):
        """
        Remove subscription
        """
        self.application.remove_subscriber(self.sprint, self)


if __name__ == '__main__':
    parse_command_line()
    application = ScrumApplication(debug=options.debug)
    server = HTTPServer(application)
    server.listen(options.port)
    signal.signal(signal.SIGINT, lambda sig, frame: shutdown(server))
    logging.info('Starting server on localhost:{}'.format(options.port))
    IOLoop.instance().start()



"""
Javascript WebSocket Client

var socket = new WebSocket('ws://localhost:8080/123')
socket.onopen = function() {
    console.log('Connection is open!');
    socket.send('ping');
};
socket.onmessage = function(message) {
    console.log('New messaage: ' + message.data);
    if (message.data == 'ping') {
        socket.send('pong');
    }
};
"""