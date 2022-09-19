from datetime import timedelta
from random import shuffle
from threading import Thread, current_thread
from time import sleep
from typing import Iterable, List, Tuple
from Utilities.ExecData import ExecData
from algos.algo import algo
from shapes.board import board
from shapes.shape import shape
from Utilities.tools import countPermutations, drawGrid, exists, findPatterns, orientations, positions
import numpy as np

class algo2(algo):
    """First optimization to exclude known impossible positions;
    Goes through all positions and orientations possible for every shape
    and check if an unsolvable position was created from the last
    piece placed.
    """
    def __init__(self, shapes:List[shape], b:board):
        super().__init__()
        self.shapes = shapes
        self.b = b

        

        # Patterns:
        # 1 means that the space has to be empty
        # 2 means that the space has to be occupied
        # 3 means that it has to be ignored (any is accepted)
        patterns = [
            [
                [3,2,3],
                [2,1,2],
                [3,2,3],
            ],
            [
                [3,2,3],
                [2,1,2],
                [2,1,2],
                [3,2,3],
            ],
            [
                [3,2,3],
                [2,1,2],
                [2,1,2],
                [2,1,2],
                [3,2,3],
            ],
            [
                [3,2,3],
                [2,1,2],
                [2,1,2],
                [2,1,2],
                [2,1,2],
            ],
            [
                [3,2,2,3],
                [2,3,1,2],
                [2,3,3,2],
                [3,2,2,3],
            ],
            [
                [3,2,2,2,3],
                [2,1,3,1,2],
                [2,3,3,2,2],
                [2,1,2,3,3],
                [3,2,3,3,3],
            ],
        ]


        orientations = list()
        # Rotations and flips
        for p in patterns:
            for i in range(4):
                r = np.rot90(p, i, (0,1))
                if not exists(r, orientations):
                    orientations.append(r)
                
                fx = np.fliplr(r)
                if not exists(fx, orientations):
                    orientations.append(fx)

                fy = np.flipud(r)
                if not exists(fy, orientations):
                    orientations.append(fy)

        self.orientations = np.array(orientations)

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
        self.algo2(ss, b)
        print(f'{current_thread().name} terminated!')

    def minesweeper(self, o, pos:Tuple[int,int], arr, thresh:int):
        mask = np.array([
            [0,1,0],
            [1,0,1],
            [0,1,0]
        ],'uint8')
        mask = 1-mask
        w, h = arr.shape
        larger = np.full((w+4, h+4), 0b01000000, 'uint8')
        larger[2:-2,2:-2] = arr[:,:]
        sw, sh = o.shape
        px, py = pos
        res = np.full((sw+2, sh+2), 9, 'uint8')
        full = np.full(larger.shape, 9, 'uint8')
        for resx, x in enumerate(range(px, px + sw + 2)):
            for resy, y in enumerate(range(py, py + sh + 2)):
                if larger[x+1,y+1] <= thresh:
                    res[resx, resy] = np.sum(larger[x:x+3,y:y+3] == mask)
        return res, full

    def algo2(self, ss:Iterable[shape], b:board):
        shapes = ss
        
        

        for i, s in enumerate(shapes):
            for _, o, (x,y) in orientations(s, b, self.execData):
                if len(shapes) < 5 and self.execData:
                    self.execData.debugIters()
                    b.draw()
                    self.execData._nextPrint += timedelta(seconds=1)
                if findPatterns(o, (x, y), b.actual, self.orientations):
                    b.undo()
                    continue
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
                res = self.algo2(inner, b)
                if res:
                    return True
        b.undo()
        if b.actual[0,0] & 0b00111111 == 0 and b.actual[0,0] != 0:
            print("hi")

    def run(self):
        count = int(input("Thread count: "))
        self.multi(count)