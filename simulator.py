'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Author: Minh Ho
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt

Apr 10th Revision 1:
    Update FCFS implementation, fixed the bug when there are idle time slices between processes
    Thanks Huang Lung-Chen for pointing out
Revision 2:
    Change requirement for future_prediction SRTF => future_prediction shortest job first(SJF), the simpler non-preemptive version.
    Let initial guess = 5 time units.
    Thanks Lee Wei Ping for trying and pointing out the difficulty & ambiguity with future_prediction SRTF.
'''
import sys
import copy

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.predict_time = 5
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum):
    schedule = []
    current_time = 0
    waiting_time = 0
    switch_time = None
    rr = []
    for process in process_list:
        if switch_time == None:
            rr.append(process)
            running_process = rr.pop(0)
            current_time = running_process.arrive_time
            schedule.append((current_time, running_process.id))
            if time_quantum > running_process.burst_time:
                switch_time = current_time + running_process.burst_time
                running_process.burst_time = 0
            else:
                switch_time = current_time + time_quantum
                running_process.burst_time -= time_quantum
        else:
            while (switch_time != None) and (switch_time <= process.arrive_time):
                current_time = switch_time
                if running_process.burst_time > 0:
                    running_process.arrive_time = current_time
                    rr.append(running_process)
                if len(rr) > 0:
                    running_process = rr.pop(0)
                    waiting_time += (current_time - running_process.arrive_time)
                    schedule.append((current_time, running_process.id))
                    if time_quantum > running_process.burst_time:
                        switch_time = current_time + running_process.burst_time
                        running_process.burst_time = 0
                    else:
                        switch_time = current_time + time_quantum
                        running_process.burst_time -= time_quantum
                else:
                    switch_time = None
            rr.append(process)
    while len(rr) > 0:
        current_time = switch_time
        if running_process.burst_time > 0:
            running_process.arrive_time = current_time
            rr.append(running_process)
        running_process = rr.pop(0)
        waiting_time += (current_time - running_process.arrive_time)
        schedule.append((current_time, running_process.id))
        if time_quantum > running_process.burst_time:
            switch_time = current_time + running_process.burst_time
            running_process.burst_time = 0
        else:
            switch_time = current_time + time_quantum
            running_process.burst_time -= time_quantum
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

def SRTF_scheduling(process_list, sim_time_increase=1):
    schedule=[]
    arrived_tasks=[]
    waiting_time =0
    current_time = 0
    tmp_complete_time = None
    running_process = None
    i = 0
    while True:
        if running_process is None:
            if len(arrived_tasks) > 0:
                arrived_tasks.sort(key=lambda x: x.burst_time)
                running_process = arrived_tasks.pop(0)
            else:
                if i < len(process_list):
                    if current_time >= process_list[i].arrive_time:
                        running_process = process_list[i]
                        i += 1
                else:
                    break
            if running_process is not None:
                tmp_complete_time = current_time + running_process.burst_time
                waiting_time += (current_time - running_process.arrive_time)
                schedule.append((current_time, running_process.id))
        else:
            if current_time >= tmp_complete_time:
                arrived_tasks.sort(key=lambda x: x.burst_time)
                if len(arrived_tasks) > 0:
                    running_process = arrived_tasks.pop(0)
                    tmp_complete_time = current_time + running_process.burst_time
                    waiting_time += (current_time - running_process.arrive_time)
                    schedule.append((current_time, running_process.id))
                else:
                    running_process = None
                    tmp_complete_time = None
            if i < len(process_list):
                if current_time >= process_list[i].arrive_time:
                    process = process_list[i]
                    if (running_process is not None) and (process.arrive_time + process.burst_time) < tmp_complete_time:
                        running_process.arrive_time = current_time
                        running_process.burst_time = tmp_complete_time - current_time
                        arrived_tasks.append(running_process)
                        running_process = process
                        tmp_complete_time = current_time + running_process.burst_time
                        schedule.append((current_time, running_process.id))
                    elif running_process is None:
                        running_process = process
                        tmp_complete_time = current_time + running_process.burst_time
                        schedule.append((current_time, running_process.id))
                    else:
                        arrived_tasks.append(process)
                    i += 1
            else:
                if not arrived_tasks:
                    break
        current_time += sim_time_increase
    average_waiting_time = waiting_time / float(len(process_list))
    return (schedule, average_waiting_time)

def SJF_scheduling(process_list, alpha, sim_time_increase=1):
    guess = {}
    real =  {}
    arrived_tasks = []
    schedule = []
    waiting_time =0
    current_time = 0
    tmp_complete_time = None
    running_process = None
    i = 0
    while True:
        if running_process is None:
            if len(arrived_tasks) > 0:
                arrived_tasks.sort(key=lambda x: x.predict_time)
                running_process = arrived_tasks.pop(0)
            else:
                if i < len(process_list):
                    if current_time >= process_list[i].arrive_time:
                        running_process = process_list[i]
                        gtime = guess.get(running_process.id, 5)
                        rtime = real.get(running_process.id, 5)
                        guess[running_process.id] = alpha * rtime + (1 - alpha) * gtime
                        i += 1
                else:
                    break
            if running_process is not None:
                tmp_complete_time = current_time + running_process.burst_time
                waiting_time += (current_time - running_process.arrive_time)
                schedule.append((current_time, running_process.id))
        else:
            if i < len(process_list):
                if current_time >= process_list[i].arrive_time:
                    arrived_tasks.append(process_list[i])
                    i += 1
            else:
                if not arrived_tasks:
                    break
            if current_time >= tmp_complete_time:
                real[running_process.id] = running_process.burst_time
                if len(arrived_tasks) > 0:
                    for process in arrived_tasks:
                        gtime = guess.get(process.id, 5)
                        rtime = real.get(process.id, 5)
                        process.predict_time = alpha * rtime + (1 - alpha) * gtime
                        guess[running_process.id] = alpha * rtime + (1 - alpha) * gtime
                    arrived_tasks.sort(key=lambda x: x.predict_time)
                    running_process = arrived_tasks.pop(0)
                    tmp_complete_time = current_time + running_process.burst_time
                    waiting_time += (current_time - running_process.arrive_time)
                    schedule.append((current_time, running_process.id))
                else:
                    running_process = None
                    tmp_complete_time = None
        current_time += sim_time_increase
    average_waiting_time = waiting_time / float(len(process_list))
    return (schedule, average_waiting_time)


def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result


def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(copy.deepcopy(process_list))
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(copy.deepcopy(process_list),time_quantum = 10)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(copy.deepcopy(process_list))
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])
