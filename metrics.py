import numpy as np
import os
instr_type = []

def remove_space(r_file, w_file):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), r_file)
    read_file = open(path, "r")
    lines = read_file.readlines()
    new_values = []
    for line in lines:
        line = line.strip()
        new_values.append(line)
    read_file.close()

    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), w_file)
    write_file = open(path, "w")
    for inst in new_values:
        write_file.write(inst + "\n")
    write_file.close()
    return None

def check_line(str):
    mem_instr1 = ["lw", "li", "lb", "lh"]
    mem_instr2 = ["sw", "sh", "sb"]

    for i in mem_instr1:
        if (str[0:2] == i):
            return "read"
    for i in mem_instr2:
        if (str[0:2] == i):
            return "write"
        
    if (str[0:3] == "lbu" or str[0:3] == "lhu"):
        return "read"
    elif (str[0] == "b"):
        return "branch"
    elif (str[0] == "j"):
        return "branch"
    else:
        return "alu"

def read_riscv(r_file):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), r_file)
    read_file = open(path, "r")
    lines = read_file.readlines()
    new_values = []
    for line in lines:
        if (line[0] != "/" and line[0] !="."):
            new_val = check_line(line)
            new_values.append(new_val)
    read_file.close()
    return new_values

instr_type = read_riscv("asm2.txt")
# print(instr_type)
# print(len(instr_type))

def mem_frac(stream, num_items): #num_items - number of objects to match
    count = 0
    r_count = 0
    w_count = 0

    for i in stream:
        if i == "read":
            r_count +=1
            count += 1
        elif i == "write":
            w_count += 1
            count += 1

    #in the loop: read array, write to var, read 2 vars
    r_loop_mem = 2 * 3 * (num_items - 1)
    w_loop_mem = 2 * (num_items - 1)
    loop_mem = r_loop_mem + w_loop_mem

    #account for mem accesses in the loops
    r_count += r_loop_mem
    w_count += w_loop_mem
    count += loop_mem
    total = len(stream) + loop_mem
    r_frac = r_count/total
    w_frac = w_count/total
    m_frac = count/total
    return [r_frac, w_frac, m_frac] #reads fraction, writes fraction, overall mem fraction

# frac = mem_frac(instr_type, 0)
# print(frac)
