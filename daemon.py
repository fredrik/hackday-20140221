import time
import logging

logger = logging.getLogger('daemon')


class SomeDaemon(object):
    def __init__(self):
        logger.info('SomeDaemon starting.')

    def run(self):
        while True:
            print 'running'
            time.sleep(0.25)


def main():
    SomeDaemon().run()


if __name__ == '__main__':
    main()
