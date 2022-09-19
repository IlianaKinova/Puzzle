from datetime import timedelta
from random import shuffle
from threading import Thread, current_thread
from time import sleep
from typing import Iterable, List
from Utilities.ExecData import ExecData
from algos.algo import algo
from shapes.board import board
from shapes.shape import shape
from Utilities.tools import countPermutations, orientations, positions


class algo1(algo):
    """Bare bones algo;
    Goes through all positions and orientations possible for every shape.
    """
    def __init__(self, shapes:List[shape], b:board):
        super().__init__()
        self.shapes = shapes
        self.b = b

    def multi(self, count:int):
        self.ts = []
        self.boards = []
        self.sh = []

        self.execData = ExecData(countPermutations(self.shapes, self.b))


        for _ in range(count):
            b = self.b.copy()
            self.boards.append(b)
            shuffle(self.shapes)
            s = list(self.shapes)
            self.sh.append(s)
            t = Thread(target=self.algoRun, args=[s, b])
            self.ts.append(t)

        for t in self.ts:    
            t.start()
        
        while not self.execData._done:
            sleep(5)
        
    def algoRun(self, ss:Iterable[shape], b:board):
        print(f'Started thread {current_thread().name}')
        self.execData.registerThread()
        self.algo1(ss, b)
        print(f'{current_thread().name} terminated!')


    def algo1(self, ss:Iterable[shape], b:board):
        shapes = ss
        if len(shapes) < 5 and self.execData:
            self.execData.debugIters()
            b.draw()
            self.execData._nextPrint += timedelta(seconds=1)
        for i, s in enumerate(shapes):
            for _ in orientations(s, b, self.execData):
                inner = list(ss)
                inner.pop(i)
                if self.execData._done:
                    return True
                if len(shapes) == 1:
                    self.execData._done = True
                    print("DONE!")
                    sleep(1)
                    b.draw()
                    return True
                res = self.algo1(inner, b)
                if res:
                    return True
        b.undo()
        if b.actual[0,0] & 0b00111111 == 0 and b.actual[0,0] != 0:
            print("hi")

    def run(self):
        count = int(input("Thread count: "))
        self.multi(count)