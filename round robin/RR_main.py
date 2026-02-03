AWT_list = []
ATT_list = []
ART_list = []

def reset_global_variables():
    global ready_rr, waiting_qeueu, process_in_cpu, process_in_future, process_in_future_time, first, CPU_time, gantt_chart
    ready_rr = []
    waiting_qeueu = []
    process_in_cpu = None
    process_in_future = None
    process_in_future_time = -1
    CPU_time = 0
    gantt_chart = []
    first = True

class Process:
    def __init__(self, name, arrival_time, bursts):
        self.name = name
        self.arrival_time = arrival_time
        self.arrival_time2 = arrival_time
        self.bursts = bursts
        self.currentBurst = bursts[0]
        self.burstIndex = 0
        self.waitingTime = 0
        self.responseTime = 0
        self.terminateTime = 0
        self.quantum_used = 0


    def __str__(self):
        return self.name

    
    def terminate(self):
        global CPU_time
        # if self.responseTime == 0:
        #     self.responseTime = CPU_time - self.arrival_time
            
        self.terminateTime = CPU_time
        endProcessInGanttChart()
        self.update_processes()
        print(f"{self.name} => Terminated => time: {CPU_time}")
        
    def transfer_to_waiting_queue(self):
        global CPU_time
        # if self.responseTime == 0:
        #     self.responseTime = CPU_time - self.arrival_time
        self.burstIndex += 1
        self.currentBurst = self.bursts[self.burstIndex]
        self.arrival_time2 = CPU_time + self.currentBurst
        waiting_qeueu.append(self)
        endProcessInGanttChart()
        self.update_processes()
        # print(f"{self.name} => Transfer To Waiting Queue => time: {CPU_time}")
        
    def remove_from_waiting_queue(self):
        global CPU_time, waiting_qeueu
        waiting_qeueu = list(filter(lambda p: p.name != self.name, waiting_qeueu))
        index = processes.index(self)
        processes[index] = self
        # print(f"{self.name} => Remove from Waiting Queue => time: {CPU_time}")
        
    # update processes
    def update_processes(self):
        global process_in_cpu
        index = processes.index(self)
        processes[index] = self
        process_in_cpu = None
        

def addWaitingTime(process):
    process.waitingTime += 1
    index = processes.index(process)
    processes[index] = process


def endProcessInGanttChart():
    global CPU_time, gantt_chart
    gantt_chart[-1]['end'] = CPU_time
        
    
def getDataFromFile(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()
    
    dispatcher_latency = int(lines[0])
    action = lines[1].lower().strip()
    processes = []
    for line in lines[2:]:
        name, values = line.split(":")
        values = list(map(int, values.split(",")))
        processes.append(Process(name, values[0], values[1:]))
        
    return dispatcher_latency, action, processes

def appendToGanttChart(process):
    global CPU_time, gantt_chart
    # print(f"appendToGanttChart => {process}")
    item = {
        'name': process.name,
        'start': CPU_time,
        'end': 0,
    }
    gantt_chart.append(item)

def clear_output():
    open("output.txt", "w").close()
    
def appendToFile(newData):
    with open("output.txt", 'a') as file:
        file.write(newData + "\n")



def clearInitialWasteTime():
    global processes
    min_val = min(processes, key=lambda p: p.arrival_time).arrival_time
    for p in processes:
        p.arrival_time -= min_val
        p.arrival_time2 -= min_val


def cpuProcessing(quantom):
    global CPU_time, ready_rr, waiting_qeueu, process_in_cpu, process_in_future,  process_in_future_time, first, processes
    
    while True:
        # print(CPU_time)
        # show_all_processes(processes)
        for p in ready_rr:
            addWaitingTime(p)
        # print(f"ready array=> {ready_rr}")
        
        arrivedProcesses = list(filter(lambda p: p.terminateTime == 0 and p.arrival_time2 == CPU_time , processes))
        # print(f"arrivedProcesses =>\n {show_all_processes(arrivedProcesses)}")
        if len(arrivedProcesses) > 0:
            # a proccess come to cpu with most wait in ready list
            newProcess = list(filter(lambda p: p.arrival_time == p.arrival_time2, arrivedProcesses))
            processes_from_waiting_queue = list(filter(lambda p: p.arrival_time != p.arrival_time2, arrivedProcesses))
            arrivedProcesses = newProcess + processes_from_waiting_queue
            for arrivedProcess in arrivedProcesses:
                # print(f"process: {arrivedProcess.name} | bursts: {arrivedProcess.bursts} | quantom_used: {arrivedProcess.quantum_used}")
                if arrivedProcess.burstIndex != 0:
                    arrivedProcess.remove_from_waiting_queue()
                ready_rr.append(arrivedProcess)
                # print(f"ready array => {ready_rr}")
                    
        if process_in_cpu:
            # show_a_process(process_in_cpu)
            if process_in_cpu.currentBurst == 0:
                process_in_cpu.quantum_used = 0
                if process_in_cpu.burstIndex + 1 == len(process_in_cpu.bursts):
                    process_in_cpu.terminate()
                else:
                    process_in_cpu.transfer_to_waiting_queue()
            elif process_in_cpu.quantum_used == quantom:
                # end process and let the other process come in cpu
                endProcessInGanttChart()
                process_in_cpu.quantum_used = 0
                ready_rr.append(process_in_cpu)
                # print(f"{process_in_cpu.name} => Quantum Expired => time: {CPU_time}")
                process_in_cpu = None
        
        if not process_in_cpu:
            # if not any process in the cpu, check the terminate list
            # if process_in_future:
            #     show_a_process(process_in_future)
            if process_in_future or (
                (len(waiting_qeueu) > 0 or
                len(list(filter(lambda p: p.terminateTime == 0, processes))) > 0)
                and len(ready_rr) == 0
            ):

                CPU_time += 1

                # Dispatcher finishes → CPU gets process
                if process_in_future_time == CPU_time:

                    process_in_cpu = process_in_future
                    process_in_cpu.quantum_used = 0
                    process_in_future = None
                    process_in_future_time = -1

                    appendToGanttChart(process_in_cpu)

                continue


            process = ready_rr.pop(0) if len(ready_rr) > 0 else None
            if not process:
                print("Done !")
                drawGanttChart()
                calculate()
                break
            
            if first:
                process_in_cpu = process
                if process_in_cpu.responseTime == 0:
                    process_in_cpu.responseTime = CPU_time - process_in_cpu.arrival_time
                # show_a_process(process_in_cpu)

                appendToGanttChart(process)
                first = False
            elif dispatchLatency == 0:
                process_in_cpu = process
                if process_in_cpu.responseTime == 0:
                    process_in_cpu.responseTime = CPU_time - process_in_cpu.arrival_time

                appendToGanttChart(process)
            else:
                process_in_future = process
                process_in_future_time = CPU_time + dispatchLatency
                
        if process_in_cpu:
            # show_a_process(process_in_cpu)
            process_in_cpu.currentBurst -= 1
            process_in_cpu.quantum_used += 1
            # show_a_process(process_in_cpu)
            # print("=-=-=-"*20)
        CPU_time += 1
                

def drawGanttChart():
    global CPU_time, gantt_chart, dispatchLatency
    lines = ["", "", "", ""]
    for i in range(len(gantt_chart)):
        if dispatchLatency != 0 and i != 0:
            difference = gantt_chart[i]['start'] - gantt_chart[i-1]['end']
            includeIdle = difference > dispatchLatency
            lines[1] += "|"
            if includeIdle:
                lines[1] += "id"
                lines[1] += "\t"
                lines[1] += "|"
            lines[1] += "dl"
            lines[1] += "\t"
            lines[3] += str(gantt_chart[i-1]['end'])
            if includeIdle:
                lines[3] += "\t"
                # difference - dispatchLatency = id
                lines[3] += str(gantt_chart[i-1]['end'] + (difference - dispatchLatency))
            lines[3] += "\t"
        lines[1] += "|"
        lines[1] += gantt_chart[i]['name']
        lines[1] += "\t"
        lines[3] += str(gantt_chart[i]['start'])
        lines[3] += "\t"
        if i + 1 == len(gantt_chart):
            lines[1] += "|"
            lines[3] += str(gantt_chart[i]['end'])
    for i in range(len(lines[1])):
        lines[0] += "-"
        lines[2] += "-"
    newData = "\n".join(lines)
    appendToFile(newData)

def calculate():
    global CPU_time, processes, newData
    count = len(processes)
    waitingTime = sum([p.waitingTime for p in processes])
    turnaroundTime = sum([p.terminateTime - p.arrival_time for p in processes])
    responseTime = sum([p.responseTime for p in processes])
    cpu_utilization = ((CPU_time - calculateWasteTime()) / CPU_time) * 100
    awt = waitingTime / count
    att = turnaroundTime / count
    art = responseTime / count
    newData = f"CPU utilization = {cpu_utilization:.2f}%\nAWT = {awt:.2f}\nATT = {att:.2f}\nART = {art:.2f}"
    appendToFile(newData)
    AWT_list.append(awt)
    ATT_list.append(att)
    ART_list.append(art)
    return newData


def calculateWasteTime():
    global gantt_chart
    waste = 0
    for i in range(len(gantt_chart) - 1):
        waste += gantt_chart[i+1]['start'] - gantt_chart[i]['end']
    return waste


_, action, processes = getDataFromFile("input.txt")

temp = [burst for p in processes for i, burst in enumerate(p.bursts) if i % 2 == 0]
maxQ = max(temp)

for Q in range(1, maxQ + 1):
    reset_global_variables()
    dispatchLatency, action, processes = getDataFromFile("input.txt")
    print(action)
    print(f"===== Testing Quantum = {Q} =====")
    clear_output()
    clearInitialWasteTime()
    cpuProcessing(Q)

    print("=================================\n")


print(f"ART_list: {ART_list}")
print(f"ATT_list: {ATT_list}")
print(f"AWT_list: {AWT_list}")
min_item_index = None

if action.lower() == "w":
    min_item_index = AWT_list.index(min(AWT_list)) + 1
elif action.lower() == "r":
    min_item_index = ART_list.index(min(ART_list)) + 1
elif action.lower() == "t":
    min_item_index = ATT_list.index(min(ATT_list)) + 1
    
    
print(f"best quantom is => {min_item_index}\n")
print(f"===== Last Quantum Test = {min_item_index} =====")
# reset Variables
reset_global_variables()
AWT_list = []
ATT_list = []
ART_list = []
# start again with the best quantom
clear_output()
clearInitialWasteTime()
cpuProcessing(min_item_index)