import numpy as np
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

SCORE = {
        'GOLD' :  5000,
        'SHOT' : -100,
        'CLIMB' : 10,
        'ACTION' : -10,
    }

class Agent:
    def __init__(self, map_size):
        self.map_size = map_size
        self.KB = CNF()
        self.vpool = IDPool()
        self.safe = np.ndarray((map_size, map_size))
        self.safe.fill(-1)
        self.safe[0][0] = 1
        self.visited = np.zeros(shape=(map_size, map_size), dtype='bool')
        self.visited[0][0] = 1
        self.KB.append([-self.vpool.id('P0,0')])
        self.KB.append([-self.vpool.id('W0,0')])
        self.KB.append([-self.vpool.id('H0,0')])
        self.KB.append([-self.vpool.id('P_G0,0')])
        self.health = 100
        self.hp_count = 0
        self.score = 0


    # set Perceive for cell (i, j)
    def setPerceive(self, percept):
        if percept == None:
            return
        for x in percept:
            self.KB.append([self.vpool.id(x)])

            
    def learn(self, clause):
        if clause not in self.KB.clauses:
            self.KB.append(clause)
            return 0
  
    # ================================ Handle WUMPUS===============================

    # find Wumpus (i, j) in KB
    def Wumpus(self, i, j):
        if i < 0 or i >= self.map_size or j < 0 or j >= self.map_size:
            return 0
        
        bind_str = 'W' + str(i) + ',' + str(j)
        solver = Solver(bootstrap_with=self.KB.clauses)
        solver.add_clause([-self.vpool.id(bind_str)])
    
        if solver.solve() == False:
            self.safe[i][j] = 0
            return 1
        
        return 0
    

    def noWumpus(self, i, j):
        if i < 0 or i >= self.map_size or j < 0 or j >= self.map_size:
            return 0
        
        bind_str = 'W' + str(i) + ',' + str(j)
        solver = Solver(bootstrap_with=self.KB.clauses)
        solver.add_clause([self.vpool.id(bind_str)])
    
        if solver.solve() == False:
            return 1
        
        return 0
    

    # Logic statement to detect if Wumpus is around (i, j)
    def detect_Wumpus(self, i, j):
        if i < 0 or i >= self.map_size or j < 0 or j >= self.map_size:
            return 0
        
        if i+1 < self.map_size:
            s1 = 'S' + str(i) + ',' + str(j)
            s2 = 'S' + str(i+1) + ',' + str(j+1)
            s3 = 'S' + str(i+1) + ',' + str(j-1)
            S = 'W' + str(i+1) + ',' + str(j)
            # BOTTOM, RIGHT
            if j+1 < self.map_size:
                S1 = 'W' + str(i) + ',' + str(j+1)
                sentence = [-self.vpool.id(s1), -self.vpool.id(s2), self.vpool.id(S1), self.vpool.id(S)]
                self.learn(sentence)
            # BOTTOM, LEFT
            if j-1 >= 0:
                S1 = 'W' + str(i) + ',' + str(j-1)
                sentence = [-self.vpool.id(s1), -self.vpool.id(s3), self.vpool.id(S1), self.vpool.id(S)]
                self.learn(sentence)
                
        if i-1 >= 0:
            s1 = 'S' + str(i) + ',' + str(j)
            s2 = 'S' + str(i-1) + ',' + str(j+1)
            s3 = 'S' + str(i-1) + ',' + str(j-1)
            S = 'W' + str(i-1) + ',' + str(j)
            # TOP, RIGHT
            if j+1 < self.map_size:
                S1 = 'W' + str(i) + ',' + str(j+1)
                sentence = [-self.vpool.id(s1), -self.vpool.id(s2), self.vpool.id(S1), self.vpool.id(S)]
                self.learn(sentence)
            # TOP, LEFT
            if j-1 >= 0:
                S1 = 'W' + str(i) + ',' + str(j-1)
                sentence = [-self.vpool.id(s1), -self.vpool.id(s3), self.vpool.id(S1), self.vpool.id(S)]
                self.learn(sentence)


    def confirm_NoWumpus(self, i, j):
        bind_str = 'W' + str(i) + ',' + str(j)
        Nwumpus_id = self.vpool.id(bind_str)
        self.learn([-Nwumpus_id])


    #SHOT the Wumpus
    def shot_Wumpus(self, i, j, Map):
        self.score += SCORE['SHOT']
        print('\t\t Agent shot the wumpus at (%d, %d)' %(i+1, j+1))
        self.confirm_NoWumpus(i, j)
        # forget 1 layer of Stench of cells around died Wumpus
        adj = adjCell(i, j, self.map_size)
        for x in adj:
            if self.visited[x] == 1:
                bind_str = 'S' + str(x[0]) + ',' + str(x[1])
                if [self.vpool.id(bind_str)] in [self.KB.clauses]:
                    self.KB.clauses.remove([self.vpool.id(bind_str)])
        
        w_id = self.vpool.id('W' + str(i) + ',' + str(j))
        clauses_to_remove = [clause for clause in self.KB.clauses if w_id in clause]
        for clause in clauses_to_remove:
            self.KB.clauses.remove(clause)
        
        # Tell the Program to remove wumpus (i, j) from the map
        Map.remove('W', i, j)


    # check if Stench at cell (i, j) or not   
    def check_Stench(self, i, j):
        if i < 0 or i >= self.map_size or j < 0 or j >= self.map_size:
            return 0
        
        bind_str = 'S' + str(i) + ',' + str(j)
        element_id = self.vpool.id(bind_str)
        query = [element_id]
        if element_id not in [lit for clause in self.KB.clauses for lit in clause]:
            return 0
        
        solver = Solver(bootstrap_with=self.KB.clauses)
        solver.add_clause([-lit for lit in query])
        if solver.solve() == False:         # Stench here
            self.detect_Wumpus(i, j)
            solver.delete()
            return 1

        self.learn([-self.vpool.id(bind_str)])      # tell KB that no Stench here
        solver.delete()
        return 0



    # ================================ Handle PIT=============================

    def noPit(self, i, j):
        if i < 0 or i >= self.map_size or j < 0 or j >= self.map_size:
            return 0
        
        bind_str = 'P' + str(i) + ',' + str(j)
        solver = Solver(bootstrap_with=self.KB.clauses)
        solver.add_clause([self.vpool.id(bind_str)])
    
        if solver.solve() == False:
            return 1
        
        return 0
    

    def confirm_NoPit(self, i, j):
        bind_str = 'P' + str(i) + ',' + str(j)
        Npit_id = self.vpool.id(bind_str)
        self.learn([-Npit_id])


    # find Pit (i, j) in KB
    def Pit(self, i, j):
        if i < 0 or i >= self.map_size or j < 0 or j >= self.map_size:
            return 0
        
        bind_str = 'P' + str(i) + ',' + str(j)
        solver = Solver(bootstrap_with=self.KB.clauses)
        solver.add_clause([-self.vpool.id(bind_str)])
    
        if solver.solve() == False:
            self.safe[i][j] = 0
            return 1
        else:
            return 0
        

    # Logic statement to detect if Pit is around (i, j)
    def detect_Pit(self, i, j):
        if i < 0 or i >= self.map_size or j < 0 or j >= self.map_size:
            return 0
        
        if i+1 < self.map_size:
            s1 = 'B' + str(i) + ',' + str(j)
            s2 = 'B' + str(i+1) + ',' + str(j+1)
            s3 = 'B' + str(i+1) + ',' + str(j-1)
            S = 'P' + str(i+1) + ',' + str(j)
            # BOTTOM, RIGHT
            if j+1 < self.map_size:
                S1 = 'P' + str(i) + ',' + str(j+1)
                sentence = [-self.vpool.id(s1), -self.vpool.id(s2), self.vpool.id(S1), self.vpool.id(S)]
                self.learn(sentence)
            # BOTTOM, LEFT
            if j-1 >= 0:
                S1 = 'P' + str(i) + ',' + str(j-1)
                sentence = [-self.vpool.id(s1), -self.vpool.id(s3), self.vpool.id(S1), self.vpool.id(S)]
                self.learn(sentence)
                
        if i-1 >= 0:
            s1 = 'B' + str(i) + ',' + str(j)
            s2 = 'B' + str(i-1) + ',' + str(j+1)
            s3 = 'B' + str(i-1) + ',' + str(j-1)
            S = 'P' + str(i-1) + ',' + str(j)
            # TOP, RIGHT
            if j+1 < self.map_size:
                S1 = 'P' + str(i) + ',' + str(j+1)
                sentence = [-self.vpool.id(s1), -self.vpool.id(s2), self.vpool.id(S1), self.vpool.id(S)]
                self.learn(sentence)
            # TOP, LEFT
            if j-1 >= 0:
                S1 = 'P' + str(i) + ',' + str(j-1)
                sentence = [-self.vpool.id(s1), -self.vpool.id(s3), self.vpool.id(S1), self.vpool.id(S)]
                self.learn(sentence)
    

    # Forget all logic statement of PIT at (x, y) after determining  (x, y) unsafe
    def forget_Breeze(self, x, y):
        # forget 1 layer of Breeze of cells around
        adj = adjCell(x, y, self.map_size)
        for cell in adj:
            if self.visited[cell] == 1:
                bind_str = 'B' + str(cell[0]) + ',' + str(cell[1])
                if [self.vpool.id(bind_str)] in [self.KB.clauses]:
                    self.KB.clauses.remove([self.vpool.id(bind_str)])
        
        p_id = self.vpool.id('P' + str(x) + ',' + str(y))
        clauses_to_remove = [clause for clause in self.KB.clauses if p_id in clause]
        for clause in clauses_to_remove:
            self.KB.clauses.remove(clause)
        self.learn([p_id])
        
        
    # check if Breeze at cell (i, j) or not   
    def check_Breeze(self, i, j):
        if i < 0 or i >= self.map_size or j < 0 or j >= self.map_size:
            return 0
        
        bind_str = 'B' + str(i) + ',' + str(j)
        element_id = self.vpool.id(bind_str)
        query = [element_id]
        if element_id not in [lit for clause in self.KB.clauses for lit in clause]:
            return 0
        
        solver = Solver(bootstrap_with=self.KB.clauses)
        solver.add_clause([-lit for lit in query])
        
        if solver.solve() == False:         #Breeze here
            solver.delete()
            return 1

        self.learn([-self.vpool.id(bind_str)])      # tell KB that no Breeze here
        solver.delete()
        return 0
    


    # ================================ Handle GOLD=============================

     # check if Gold at cell (i, j) or not 
    def check_Gold(self, i, j):
        if i < 0 or i >= self.map_size or j < 0 or j >= self.map_size:
            return 0
        
        bind_str = 'G' + str(i) + ',' + str(j)
        element_id = self.vpool.id(bind_str)
        query = [element_id]
        if element_id not in [lit for clause in self.KB.clauses for lit in clause]:
            return 0
        
        solver = Solver(bootstrap_with=self.KB.clauses)
        solver.add_clause([-lit for lit in query])
        
        if solver.solve() == False:                 # Gold here
            solver.delete()
            return 1

        solver.delete()
        return 0


    # delete the Gold at cell (i, j) in KB to avoid multiple grabbing
    def grabGold(self, i, j):
        self.score += SCORE['GOLD']
        self.score += SCORE['ACTION']
        G_clause = 'G' + str(i) + ',' + str(j)
        self.KB.clauses.remove([self.vpool.id(G_clause)])
    

        
    # ================================ Handle HEALING POTION=============================

    # find Healing Potion (i, j) in KB
    def isHP(self, i, j):
        if i < 0 or i >= self.map_size or j < 0 or j >= self.map_size:
            return 0
        
        bind_str = 'H' + str(i) + ',' + str(j)

        solver = Solver(bootstrap_with=self.KB.clauses)
        solver.add_clause([-self.vpool.id(bind_str)])

        if solver.solve() == False:
            self.safe[i][j] = 1
            return 1
        else:
            return 0
        
        
    def confirm_NoHP(self, i, j):
        bind_str = 'H' + str(i) + ',' + str(j)
        Nhp_id = self.vpool.id(bind_str)
        self.learn([-Nhp_id])
    

    def detect_HP(self, i, j):
        if i < 0 or i >= self.map_size or j < 0 or j >= self.map_size:
            return 0
        
        if i+1 < self.map_size:
            s1 = 'G_L' + str(i) + ',' + str(j)
            s2 = 'G_L' + str(i+1) + ',' + str(j+1)
            s3 = 'G_L' + str(i+1) + ',' + str(j-1)
            S = 'H' + str(i+1) + ',' + str(j)
            # BOTTOM, RIGHT
            if j+1 < self.map_size:
                S1 = 'H' + str(i) + ',' + str(j+1)
                sentence = [-self.vpool.id(s1), -self.vpool.id(s2), self.vpool.id(S1), self.vpool.id(S)]
                self.learn(sentence)
            # BOTTOM, LEFT
            if j-1 >= 0:
                S1 = 'H' + str(i) + ',' + str(j-1)
                sentence = [-self.vpool.id(s1), -self.vpool.id(s3), self.vpool.id(S1), self.vpool.id(S)]
                self.learn(sentence)
                
        if i-1 >= 0:
            s1 = 'G_L' + str(i) + ',' + str(j)
            s2 = 'G_L' + str(i-1) + ',' + str(j+1)
            s3 = 'G_L' + str(i-1) + ',' + str(j-1)
            S = 'H' + str(i-1) + ',' + str(j)
            # TOP, RIGHT
            if j+1 < self.map_size:
                S1 = 'H' + str(i) + ',' + str(j+1)
                sentence = [-self.vpool.id(s1), -self.vpool.id(s2), self.vpool.id(S1), self.vpool.id(S)]
                self.learn(sentence)
            # TOP, LEFT
            if j-1 >= 0:
                S1 = 'H' + str(i) + ',' + str(j-1)
                sentence = [-self.vpool.id(s1), -self.vpool.id(s3), self.vpool.id(S1), self.vpool.id(S)]
                self.learn(sentence)


    # check if Glow at cell (i, j) or not   
    def check_Glow(self, i, j):
        if i < 0 or i >= self.map_size or j < 0 or j >= self.map_size:
            return 0
        
        bind_str = 'G_L' + str(i) + ',' + str(j)
        element_id = self.vpool.id(bind_str)
        query = [element_id]
        if element_id not in [lit for clause in self.KB.clauses for lit in clause]:
            
            return 0
        
        solver = Solver(bootstrap_with=self.KB.clauses)
        solver.add_clause([-lit for lit in query])
        
        if solver.solve() == False:                 # Glow here
            solver.delete()
            return 1

        solver.delete()
        return 0
    
    
    def check_HP(self, i, j):
        if i < 0 or i >= self.map_size or j < 0 or j >= self.map_size:
            return 0
        
        bind_str = 'H' + str(i) + ',' + str(j)
        element_id = self.vpool.id(bind_str)
        query = [element_id]
        if element_id not in [lit for clause in self.KB.clauses for lit in clause]:
            return 0
        
        solver = Solver(bootstrap_with=self.KB.clauses)
        solver.add_clause([-lit for lit in query])
        
        if solver.solve() == False:                 # HP here
            solver.delete()
            return 1

        solver.delete()
        return 0
    

    # delete the Healing Potion at cell (i, j) in KB to avoid multiple grabbing
    def grabHP(self, i, j, Map):
        self.hp_count += 1
        self.score += SCORE['ACTION']
        self.forget_HP(i, j, Map)


    # Forget all logic statement of HP at (x, y) after determining
    def forget_HP(self, x, y, Map):
        # forget 1 layer of Glow of cells around
        adj = adjCell(x, y, self.map_size)
        for cell in adj:
            if self.visited[cell] == 1:
                gl_id = self.vpool.id('G_L' + str(cell[0]) + ',' + str(cell[1]))
                clauses_to_remove = [clause for clause in self.KB.clauses if gl_id in clause]
                for clause in clauses_to_remove:
                    self.KB.clauses.remove(clause)

        hp_id = self.vpool.id('H' + str(x) + ',' + str(y))
        clauses_to_remove = [clause for clause in self.KB.clauses if hp_id in clause]
        for clause in clauses_to_remove:
            self.KB.clauses.remove(clause)

        # Tell the Program to remove HP (i, j) from the map
        Map.remove('H', x, y)


    # ================================ Handle POISONOUS GAS=============================

    def isPG(self, i, j):
        if i < 0 or i >= self.map_size or j < 0 or j >= self.map_size:
            return 0
        
        bind_str = 'P_G' + str(i) + ',' + str(j)
        solver = Solver(bootstrap_with=self.KB.clauses)
        solver.add_clause([-self.vpool.id(bind_str)])
    
        if solver.solve() == False:             # PG here
            return 1
        else:
            return 0
        

    # check if Whiff at cell (i, j) or not   
    def check_Whiff(self, i, j):
        if i < 0 or i >= self.map_size or j < 0 or j >= self.map_size:
            return 0
        
        bind_str = 'W_H' + str(i) + ',' + str(j)
        element_id = self.vpool.id(bind_str)
        query = [element_id]
        if element_id not in [lit for clause in self.KB.clauses for lit in clause]:
            return 0
        
        solver = Solver(bootstrap_with=self.KB.clauses)
        solver.add_clause([-lit for lit in query])
        
        if solver.solve() == False:                 # Whiff here
            solver.delete()
            return 1

        solver.delete()
        return 0
    

    # check if Poison Gas at cell (i, j) or not   
    def check_PG(self, i, j):
        if i < 0 or i >= self.map_size or j < 0 or j >= self.map_size:
            return 0
        
        bind_str = 'P_G' + str(i) + ',' + str(j)
        element_id = self.vpool.id(bind_str)
        query = [element_id]
        if element_id not in [lit for clause in self.KB.clauses for lit in clause]:
            return 0
        
        solver = Solver(bootstrap_with=self.KB.clauses)
        solver.add_clause([-lit for lit in query])
        
        if solver.solve() == False:                 # Poisonous Gas here
            solver.delete()
            return 1

        solver.delete()
        return 0
    

    def confirm_NoPG(self, i, j):
        bind_str = 'P_G' + str(i) + ',' + str(j)
        Npg_id = self.vpool.id(bind_str)
        self.learn([-Npg_id])


    def detect_PG(self, i, j):
        if i < 0 or i >= self.map_size or j < 0 or j >= self.map_size:
            return 0
        
        if i+1 < self.map_size:
            s1 = 'W_H' + str(i) + ',' + str(j)
            s2 = 'W_H' + str(i+1) + ',' + str(j+1)
            s3 = 'W_H' + str(i+1) + ',' + str(j-1)
            S = 'P_G' + str(i+1) + ',' + str(j)
            # BOTTOM, RIGHT
            if j+1 < self.map_size:
                S1 = 'P_G' + str(i) + ',' + str(j+1)
                sentence = [-self.vpool.id(s1), -self.vpool.id(s2), self.vpool.id(S1), self.vpool.id(S)]
                self.learn(sentence)
            # BOTTOM, LEFT
            if j-1 >= 0:
                S1 = 'P_G' + str(i) + ',' + str(j-1)
                sentence = [-self.vpool.id(s1), -self.vpool.id(s3), self.vpool.id(S1), self.vpool.id(S)]
                self.learn(sentence)
                
        if i-1 >= 0:
            s1 = 'W_H' + str(i) + ',' + str(j)
            s2 = 'W_H' + str(i-1) + ',' + str(j+1)
            s3 = 'W_H' + str(i-1) + ',' + str(j-1)
            S = 'P_G' + str(i-1) + ',' + str(j)
            # TOP, RIGHT
            if j+1 < self.map_size:
                S1 = 'P_G' + str(i) + ',' + str(j+1)
                sentence = [-self.vpool.id(s1), -self.vpool.id(s2), self.vpool.id(S1), self.vpool.id(S)]
                self.learn(sentence)
            # TOP, LEFT
            if j-1 >= 0:
                S1 = 'P_G' + str(i) + ',' + str(j-1)
                sentence = [-self.vpool.id(s1), -self.vpool.id(s3), self.vpool.id(S1), self.vpool.id(S)]
                self.learn(sentence)


    # Forget all logic statement of PG at (x, y) after determining
    def forget_Whiff(self, x, y):
        pg_id = self.vpool.id('P_G' + str(x) + ',' + str(y))
        clauses_to_remove = [clause for clause in self.KB.clauses if pg_id in clause]
        for clause in clauses_to_remove:
            self.KB.clauses.remove(clause)

        pg_id = self.vpool.id('P_G' + str(x) + ',' + str(y))
        self.learn([pg_id])
   

    #   ============= Agent makes decision at cell (i, j) base on KB
    def makeDecision(self, i, j, Map):
        self.score += SCORE['ACTION']
        
        Stench = self.check_Stench(i, j)
        Breeze = self.check_Breeze(i, j)
        Gold = self.check_Gold(i, j)
        Glow = self.check_Glow(i, j)
        Healing_Potion = self.check_HP(i, j)
        Whiff = self.check_Whiff(i, j)
        P_Gas = self.check_PG(i, j)
        
        bind_str = str(i) + ',' + str(j)
        
        # -------------------consider WUMPUS--------------------------
        if Stench == True:  
            self.confirm_NoWumpus(i, j)
            wumpus_pos = []
            print(' |---> Agent can feel Stench at (%d, %d)' %(i+1, j+1))
            # check if wumpus is around (i, j)
            self.detect_Wumpus(i, j)
            if self.Wumpus(i+1, j): 
                print('   |-------> Wumpus at (%d, %d)' %(i+2,j+1))
                wumpus_pos.append((i+1, j))
            if self.Wumpus(i-1, j): 
                print('   |-------> Wumpus at (%d, %d)' %(i,j+1))
                wumpus_pos.append((i-1, j))
            if self.Wumpus(i, j-1): 
                print('   |-------> Wumpus at (%d, %d)' %(i+1,j))
                wumpus_pos.append((i, j-1))
            if self.Wumpus(i, j+1): 
                print('   |-------> Wumpus at (%d, %d)' %(i+1,j+2))
                wumpus_pos.append((i, j+1))

            # If Agent know exact position of wumpus, let KB know
            for pos in wumpus_pos:
                # SHOT it
                self.shot_Wumpus(pos[0], pos[1], Map)
                self.safe[pos] = -1

            # All the adjacent cells of Stench that unvisited will be unsafe
            if wumpus_pos == []:
                adj = adjCell(i, j, self.map_size)
                for x in adj:
                    if self.visited[x] != 1:
                        self.safe[x] = 0

        else:
            # This cell has no Stench
            # which means, no Wumpus around this cell !
            self.learn([-self.vpool.id('S' + bind_str)])    
            adj = adjCell(i, j, self.map_size)
            for x in adj:
                self.confirm_NoWumpus(x[0], x[1])


        # -------------------consider PIT--------------------------
        if Breeze == True:   
            self.confirm_NoPit(i, j)
            pit_pos = []
            print(' |---> Agent can feel Breeze at (%d, %d)' %(i+1, j+1))
            # check if pit is around (i, j)
            self.detect_Pit(i, j)
            if self.Pit(i+1, j): 
                print('   |-------> Pit at (%d, %d)' %(i+2,j+1))
                pit_pos.append((i+1, j))
            if self.Pit(i-1, j): 
                print('   |-------> Pit at (%d, %d)' %(i,j+1))
                pit_pos.append((i-1, j))
            if self.Pit(i, j-1): 
                print('   |-------> Pit at (%d, %d)' %(i+1,j))
                pit_pos.append((i, j-1))
            if self.Pit(i, j+1): 
                print('   |-------> Pit at (%d, %d)' %(i+1,j+2))
                pit_pos.append((i, j+1))

            # If Agent know exact position of pit, let KB know
            for pos in pit_pos:
                self.learn([self.vpool.id('P' + str(pos[0]) + ',' + str(pos[1]))])
                self.safe[pos] = 0
                self.forget_Breeze(pos[0], pos[1])

            # All the adjacent cells of Breeze that unvisited will be unsafe
            adj = adjCell(i, j, self.map_size)
            for x in adj:
                if self.visited[x] != 1:
                    self.safe[x] = 0

        else:
            # This cell has no Breeze
            # which means, no Pit around this cell !
            self.learn([-self.vpool.id('B' + bind_str)])    
            adj = adjCell(i, j, self.map_size)
            for x in adj:
                self.confirm_NoPit(x[0], x[1])


        # -------------------consider HEALING POTION--------------------------
        if Glow == True:
            self.confirm_NoHP(i, j)
            print(' |---> Agent can feel Glow at (%d, %d)' %(i+1, j+1))
            # check if HP is around (i, j)
            hp_pos = []
            self.detect_HP(i, j)
            if self.isHP(i+1, j): 
                print('   |-------> Heal potion at (%d, %d)' %(i+2,j+1))
                hp_pos.append((i+1, j))
            if self.isHP(i-1, j): 
                print('   |-------> Heal potion at (%d, %d)' %(i,j+1))
                hp_pos.append((i-1, j))
            if self.isHP(i, j-1): 
                print('   |-------> Heal potion at (%d, %d)' %(i+1, j))
                hp_pos.append((i, j-1))
            if self.isHP(i, j+1): 
                print('   |-------> Heal potion at (%d, %d)' %(i+1,j+2))
                hp_pos.append((i, j+1))
            
            # If Agent know exact position of HP, let KB know
            for pos in hp_pos:
                self.learn([self.vpool.id('H' + str(pos[0]) + ',' + str(pos[1]))])
                if self.safe[pos] != 0:
                    self.safe[pos] = 1

        else:
            # This cell has no Glow 
            # which means, no HP around this cell!
            self.learn([-self.vpool.id('G_L' + bind_str)])    
            adj = adjCell(i, j, self.map_size)
            for x in adj:
                self.confirm_NoHP(x[0], x[1])


        # -------------------grab HEALING POTION--------------------------
        if Healing_Potion == True:
            print(' |---> Agent grabs Healing Potion at (%d, %d)' %(i+1, j+1))
            self.grabHP(i, j, Map)
        else:
            self.confirm_NoHP(i, j)


        # -------------------consider GOLD--------------------------
        if Gold == True:
            # Grab the gold
            print(' |---> Agent grabs Gold at (%d, %d)' %(i+1, j+1))
            self.grabGold(i, j)


        # -------------------consider POISONOUS GAS--------------------------
        if Whiff == True:
            self.confirm_NoPG(i, j)
            print(' |---> Agent can feel Whiff at (%d, %d)' %(i+1, j+1))
            # check if HP is around (i, j)
            pg_pos = []
            self.detect_PG(i, j)
            if self.isPG(i+1, j): 
                print('   |-------> Poisonous Gas at (%d, %d)' %(i+2,j+1))
                pg_pos.append((i+1, j))
            if self.isPG(i-1, j): 
                print('   |-------> Poisonous Gas at (%d, %d)' %(i,j+1))
                pg_pos.append((i-1, j))
            if self.isPG(i, j-1): 
                print('   |-------> Poisonous Gas at (%d, %d)' %(i+1,j))
                pg_pos.append((i, j-1))
            if self.isPG(i, j+1): 
                print('   |-------> Poisonous Gas at (%d, %d)' %(i+1,j+2))
                pg_pos.append((i, j+1))
            
            # If Agent know exact position of PG, let KB know
            for pos in pg_pos:
                self.learn([self.vpool.id('P_G' + str(pos[0]) + ',' + str(pos[1]))])
                self.forget_Whiff(pos[0], pos[1])
                if self.health >= 50 and self.safe[pos] != 0:
                    self.safe[pos] = 1
                else: 
                    self.safe[pos] = 0

            # All the adjacent cells of Whiff that unvisited will be unsafe
            adj = adjCell(i, j, self.map_size)
            for x in adj:
                if self.visited[x] != 1:
                    self.safe[x] = 0

        else:
            # This cell has no Whiff 
            # which means, no PG around this cell!
            self.learn([-self.vpool.id('W_H' + bind_str)])    
            adj = adjCell(i, j, self.map_size)
            for x in adj:
                self.confirm_NoPG(x[0], x[1])
              
         
        # if P_Gas == True:
        #     self.health = max(0, self.health - 25)

        #     if self.health <= 75 and self.hp_count > 0:             # Use a HP
        #         self.health += 25
        #         self.hp_count -= 1
        #         print('Agent has used Healing Potion at (%d, %d)' %(i,j))
        #         self.score += SCORE['ACTION']

        #     if self.health < 50:                    # For returning back, if Agent's health less than 50 
        #         self.safe[i][j] = 0                 # he should not go thourgh it again

        if P_Gas == True:
            if self.hp_count == 0 and self.health <= 25:
                print('Agent has been died at (%d, %d)' %(i+1,j+1))
                return
            
            if self.hp_count == 0 and self.health > 25:
                print('Agent\'s health has been reduced at (%d, %d)' %(i+1,j+1))
                self.health -= 25
                print('Agent\'s health:  (%d)' %self.health)

            else:
                self.hp_count -= 1
                print('Agent has used Healing Potion at (%d, %d)' %(i+1,j+1))
                print('Agent\'s health:  (%d)' %self.health)
                self.score += SCORE['ACTION']
                        
        
        # ------------Consider which cell is safe?-------------------
        if self.safe[i][j] == 1:
            adj = adjCell(i, j, self.map_size)
            if Stench == False and Breeze == False:     
                for x in adj:
                    self.confirm_NoWumpus(x[0], x[1])
                    self.confirm_NoPit(x[0], x[1])
                    self.safe[x] = 1
            else:
                for x in adj:                           #This cell maybe Stench or Breeze, lead to all visited adjCell safe
                    if self.visited[x] == 1:
                        self.confirm_NoWumpus(x[0], x[1])
                        self.confirm_NoPit(x[0], x[1])
                        self.safe[x] = 1
        
        return
    

    def explore_map(self, Map, agent, i, j):
        if i < 0 or i >= Map.map_size or j < 0 or j >= Map.map_size:
            return
        
        agent.visited[i][j] = 1

        # Agent perceive
        agent.setPerceive(Map.getPerceive(i, j))
        agent.safe[i][j] = 1

        #   Agent decide what cell safe, or unsafe
        agent.makeDecision(i, j, Map)

        if i+1 < Map.map_size and agent.safe[i+1][j] != 0 and agent.visited[i+1][j] != 1:
            self.explore_map(Map, agent, i+1, j)

        if j+1 < Map.map_size and agent.safe[i][j+1] != 0 and agent.visited[i][j+1] != 1:
            self.explore_map(Map, agent, i, j+1)
            
        if 0 <= j-1 and agent.safe[i][j-1] != 0 and agent.visited[i][j-1] != 1:
            self.explore_map(Map, agent, i, j-1)

        if i == 0 and j == 0:
            print('Agent has climbed out!')


def literal_to_str(literal, vpool):
    if literal < 0:
        return f"-{vpool.obj(abs(literal))}"
    else:
        return vpool.obj(literal)


# return all adjacent cells
def adjCell(i, j, map_size):
    adj = []
    if i - 1 >= 0:
        adj.append((i-1, j))
    if i + 1 < map_size:
        adj.append((i+1, j))
    if j - 1 >= 0:
        adj.append((i, j-1))
    if j + 1 < map_size:
        adj.append((i, j+1))
        
    return adj