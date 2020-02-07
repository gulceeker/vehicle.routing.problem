
# Data Pre-process Functions here #
def read_text_file(path):
    # In this function, the given sample txt file is read and kept as a table.
    
    INFOTABLE=[]
    NUMBER = 0
    CAPACITY = 0
    with open(path) as f:
        for i, row in enumerate(f):
            if i == 4:
                row = row.split()
                NUMBER, CAPACITY = row[0], row[1]
            if i > 8:
                INFOTABLE.append(row.split())
    
    for i,row in enumerate(INFOTABLE):
        INFOTABLE[i] = list(map(lambda x: int(x), row))

    return INFOTABLE, int(NUMBER), int(CAPACITY)

def create_distance_matrix(table):
    # In this function, the distances of the nodes are calculated according to 
    # the Euclidean distance method and stored in a matrix.

    distance_matrix = []
    for i, row in enumerate(table): # table is info_table
        tmp_distances = []
        for j, tmp_row in enumerate(table): 
            if i != j:  #if it not diagonal
                x1, y1= row[1], row[2]
                x2, y2 = tmp_row[1], tmp_row[2]
                distance = (((x1-x2)**2) + ((y1-y2)**2))**0.5 # euclidian distance calculation
                tmp_distances.append(distance)
            else:
                tmp_distances.append(0) # if it is diagonal add value to tmp_distance
        
        distance_matrix.append(tmp_distances) # add distance value to distance matrix
    
    return distance_matrix

# Heuristic Steps Here #
def get_earliest_due_date_customer(table, ALL_POSSIBLE_ROUTES):
    # In this function, the initial tour is determined by the earliest due date.

    customerNo = 0

    if len(ALL_POSSIBLE_ROUTES) == 0:  # if it is the very first route 
        tmp = table[0][5] # depot due date as default starting to search
        for i, row in enumerate(table):
            if row[5] < tmp:
                tmp = row[5]
                customerNo = i
        #print ("First Initial tour starts with " + str(customerNo))
    else:  # it is create initial tour except very first one
        tmp_set = set()     
        for route in ALL_POSSIBLE_ROUTES: #it is eleminate used nodes for initial route
            for cust in route:    
                tmp_set.add(cust)
        used_custs = list(tmp_set)

        tmp = table[0][5] # depot due date as default starting to search
        for i, row in enumerate(table): 
            if i not in used_custs: # for all row of info table it is looking for node which is not used before
                if row[5] < tmp:
                    tmp = row[5]
                    customerNo = i  # based on this customer no new initial tour is created
    
    #print ("Initial tour starts with " + str(customerNo))
    return customerNo

def get_possible_combinations(INFO_TABLE, rootCombination, ALL_POSSIBLE_ROUTES):
    # In this function, combinations of the initial tour are created. 
    # New possible nodes are inserted into the tour.

    n = len(rootCombination)-1  # root combination is initial combination
    sub_combinations = []
    
    if len(ALL_POSSIBLE_ROUTES) == 0: # if it is very first tour (ex: 0-8-0)
        for row in INFO_TABLE:
            custNo = row[0]
            for i in range(1,n+1):  
                if custNo not in rootCombination: 
                    tmp = list(rootCombination)
                    tmp.insert(i,custNo)
                    sub_combinations.append(tmp)
    else:
        tmp_set = set()
        for route in ALL_POSSIBLE_ROUTES:
            for cust in route:
                tmp_set.add(cust)
        used_custs = list(tmp_set)

        for row in INFO_TABLE:
            custNo = row[0]
            for i in range(1,n+1):
                if custNo not in rootCombination and custNo not in used_custs:
                    tmp = list(rootCombination)
                    tmp.insert(i,custNo)
                    sub_combinations.append(tmp)
    
    return sub_combinations
  
def pre_elimination(info_table, distance_matrix, combinations, CAPACITY):
    # In this function, all combinations of the current tour are eliminated based on 
    # rules which are total capacity check, time window control and depot due date control.

    to_be_deleted=[]

    for j in range(len(combinations)):  
        #print j
        comb = combinations[j]
        arrival_time = 0
        #print comb
        
        total_demand=0
        for i in comb:
            total_demand+= info_table[i][3] # sum of nodes demand
        
        if total_demand > CAPACITY: # capacity check
            to_be_deleted.append(comb)
            continue 

        for i in range (len(comb)-2): # till the go back to depot
            cust = comb[i]
            nextCust = comb[i+1]
            #print cust, nextCust
            nextcust_ready_time = info_table[nextCust][4]
            #print "next_ready time ", nextcust_ready_time
            #print "next distance ", distance_matrix[cust][nextCust]
            
            distance_between_nodes = distance_matrix[cust][nextCust] 
            
            if i == 0: # first distance is our arrival_time! ONLY FIRST ITERATION 
                arrival_time = distance_matrix[cust][nextCust] 
                if arrival_time > info_table[nextCust][5]: # due date check
                    to_be_deleted.append(comb) # this combination should be deleted
                    break   # do not have to continue so start over
                if arrival_time >= nextcust_ready_time: # ready time check
                    if i != len(comb)-3: 
                        arrival_time += info_table[nextCust][6] # add service time over to arrival time.
                else:   
                    if i != len(comb)-3: 
                        arrival_time = nextcust_ready_time + info_table[nextCust][6] #service time
                    else:
                        arrival_time = nextcust_ready_time
            else: # Rest of goes here always
                if arrival_time + distance_between_nodes > info_table[nextCust][5]: # due date check
                    to_be_deleted.append(comb)
                    break
                    
                if arrival_time + distance_between_nodes >= nextcust_ready_time:
                    if i != len(comb)-3:
                        arrival_time += distance_between_nodes + info_table[nextCust][6] #service time
                    else:
                        arrival_time += distance_between_nodes
                else:
                    if i != len(comb)-3:
                        arrival_time = nextcust_ready_time + info_table[nextCust][6] #service time
                    else:
                        arrival_time = nextcust_ready_time
                
            if arrival_time + info_table[nextCust][6] + distance_matrix[nextCust][0] > info_table[0][5]: # Depot due date check
                to_be_deleted.append(comb)  
                break 
         
            #print arrival_time
        
    for i in to_be_deleted:
        combinations.remove(i)

    return combinations  

def best_route_selection(a1, a2, L, combinations, info_table, distance_matrix, initial_combination):
    
    initial_total_distance = 0

    #COMBINATIONS TOTAL TIME CALCUTAION 
    for j in range(len(combinations)):
        comb = combinations[j]
        arrival_time = 0
        for i in range (len(comb)-2):
            cust = comb[i]
            nextCust = comb[i+1]
            nextcust_ready_time = info_table[nextCust][4]
            distance_between_nodes = distance_matrix[cust][nextCust]

            if i == 0: # first distance is our arrival_time! ONLY FIRST ITERATION
                arrival_time = distance_matrix[cust][nextCust] 
                if arrival_time >= nextcust_ready_time:
                    if i != len(comb)-3:
                        arrival_time += info_table[nextCust][6] #service time
                else:
                    if i != len(comb)-3:
                        arrival_time = nextcust_ready_time + info_table[nextCust][6] #service time
                    else:
                        arrival_time = nextcust_ready_time

            else:
                if arrival_time + distance_between_nodes >= nextcust_ready_time:
                    if i != len(comb)-3:
                        arrival_time += distance_between_nodes + info_table[nextCust][6] #service time
                    else:
                        arrival_time += distance_between_nodes
                else:
                    if i != len(comb)-3:
                        arrival_time = nextcust_ready_time + info_table[nextCust][6] #service time
                    else:
                        arrival_time = nextcust_ready_time

        total_time = arrival_time + info_table[nextCust][6] + distance_matrix[nextCust][0]

    #INITIAL TOURS TOTAL TIME CALCULATION 
    arrival_time = 0
    for j in range (len(initial_combination)-1):
        cust = initial_combination[j]
        nextCust = initial_combination[j+1]
        nextcust_ready_time = info_table[nextCust][4]
        distance_between_nodes = distance_matrix[cust][nextCust]

        if j == 0: # first distance is our arrival_time! ONLY FIRST ITERATION
            arrival_time = distance_matrix[cust][nextCust] 
            if arrival_time >= nextcust_ready_time:
                if j != len(comb)-1:
                    arrival_time += info_table[nextCust][6] #service time
            else:
                if j != len(comb)-1:
                    arrival_time = nextcust_ready_time + info_table[nextCust][6] #service time
                else:
                    arrival_time = nextcust_ready_time

        else:
            if arrival_time + distance_between_nodes >= nextcust_ready_time:
                if j != len(comb)-1:
                    arrival_time += distance_between_nodes + info_table[nextCust][6] #service time
                else:
                    arrival_time += distance_between_nodes
            else:
                if j != len(comb)-1:
                    arrival_time = nextcust_ready_time + info_table[nextCust][6] #service time
                else:
                    arrival_time = nextcust_ready_time
        total_time_initial = arrival_time + info_table[nextCust][6] + distance_matrix[nextCust][0]

    # INITIAL TOURS TOTAL DISTANCE CALCULATION
    for j in range(len(initial_combination)-1):
        cust = initial_combination[j]
        nextCust = initial_combination[j+1]
        initial_total_distance += distance_matrix[cust][nextCust]
    best_f2_value = 0
    best_combination = None       

    # COMBINATIONS DISTANCE AND F VALUES CALCULATION
    for i, comb in enumerate(combinations):
        total_distance = 0
        best_comb_distance = 0
        for j in range(len(comb)-1):
            cust = comb[j]
            nextCust = comb[j+1]
            total_distance += distance_matrix[cust][nextCust]
        last_node_distance_to_depot = distance_matrix[comb[j]][0] # comb[j] is cust!

        f1_value = a1 * (total_distance - initial_total_distance) + a2 * (total_time - total_time_initial)
        f2_value = L * last_node_distance_to_depot - f1_value
        
        if i==0:
            best_f2_value = f2_value
            best_combination = comb

            
        if f2_value > best_f2_value:
            best_f2_value = f2_value
            best_combination = comb
   
    #print "INITIAL: ",initial_combination,"\n"
    #print "BEST COMBINATION: ",best_combination,"\n"
    #print "FEASIBLE COMBINATIONS: ",combinations,"\n"  
    #print "TOTAL TIME OF COMB: ",total_time,"\n"  
    #print "TOTAL TIME OF INITIAL TOUR : ",total_time_initial,"\n"
    #print "DIFFERENCE: ",(total_time - total_time_initial),"\n\n\n"   
      
    return best_combination

def cycle(INFO_TABLE, DISTANCE_MATRIX, ALL_POSSIBLE_ROUTES, A1, A2, L, NUMBER, CAPACITY, initial_combination=None):
    
    while 1:
        if initial_combination == None:
            customerNo = get_earliest_due_date_customer(INFO_TABLE, ALL_POSSIBLE_ROUTES)
            if customerNo == 0:
                break
            initial_combination = [0,customerNo,0]
        
        combinations = get_possible_combinations(INFO_TABLE, initial_combination, ALL_POSSIBLE_ROUTES)
        if len(combinations) != 0:
            #print ("subcomb count:", len(combinations))
            combinations = pre_elimination(INFO_TABLE, DISTANCE_MATRIX, combinations, CAPACITY)
            #print ("after elim subcomb count:", len(combinations))

        if len(combinations) == 0:
            #print "No more sub combinations for ", initial_combination
            ALL_POSSIBLE_ROUTES.append(initial_combination)
            initial_combination=None
        else:
            best_combination  = best_route_selection(A1, A2, L, combinations, INFO_TABLE, DISTANCE_MATRIX, initial_combination)
            #print "Best",best_combination,"\n\n"
            initial_combination = best_combination


def main():
    # Parameters
    path = './c101_10.txt'
    A1 = 1
    A2 = 0
    L = 1

    # data pre-prodcessing 
    INFO_TABLE, NUMBER, CAPACITY = read_text_file(path)
    DISTANCE_MATRIX = create_distance_matrix(INFO_TABLE)
    ALL_POSSIBLE_ROUTES = []

    cycle(INFO_TABLE, DISTANCE_MATRIX, ALL_POSSIBLE_ROUTES, A1, A2, L, NUMBER, CAPACITY)
    print "\n"  
    number_of_vehicle = len(ALL_POSSIBLE_ROUTES)
    remaining_vehicle = NUMBER - number_of_vehicle

    total_distance = 0
    grand_total = 0
    number_of_tour = 0 

    for i, comb in enumerate(ALL_POSSIBLE_ROUTES):
        total_distance = 0
        number_of_tour = i+1
        for j in range(len(comb)-1):
            cust = comb[j]
            nextCust = comb[j+1]
            total_distance += DISTANCE_MATRIX[cust][nextCust] 
        grand_total += total_distance

        if i==0:
            print number_of_tour,"st combination is ",comb,"and total distance of route is",total_distance 
        elif i==1 or i==2:
            print number_of_tour,"nd combination is ",comb,"and total distance of route is",total_distance 
        else:  
            print number_of_tour,"th combination is ",comb,"and total distance of route is",total_distance   

    print "The total distance traveled is",grand_total 
    print "Number of vehicle used is",number_of_vehicle
    print "Remaining number of vehicle is",remaining_vehicle
    print "\n"  

if __name__ == "__main__":
    main()
