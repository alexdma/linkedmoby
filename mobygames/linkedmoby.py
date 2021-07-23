'''
Created on 23 lug 2021

@author: adamou
'''

import requests, time

from rdf.config import config as cfg

ENDPOINT = cfg['moby']['endpoint']
API_STEP = 100
REQ_RATE = cfg['moby']['rate']


def RateLimited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)

    def decorate(func):
        lastTimeCalled = [0.0]

        def rateLimitedFunction(*args, **kargs):
            elapsed = time.perf_counter() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait > 0:
                time.sleep(leftToWait)
            ret = func(*args, **kargs)
            lastTimeCalled[0] = time.perf_counter()
            return ret

        return rateLimitedFunction

    return decorate


@RateLimited(REQ_RATE)  # Default is one in ten seconds
def callMoby(resource, auth):
    print('calling <{}> ... '.format(resource), end='')
    response = requests.get('/'.join((ENDPOINT, resource)), auth=auth)
    return response.json()
