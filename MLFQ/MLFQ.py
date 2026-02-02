ready_rr = []
ready_prt = []
waitingQueue = []
processInCpu = None
processInFuture = None
processInFutureTime = -1
CPUtime = 0
first = True
ganttChart = []


class Process:
    def __init__(self, name, arrivalTime, priority, bursts):
        self.name = name
        self.arrivalTime = arrivalTime
        self.arrivalTime2 = arrivalTime
        self.priority = priority
        self.bursts = bursts
        self.currentBurst = bursts[0]
        self.burstIndex = 0
        self.queueNumber = 1
        self.waitingTime = 0
        self.responseTime = 0
        self.terminateTime = 0

    def __str__(self):
        return self.name

    def terminate(self):
        global CPUtime
        if self.responseTime == 0:
            # زمانی که برای اولین بار درخواست I/O میدهد.
            self.responseTime = CPUtime - self.arrivalTime
        self.terminateTime = CPUtime
        endProcessInGanttChart()
        self.updateProcesses()
        print(f"{self.name} => Terminate => time: {CPUtime}")

    def transferToWaitingQueue(self):
        global CPUtime
        if self.responseTime == 0:
            self.responseTime = CPUtime - self.arrivalTime
        self.burstIndex += 1
        self.currentBurst = self.bursts[self.burstIndex]
        self.arrivalTime2 = CPUtime + self.currentBurst
        waitingQueue.append(self)
        endProcessInGanttChart()
        self.updateProcesses()
        print(f"{self.name} => Transfer To Waiting Queue => time: {CPUtime}")

    def transferToReadyPrt(self):
        global CPUtime
        self.queueNumber += 1
        ready_prt.append(self)
        endProcessInGanttChart()
        self.updateProcesses()
        print(f"{self.name} => Transfer To Ready Queue 2 => time: {CPUtime}")

    def removeFromReadyPrt(self):
        global ready_prt
        ready_prt = list(filter(lambda p: p.name != self.name, ready_prt))

    def removeFromWaitingQueue(self):
        global waitingQueue, CPUtime
        waitingQueue = list(filter(lambda p: p.name != self.name, waitingQueue))
        self.burstIndex += 1
        self.currentBurst = self.bursts[self.burstIndex]
        self.queueNumber = 1
        index = processes.index(self)
        processes[index] = self
        print(f"{self.name} => Remove from Waiting Queue => time: {CPUtime}")

    def updateProcesses(self):
        global processInCpu
        index = processes.index(self)
        processes[index] = self
        processInCpu = None

# reade data from file line by line 
def getDataFromFile(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()
    dispatchLatency = int(lines[0])
    quantum = int(lines[1])
    processes = []
    for line in lines[2:]:
        name, values = line.split(":")
        values = list(map(int, values.split(",")))
        processes.append(Process(name, values[0], values[1], values[2:]))
    return dispatchLatency, quantum, processes

# delete every things in the text file
def clearOutput():
    open("output.txt", 'w').close()

# write into text file
def appendToFile(newData):
    with open("output.txt", 'a') as file:
        file.write(newData + "\n")

# find the minimum proccess by priority number
def getMinPriority(process):
    min_priority_process = min(process, key=lambda p: p.priority)
    min_priority_process.removeFromReadyPrt()
    return min_priority_process


def addWaitingTime(process):
    process.waitingTime += 1
    index = processes.index(process)
    processes[index] = process


def appendToGanttChart(process):
    global CPUtime, ganttChart
    print(f"appendToGanttChart => {process}")
    item = {
        'name': process.name,
        'start': CPUtime,
        'end': 0,
    }
    ganttChart.append(item)

# set the end time for each proccess => now cpu time
def endProcessInGanttChart():
    global CPUtime, ganttChart
    ganttChart[-1]['end'] = CPUtime


def clearInitialWasteTime():
    global processes
    min_val = min(processes, key=lambda p: p.arrivalTime).arrivalTime
    for p in processes:
        p.arrivalTime -= min_val
        p.arrivalTime2 -= min_val


def cpuProcessing():
    global CPUtime, ready_rr, ready_prt, waitingQueue, processes, processInCpu, processInFuture, processInFutureTime, first
    while True:
        # readyQueue1 = list(map(addWaitingTime, readyQueue1))
        # readyQueue2 = list(map(addWaitingTime, readyQueue2))
        for p in ready_rr:
            addWaitingTime(p)
        for p in ready_prt:
            addWaitingTime(p)
        #! The principle of oppression
        arrivedProcesses = list(filter(lambda p: p.terminateTime == 0 and p.arrivalTime2 == CPUtime, processes))
        if len(arrivedProcesses) > 0:
            # a proccess come to cpu with most wait in ready list
            newProcesses = list(filter(lambda p: p.arrivalTime == p.arrivalTime2, arrivedProcesses))
            processesFromWaitingQueue = list(filter(lambda p: p.arrivalTime != p.arrivalTime2, arrivedProcesses))
            arrivedProcesses = newProcesses + processesFromWaitingQueue
            for arrivedProcess in arrivedProcesses:
                if arrivedProcess.burstIndex != 0:
                    arrivedProcess.removeFromWaitingQueue()
                if arrivedProcess.queueNumber == 1:
                    #! go to round robin
                    ready_rr.append(arrivedProcess)
                else:
                    #! go to priority queue
                    ready_prt.append(arrivedProcess)
        if processInCpu:
            if processInCpu.currentBurst == 0:
                if processInCpu.burstIndex + 1 == len(processInCpu.bursts):
                    processInCpu.terminate()
                else:
                    processInCpu.transferToWaitingQueue()
            elif processInCpu.queueNumber == 1 and processInCpu.bursts[processInCpu.burstIndex] - processInCpu.currentBurst == quantum:
                processInCpu.transferToReadyPrt()
        if not processInCpu:
            # idel
            # if not any proccess in the cpu, check the terminate list and the other queues
            if processInFuture or ((len(waitingQueue) > 0 or len(list(filter(lambda p: p.terminateTime == 0, processes))) > 0) and len(ready_rr) == 0 and len(ready_prt) == 0):
                CPUtime += 1
                if processInFutureTime == CPUtime:
                    processInCpu = processInFuture
                    processInFuture = None
                    processInFutureTime = -1
                    appendToGanttChart(processInCpu)
                continue
            process = ready_rr.pop(0) if len(ready_rr) > 0 else getMinPriority(ready_prt) if len(ready_prt) > 0 else None
            if not process:
                drawGanttChart()
                calculate()
                break
            if first:
                processInCpu = process
                appendToGanttChart(process)
                first = False
            elif dispatchLatency == 0:
                processInCpu = process
                appendToGanttChart(process)
            else:
                processInFuture = process
                processInFutureTime = CPUtime + dispatchLatency
        if processInCpu:
            processInCpu.currentBurst -= 1
        CPUtime += 1


def drawGanttChart():
    global CPUtime, ganttChart, dispatchLatency
    lines = ["", "", "", ""]
    for i in range(len(ganttChart)):
        if dispatchLatency != 0 and i != 0:
            difference = ganttChart[i]['start'] - ganttChart[i-1]['end']
            includeIdle = difference > dispatchLatency
            lines[1] += "|"
            if includeIdle:
                lines[1] += "id"
                lines[1] += "\t"
                lines[1] += "|"
            lines[1] += "dl"
            lines[1] += "\t"
            lines[3] += str(ganttChart[i-1]['end'])
            if includeIdle:
                lines[3] += "\t"
                # difference - dispatchLatency = id
                lines[3] += str(ganttChart[i-1]['end'] + (difference - dispatchLatency))
            lines[3] += "\t"
        lines[1] += "|"
        lines[1] += ganttChart[i]['name']
        lines[1] += "\t"
        lines[3] += str(ganttChart[i]['start'])
        lines[3] += "\t"
        if i + 1 == len(ganttChart):
            lines[1] += "|"
            lines[3] += str(ganttChart[i]['end'])
    for i in range(len(lines[1])):
        lines[0] += "-"
        lines[2] += "-"
    newData = "\n".join(lines)
    appendToFile(newData)


def calculate():
    global CPUtime, processes
    count = len(processes)
    waitingTime = sum([p.waitingTime for p in processes])
    turnaroundTime = sum([p.terminateTime - p.arrivalTime for p in processes])
    responseTime = sum([p.responseTime for p in processes])
    cpu_utilization = ((CPUtime - calculateWasteTime()) / CPUtime) * 100
    awt = waitingTime / count
    att = turnaroundTime / count
    art = responseTime / count
    newData = f"CPU utilization = {cpu_utilization:.2f}%\nAWT = {awt:.2f}\nATT = {att:.2f}\nART = {art:.2f}"
    appendToFile(newData)


def calculateWasteTime():
    global ganttChart
    waste = 0
    for i in range(len(ganttChart) - 1):
        waste += ganttChart[i+1]['start'] - ganttChart[i]['end']
    return waste


dispatchLatency, quantum, processes = getDataFromFile("./input_main.txt")
clearOutput()
clearInitialWasteTime()
cpuProcessing()