import numpy as np
import metrics
import math

class cache():
    def __init__(self, memory1, num_sets, assoc, block_size, write_policy, write_allocate, replacement) -> None:
        self.sets = num_sets
        self.assoc = assoc
        self.bl_size = block_size
        self.wr_policy = write_policy
        self.wr_alloc = write_allocate
        self.repl_pol = replacement
        self.total_size = self.bl_size * self.assoc * self.sets

        self.cache_data = self.initialize_cache()
        self.cache_tags = self.initialize_tag_storage()
        self.valid = self.initialize_valid_bits()
        self.dirty = self.initialize_dirty_states()
        self.lru_queue = self.initialize_lru_queue()

        self.memory = memory1 # memory instance
        self.addr_space = self.memory.capacity()
        self.word = 4 # 32-bit word

        self.cycle_count = 0
        self.read_mem_cycles = 200
        self.write_mem_cycles = 300
        self.hit_cycles = 1

        self.hits = 0
        self.misses = 0

    def access_stats(self):
        if ((self.hits + self.misses) == 0):
            return (0,0,0)
        else:
            miss_rate = self.misses/(self.hits+self.misses)
            return (self.hits, self.misses, miss_rate)
    
    def view_cache_contents(self):
        return self.cache_data, self.cache_tags, self.valid, self.dirty, self.lru_queue
    
    def tag_to_addr(self, tag, set, bl_offset):
        binary = bin(self.addr_space)
        binary = binary[2:]
        total_bits = len(binary)
        bl_bits = math.floor(np.log2(self.bl_size))
        set_bits = math.floor(np.log2(self.sets))
        tag_bits = total_bits - bl_bits - set_bits
        
        tag = bin(tag)[2:]
        set = bin(set)[2:]
        bl_offset = bin(bl_offset)[2:]

        for i in range(0, tag_bits-len(tag)):
            tag = "0" + tag
        for i in range(0, set_bits-len(set)):
            set = "0" + set
        for i in range(0, bl_bits-len(bl_offset)):
            bl_offset = "0" + bl_offset
        
        new_addr = int(tag + set + bl_offset, base=2)
        return new_addr

    def addr_to_tag(self, addr): #int addr -> cache tag, set idx, bl offset
        binary = bin(self.addr_space)
        binary = binary[2:]
        num_bits = len(binary)
        bl_bits = math.floor(np.log2(self.bl_size))
        set_bits = math.floor(np.log2(self.sets))
        tag_bits = num_bits - bl_bits - set_bits

        binary_addr = bin(addr)
        binary_addr = binary_addr[2:]

        len_dif = len(binary) - len(binary_addr)
        if (len_dif > 0):
            for i in range(0, len_dif):
                binary_addr = "0" + binary_addr

        tag = binary_addr[0:tag_bits]
        tag = int(tag, base=2)
        if (set_bits == 0): #fully associative
            set_idx = 0
        else:
            set_idx = binary_addr[tag_bits:(tag_bits+set_bits)]
            set_idx = int(set_idx, base=2)
            set_idx = set_idx % self.sets #wrap around if exceeds # of sets

        bl_offset = binary_addr[(tag_bits+set_bits):(tag_bits+set_bits+bl_bits)]
        bl_offset = int(bl_offset, base=2)
        bl_offset = bl_offset % self.bl_size # same thing as set idx

        return (tag, set_idx, bl_offset)
 
    def initialize_cache(self):
        sets = np.zeros(self.sets, dtype=object)
        
        for i in range(0,self.sets):
            a = []
            for j in range(0, self.assoc):
                b = []
                for k in range(0, self.bl_size):
                    b.append(0)
                a.append(b)
            sets[i] = a

        data = sets
        return data
    
    def initialize_tag_storage(self):
        sets = np.zeros(self.sets, dtype=object)
        
        for i in range(0,self.sets):
            inner = []
            for j in range(0, self.assoc): #associativity= # of blocks per set
                inner.append(0)
            sets[i] = inner

        data = sets
        return data
    
    def initialize_valid_bits(self): #use to check if a block is being occupied
        sets1 = np.zeros(self.sets, dtype=object)

        for i in range(0, self.sets):
            sets1[i] = []

        for i in sets1:
            for j in range(0, self.assoc):
                i.append(0)
        return sets1
    
    def initialize_lru_queue(self): #need to keep a queue for each individual set
        sets = np.zeros(self.sets, dtype=object)
        for i in range(0,self.sets):
            sets[i] = []
        return sets

    def initialize_dirty_states(self):
        sets = np.zeros(self.sets, dtype=object)    
        for i in range(0, self.sets):
            sets[i] = np.zeros(self.assoc)
        return sets
    
    def flush(self): #delete everything from cache
        self.cache_data = self.initialize_cache()
        self.cache_tags = self.initialize_tag_storage()
        self.valid = self.initialize_valid_bits()
        self.dirty = self.initialize_dirty_states()
        self.lru_queue = self.initialize_lru_queue()
        return None
    
    def num_cycles(self):
        return self.cycle_count
    
    def block_replacement(self, addr, set_idx): #List of queues of (set_idx, bl_sel)
        #return the block number
        if self.repl_pol == "LRU":
            Full = True
            bl_num = None
            for i in range(0, self.assoc):
                if (self.valid[set_idx][i] == 0):
                    Full = False 
                    bl_num = i
                    break

            if (Full):
                queue_item = self.lru_queue[set_idx].pop(0)
                self.lru_queue[set_idx].append(queue_item)
                bl_num = queue_item
                self.block_repl_writes(addr, set_idx, bl_num)
                return bl_num
            else:
                if (self.lru_queue[set_idx].__contains__(bl_num)):
                    self.lru_queue[set_idx].remove(bl_num)
                    self.lru_queue[set_idx].append(bl_num)
                else:
                    self.lru_queue[set_idx].append(bl_num)
                return bl_num
            
        elif self.repl_pol == "random":
            Full = True
            bl_num = None
            for i in range(0, self.assoc):
                if (self.valid[set_idx][i] == 0):
                    Full = False 
                    bl_num = i
                    break
            
            if (Full):
                bl_num = np.random.randint(0, self.assoc)
                self.block_repl_writes(addr, set_idx, bl_num)
                return bl_num
            else:
                return bl_num
        
        else:
            ValueError("Unsupported replacement policy")            
    

    def read(self, addr, size):
        #read arbitrary size
        hit_status = None
        missed_blocks = set() #no duplicates
        miss = False
        for i in range(0, size):
            bit_data = self.addr_to_tag(addr+i)
            tag = bit_data[0]
            set_idx = bit_data[1]
            bl_offset = bit_data[2]

            tag_match = False
            block_sel = None

            for j, v in enumerate(self.cache_tags[set_idx]):
                if tag == v:
                    tag_match = True
                    block_sel = j
                    break
            
            if block_sel == None:
                valid = False
            else:
                valid = (self.valid[set_idx][block_sel] == 1)

            if (tag_match == False or valid == False): #read miss
                miss = True
                aligned_addr = (addr+i) - ((addr+i) % self.bl_size)
                if (self.addr_to_tag(aligned_addr)[1] == set_idx): #its possible for an address (not a power of 2) to index into diff set once aligned
                    missed_blocks.add(aligned_addr)

        blocks_accessed = set() #for cache hits we still need to update lru queue          
        if (len(missed_blocks) > 0 or miss == True): #if cache misses, just read directly from memory
            output_data = self.memory.read(addr, size)
            hit_status = False
            self.cycle_count += self.read_mem_cycles
            self.misses += 1
        
        else: #if cache hit, read data from cache
            self.cycle_count += self.hit_cycles
            self.hits += 1
            output_data = []
            hit_status = True
            for i in range(0, size):
                bit_data = self.addr_to_tag(addr+i)
                tag = bit_data[0]
                set_idx = bit_data[1]
                bl_offset = bit_data[2]

                bl_sel = None
                for j, v in enumerate(self.cache_tags[set_idx]):
                    if tag == v:
                        bl_sel = j
                        break
                
                blocks_accessed.add((set_idx, bl_sel))
                byte_data = self.cache_data[set_idx][bl_sel][bl_offset]
                output_data.append(byte_data)
            
            for i in blocks_accessed:
                if self.lru_queue[i[0]].__contains__(i[1]):
                    self.lru_queue[i[0]].remove(i[1])
                    self.lru_queue[i[0]].append(i[1])
                else:
                    self.lru_queue[i[0]].append(i[1])

        for i in missed_blocks: #i is an address
            read_data = self.memory.read(i, self.bl_size)
            bit_data = self.addr_to_tag(i)
            tag = bit_data[0]
            set_idx = bit_data[1]
            bl_offset = bit_data[2]
            block_sel = self.block_replacement(i, set_idx)
            self.cache_data[set_idx][block_sel] = read_data
            self.cache_tags[set_idx][block_sel] = tag
            self.valid[set_idx][block_sel] = 1
        return (output_data, hit_status)
    
    
    def block_repl_writes(self, addr, set_idx, bl_num):
        if self.wr_policy == "write-back":
            dirty_bit = self.dirty[set_idx][bl_num]
            if dirty_bit == 1:
                data = self.cache_data[set_idx][bl_num]
                tag = self.cache_tags[set_idx][bl_num]
                new_addr = self.tag_to_addr(tag, set_idx, 0)
                self.memory.write(new_addr, data, len(data))
                self.dirty[set_idx][bl_num] = 0

                self.cycle_count += self.write_mem_cycles
        elif self.wr_policy == "write-through":
            return None
        return None
 
    def write_hit(self, addr, data): #only call if there is a cache hit.
        blocks_accessed = set()
        if self.wr_policy == "write-through":
            self.cycle_count += self.write_mem_cycles
            self.memory.write(addr, data, len(data))
            for i in range(0, len(data)):
                bit_data = self.addr_to_tag(addr+i)
                tag = bit_data[0]
                set_idx = bit_data[1]
                bl_offset = bit_data[2]

                block = None
                for j, v in enumerate(self.cache_tags[set_idx]):
                    if v == tag:
                        block = j
                        break

                blocks_accessed.add((set_idx, block))
                self.cache_data[set_idx][block][bl_offset] = data[i]
                self.valid[set_idx][block] = 1
                self.cache_tags[set_idx][block] = tag

        elif self.wr_policy == "write-back":
            self.cycle_count += self.hit_cycles

            for i in range(0, len(data)):
                bit_data = self.addr_to_tag(addr+i)
                tag = bit_data[0]
                set_idx = bit_data[1]
                bl_offset = bit_data[2]

                block = None
                for j, v in enumerate(self.cache_tags[set_idx]):
                    if v == tag:
                        block = j
                        break
                
                blocks_accessed.add((set_idx, block))
                self.cache_data[set_idx][block][bl_offset] = data[i]
                self.valid[set_idx][block] = 1
                self.cache_tags[set_idx][block] = tag
                self.dirty[set_idx][block] = 1

        for i in blocks_accessed:
            if self.lru_queue[i[0]].__contains__(i[1]):
                self.lru_queue[i[0]].remove(i[1])
                self.lru_queue[i[0]].append(i[1])
            else:
                self.lru_queue[i[0]].append(i[1])


    def write(self, addr, data, size): #data should be list
        missed_blocks = set() #no duplicates
        miss = False
        block = {}
        for i in range(0, size):
            bit_data = self.addr_to_tag(addr+i)
            tag = bit_data[0]
            set_idx = bit_data[1]
            bl_offset = bit_data[2]
            
            block_sel = None
            tag_match = False
            for j, v in enumerate(self.cache_tags[set_idx]):
                if v == tag:
                    block_sel = j
                    tag_match = True
                    break

            if (block_sel == None):
                valid = False
            else:   
                valid = (self.valid[set_idx][block_sel] == 1)

            if (tag_match == False or valid == False): #write miss
                aligned_addr = (addr+i) - ((addr+i) % self.bl_size)
                miss = True
                if (self.addr_to_tag(aligned_addr)[1] == set_idx): #its possible for an address (not a power of 2) to index into diff set once aligned
                    missed_blocks.add(aligned_addr)
            else:
                aligned_addr = (addr+i) - ((addr+i) % self.bl_size) #need to add this bc: it's possible for a cache write to hit on 1 block and miss on another
                block[aligned_addr] = block_sel

        for i in missed_blocks: #i is an address
            if self.wr_alloc == "write-allocate": #write allocate requires block replacement
                bit_data = self.addr_to_tag(i)
                tag = bit_data[0]
                set_idx = bit_data[1]
                bl_offset = bit_data[2]

                block_sel = self.block_replacement(i, set_idx)
                block[i] = block_sel
                data = self.memory.read(i, self.bl_size)
                self.cache_data[set_idx][block_sel] = data
                self.cache_tags[set_idx][block_sel] = tag
                self.valid[set_idx][block_sel] = 1

        if (len(missed_blocks) > 0 or miss == True): # we have a write miss
            if self.wr_alloc == "write-allocate": #write data to cache
                for i in range(0, size):
                    bit_data = self.addr_to_tag(addr+i)
                    tag = bit_data[0]
                    set_idx = bit_data[1]
                    bl_offset = bit_data[2]
                    aligned_addr = (addr+i) - ((addr+i) % self.bl_size)
                    block_sel = block[aligned_addr]

                    self.cache_data[set_idx][block_sel][bl_offset] = data[i]
                    self.cache_tags[set_idx][block_sel] = tag
                    self.valid[set_idx][block_sel] = 1

            #all cases of miss
            self.memory.write(addr, data, size)

            self.cycle_count += self.write_mem_cycles
            self.misses += 1
            return False
        
        else: #hit
            self.hits += 1
            self.write_hit(addr, data) #cycle count updated in write_hit
            return True

                
class memory():
    def __init__(self) -> None:
        self.cap = 100000
        self.mem_data = np.zeros(self.cap, dtype=object)

    def view(self, start, end):
        return self.mem_data[start:end]
    
    def capacity(self):
        return self.cap
    
    def flush(self):
        self.mem_data = np.zeros(self.cap, dtype=object)

    def write(self, addr, data, size):
        for i, v in enumerate(data):
            self.mem_data[addr+i] = v
        return None
    
    def read(self, addr, size): #size in bytes
        data = []
        for i in range(0, size):
            data.append(self.mem_data[addr+i])
        return data

