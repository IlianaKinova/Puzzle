from algos.algo import algoSelector
from algos.algo1.algo1 import algo1
from algos.algo2.algo2 import algo2
from algos.algo4.algo4 import algo4
from shapes.board import *
from shapes.shape import *

def main():

    shapes = [
        shape(
            "OOO",
            " O ",
            " O ",
        ),
        shape(
            "  O",
            " OO",
            "OO ",
        ),
        shape(
            "O ",
            "O ",
            "O ",
            "OO",
        ),
        shape(
            " OO",
            " O ",
            "OO ",
        ),
        shape(
            " O",
            " O",
            "OO",
            "O ",
        ),
        shape(
            "O ",
            "OO",
            "O ",
            "O ",
        ),
        shape(
            "OO",
            "OO",
            "O ",
        ),
        shape(
            "OO",
            "O ",
            "OO",
        ),
        shape(
            " OO",
            "OO ",
            " O ",
        ),
    ]

    b = board(
        "          ",
        "          ",
        "          ",
        "          ",
        "          ",)

    sel = algoSelector()
    sel.register(algo1(shapes, b))
    sel.register(algo2(shapes, b))
    sel.register(algo4(shapes, b))
    sel.run()


main()