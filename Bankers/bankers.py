from tabulate import tabulate
from sys import exit


proccess = []
# class Process to define each proccess information
class Proccess:
    def __init__(self, name, Allocation, Need, requests):
        global resources_data
        self.name = name
        self.Allocation = Allocation
        self.Need = Need
        self.requests = requests
        self.is_done = [False for i in range(len(resources_data))]
        self.is_request = [False for i in range(len(resources_data))]

    def Reset(self):
        self.is_done = [False for i in range(len(resources_data))]
        self.is_request = [False for i in range(len(resources_data))]


requests = None
# get data from text file
def getDataFromFile(input):
    allocation = []
    maximom = []
    with open(input, "r") as file:
        # reading lines
        lines = file.readlines()
        resources = lines[0].split(":")[1].split(",")
        resources = [i.strip() for i in resources]
        # remove the top line => resource
        lines = lines[2:]
        # get allocation from file
        for allocate in lines:
            if allocate == "########################################\n":
                save_tag = lines.index(allocate)
                break
            allocation.append(allocate.strip())  # remove '\n'
        # create new line list to get the max
        lines = lines[save_tag+1:]

        # get the max
        for maxx in lines:
            if maxx == "########################################\n":
                save_tag = lines.index(maxx)
                break
            maximom.append(maxx.strip())  # remove '\n'

        lines = lines[save_tag+1:]

        # remove '\n' from each request and map to process
        requests = {request.split(':')[0]: request.split(':')[1] for request in lines if request.strip()}
    # return all things i want :)
    return resources, allocation, maximom, requests

# get the resources from file
resources, allocation, maximom, requests = getDataFromFile("./input.txt")


# get the recourses items
# all things after "=" | find the index of equal and save every thing after it. must sum it with 1
# it may be diffrent in the name of the rescourses
resources_data = [resources[i][resources[i].find("=")+1 :] for i in range(len(resources))]
# make data to integer from string
resources_data = [int(i) for i in resources_data]

# Create data list dynamically



NewAllocate = []
NewMaximom = []
need = []
p_name = []

# create allocation
for item in allocation:
    oo = item.split(":")
    p_name.append(oo[0])
    NewAllocate.append(oo[1].split(","))

# create max
for item in maximom:
    oo = item.split(":")
    NewMaximom.append(oo[1].split(","))

# make allocation and max datas to int number
NewAllocate = [[int(item) for item in sublist] for sublist in NewAllocate]
NewMaximom = [[int(item) for item in sublist] for sublist in NewMaximom]

# Iterate over each sublist in NewAllocate and NewMaximom
for allocate, maximom2 in zip(NewAllocate, NewMaximom):
    # Calculate the difference between corresponding elements in allocate and maximom
    # Append the result to the Need list
    need.append([max - alloc for max, alloc in zip(maximom2, allocate)])



# append class proccess to the proccess list
for i in range(len(allocation)):
    # get proccess name
    process_name = p_name[i]
    # request is a dictionary => get the value of the keys
    req_val = requests.get(process_name, "").strip()
    # append data to list with the class format
    proccess.append(Proccess(process_name, NewAllocate[i], need[i], req_val.split(",") if req_val else []))


# create avalable list
Available = []
# todo: change the list to dynamic
sum_allocations = [0 for zero in range(len(NewAllocate))]
# sum the allocations in each columns
for pro in proccess:
    sum_allocations = [sum_alloc + int(pro_) for sum_alloc, pro_ in zip(sum_allocations, pro.Allocation)]

# make the avalable and push it in the list 
for j in range(len(resources_data)):
    Available.append(resources_data[j] - sum_allocations[j])


main_table = []

for pp in proccess:
    main_table.extend([[pp.name, pp.Allocation, pp.Need, pp.requests, pp.is_done]])

new_list = [Available, None, None, None, None]

for i in range(len(main_table)):
    main_table[i].insert(2, NewMaximom[i])

for i in range(len(main_table)):
    main_table[i].append(new_list[i])


print(tabulate(main_table, headers=['Process', 'Allocation', "Max", "Need","requests", "is_done","Available"], tablefmt='orgtbl'))
#! print("\n________________________________________________________________________________________\n")

state = 0

def is_safe():
    global work
    counter = 0
    sequence = []
    # get a copy of the usage list
    work = Available.copy()
    CopyProcess = proccess.copy()
    MAX_ITERATIONS = 1000
    while True:
        counter += 1
        if counter > MAX_ITERATIONS:
            print(f"state {state} not Safe")
            return False
        
        for far in CopyProcess:
            for ii in range(len(far.Allocation)):
                if far.Need[ii] <= work[ii] and far.is_done[ii] == False:
                    far.is_done[ii] = True

            for iii in range(len(Available)):
                if all(far.is_done):
                    work[iii] += far.Allocation[iii]
                    for oo in CopyProcess:
                        if oo.name == far.name:
                            sequence.append(far.name)
                            CopyProcess.remove(oo)
                else:
                    far.is_done[iii] = False

        if len(CopyProcess) == 0:
            print(f"state {state} is Safe")
            return True


# check if the squense is safe or not for the first time
state += 1
is_safe()

# reset the 
for prc in proccess:
    prc.Reset()

#! STEP 2 ALG

requestProcess = list(filter(lambda ppp: len(ppp.requests) != 0, proccess)) # filter process to get that process that have request


# cheking the loop for the request
for action in requests:
    for prc in requestProcess:
        if action == prc.name:
            newAllocation = prc.Allocation 
            for num in range(len(Available)):
                if int(prc.requests[num]) <= Available[num] and int(prc.requests[num]) <= prc.Need[num]:
                    # make all requests True if the above condition is True
                    prc.is_request[num] = True
                    

            # if all requets was True, change the value of allocation and need
            for num3 in range(len(Available)):
                if all(prc.is_request):
                    prc.Allocation[num3] += int(prc.requests[num3])
                    prc.Need[num3] -= int(prc.requests[num3])
                    Available[num3] -= int(prc.requests[num3])
                else:
                    print("state 2 is not safe")
                    exit()

state += 1

with open("./output.txt", 'w') as outputFile:
    if is_safe():
        outputFile.write("yes")
    else:
        outputFile.write("no")
        

