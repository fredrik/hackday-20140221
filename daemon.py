import gevent
from gevent.wsgi import WSGIServer

from app import app


class SomeDaemon(object):
    def __init__(self):
        self._status = {
            'status': 'ok',
            'units': 0,
        }

    def start(self):
        """Boot workers."""
        worker = gevent.spawn(self.run)
        status = gevent.spawn(self.status)

        worker.join()
        print 'worker done:', worker.get()
        status.kill()
        print 'done.'

    def status(self):
        app._status = self._status
        http_server = WSGIServer(('', 5000), app)
        http_server.serve_forever()

    def run(self):
        for i in range(5):
            print 'running'
            self._status['units'] += 1
            gevent.sleep(0.25)
        return 32


def main():
    SomeDaemon().start()


if __name__ == '__main__':
    main()
