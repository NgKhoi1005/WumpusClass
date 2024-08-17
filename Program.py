import numpy as np

'''
Elements = {'Wumpus' : 0,
           'Pit' : 1,
            }

'''
class Program:
    
    # init a map
    def __init__(self):
        return self
    
    def __init__(self, size):
        self.map_size = size
        self.map = np.ndarray(shape=(size, size), dtype=np.str_)
        '''
        self.map = [['A', '-', 'P', '-'],
                    ['-', '-', '-', '-'],
                    ['W', 'G', '-', '-'],
                    ['W', '-', '-', 'P']]
        '''
        self.map =  [
            ['H', 'H', 'P', 'W', 'H', 'H'],
            ['H', 'H', 'H', 'H', 'H', 'P'],
            ['H', 'H', 'H', 'H', 'H', 'H'],
            ['W', 'G', 'H', 'H', 'P', 'H'],
            ['H', 'H', 'P', 'H', 'H', 'H'],
            ['H', 'H', 'H', 'H', 'W', 'H']
        ]
        
        
        
    # access a cell
    def getCell(self, i, j):
        return self.map[i][j]
    
    # Let Agent know what adjacent to the cell(i, j)
    def getPerceive(self, i, j):
        if i < 0 or i >= self.map_size or j < 0 or j >= self.map_size:
            return None
        
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        percept = []
        print('From cell ', i, j)

        # check for Gold, because it does not have signal
        if self.map[i][j] == 'G':
            print('-- Program tell Gold here!')
            percept.append('G' + str(i) + ',' + str(j))
            self.map[i][j] = '-'                            # because the Agent will grab it immediately

        if self.map[i][j] == 'H':
            print('-- Program tell Healing Potion here!')
            percept.append('H' + str(i) + ',' + str(j))
            self.map[i][j] = '-'                            # because the Agent will grab it immediately


        # check for around cells (i, j) to send signal
        for direction in directions:
            x, y = i + direction[0], j + direction[1]
            if(x >= 0 and x < self.map_size and y >= 0 and y < self.map_size):
                
                if self.map[x][y] == 'W':   # Wumpus around (i, j) -> (i, j) must be Stench
                    print('-- Program tell Stench here!')
                    temp = 'S' + str(i) + ',' + str(j)
                    percept.append(temp)
                    
                if self.map[x][y] == 'P':   # Pit around (i, j) -> (i, j) must be Breeze
                    print('-- Program tell Breeze here!')
                    temp = 'B' + str(i) + ',' + str(j)
                    percept.append(temp)

                if self.map[x][y] == 'H':   # Healing Potion around (i, j) -> (i, j) must be Glow
                    print('-- Program tell Glow here!')
                    temp = 'L' + str(i) + ',' + str(j)
                    percept.append(temp)
                    

        return percept


    def remove(self, lit, x, y):
        if self.map[x][y] == lit:
            self.map[x][y] = '-'