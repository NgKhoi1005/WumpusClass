from Agent import Agent

class Program:
    def __init__(self, fileName):
        self.map = self.read_Map('maps/' + fileName)
        self.map_size = len(self.map[0])
        agent = Agent(self.map_size)

        agent.explore_map(self, agent, 0, 0)
        print(f"Total Score: {agent.score}")

        
    def read_Map(self, filename):
        self.map = []
        with open(filename, 'r') as f:
            n = int(f.readline().strip())

            for _ in range(n):
                line = f.readline().strip()
                row = line.split('.')
                self.map.append(row)
        return self.map
    
    
    def write_Map(self, filename):
        filename = "result" + filename.split('.')[0][-1] + ".txt"
        
    # access a cell
    def getCell(self, i, j):
        return self.map[i][j]
    
    # Let Agent know what adjacent to the cell(i, j)
    def getPerceive(self, i, j):
        if i < 0 or i >= self.map_size or j < 0 or j >= self.map_size:
            return None
        
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        percept = []
        print('From cell ', i+1, j+1)

        # check for Gold, because it does not have signal
        if self.map[i][j] == 'G':
            print('-- Program tell Gold here!')
            percept.append('G' + str(i) + ',' + str(j))
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

                if self.map[x][y] == 'H_P':   # Healing Potion around (i, j) -> (i, j) must be Glow
                    print('-- Program tell Glow here!')
                    temp = 'G_L' + str(i) + ',' + str(j)
                    percept.append(temp)

                if self.map[x][y] == 'P_G':   # Poisonous Gas around (i, j) -> (i, j) must be Whiff
                    print('-- Program tell Whiff here!')
                    temp = 'W_H' + str(i) + ',' + str(j)
                    percept.append(temp)
                    
        return percept

    def remove(self, lit, x, y):
        if self.map[x][y] == lit:
            self.map[x][y] = '-'