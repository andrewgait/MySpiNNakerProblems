class spks:
    def __init__(self):
        self.tb = []
        self.bt =[]
        self.rl =[]
        self.lr = []
        self.sptc = []
        self.sptcTB = []
        self.sptcBT = []
        self.sptcRL = []
        self.sptcLR = []
        self.input = []
        self.inputTB = []
        self.inputBT = []
        self.inputLR = []
        self.inputRL = []

    def give(self, i):
        if i == 'lr':
            return self.lr
        elif i == 'rl':
            return self.rl
        elif i == 'tb':
            return self.tb
        elif i == 'bt':
            return self.bt
        elif i == 'sptc':
            return self.sptc
        elif i == 'sptcRL':
            return self.sptcRL
        elif i == 'sptcLR':
            return self.sptcLR
        elif i == 'sptcsptcTB':
            return self.sptcTB
        elif i == 'sptcBT':
            return self.sptcBT

        elif i == 'input':
            return self.input
        elif i == 'inputRL':
            return self.inputRL
        elif i == 'inputLR':
            return self.inputLR
        elif i == 'inputTB':
            return self.inputTB
        elif i == 'inputBT':
            return self.inputBT


