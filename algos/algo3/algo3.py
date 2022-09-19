from datetime import timedelta
from random import shuffle
from threading import Thread, current_thread
from time import sleep
from typing import Iterable, List
from Utilities.ExecData import ExecData
from algos.algo import algo
from cudashapes.board import board
from cudashapes.shape import shape
from Utilities.tools import countPermutations, exists
from Utilities.cudatools import findPatterns, orientations
import numpy as np
import pycuda.compiler as compiler
import pycuda.driver as cuda
import pycuda.gpuarray as gpuarray

class algo3(algo):
    """CUDA accelerated, first optimization to exclude known impossible positions;
    Goes through all positions and orientations possible for every shape
    and check if an unsolvable position was created from the last
    piece placed.
    Cuda acceleration
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

        self.orientations = gpuarray.to_gpu(np.array(orientations))

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
        self.algo3(ss, b)
        print(f'{current_thread().name} terminated!')

    def algo3(self, ss:Iterable[shape], b:board):
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
                res = self.algo3(inner, b)
                if res:
                    return True
        b.undo()
        if b.actual[0,0] & 0b00111111 == 0 and b.actual[0,0] != 0:
            print("hi")

    def run(self):
        self.algoRun(self.shapes, self.b)