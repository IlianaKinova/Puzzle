class algo:
    def __init__(self):
        pass


    def run(self):
        pass

class algoSelector:
    def __init__(self):
        self.algos:list[algo] = list()

    def register(self, algo:algo):
        self.algos.append(algo)

    def run(self):
        s = 'Select algo:\n'
        for i, a in enumerate(self.algos):
            s += f'\t{i} -> {a.__class__.__name__}: {a.__class__.__doc__.split(";")[0]}\n'
        s+='\n-> '
        index = int(input(s))

        desc = self.algos[index].__class__.__doc__.split(';')
        print(f'\nStarting {self.algos[index].__class__.__name__}...\nDesc:\n{desc[0]}\n{desc[1]}')
        self.algos[index].run()


