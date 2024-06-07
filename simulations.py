import metrics
import numpy as np
from backend import memory
from backend import cache
import os
import matplotlib.pyplot as plt
import math
import time

def parse_machine_code(r_file):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), r_file)
    read_file = open(path, "r")
    lines = read_file.readlines()
    new_values = []
    for line in lines:
        hex1 = line[0:2]
        hex2 = line[2:4]
        hex3 = line[4:6]
        hex4 = line[6:8]
        data = [hex1, hex2, hex3, hex4]
        for i in data:
            new_values.append(i)

    read_file.close()
    return new_values

def simulation1(data, params, stream): #all instructions, loops only 1 iteration
    num_sets = params[0]
    blcks_per_set = params[1]
    blck_size = params[2]
    write_policy = params[3]
    write_alloc = params[4]
    replacement = params[5]
    mem1 = memory()
    mem1.write(10000, data, len(data))

    cache1 = cache(mem1, num_sets, blcks_per_set, blck_size, write_policy, write_alloc, replacement)

    hits = 0
    misses = 0
    for i in stream:
        if i == "read":
            r_addr = np.random.randint(0, mem1.capacity()) #testing no locality
            r_data = cache1.read(r_addr, 4)

            if (r_data[1]): #true means hit
                hits += 1
            else:
                misses += 1

        elif i == "write":
            w_addr = np.random.randint(0, mem1.capacity())
            data = ["de", "ed", "be", "ef"] 
            w_status = cache1.write(w_addr, data, len(data))

            if (w_status):
                hits += 1
            else:
                misses += 1
        
    hit_rate = hits/(hits+misses)
    miss_rate = misses/(hits+misses)
    cycle_count = cache1.num_cycles()
    return (cycle_count, hit_rate, miss_rate)

#all hits - 1 cycle
#read miss - 200 cycles
#write miss - 300 cycles

def loop_simulation(data, params, loop_content_inc, addrs_inc, loop_content_const, addrs_const, iter): #loop memory accesses, corresponding addresses
    num_sets = params[0]
    blcks_per_set = params[1]
    blck_size = params[2]
    write_policy = params[3]
    write_alloc = params[4]
    replacement = params[5]
    mem1 = memory()
    mem1.write(0, data, len(data))

    cache1 = cache(mem1, num_sets, blcks_per_set, blck_size, write_policy, write_alloc, replacement)

    hits = 0
    misses = 0
    for i in range(0,iter):
        for j, v in enumerate(loop_content_inc):
            if v == "read":
                result = cache1.read(addrs_inc[j]+i*4, 4)
                # print(cache1.addr_to_tag(addrs_inc[j]+i*4))
                # print(result[1])
                if (result[1]):
                    hits += 1
                else:
                    misses += 1

            elif v == "write":
                result = cache1.write(addrs_inc[j]+i*4, [i, i, i, i], 4)
                if (result):
                    hits += 1
                else:
                    misses += 1

        for n, instr in enumerate(loop_content_const):
            if instr == "read":
                result = cache1.read(addrs_const[n], 4)
                # print(cache1.addr_to_tag(addrs_const[n]))
                # print(result[1])
                if (result[1]):
                    hits += 1
                else:
                    misses += 1
            
            elif instr == "write":
                result = cache1.write(addrs_const[n], ["de", "ad", "be", "ef"], 4)
                # print(cache1.addr_to_tag(addrs_const[n]))
                # print(result)
                if (result):
                    hits += 1
                else:
                    misses += 1
        c_data, c_tags, c_valid, c_dirty, c_lru = cache1.view_cache_contents()
        # print("cache data: \n",c_data)
        # print("cache tags: ",c_tags)
        # print("valid bits: ", c_valid)
        # print("dirty bits: ", c_dirty)
        # print("cache lru queue: ",c_lru)
        # input()

    cycle_count = cache1.num_cycles()
    miss_rate = misses/(hits+misses)
    return (cycle_count, miss_rate)

def program_simulation1(stream, data, data_size, params, addrs, iter):
    num_sets = params[0]
    blcks_per_set = params[1]
    blck_size = params[2]
    write_policy = params[3]
    write_alloc = params[4]
    replacement = params[5]
    mem1 = memory()
    mem1.write(0, data, len(data))

    cache1 = cache(mem1, num_sets, blcks_per_set, blck_size, write_policy, write_alloc, replacement)
    cycle_count = 0
    #declare addresses
    len1 = 0

    obj = addrs[0]
    obj_list = addrs[1]
    curr_obj = addrs[2]
    obj_check_result = addrs[3]
    item_sighted = addrs[4]
    item = addrs[5]
    direc = addrs[6]

    speed = addrs[7]
    arm = addrs[8]
    grab = addrs[9]

    filler_data = ["ff" for i in range(0,data_size)]
    #obj_check
    for i in range(0, iter):
        result = cache1.read(len1, data_size)
        result = cache1.read(obj_list+i*data_size, data_size)
        result = cache1.write(curr_obj, result[0], data_size)
        result = cache1.read(curr_obj, data_size)
        result = cache1.read(obj, data_size)
    
    #perform_task
    result = cache1.read(item_sighted, data_size)
    result = cache1.read(speed, data_size)
    result = cache1.read(direc, data_size)
    result = cache1.write(arm, result[0], data_size)
    result = cache1.read(item, data_size)
    for i in range(0, iter):
        result = cache1.read(len1, data_size)
        result = cache1.read(obj_list+i*data_size, data_size)
        result = cache1.write(curr_obj, result[0], data_size)
        result = cache1.read(curr_obj, data_size)
        result = cache1.read(obj, data_size)
    result = cache1.write(obj_check_result, filler_data, data_size)
    result = cache1.write(grab, filler_data, data_size)
    result = cache1.write(speed, filler_data, data_size)
    result = cache1.read(direc, data_size)
    result = cache1.write(arm, result[0], data_size)
    result = cache1.write(grab, filler_data, data_size)

    # assume stream has non-mem instructions
    for i in stream:
        cycle_count += 1

    cycle_count += cache1.num_cycles()
    cache_stats = cache1.access_stats()
    return (cycle_count, cache_stats)

#simple test on cache---------------------

def simple_sim(data, data_size, params, addrs, iter):
    new_mem = memory()
    num_sets = params[0]
    blcks_per_set = params[1]
    blck_size = params[2]
    write_policy = params[3]
    write_alloc = params[4]
    replacement = params[5]
    data = parse_machine_code("testing2.txt")
    cycles = 0
    new_mem.write(0,[np.random.randint(1, 999) for i in range(0, 20000)], 20000)

    new_cache = cache(new_mem, num_sets, blcks_per_set, blck_size, write_policy, write_alloc, replacement)
    for i in range(0, len(data)):
        r_d = new_cache.write(addrs[0]+i*data_size, ["ff" for j in range(0, data_size)], data_size)
        r_d2 = new_cache.read(addrs[0]+i*data_size, data_size)
        c_data, c_tags, c_valid, c_dirty, c_lru = new_cache.view_cache_contents()
        cycles = new_cache.num_cycles()
        # print("cache data: \n",c_data)
        # print("cache tags: ",c_tags)
        # print("valid bits: ", c_valid)
        # print("dirty bits: ", c_dirty)
        # print("cache lru queue: ",c_lru)
        # print("memory content: ", new_mem.view(1600,1650))
        # input(r_d)
    cycle_count = new_cache.num_cycles()
    c_stats = new_cache.access_stats()
    # print(miss_rate)
    return (cycle_count, c_stats)
#-----------------------------------------
#sim 1 no locality, access random addresses
# stream1 = metrics.read_riscv("asm2.txt")
# params1 = [8, 4, 16, "write-through", "write-allocate", "LRU"]
# data1 = parse_machine_code("testing2.txt")
# outputs1 = simulation1(data1, params1, stream1)
# print(outputs1)

# #loop sim
# data = parse_machine_code("testing2.txt")
# data = [np.random.randint(101, 999) for i in range(0,20000)]
# params1 = [8, 2, 16, "write-through", "write-allocate", "LRU"]
# loop_content1 = ["read"]
# loop_addr1 = [0]
# loop_content2 = ["read", "write","read"]
# loop_addr2 = [np.random.randint(0,100), np.random.randint(101,1000), np.random.randint(2000,9999)]
# outputs2 = loop_simulation(data, params1, loop_content1, loop_addr1, loop_content2, loop_addr2, 100)
# print(outputs2)

# #-------program sim-------------
def filter_stream(stream_data):
    new_data = []
    for i in stream_data:
        if i != "read" and i != "write":
            new_data.append(i)
    return new_data

def instr_stats(start, end):
  stream = metrics.read_riscv("asm2.txt")
  instr_perc = []
  for i in range(start, end):
    instr_breakdown = metrics.mem_frac(stream, i)[2]
    instr_perc.append(instr_breakdown)

  plt.figure(0)
  plt.xlabel("Number of Items")
  plt.ylabel("Memory Access Instructions Percentage")
  plt.plot(np.arange(start, end), instr_perc, color="navy")
  plt.show()
  return None

def trials(num_trials, params, num_items):
  stream = metrics.read_riscv("asm2.txt")
  stream = filter_stream(stream) # need to estimate instruction stream better
  data = parse_machine_code("testing2.txt")
  data_size = 4
  cycles = 0
  miss_rate = 0

  for j in range(0, num_trials):
    addrs = []
    for i in range(0,10):
        addrs.append(np.random.randint(2000*i, 2000*i+1999))
    output = program_simulation1(stream, data, data_size, params, addrs, num_items)
    # output = simple_sim(data, data_size, params,addrs, num_items)
    cycles += output[0]

    miss_rate += output[1][2]
  
  avg_cycles = cycles/num_trials
  avg_miss_rate = miss_rate/num_trials

  return avg_cycles, avg_miss_rate

# params = [2, 2, 8, "write-through", "write-no-allocate", "LRU"] 
# a, b = trials(100, params)
# print(a,b)
def calculate_carbon(speedup): #the epa uses a linear scaling between kWh and kg of carbon
    #100 million kWh => 41,690,375 kg of CO2e
    #=> 1 kWh = .41690375 kg of Carbon
    #article says caches consume 13-45% of total CPU power
    # midpoint: 29% => .29 * 63 (use Ultrasparc t1 figure) = 18.27W for cache
    #assume 10,000 hours of usage
    baseline = ((18.27/1000) * 10000) * .41690375 #CO2 of baseline
    improved_c = baseline/speedup
    return improved_c

def experiment1(): #222828 cycles for all misses (no cache) in program_sim #74000 cycles for simple_sim

    sizes = [16, 32, 64, 128, 256, 512, 1024]
    assoc = [1, 2, 4, None]
    num_sets = 0
    num_trials = 2
    best_designs = []
    bd_co2 = []
    for i in range(0, len(sizes)):
        size_data_x = []
        size_data_y = []
        miss_data_y = []
        for j in range(2, int(np.log2(sizes[i])-1)):
            block_size = int(2**j)
            if not assoc.__contains__(int(sizes[i]/block_size)):
                assoc[3] = int(sizes[i]/block_size)
            for h,k in enumerate(assoc):
                if k == None:
                    break
                
                num_sets = int(sizes[i]/(k*block_size))
                if block_size*k > sizes[i]:
                    break

                params = [num_sets, k, block_size, "write-back", "write-allocate", "LRU"]
                a,b = trials(num_trials, params)
                size_data_x.append((num_sets, k, block_size))
                size_data_y.append((a,b))
        
        speedup = [74000/i[0] for i in size_data_y]
        smallest = 99999999
        idx = 0
        for f,v in enumerate(size_data_y):
            if v[0] < smallest:
                smallest = v[0]
                idx = f

        best_designs.append(size_data_x[idx])
        bd_co2.append(calculate_carbon(speedup[idx]))

        fig, ax = plt.subplots(figsize=(10,9))
        plt.title(str(sizes[i])+"-byte")
        ax2 = ax.twinx()
        ax.set_xticks(ticks=np.arange(0, len(size_data_y)), labels=[str(i[0])+"/"+str(i[1])+"/"+str(i[2]) for i in size_data_x])
        max_y = 4
        y_inc = .2
        if (max(speedup) > 4):
            max_y = math.ceil(max(speedup)) + 2
            y_inc = max_y/20
        ax.set_yticks(np.arange(1, max_y, y_inc))
        ax.set_ylim(.9, max_y)
        ax.set_ylabel("Speedup over naive cache")
        ax.set_xlabel("Number of sets/Associativity/Block size")
        fig.autofmt_xdate()
        line1 = ax.plot(np.arange(0, len(size_data_y)), speedup, label="Speedup", color="navy")
        ax.scatter(np.arange(0, len(size_data_y)), speedup, color="navy")

        ax2.set_ylim((0, 1.1))
        ax2.set_ylabel("Miss rate")
        ax2.set_yticks(np.arange(0, 1.1, .1))
        line2 = ax2.plot(np.arange(0, len(size_data_y)), [i[1] for i in size_data_y],label="Miss rate", color="maroon")
        ax2.scatter(np.arange(0, len(size_data_y)), [i[1] for i in size_data_y], color="maroon")
        
        lns = line1+line2
        labels = [l.get_label() for l in lns]
        ax.legend(lns, labels, loc=0)
        #plt.show()

    print(best_designs)
    print(bd_co2)
    fig, ax = plt.subplots(figsize=(10,9))
    ax.set_xticks(ticks=np.arange(0, len(best_designs)), labels=[str(i[0])+"/"+str(i[1])+"/"+str(i[2]) for i in best_designs])
    max_y = 100
    y_inc = max_y/20
    ax.set_yticks(np.arange(0,max_y, y_inc))
    ax.set_ylim(0,max_y)
    ax.set_ylabel("CO2 footprint (kg)")
    ax.set_xlabel("Number of sets/Associativity/Block size")
    fig.autofmt_xdate()
    line1 = ax.bar(np.arange(0, len(bd_co2)), [76.168 for i in range(0, len(bd_co2))], color="orange")
    line2 = ax.bar(np.arange(0, len(bd_co2)), bd_co2, color="limegreen")
    plt.legend(["Baseline", "Improved"])
    plt.show()

#experiment1()



# instr_stats(0,100)
# instr_stats(100,1000)
def perc_dec(co2_val, baseline):
    return (1 - co2_val/baseline)*100

# def calculate_carbon_cycles(cycles):
#     #assume 2ghz
    
#     baseline = ((18.27/1000) * 10000) * .41690375 #CO2 of baseline
#     improved_c = baseline/speedup
#     return improved_c

def experiment2(): #222828 cycles for all misses (naive cache) in program_sim #74000 cycles for simple_sim
    t1 = time.time()
    naive_cache = 222828
    baseline_c = 76.168
    sizes = [1024]
    assoc = [1, 2, 4, None]
    num_sets = 0
    num_trials = 100
    best_designs = []
    bd_co2 = []
    params = []

    for i in range(0, len(sizes)):
        size_data_x = []
        size_data_y = []
        miss_data_y = []
        for j in range(2, int(np.log2(sizes[i])-1)):
            block_size = int(2**j)
            if not assoc.__contains__(int(sizes[i]/block_size)):
                assoc[3] = int(sizes[i]/block_size)
            for h,k in enumerate(assoc):
                if k == None:
                    break
                
                num_sets = int(sizes[i]/(k*block_size))
                if block_size*k > sizes[i]:
                    break

                params = [num_sets, k, block_size, "write-through", "write-no-allocate", "LRU"]
                a,b = trials(num_trials, params)
                size_data_x.append((num_sets, k, block_size))
                size_data_y.append((a,b))
        
        speedup = [naive_cache/i[0] for i in size_data_y]
        # smallest = 99999999
        # idx = 0
        # for f,v in enumerate(size_data_y):
        #     if v[0] < smallest:
        #         smallest = v[0]
        #         idx = f

        # best_designs.append(size_data_x[idx])
        # bd_co2.append(calculate_carbon(speedup[idx]))

        co2 = [calculate_carbon(i) for i in speedup]
        fig, ax = plt.subplots(figsize=(10,9))
        plt.title(params[3] +", " + params[4] + ", "+params[5])
        ax2 = ax.twinx()
        ax.set_xticks(ticks=np.arange(0, len(size_data_y)), labels=[str(i[0])+"/"+str(i[1])+"/"+str(i[2]) for i in size_data_x])
        max_y = 4
        y_inc = .2
        if (max(speedup) > 4):
            max_y = math.ceil(max(speedup)) + 2
            y_inc = max_y/20
        ax.set_yticks(np.arange(1, max_y, y_inc))
        ax.set_ylim(.9, max_y)
        ax.set_ylabel("Speedup over naive cache")
        ax.set_xlabel("Number of sets/Associativity/Block size")
        fig.autofmt_xdate()
        line1 = ax.plot(np.arange(0, len(size_data_y)), speedup, label="Speedup", color="black")
        ax.scatter(np.arange(0, len(size_data_y)), speedup, color="black")

        ax2.set_ylim((0, 1.1))
        ax2.set_ylabel("Miss rate")
        ax2.set_yticks(np.arange(0, 1.1, .1))
        line2 = ax2.plot(np.arange(0, len(size_data_y)), [i[1] for i in size_data_y],label="Miss rate", color="gray")
        ax2.scatter(np.arange(0, len(size_data_y)), [i[1] for i in size_data_y], color="gray")
        
        lns = line1+line2
        labels = [l.get_label() for l in lns]
        ax.legend(lns, labels, loc=0)
        #plt.show()
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "i.png")
        plt.savefig(path)

    perc_reduc = [perc_dec(i, baseline_c) for i in co2]
    fig, ax = plt.subplots(figsize=(10,9))
    plt.title(params[3] +", " + params[4] + ", "+params[5])
    ax.set_xticks(ticks=np.arange(0, len(size_data_x)), labels=[str(i[0])+"/"+str(i[1])+"/"+str(i[2]) for i in size_data_x])
    max_y = 100
    y_inc = max_y/20
    ax.set_yticks(np.arange(0,max_y, y_inc))
    ax.set_ylim(0,max_y)
    ax.set_ylabel("CO2 footprint (kg)/Percentage Reduction")
    ax.set_xlabel("Number of sets/Associativity/Block size")
    fig.autofmt_xdate()

    line1 = ax.plot(np.arange(0, len(co2)), [baseline_c for i in range(0, len(co2))], linestyle="dashed", color="darkgray")
    line2 = ax.plot(np.arange(0, len(co2)), co2, color="black")
    ax.plot(np.arange(0,len(perc_reduc)), perc_reduc, color="dimgray")
    plt.legend(["Baseline CO2", "Improved CO2", "Percent Reduction"])
    ax.scatter(np.arange(0, len(co2)), co2, color="black")
    ax.scatter(np.arange(0,len(perc_reduc)), perc_reduc, color="dimgray")
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "j.png")
    plt.savefig(path)
    t2 = time.time()
    print("Experiment 2 took ", (t2-t1)/60, " minutes.")

# experiment2()

def experiment3(): # pick a particular design, see scaling w # items
    t1 = time.time()
    #num of items range
    start = 1
    end = 101

    num_trials = 100
    num_sets = 4
    assoc = 4
    block_size = 64
    params = []

    items = [i for i in range(start, end)]
    size_data_x = []
    size_data_y = []
    
    r_frac = []
    w_frac = []
    m_frac = []

    baseline_cycles = []
    stream = metrics.read_riscv("asm2.txt")
    stream = filter_stream(stream)

    for i in items:
        params = [num_sets, assoc, block_size, "write-back", "write-allocate", "LRU"]
        a,b = trials(num_trials, params, i)
        size_data_x.append((num_sets, assoc, block_size))
        size_data_y.append((a,b))

        mem_acc = metrics.mem_frac(stream, i)
        r_frac.append(mem_acc[0])
        w_frac.append(mem_acc[1])
        m_frac.append(mem_acc[2])

    for i in items:
        params = [1, 1, 4, "write-back", "write-allocate", "LRU"]
        a,b = trials(num_trials, params, i)
        baseline_cycles.append((a,b)) #naive cache has ~95% miss rate

    speedup = [baseline_cycles[i][0]/size_data_y[i][0] for i in range(0, len(size_data_y))]
    
    fig, ax = plt.subplots(figsize=(10,8))
    plt.title(params[3] +", " + params[4] + ", "+params[5]+", "+"4/4/64")
    ax2 = ax.twinx()
    ax.set_xticks(ticks=np.arange(0, len(size_data_y), len(size_data_y)/20))
    max_y = 4
    y_inc = .2
    if (max(speedup) > 4):
        max_y = math.ceil(max(speedup)) + 2
        y_inc = max_y/20
    ax.set_yticks(np.arange(1, max_y, y_inc))
    ax.set_ylim(.9, max_y)
    ax.set_ylabel("Speedup over naive cache")
    ax.set_xlabel("Number of items")
    # ax.scatter(np.arange(0, len(speedup)), speedup, color="black")

    ax2.set_ylim((0, 1))
    ax2.set_ylabel("Memory Access Fraction")
    ax2.set_yticks(np.arange(0, 1, .05))
    line2 = ax2.plot(np.arange(start, len(r_frac)+start), [i for i in r_frac],label="Loads", color="lightgray")
    line3 = ax2.plot(np.arange(start, len(w_frac)+start), [i for i in w_frac],label="Stores", color="darkgray")
    line4 = ax2.plot(np.arange(start, len(m_frac)+start), [i for i in m_frac],label="Total", color="dimgray")
    line1 = ax.plot(np.arange(start, len(speedup)+start), speedup, label="Speedup", color="black")
    # ax2.scatter(np.arange(0, len(size_data_y)), [i[1] for i in size_data_y], color="gray")
    
    lns = line2+line3+line4+line1
    labels = [l.get_label() for l in lns]
    ax.legend(lns, labels, loc=0)

    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "mem3.png")
    # plt.savefig(path)
    plt.show()
    t2 = time.time()
    print("Experiment 3 took ", (t2-t1)/60, " minutes.")

experiment3()