from enum import Enum
from re import S
import re
from typing import Any, Callable, Dict, Iterable, List, Tuple, Union
import numpy as np

Entry = Union[str, float, int]

BaseEntry = Union[Callable[[],Entry], Entry]

class CombineCells:
    def __init__(self, value:BaseEntry, count):
        self.value = value
        self.count = count

AnyEntry = Union[BaseEntry, CombineCells]

class DebugGridState:
    def __init__(self):
        self.row = -1
        self.column = 0
        self.indentation = 0
        self.grid:list[list[AnyEntry]] = list()

    def indent(self):
        self.indentation += 1
    
    def unindent(self):
        self.indentation = max(0, self.indentation - 1)

    def appendRow(self, *args:AnyEntry, values:Iterable[AnyEntry]=None):
        self.column = 0
        self.grid.append(list())
        self.row += 1
        for _ in range(self.indentation):
            self.appendColumn()
        if values is not None:
            for v in values:
                self.appendColumn(v)
        elif len(args) > 0:
            for v in args:
                self.appendColumn(v)
                
    
    def appendColumn(self, entry:AnyEntry=None):
        if isinstance(entry, CombineCells):
            [self.grid[self.row].append('') for _ in range(entry.count)]
            self.grid[self.row][self.column] = entry
            self.column += entry.count
        else:
            self.grid[self.row].append(entry if entry is not None else '')
            self.column += 1

class DebugStyle:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def apply(self, state:DebugGridState, tag:str, value):
        pass

    def valid(self, tag:str):
        return not tag.startswith('_')

class EntryDebugStyle(DebugStyle):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def apply(self, state: DebugGridState, tag: str, value):
        state.appendColumn()

class ListStyle(Enum):
    Horizontal = 0
    Vertical = 1
    Grid = 2

class ListDebugStyle(DebugStyle):
    def __init__(self, listing:ListStyle, maxColumns:int = 5, **kwargs):
        self.listing = listing
        self.maxColumns = maxColumns
        super().__init__(**kwargs)

    def apply(self, state: DebugGridState, tag:str, value:Iterable):
        if not self.valid(tag):
            return
        state.appendRow(tag)
        if self.listing == ListStyle.Horizontal:
            for v in value:
                state.appendColumn(v)
        elif self.listing == ListStyle.Vertical:
            state.indent()
            for i, v in enumerate(value):
                if i != 0:
                    state.appendRow()
                state.appendColumn(v)
            state.unindent()
        else:
            state.indent()
            for i, v in enumerate(value):
                if i != 0 and i % self.maxColumns == 0:
                    state.appendRow()
                state.appendColumn(v)
            state.unindent()

class DictDebugStyle(DebugStyle):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def apply(self, state: DebugGridState, tag: str, value:Dict[str, AnyEntry]):
        if not self.valid(tag):
            return
        state.appendRow(tag)
        state.indent()
        first = True
        for k, v in value.items():
            if not self.valid(k):
                continue
            if not first:
                state.appendRow(k, v)
            else:
                first = False
                state.appendColumn(k)
                state.appendColumn(v)
        state.unindent()

class ObjectAsDictDebugStyle(DictDebugStyle):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def apply(self, state: DebugGridState, tag: str, value: Any):
        return super().apply(state, tag, value.__dict__)

class DebugStyleFilter:
    def __init__(self, whitelist:List[Union[str,Any]]=None, blacklist:List[Union[str,Any]]=None):
        self.clsWhitelist = list()
        self.tagWhitelist = list()
        self.clsBlacklist = list()
        self.tagBlacklist = list()

        if whitelist is not None:
            for f in whitelist:
                if isinstance(f, str):
                    self.tagWhitelist.append(f)
                else:
                    self.clsWhitelist.append(f)

        if blacklist is not None:
            for f in blacklist:
                if isinstance(f, str):
                    self.tagBlacklist.append(f)
                else:
                    self.clsBlacklist.append(f)
        
    def valid(self, tag:str, value:Any):
        for f in self.tagBlacklist:
            if re.match(f, tag) is not None:
                return False
        for f in self.clsBlacklist:
            if isinstance(value, f):
                return False
        for f in self.tagWhitelist:
            if re.match(f, tag):
                return True
        for f in self.clsWhitelist:
            if isinstance(value, f):
                return True
        return False

DebugEntry = Union[AnyEntry, List[AnyEntry], Dict[str, AnyEntry], Any]

class DebugGrid:
    def __init__(self):
        """Provide dictionaries or objects to display in a grid"""
        """Members starting with a '_' will be ignored"""

        self.values:Dict[str,DebugEntry] = dict()
        self.styles:list[Tuple[DebugStyleFilter, DebugStyle]] = list()
        self.state = DebugGridState()

    def addFilter(self, f:DebugStyleFilter, s:DebugStyle):
        self.styles.append((f, s))

    def findStyle(self, k:str, v:DebugEntry):
        if callable(v):
            v = v()
        for f, s in self.styles:
            if f.valid(k, v):
                return s
        if isinstance(v, (int, float, str)):
            return EntryDebugStyle()
        return None

    def explore(self, entries:Dict[str, AnyEntry]):
        for k, v in entries.items():
            s = self.findStyle(k, v)
            if isinstance(s, EntryDebugStyle):
                self.state.appendRow(k, v)
            elif s is not None:
                s.apply(self.state, k, v)
    
    def display(self, **kwargs:DebugEntry):
        self.values = kwargs
        self.state = DebugGridState()

        self.explore(self.values)

        columnCount = max([len(l) for l in self.state.grid])
        sizes = np.zeros((columnCount),'int64')
        for row in self.state.grid:
            for i, cell in enumerate(row):
                sizes[i] = int(max(len(str(cell)), sizes[i]))

        s = ''
        for row in self.state.grid:
            for i, cell in enumerate(row):
                l = len(str(cell))
                s += str(cell)
                for _ in range(sizes[i] - l):
                    s+=' '
                s+='\t'
            s+='\n'
        print(s)

                
class DataClass:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def testDisplay():
    data = DataClass(Foo="Hello", Bar="Bye")

    grid = DebugGrid()

    grid.addFilter(DebugStyleFilter(whitelist=[list]),ListDebugStyle(ListStyle.Horizontal))
    grid.addFilter(DebugStyleFilter(whitelist=[DataClass]), ObjectAsDictDebugStyle())

    grid.display(names=["values"], x=1, y=[3,5,6], data=data)


testDisplay()