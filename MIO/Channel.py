__author__ = 'ap'

from os import getcwd, makedirs, unlink
from os.path import normpath, join, exists, getsize
import subprocess

class Channel():

    def __init__(self, id, path, mode):
        self.id   = id
        self.path = path
        self.mode = mode
        self.bufSizeLimit = 4096
        self.isClosed = False

        self.setup()

    def setup(self):

        # make sure the dir for the channel exists
        if not exists(self.path): makedirs( self.path )

        if not exists(self.path):
            msg = "ERROR could not create path for channel: ", self.id, ' as ', self.path, ' for ', self.mode
            raise Exception(msg)

        # set up buffer for writing:
        self.buffer = None
        if self.mode == 'w':
            self.bufPath = normpath( join(self.path, 'buf_'+str(self.id)) )
            if exists(self.bufPath):
                #-todo: cleanup/restore ???
                print "removing already existing buffer file at ", self.bufPath
                unlink(self.bufPath)
            self.buffer = open(self.bufPath, self.mode)

        # set up file
        self.filePath = normpath( join(self.path, 'file_'+str(self.id)) )
        if self.mode == 'w' and exists(self.filePath):
            print "removing already existing data file at ", self.filePath
            unlink(self.filePath)
        self.dataFile = open(self.filePath, self.mode)

        #-todo: set up transaction buffer

        return

    def __del__(self):
        self.close()
        return

    def close(self):

        # ignore if already called
        if self.isClosed: return

        self.flushBuffer()

        #-todo: close transaction

        self.dataFile.close()

        # clean up buffer
        if exists(self.bufPath):
            self.buffer.close()
            unlink(self.bufPath)

        self.isClosed = True

        return


    def flushBuffer(self):
        self.checkWriteMode()

        # copy the buffer over to the end of the file
        self.buffer.close()
        tmpBuf = open( self.bufPath, 'r')
        self.dataFile.write( tmpBuf.read() )
        tmpBuf.close()

        # re-create an empty buffer
        unlink(self.bufPath)
        self.buffer = open(self.bufPath, self.mode)


    def checkWriteMode(self):
        if self.mode != 'w':
            msg = "ERROR: attempting to write in readonly channel: ", self.id, ' as ', self.path, ' for ', self.mode
            raise Exception(msg)

    def write(self, what):
        self.checkWriteMode()
        self.buffer.write(what)
        if getsize(self.bufPath) > self.bufSizeLimit:
            self.flushBuffer()

