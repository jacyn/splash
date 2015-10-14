import os
import errno
import datetime

# taken from: http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

class YmdFile(object):
    """
    Encapsulates writing to yymmdd in a auto-flush-to-disk manner
    """

    def __init__(self, extension='', basedir=''):
        self.ext = extension
        self.basedir = basedir

    def write(self, data, now=datetime.datetime.now()):
        ymd = now.strftime("%y%m%d")
        ym = now.strftime("%y%m")

        ym_path = os.path.join(self.basedir, ym)
        mkdir_p(ym_path)

        full_path = os.path.join(self.basedir, ym, ''.join([ymd, self.ext]))
        f = file(full_path, 'a')
        f.write(data)
        f.close()

