from typing import List
import numpy as np
import pycuda.gpuarray as gpuarray
import pycuda.driver as cuda
import pycuda.compiler as compiler

class board:
    def __init__(self, *strRepresentation:str):
        self.colors = [
            '\033[0;30;41m',
            '\033[0;30;42m',
            '\033[0;30;43m',
            '\033[0;30;44m',
            '\033[0;30;45m',
            '\033[0;30;46m',
            '\033[0;30;47m',
            '\033[0;31;41m',
            '\033[0;31;42m',
            '\033[0;31;43m',
            '\033[0;31;44m',
            '\033[0;31;45m',
            '\033[0;31;46m',
            '\033[0;31;47m',
            ]
        self.black = '\033[0;37;40m'
        self.repr = strRepresentation

        lines = strRepresentation
        self.empty = np.zeros((len(lines[0]), len(lines)), 'uint8')

        boardcode = """
        __global__ void place(%(dtype)s* board, %(dtype)s* shape, const %(dtype)s newId, const int x, const int y, const int shapew, const int shapeh, %(dtype)s* res, %(dtype)s* success)
        {
            const int idx = threadIdx.x + ncols * threadIdx.y;
            const int shapeidx = (threadIdx.x - x) + shapew * (threadIdx.y - y);
            if (x <= threadIdx.x && threadIdx.x < x + shapew && y <= threadIdx.y && threadIdx.y < y + shapeh)
                res[idx] = board[idx] + shape ? (shape[shapeidx] + newId) : 0;
            else
                res[idx] = board[idx]
            if (res[idx] >= 0b10000000) *sucess = false;
        }

        __global__ void undo(%(dtype)s* board, const %(dtype)s id, const int x, const int y)
        {
            const int idx = threadIdx.x + x + %(ncols)s * (threadIdx.y + y);
            if (board[idx] & 0b00111111 == id) board[idx] = 0;
        }
        """ % { 
            'dtype':"unsigned char",
            'ncols':self.empty.shape[0],
            }


        boardmod = compiler.SourceModule(boardcode)
        self.cudaPlace = boardmod.get_function('place')
        self.cudaUndo = boardmod.get_function('undo')

        for i, line in enumerate(lines):
            for ii, c in enumerate(line):
                if c is ' ':
                    self.empty[ii,i] = 0b00000000
                elif c is 'O':
                    self.empty[ii,i] = 0b01000000
        self.empty = gpuarray.to_gpu(self.empty)
        self.res = self.empty.copy()
        self.clear()

    def clear(self):
        self.idGen = 0
        self.actual = self.empty.copy()

    def copy(self):
        return board(*self.repr)

    def place(self, shape, pos):
        newId = self.idGen + 1
        success = gpuarray.to_gpu(np.array([1], 'uint8'))

        w, h = shape.shape
        x, y = pos

        self.cudaPlace(cuda.In(self.actual), cuda.In(shape), np.ubyte(newId), np.ubyte(x), np.ubyte(y), np.ubyte(w), np.ubyte(h), success, cuda.Out(self.res),
        cuda.InOut(success))
        
        if not success.get()[0]:
            return False
        
        self.actual = self.res.copy()
        self.idGen = newId
        return True

    def undo(self):
        self.actual -= np.array(((self.actual & 0b00111111) == self.idGen) * (0b01111111 & self.idGen | 0b01000000), 'uint8')
        self.idGen -= 1

    def draw(self):
        b = np.fliplr(np.rot90(self.actual, 3))
        s = self.black
        s = '+'
        for _ in range(len(b[0] - 1)):
            s+='-'
        s+='+\n'
        for i, rows in enumerate(b):
            s+=self.black + '|'
            for ii, v in enumerate(rows):
                s+=f"{self.colors[int(b[i,ii] & 0b00111111)]}{int(b[i,ii] & 0b00111111) if b[i,ii] != 0 else self.black + ' '}"
                # s+=f"{int(b[i,ii] & 0b00111111) if b[i,ii] != 0 else ' '}|"
            s+=self.black + '|\n'
            # s+='\n+'
            # for _ in range(len(rows)):
            #     s+='-+'
            # s+='\n'
        s+= '+'
        for _ in range(len(b[0] - 1)):
            s+='-'
        s+='+\n'
        print(s)
    
