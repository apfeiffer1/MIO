__author__ = 'ap'

from os import getcwd, makedirs
from os.path import normpath, join, exists
import glob

from Channel import Channel

class Dataset():

    def __init__(self, name, mode, nClients=1):

        self.dsName = name
        self.dsMode = mode
        self.nChan  = nClients

        self.channels = []

        try:
            self.setup()
        except Exception, e:
            msg = "ERROR could not create Dataset: %s in %s for %s " % (self.dsName , getcwd(), self.dsMode)
            if str(e): msg += '\n'+str(e)
            raise Exception(msg)

    def setup(self):

        self.basePath = normpath( self.dsName )
        if not self.dsName.startswith('/'):
            self.basePath = normpath( join( getcwd(), self.dsName ) )

        if self.dsMode == 'r':
            if not exists(self.basePath):
                msg = "ERROR: no Dataset found at %s " % (self.dsName,)
                raise Exception(msg)
            self.fileList = glob.glob( self.basePath+'/*/file*' )
            self.actualFileIndex = 0
            self.actualFile = open(self.fileList[self.actualFileIndex], 'rb')
            self.allRead  = False
            return

        # writing mode from here:
        if not exists(self.basePath): makedirs( self.basePath )

        if not exists(self.basePath):
            msg = "ERROR could not create Dataset: %s in %s for %s " % (self.dsName , getcwd(), self.dsMode)
            raise Exception(msg)

        return

    def __del__(self):
        if self.dsMode == 'w':
            # write out some meta data, like the number of channels used for writing
            #-todo: check what to do for append/update mode
            metaFile = open( normpath( join( self.basePath, 'meta.info') ), 'w' )
            metaFile.write( "writers : " + str(len(self.channels)) )
            metaFile.close()

        if self.dsMode == 'r':
            if self.actualFile:
                self.actualFile.close()


        for c in self.channels:
            c.close()
            del c

    def getChannel(self):

        id = len(self.channels)
        path = normpath( join( self.basePath, str(id) ) )
        chan = Channel( id, path, self.dsMode )
        self.channels.append( chan )

        return chan

    def nextFile(self):
        self.nextFileIndex += 1
        if self.nextFileIndex > len(self.fileList):
            return -1
        return self.nextFileIndex

    def updateActualFile(self):

        self.actualFileIndex += 1
        if self.actualFileIndex >= len(self.fileList):
            self.actualFile = None
            self.allRead = True
            return

        self.actualFile = open(self.fileList[self.actualFileIndex], 'rb')

        return

    def read(self, bufSize=512):
        if self.allRead: return

        chunk = self.actualFile.read(bufSize)
        if chunk: return chunk

        # go for next file
        self.updateActualFile()
        return self.read(bufSize)