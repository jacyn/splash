import os
from datetime import datetime

from webapp import ymdfile


class AppLogger(object):

    def __init__(self, logdir="%(HOME)s/log", log_ext=".splashsite",
            log_enabled=True, debug_log_ext=".splashsite.debug", debug_log_enabled=True,
            **kwargs):
        self.logdir = logdir
        self.log_ext = log_ext
        self.log_enabled = log_enabled
        self.debug_log_enabled = debug_log_enabled
        self.debug_log_ext = debug_log_ext

    def log(self, log_info=None):

        log = None
        debug_log = None

        if self.log_enabled:
            log = ymdfile.YmdFile(extension=self.log_ext, basedir=self.logdir % os.environ)
        if self.debug_log_enabled:
            debug_log = ymdfile.YmdFile(extension=self.debug_log_ext, basedir=self.logdir % os.environ)

        if log and log_info:
            now = datetime.now().replace(microsecond=0)
            log.write(log_info, now=now)


