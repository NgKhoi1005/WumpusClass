from Program import Program
# def literal_to_str(literal, vpool):
#     if literal < 0:
#         return f"-{vpool.obj(abs(literal))}"
#     else:
#         return vpool.obj(literal)
  
def main():
    Map = Program()
    
    # for clause in agent.KB.clauses:
    #     literal_clause = [literal_to_str(lit, agent.vpool) for lit in clause]
    #     print("  |  ".join(literal_clause))

    # print('Safe matrix: ')
    # print(agent.safe)
    # print(agent.visited)
    

if __name__ == "__main__":
    main()


    
    # kb = CNF()
    # vpool = IDPool()
    
    # kb.append([-vpool.id('S1,2'), -vpool.id('S2,1'), -vpool.id('S3,2'), -vpool.id('S2,3'), vpool.id('W2,2')])
    # kb.append([vpool.id('W2,2')])
    # kb.append([vpool.id('S1,2')])
    # kb.append([vpool.id('S2,1')])
    # kb.append([vpool.id('S2,1')])
    # kb.append([vpool.id('S2,1')])
    # kb.append([vpool.id('S2,1')])
    # kb.append([vpool.id('S2,3')])
    # kb.append([vpool.id('S3,2')])
    # # Query the KB for different literals or combinations
    # query = [vpool.id('W2,2')]
    # solver = Solver(bootstrap_with=kb.clauses)
    # solver.add_clause([lit for lit in query])
    
    # if solver.solve() == False:
    #     print("Query true")
    # else:
    #     print("Query false")

    # print(kb.clauses.remove([vpool.id('S2,1')]))
    # for clause in kb.clauses:
    #     literal_clause = [literal_to_str(lit, vpool) for lit in clause]
    #     print("  |  ".join(literal_clause))
        
    
    # solver.delete()
    
    
