#!/usr/bin/env python

import MIO
import math
import time
# from threading import Thread as Multi
from multiprocessing import Process as Multi

class Writer(Multi) :
    def __init__(self, channelIn, nMaxIn, id):
        Multi.__init__(self)
        self.channel = channelIn
        self.nMax = nMaxIn
        self.id = " "+str(id)+"_"

    def run(self):

        for i in range(self.nMax):
            self.channel.write( self.id + str(i) )


def doIt(dsName, nThreads, nWords):

    ds = MIO.Dataset(dsName, 'w')

    threadList = []
    for i in range(nThreads):
        chan = ds.getChannel()
        threadList.append( Writer(chan, int(nWords/nThreads), i) )

    start = time.time()
    for t in threadList:
        t.start()

    for t in threadList:
        t.join()
    stop = time.time()

    print "running with ", nThreads, ' took ', stop-start, 'sec.'
    return stop-start

def measure():

    dsName = '/tmp/testFile.ds'

    finals = {}
    for k in [4,5,6]:
        results = {}
        nWords = math.pow(10,k)
        print '\n size: ', nWords
        for nth in [1,2,4,10]:
            dt = doIt(dsName, nth, nWords)
            results[nth] = dt
        finals[nWords] = results
    from pprint import pprint
    pprint(finals)

    # os.system('ls -lhR '+dsName)

# dsName = '/tmp/testFile.ds'
# dt = doIt(dsName, 2, 100000)
# print dt

measure()