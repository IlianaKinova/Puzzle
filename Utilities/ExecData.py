
from datetime import datetime
from threading import current_thread
from time import sleep
import functools
from Utilities.DebugGrid import *


def registerThread(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        execData = kwargs['execData']
        execData.registerThread()
        return func(*args, **kwargs)
    return wrapper

def countIters(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        execData = kwargs['execData']
        execData.addIter()
        return func(*args, **kwargs)
    return wrapper


class ThreadExecData:
    def __init__(self):
        self.totalIters = 0
        self._lastItersSnapshot = 0
        self.isDone = False
        self._lastSnapshot = datetime.now()
        self.itersPerSecond = 0
    
    
    def snapshotDeltaIters(self):
        d = self._lastItersSnapshot
        self._lastItersSnapshot = self.totalIters
        now = datetime.now()
        delta = self.totalIters - d
        self.itersPerSecond = round(delta / (now - self._lastSnapshot).total_seconds(), 2)
        self._lastSnapshot = now
        return delta

class ExecData:
    def __init__(self, permutations, **kwargs):
        self._nextPrint = datetime.now()
        self._done = False
        self._mainThread = -1
        self._iters = {}
        self._lastPrint = datetime.now()
        self.data = kwargs
        self.grid = DebugGrid()
        self._permutations = permutations

        self.grid.addFilter(DebugStyleFilter(whitelist=[list]),ListDebugStyle(ListStyle.Horizontal))
        self.grid.addFilter(DebugStyleFilter(whitelist=[ThreadExecData]), ObjectAsDictDebugStyle())
        self.grid.addFilter(DebugStyleFilter(whitelist=[str, float, int], blacklist=['_*']), EntryDebugStyle())

    def registerThread(self):
        if current_thread().ident in self._iters.keys():
            return
        self._iters[current_thread().ident] = ThreadExecData()
        print(f'Registered thread: {current_thread().ident}')
        sleep(1)

    def addIter(self):
        self._iters[current_thread().ident].totalIters += 1
            
    def debugIters(self):
        sum = 0
        totalSum = 0
        for k, v in self._iters.items():
            sum+=v.snapshotDeltaIters()
            totalSum+=v.totalIters
        delta = datetime.now() - self._lastPrint
        self._lastPrint = datetime.now()
        d = {"Threads": ["Total iters", "Iters per second", "Is done"]}

        for k, v in self._iters.items():
            v:ThreadExecData
            d[f'Thread {k}'] = [v.totalIters, v.itersPerSecond, v.isDone]
        self.grid.display(Iters=totalSum, ItersPerSec=round(sum/delta.total_seconds(), 2), 
            permutations=self._permutations, permutationsLeft=self._permutations-totalSum,
            **self.data, **d)

    def __bool__(self):
        if self._mainThread == -1:
            self._mainThread = current_thread().ident
        return current_thread().ident == self._mainThread and self._nextPrint < datetime.now()