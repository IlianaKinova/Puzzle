from typing import List, Tuple
from Utilities.ExecData import ExecData
from shapes.board import board
from shapes.shape import shape
import numpy as np

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

def drawGrid(g):
    g = np.fliplr(np.rot90(g, 3))
    s = '+'
    for _ in range(len(g[0] - 1)):
        s+='-'
    s+='+\n'
    for i, rows in enumerate(g):
        s+='|'
        for ii, v in enumerate(rows):
            s+=f"{int(g[i,ii] & 0b00111111) if g[i,ii] != 0 else ' '}"
        s+='|\n'
    s+= '+'
    for _ in range(len(g[0] - 1)):
        s+='-'
    s+='+\n'
    print(s)

def countPermutations(shapes:List[shape], b:board):
    accumulation = 1
    for s in shapes:
        w1, h1 = b.actual.shape
        w2, h2 = s.orig.shape
        w = w1-w2
        h = h1-h2
        accumulation *= h * w * len(s.orientations)
    return accumulation


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

def exists(orientation, orientations):
    for o in orientations:
        if np.array_equal(o, orientation):
            return True
    return False

def testPatterns():
    patterns = [
        [
            [2,2,2,1],
            [2,1,2,1],
            [2,2,3,1],
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

    b = board(
        "        ",
        "        ",
        "        ",
        "        ",
        "        ",
    )

    shapes = [
        shape(
            "OOO",
            "O O",
            " OO",
        )
    ]
    patterns = np.array(orientations)
    assert(b.place(shapes[0].orientations[0], (5,0)))
    r = findPatterns(shapes[0].orientations[0],(5,0), b.actual, patterns)
    assert(r)

testPatterns()

