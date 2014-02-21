import gevent

from daemon import Daemon


class EggDaemon(Daemon):
    VERSION = '3.1415'
    TYPE = 'egg'

    def work(self):
        print 'hatching eggs.'
        while True:
            gevent.sleep(1.25)
            print 'one small egg ready.'
            self._stats['eggs'] += 1


if __name__ == '__main__':
    EggDaemon().run()
