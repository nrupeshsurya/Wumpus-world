#!/usr/bin/env python3
from Agent import * # See the Agent.py file
import itertools
import copy

#### All your code can go here.

#### You can change the main function as you wish. Run this program to see the output. Also see Agent.py code.

total_count=0

kb=[]           #main knowledge base to store the propositional sentences in cnf form 


actions = []    #store the moves taken by the agent 

current_status = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]      #keep track of the safe spots in the map 
allowed_moves = [[0,1],[0,-1],[1,0],[-1,0]]                     
moves = ['Up','Down','Right','Left']
moves_taken = []

def FindAdjacentRooms(cl):
    cLoc = cl
    validMoves = [[0,1],[0,-1],[-1,0],[1,0]]
    adjRooms = []
    for vM in validMoves:
        room = []
        valid = True
        for v, inc in zip(cLoc,vM):
            z = v + inc
            if z<1 or z>4:
                valid = False
                break
            else:
                room.append(z)
        if valid==True:
            adjRooms.append(room)
    return adjRooms

def legal(r,c):
    if(r>=0 and r<4 and c>=0 and c<4):
        return True
    else:
        return False


def bfs(current,target):                    #### used for going from one safe path to another 
    # print(current_status)                 #### using the current_status list which keeps track of all the safe paths
    visited = []
    for i in range(4):                                      #maintaining the visited list 
        visited.append([False,False,False,False])
    q = []
    dir = {(current[0],current[1]):(None,None)}             #used for keeping track of the directions moved
    q.append((current[0],current[1]))
    visited[current[0]][current[1]]=True                    
    while q:
        s = q.pop(0)
        # print(s)
        # time.sleep(1)
        if s[0]==target[0] and s[1]==target[1]:             #checking if target has been reached 
            break
        for i in range(4):
            newr = s[0]+allowed_moves[i][0]
            newc = s[1]+allowed_moves[i][1]
            if legal(newr,newc) and current_status[newr][newc]==1 and visited[newr][newc]==False:   #checking if next move is legal
                visited[newr][newc]=True                    #update the visited list 
                q.append((newr,newc))
                dir[(newr,newc)]=((s[0],s[1]),moves[i])

    target_moves = []
    top = (target[0],target[1])
    while top!=(current[0],current[1]):
        # print(dir[top][1])                                #adding the moves taken to reach the target
        target_moves.append(dir[top][1])
        top = dir[top][0]
    
    target_moves.reverse()                                  #reversing the list to get the correct order 
    return target_moves


def initialize(ag):                                     #initialize the knowledge base with the rules of the game      
    big_s1 = set()  
    big_s2 = set()
    for i in range(4):
        for j in range(4):
            for l, r in (('B', 'P'), ('S', 'W')):
                neighbours = FindAdjacentRooms([i+1,j+1])
                first_element = set()
                for x,y in neighbours:
                    first_element.add((f'{r}{x}{y}',1))     # converting the formula of bidirection here
                first_element.add((f'{l}{i+1}{j+1}',0))     #  p <=> r V q === (~pVrVq)and(pV~r)and(pV~q)
                kb.append(first_element)                    #first expression is (~pVrVq...)
                for x,y in neighbours:                      #
                    kb.append({(f'{r}{x}{y}',0),(f'{l}{i+1}{j+1}',1)})  ## this expression corresponds to (pV~r)and(pV~q) and so on
                if(r=='P'):
                    big_s1.add((f'{r}{i+1}{j+1}',1))    
                else:
                    big_s2.add((f'{r}{i+1}{j+1}',1))

    kb.append(big_s1)                   #there is atleast one Pit Condition 
    kb.append(big_s2)                   #there is atleast one Wumpus condition 

    # new_big1 = []
    # new_big2 = []]
    k=0
    store = dict()
    for i in range(4):
        for j in range(4):
            for i1 in range(4):
                for j1 in range(4):
                    if i1==i and j1 ==j:
                        continue
                    else:
                        temp = set()
                        temp.add((f'W{i+1}{j+1}',0))
                        temp.add((f'W{i1+1}{j1+1}',0))
                        temp1 = ((f'W{i+1}{j+1}',0),(f'W{i1+1}{j1+1}',0))
                        temp2 = ((f'W{i1+1}{j1+1}',0),(f'W{i+1}{j+1}',0))
                        if (temp1 not in store) or (temp2 not in store):
                            store[temp1]=1
                            store[temp2]=1
                            # print(temp1)
                            k+=1
                            kb.append({(f'W{i+1}{j+1}',0),(f'W{i1+1}{j1+1}',0)})        #there are atmost one wumpus
                            kb.append({(f'P{i+1}{j+1}',0),(f'P{i1+1}{j1+1}',0)})        #there are atmost one pit 
    
    # print(k)
    # ag._curLoc=[1,1]
  

def literal_expr(expr):                 #select the first literal 
    for c in expr:
        for d in c:
            return d[0]
 

def dpll(expr):   
    global total_count
    total_count+=1       
    # print("before",len(expr))                   
    ps = pure_symbols(expr)                 #using the pure symbol function get all the pure symbols 
    # print("ps:")
    # print(ps)
    expr_new = []
    to_add = True
    if len(ps)!=0:
        for c in expr:
            for k in c:
                if k in ps:
                    to_add = False          #checking if pure symbol exists in the clause and removing it if it exists 
                    break
            if to_add==True:
                expr_new.append(c)
            to_add = True
    else:
        expr_new = copy.deepcopy(expr)

    # print("after",len(expr_new))
    # print("after removing ps:")
    # print(expr_new)

    polarity,uc = unit_clauses(expr_new)     #getting unit clauses and also checking if they are any polarising unit clauses 
    if polarity==False:                     # for eg p, ~p 
        # print("i was here")
        return False

    if len(uc)!=0:

        # print("uc is :")
        # print(uc)
        # print("inner clauses are:")
        for i in uc:
            # print(i)
            expr_new.remove(i)               #first remove all the unit clauses 

        # print("after removing unit clauses:")
        # print(expr_new)

        to_change = []
        to_add = True
        for k in expr_new:
            for j in k:
                for i in uc:
                    for z in i:
                        if z==j:
                            # print("was i here?")
                            to_add=False
                            break
                if to_add==False:
                    break
            if to_add==True:
                to_change.append(k)             #remove other clauses containing the unit clauses 
            to_add=True

        # print("after removing inner unit clauses:")
        # print(to_change)
        
        for i in uc:
            new_one= None
            for k in i:
                new_one = {(k[0],1-k[1])}
            # print("new one is :")
            # print(new_one)
            to_change = [c.difference(new_one) for c in to_change]      #remove the negation of the unit clauses from the clauses 
            # print("after removing:")
            # print(to_change)

        # print("after removing negation of inner unit clauses:")
        # print(to_change)
        
        expr_new= copy.deepcopy(to_change)
    
    # print("after1",len(expr_new))

    if(len(expr_new)==0):                            # early termination condition : if there are no clauses its true
        # print("here1")
        return True

    if any([len(c)==0 for c in expr_new]):           # if there is a box clause 
        return False

    if(expr_new!=expr):                              #check if pure symbol/unit clause heurestic did anything 
        # print("took this path")
        return dpll(expr_new)
    else:                                           #at this point pure symbol and unit clause have not produced any effect so start
        # print("took the other one")               #assigning values to variables 
        cnf = copy.deepcopy(expr_new)
        l = literal_expr(cnf)
        expr_new_one=[]
        # expr_new_one = [c for c in cnf if (l, 1) not in c]
        for c in cnf:
            if (l,1) not in c:
                expr_new_one.append(c)
        expr_new_one = [c.difference({(l, 0)}) for c in expr_new_one]
        done = dpll(expr_new_one)
        if done==True:
            return done

        expr_new_one = []

        for c in cnf:
            if (l,0) not in c:
                expr_new_one.append(c)
        expr_new_one = [c.difference({(l, 1)}) for c in expr_new_one]
        done = dpll(expr_new_one)
        if done==True:
            return done

        return False                                               #return false if both fail
    return None

def pure_symbols(expr):
    symbols = set()                             #get the list of symbols             
    for c in expr:
        for d in c:
            symbols.add(d[0])

    main_list = dict()                      
    holding_val = dict()
    for i in symbols:
        main_list[i]=True                       #initially mark all symbols as pure symbols 
    
    for a in expr:
        for b in a:
            # print(b[0])
            if main_list[b[0]]==False:
                continue
            if b[0] in holding_val:
                if b[1]!=holding_val[b[0]]:                #check if var already exists in the dict and mark it as false if other 
                    main_list[b[0]]=False                  #form exists 
            else:
                holding_val[b[0]]=b[1]

    to_ret = set()
    for i in main_list:
        if main_list[i]==True:                              #make a set to return 
            to_ret.add((i,holding_val[i]))

    # print(to_ret)
    return to_ret

def unit_clauses(expr):
    to_ret = list()
    to_ret_cons = True
    track_truth = dict()                            #find unit clauses and also check if complimentary unit clauses are present 
    for d in expr:
        if(len(d)==1):
            for t in d:
                to_ret.append({t})
                if t[0] not in track_truth:
                    track_truth[t[0]]=t[1]
                else:
                    if t[1]!=track_truth[t[0]]:
                        to_ret_cons=False
                        break

    return to_ret_cons,to_ret



def simulation(ag):

    stack = [[1,1]]                 #stack which contains places which are safe to visit 
    current_status[0][0]=1          #current_status list which has places which are marked safe 
    visited = dict()                #dict which keeps track of tiles which have already been visited 
    visited[(0,0)]=1

    while(ag.FindCurrentLocation()!=[4,4]):
        my_tile = ag.FindCurrentLocation()
        stack.pop()                                 #pop the current element from visited 
        visited[(my_tile[0],my_tile[1])]=1           #mark the current element as visited 
        # print("current location is: ") 
        # print(ag.FindCurrentLocation())
        breeze,stench = ag.PerceiveCurrentLocation()
       
        if breeze == True:                                              #add the perception around the environment 
            # print("i feel a breeze")
            kb.append({(f'B{my_tile[0]}{my_tile[1]}',1)})
        else:
            # print("i do not feel a breeze")
            kb.append({(f'B{my_tile[0]}{my_tile[1]}',0)})
        
        if stench == True:
            # print("i smell a stench")
            kb.append({(f'S{my_tile[0]}{my_tile[1]}',1)})
        else:
            # print("i do not smell a stench")
            kb.append({(f'S{my_tile[0]}{my_tile[1]}',0)})

        adj_rooms = FindAdjacentRooms([my_tile[0],my_tile[1]])

        for room in adj_rooms:                                          #check on the neighbours using dpll 
            if (room[0],room[1]) in visited:                            # check if the room is already visited 
                continue
            # print("the room being checked is :")
            # print(room)
            wump_alive = {(f'W{room[0]}{room[1]}',1)}                   #check if wumpus is not present by using kb^~alpha is unsat
            kb.append(wump_alive)
            val1 = dpll(kb)
            if val1 == True :
                # print("marked this room as unsafe for now: ")
                kb.remove(wump_alive)
                wump_alive_here = {(f'W{room[0]}{room[1]}',0)}          #check if wumpus is present 
                kb.append(wump_alive_here)
                val11 = dpll(kb)
                if(val11==False):
                    kb.remove(wump_alive_here)
                    kb.append(wump_alive)
                    # print("the wumpus is probably definitely here")
                    current_status[room[0]-1][room[1]-1]=2              #mark the wumpus is present 
                else:
                    kb.remove(wump_alive_here)
                continue
            kb.remove(wump_alive)
            kb.append({(f'W{room[0]}{room[1]}',0)})                 #check the same conditions for the pit as well 
            pit_present = {(f'P{room[0]}{room[1]}',1)}
            kb.append(pit_present)
            val2 = dpll(kb)
            if val2 == True:
                # print("marked this room as unsafe for now: ")
                kb.remove(pit_present)
                pit_present_here = {(f'P{room[0]}{room[1]}',0)}
                kb.append(pit_present_here)
                val21 = dpll(kb)
                if(val21==False):
                    kb.remove(pit_present_here)
                    kb.append(pit_present)
                    # print("the pit is probably definitely here")
                    current_status[room[0]-1][room[1]-1]=2
                else:
                    kb.remove(pit_present_here)
                continue
            kb.remove(pit_present)
            kb.append({(f'P{room[0]}{room[1]}',0)})
            stack.append(room)                                  # adding room to the stack
            current_status[room[0]-1][room[1]-1]=1         #marking the room as safe 
            


        new_location = []


        if len(stack)==0:                                               #backtracking back to the start if stack is empty 
            stack.append([1,1])
            visited.clear()

        new_location = stack[-1] 
        p1 = [my_tile[0]-1,my_tile[1]-1]
        p2 = [new_location[0]-1,new_location[1]-1]
        path = bfs(p1,p2)

        for p in path:                                  #move to the new location 
            ag.TakeAction(p)
            actions.append(p)
            moves_taken.append(ag.FindCurrentLocation())

    print("tiles gone to reach: ",moves_taken)
    print("actions taken to reach: ",actions)
    print("total number of calls to dpll: ",total_count)
    return None

def main():
    ag = Agent()
    initialize(ag)
    simulation(ag)


if __name__=='__main__':
    main()