from typing import List
import numpy as np


class shape:
    def __init__(self, *strRepresentation:str):
        lines = strRepresentation
        self.orig = np.zeros((len(lines[0]),len(lines)), 'uint8')
        
        for i, line in enumerate(lines):
            for ii, c in enumerate(line):
                assert(len(line) == len(lines[0]))
                if c is ' ':
                    self.orig[ii,i] = 0b00000000
                elif c is 'O':
                    self.orig[ii,i] = 0b01000000

        orientations = []

        # Rotations and flips
        for i in range(4):
            r = np.rot90(self.orig, i, (0,1))
            if not self.exists(r, orientations):
                orientations.append(r)
            
            fx = np.fliplr(r)
            if not self.exists(fx, orientations):
                orientations.append(fx)

            fy = np.flipud(r)
            if not self.exists(fy, orientations):
                orientations.append(fy)

        self.orientations = np.array(orientations)


        
                
    def exists(self, orientation, orientations):
        for o in orientations:
            if np.array_equal(o, orientation):
                return True
        return False


