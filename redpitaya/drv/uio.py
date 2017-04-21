import fcntl
import mmap

from pyudev import Devices, Context
from pathlib import Path

class _uio_map (object):
    def __init__(self, path: Path):
        self.index  = int(path.name[-1])
        self.name   =     self.read(path, 'name')
        self.addr   = int(self.read(path, 'addr'  ), 16)
        self.offset = int(self.read(path, 'offset'), 16)
        self.size   = int(self.read(path, 'size'  ), 16)
    def read (self, path, name):
        with Path(path, name).open() as attr:
            return (attr.read())

class uio (object):
    """UIO class provides user space access to UIO devices.

    When instantiating this class the next steps are performed:

    1. The provided UIO device file is first opened.
    2. An attempt is made to exclusively lock the device file.
       If another process has already locked this file
       an error will be rised. This prevents multiple
       applications from accessing the same HW module.
    3. If locking is sucessfull sysfs arguments will be read
       to determine the maps listed in the device tree.
       All maps will be `mmap`ed into memory and provided
       as a tuple.

    When an instance of :class:`uio` is deleted the next steps are performed:

    1. Close all memory mappings.
    2. Close the UIO device file, which also releases the exclusive lock.

    Parameters
    ----------
    uio : :obj:`str`
        device node path

    Attributes
    ----------
    uio_mmaps : :obj:`touple` of :class:`mmap` objects
        List of all memory maps derived from device tree node for the UIO device.
    """

    def __init__(self, uio: str):
        # store UIO device node path
        self.uio_path = uio

        # open device file
        try:
            self.uio_dev = open(self.uio_path, 'r+b')
        except OSError as e:
            raise IOError(e.errno, "Opening {}: {}".format(self.uio_path, e.strerror))

        # exclusive lock
        try:
            fcntl.flock(self.uio_dev, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError as e:
            raise IOError(e.errno, "Locking {}: {}".format(self.uio_path, e.strerror))

        # mmap all maps listed in device tree
        self.uio_mmaps = (self._uio_mmap(uio_map) for uio_map in self._uio_maps())

    def __del__(self):
        print('UIO __del__ was activated.')
        # close memory mappings
        for uio_mmap in self.uio_mmaps:
            uio_mmap.close()
        # close uio device (also releases exclusive lock)
        try:
            self.uio_dev.close()
        except OSError as e:
            raise IOError(e.errno, "Closing {}: {}".format(self.uio_path, e.strerror))

    def _uio_maps(self):
        # UDEV device path
        uio_udev_path  = Devices.from_device_file(Context(), self.uio_path)
        # UIO maps path
        uio_maps_path  = Path(uio_udev_path.sys_path, 'maps')
        # list od UIO maps paths
        uio_maps_paths = list(uio_maps_path.iterdir())
        # list of UIO map objects
        return [_uio_map(uio_map_path) for uio_map_path in uio_maps_paths]

    def _uio_mmap (self, uio_map: _uio_map):
        try:
            uio_mmap = mmap.mmap(fileno = self.uio_dev.fileno(),
                                 length = uio_map.size,
                                 offset = uio_map.index * mmap.PAGESIZE,
                                 flags  = mmap.MAP_SHARED,
                                 prot   = mmap.PROT_READ | mmap.PROT_WRITE)
        except OSError as e:
            raise IOError(e.errno, "Mapping {} map {} size {}: {}".format(self.uio_path, uio_map.name, uio_map.size, e.strerror))
        return uio_mmap

    def pool(self):
        """
        TODO: implement interrupt support
        """
        pass
