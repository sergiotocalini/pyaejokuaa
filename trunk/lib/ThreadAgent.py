#!/usr/bin/env python
from threading import Thread

class Agent(Thread):
    def __init__(self, worker_class, args, callbacks=[]):
        Thread.__init__(self)
        self._args = args
        self._worker_class = worker_class
        self._callbacks = callbacks
                
    def run(self):
        pa = [self._worker_class(i) for i in self._args]
        [x.start() for x in pa]
        [x.join() for x in pa]
        res = [x.get_result() for x in pa]
        [x(res) for x in self._callbacks]

