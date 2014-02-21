import json
import requests
from time import sleep
from datetime import datetime


TOWER = 'http://localhost:6400/'


def fetch_daemons():
    try:
        response = requests.get(TOWER)
        daemons = json.loads(response.text)
        return daemons
    except:
        print 'failed to fetch daemons.'


def fetch_daemon_detail(daemon):
    try:
        response = requests.get(daemon['address'])
        details = json.loads(response.text)
        return details
    except:
        print 'failed to fetch daemon data'


def main():
    while True:
        print datetime.utcnow()
        daemons = fetch_daemons()
        for worker_id, daemon in daemons.iteritems():
            print worker_id, daemon
            details = fetch_daemon_detail(daemon)
            if details:
                print ' =>', details

        print '---'
        sleep(2)
        print

if __name__ == '__main__':
    main()
