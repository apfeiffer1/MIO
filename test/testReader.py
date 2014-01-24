#!/usr/bin/env python

import MIO
import os
import time


def doIt(dsName):
    ds = MIO.Dataset(dsName, 'r')

    start = time.time()
    nBytes = read(ds)
    stop = time.time()

    print 'reading ',nBytes,'took ', stop-start, 'sec.'


    return

def read(ds):
    content = ds.read()
    count = 0
    blocksize = 512
    last = None
    while (content):
        # if count < 10 : print count, str(content)
        last = content
        content = ds.read(blocksize)
        count += 1
    print "last:", last[:-4]

    print "got ", count, ' blocks from ds, ', count*blocksize,'bytes.'

    return count*blocksize

dsName = '/tmp/testFile.ds'
doIt(dsName)