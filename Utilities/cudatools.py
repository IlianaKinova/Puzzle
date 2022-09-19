from typing import List, Tuple
from Utilities.ExecData import ExecData
from cudashapes.board import board
from cudashapes.shape import shape
import numpy as np
import pycuda.gpuarray as gpuarray

def orientations(s:shape, b:board, execData:ExecData):
    for o in s.orientations:
        for x in positions(s, b, o, execData):
            yield x

def positions(s:shape, b:board, o, execData:ExecData):
    w1, h1 = b.actual.shape
    w2, h2 = o.shape
    w = w1-w2
    h = h1-h2 + 1
    for ww in range(w):
        for hh in range(h):
            res = b.place(o, (ww, hh))
            execData.addIter()
            if res:
                yield res, o, (ww, hh)

def findPattern(o, pos:Tuple[int, int], arr, pattern):
    w, h = arr.shape
    ptw, pth = pattern.shape
    larger = np.full((w+2*(ptw-1), h+2*(pth-1)), 2, 'uint8')
    
    larger[ptw-1:-(ptw-1),pth-1:-(pth-1)] = (arr!=0) + 1
    sw, sh = o.shape
    px, py = pos
    for resx, x in enumerate(range(px, (px + sw + 4) - (ptw-1))):
        for resy, y in enumerate(range(py, (py + sh + 4) - (pth-1))):
            l = larger[x:x+ptw,y:y+pth]
            r = l & pattern
            if np.all(r):
                return True

def findPatterns(o, pos:Tuple[int,int], arr, patterns):
    for pattern in patterns:
        if findPattern(o, pos, arr, pattern):
            return True
    return False

