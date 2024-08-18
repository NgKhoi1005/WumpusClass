from Program import Program
from Agent import Agent, SCORE

from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

def explore_map(Map, agent, i, j):
    if i < 0 or i >= Map.map_size or j < 0 or j >= Map.map_size or agent.health == 0:
        return
    agent.visited[i][j] = 1
    # Agent perceive
    agent.setPerceive(Map.getPerceive(i, j))
    agent.safe[i][j] = 1
    #   ....
    #   Agent decide what cell safe, or unsafe
    agent.makeDecision(i, j, Map)
    
    if i+1 < Map.map_size and agent.safe[i+1][j] != 0 and agent.visited[i+1][j] != 1:
        explore_map(Map, agent, i+1, j)
        agent.score += SCORE['ACTION']
        # For returning back
        if Map.map[i+1][j] == 'P_G':
            agent.health = max(0, agent.health - 25)
    
    if j+1 < Map.map_size and agent.safe[i][j+1] != 0 and agent.visited[i][j+1] != 1:
        explore_map(Map, agent, i, j+1)
        agent.score += SCORE['ACTION']
        # For returning back
        if Map.map[i][j+1] == 'P_G':
            agent.health = max(0, agent.health - 25)
        
    if 0 <= j-1 and agent.safe[i][j-1] != 0 and agent.visited[i][j-1] != 1:
        explore_map(Map, agent, i, j-1)
        agent.score += SCORE['ACTION']
        # For returning back
        if Map.map[i][j-1] == 'P_G':
            agent.health = max(0, agent.health - 25)

    if agent.health == 0:
        agent.score -= 10000
        return

    if i == 0 and j == 0:
        print('Agent has climbed out!')
        agent.score += SCORE['CLIMB']


def literal_to_str(literal, vpool):
    if literal < 0:
        return f"-{vpool.obj(abs(literal))}"
    else:
        return vpool.obj(literal)
  
def main():
    
    n = 6
    Map = Program(n)
    agent = Agent(n)
    explore_map(Map, agent, 0, 0)
    
    # for clause in agent.KB.clauses:
    #     literal_clause = [literal_to_str(lit, agent.vpool) for lit in clause]
    #     print("  |  ".join(literal_clause))

    print('Final score: %d' %agent.score)
    print('HP left: %d' %agent.health)
    # print('Safe matrix: ')
    # print(agent.safe)
    #print(agent.visited)
    

if __name__ == "__main__":
    main()
    '''
    kb = CNF()
    vpool = IDPool()
    
    kb.append([-vpool.id('S1,2'), -vpool.id('S3,2'), -vpool.id('S2,3'), vpool.id('W2,2')])
    #kb.append([vpool.id('W2,2')])
    kb.append([vpool.id('S1,2')])
    kb.append([-vpool.id('S3,2')])
    # Query the KB for different literals or combinations
    query = [vpool.id('W2,2')]
    solver = Solver(bootstrap_with=kb.clauses)
    solver.add_clause([lit for lit in query])
    
    if solver.solve() == False:
        print("Query true")
    else:
        print("Query false")

    a = vpool.id('W2,2')
    clauses_to_remove = [clause for clause in kb.clauses if a in clause]
    for clause in clauses_to_remove:
        kb.clauses.remove(clause)

    for clause in kb.clauses:
        literal_clause = [literal_to_str(lit, vpool) for lit in clause]
        print("  |  ".join(literal_clause))
        
    
    solver.delete()


    sahjdkjashdjkahsdkjahskjdhasjkdhkasjhdjkashdkjashdkjákhjdkjashdkjhaskjdhasjhkd
    ákjdhiuashdkasjhdkjashdkjashdk
    '''
    
