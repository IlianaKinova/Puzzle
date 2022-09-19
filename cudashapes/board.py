from typing import List
import numpy as np

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


        for i, line in enumerate(lines):
            for ii, c in enumerate(line):
                if c is ' ':
                    self.empty[ii,i] = 0b00000000
                elif c is 'O':
                    self.empty[ii,i] = 0b01000000
        self.verify = np.full(np.shape(self.empty), 0b10000000)
        self.clear()

    def clear(self):
        self.idGen = 0
        self.actual = np.array(self.empty)

    def copy(self):
        return board(*self.repr)

    def place(self, shape, pos):
        newId = self.idGen + 1
        w, h = np.shape(shape)
        x, y = pos
        s = (shape + newId) * (shape > 0)
        res = np.array(self.actual)
        try:
            res[x:x+w,y:y+h] += np.array(s, 'uint8')
        except:
            return False

        if np.any(res >= self.verify):
            return False
        self.actual = res
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
    
