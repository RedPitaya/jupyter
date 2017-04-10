import fcntl
import mmap

import numpy as np

class uio (object):
    regset_dtype = np.dtype([])

    def __init__ (self, uio:str):

        # open device file
        try:
            self.uio_dev = open(uio, 'r+b')
        except OSError as e:
            raise IOError(e.errno, "Opening {}: {}".format(uio, e.strerror))

        # exclusive lock
        try:
            fcntl.flock(self.uio_dev, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError as e:
            raise IOError(e.errno, "Locking {}: {}".format(uio, e.strerror))

        # map regset
        try:
            self.uio_reg = mmap.mmap(
                fileno=self.uio_dev.fileno(), length=mmap.PAGESIZE, offset=0x0,
                flags=mmap.MAP_SHARED, prot=(mmap.PROT_READ | mmap.PROT_WRITE))
        except OSError as e:
            raise IOError(e.errno, "Mapping (regset) {}: {}".format(uio, e.strerror))

        regset_array = np.recarray(1, self.regset_dtype, buf=self.uio_reg)
        self.regset = regset_array[0]

    def __del__ (self):
        print ('UIO __del__ was activated.')
        self.uio_reg.close()
        try:
            self.uio_dev.close()
        except OSError as e:
            raise IOError(e.errno, "Closing {}: {}".format(uio, e.strerror))
