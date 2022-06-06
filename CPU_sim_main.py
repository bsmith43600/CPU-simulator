
# Create class for memory designated to hold instructions. For this purposes of this simulation, instructions are being held
# in a separate place from data.

class MainMemory:
    def __init__(self):
        # mem_list represents a memory array. Each entry is meant to represent 1 byte of data memory > index 20 will be allocated for stored data indexes < 500 will be for instructions
        self.mem_list = [None] * 1000
        self.next_mem_address = 0

    def load_instructions_to_memory(self, instructions):
        global label_dict
        # Break text file into individual lines. Each line in file should be a single command in MIPS format
        lines = instructions.readlines()
        for line in lines:
            # Remove line comments
            line = line.split('#')[0]

            if ':' in line:
                [label, line] = line.split(':')
                label_dict[label] = self.next_mem_address


            # Trim excess spaces or characters from input line
            line = line.strip()

            # If there is nothing left after removing comment and excess space, then line contains no code, skip to next loop
            if line == '':
                continue

            
            
            # Collect opcode from line by taking all characters before the first space in string
            space_idx = line.find(' ')
            opcode = line[:space_idx]

            # Collect operands from remainder of string by delimiting with ','
            operands = line[space_idx:].split(',')
            
            for idx in range(0,4):

                if idx == 0:
                    # Save opcode to first address in memory word
                    self.mem_list[self.next_mem_address] = opcode
                else:
                    
                    # Save operands to remaining addresses in word
                    try:
                        self.mem_list[self.next_mem_address] = operands[idx - 1].strip()
                    
                    # If instruction has fewer than 3 operands, store a None to maintain word alignment
                    except:
                        pass
                
                self.next_mem_address += 1

        
        pass

class Register:
    def __init__(self):
        self.data = [None]*32
        self.data[0] = 0

        # Build and populate the list of register codes, to their relevant location in a lookup list
        self.register_name_code_list = ['$zero', '$at', '$v0', '$v1', '$a0', '$a1', '$a2', '$a3']
        for x in range(0, 8):
            self.register_name_code_list.append('$t' + str(x))
        for x in range(0, 8):
            self.register_name_code_list.append('$s' + str(x))
        
        self.register_name_code_list += ['$t8', '$t9', '$k0', '$k1', '$gp', '$sp', '$fp', '$ra']

    def retrieve_data(self, register_code):
        
        if register_code is None:
            return None

        # If constant is fed in, return constant
        if '$' not in register_code:
            return int(register_code)
        
        return self.data[self.register_name_code_list.index(register_code)]

#    def write_data(self, register_code, data):
#        self.data[self.register_name_code_list.index(register_code)] = data


def execute_instructions(instructions):
    global data_register
    global memory_address
    global label_dict

    # Initiate program counter to track steps held in instructions
    program_counter = 0

    # Loop until program_counter exceeds 20... instructions cannot be > index 20
    while main_memory.mem_list[program_counter] is not None:
        print('\n')
        print('Executing MIPS line {}'.format(int(program_counter/4+1)))
        current_instruction = instructions[program_counter:program_counter+4]


        opcode = current_instruction[0]
        opr1 = current_instruction[1]
        opr2 = current_instruction[2]
        opr3 = current_instruction[3]

        print('Executing {} operation on operands {}, {}, and {}'.format(opcode, opr1, opr2, opr3))

        # Special execution for load word opcode
        if opcode == 'lw':
            # For load word function, opr2 should have offset format. Use following lines to parse offset format
            [offset, register_code] = opr2.split('(')
            register_code = register_code[:register_code.find(')')]

            # Use ALU 'add' operation to add offset to data saved at "register_code" and save data to the memory_address special register
            ALU('add', 'mem_add', reg.retrieve_data(offset), reg.retrieve_data(register_code))

            # Pull data from memory address, save to data_register - because this simulation does not use binary data broken into bytes it is not necessary
            # to concatenate multiple data addresses to form word
            data_register = main_memory.mem_list[memory_address]

            # Write data now stored in data_register to register indicated by opr1
            reg.data[reg.register_name_code_list.index(opr1)] = data_register

            print('Loading word "{}" into register {} from memory address {}.'.format(data_register, opr1, memory_address))

        elif opcode == 'sw':
            # For store word function, opr2 should have offset format. Use following lines to parse offset format
            [offset, register_code] = opr2.split('(')
            register_code = register_code[:register_code.find(')')]

            # Use ALU 'add' operation to add offset to data saved at "register_code" and save data to the memory_address special register
            ALU('add', 'mem_add', reg.retrieve_data(offset), reg.retrieve_data(register_code))

            # Store the data from opr1 into data register
            data_register = reg.data[reg.register_name_code_list.index(opr1)] 

            # Store data now stored in data register to address stored in memory_address
            main_memory.mem_list[memory_address] = data_register

            print('Saving word "{}" into memory address {}'.format(data_register, memory_address))

        elif opcode == 'bne':
            # Use subtraction to determine if inputs are equal, store result in the data
            ALU('sub', '$t8', reg.retrieve_data(opr1), reg.retrieve_data(opr2))

            if reg.retrieve_data('$t8') != 0:
                print('{} is NOT equal to {}, branching to {}'.format(reg.retrieve_data(opr1), reg.retrieve_data(opr2), opr3))
                program_counter = label_dict[opr3]
                continue
            print('{} IS equal to {} proceeding to next line of code'.format(reg.retrieve_data(opr1), reg.retrieve_data(opr2)))
        
        elif opcode == 'beq':
            # Use subtraction to determine if inputs are equal, store result in the data
            ALU('sub', '$t8', reg.retrieve_data(opr1), reg.retrieve_data(opr2))

            if reg.retrieve_data('$t8') == 0:
                print('{} IS equal to {}, branching to {}'.format(reg.retrieve_data(opr1), reg.retrieve_data(opr2), opr3))
                program_counter = label_dict[opr3]
                continue
            print('{} is NOT equal to {} proceeding to next line of code'.format(reg.retrieve_data(opr1), reg.retrieve_data(opr2)))

        elif opcode == 'j':
            print('Jumping to {}'.format(opr1))
            program_counter = label_dict[opr1]
            continue



        else:
        # Pass the opcode, destination register and data from the operand into ALU
            ALU(opcode, opr1, reg.retrieve_data(opr2), reg.retrieve_data(opr3))


        # Instruction words use a total of 4 memory addresses increment by 4 to reach the start of the next instruction
        program_counter += 4
        if instructions[program_counter] == None:
            break

def ALU(opcode, dest_reg, data1, data2):
    global memory_address
    # Different logic is not used for different versions of ADD
    if opcode[:3] == 'add':
        output = data1 + data2
    elif opcode[:3] == 'sub':
        output = data1 - data2
    elif opcode[:3] == 'mul':
        output = data1 * data2
    elif opcode[:3] == 'div':
        output = data1 / data2

    # If function calls for result to be written to the memory address register
    if dest_reg == 'mem_add':
        print('Saving {} to the memory address register'.format(output))
        memory_address = output
    else:
        print('Saving {} to register {}'.format(output, dest_reg))
        reg.data[reg.register_name_code_list.index(dest_reg)] = output


#############################################################################################################
###### Start of main program
#############################################################################################################


memory_address = None
data_register = None


# Instantiate main_memory
main_memory = MainMemory()

# Instantiate register
reg = Register()

# Instantiate label_dict
label_dict = {}


# Load instructions to main_memory
with open('mips_instructions.txt') as instructions:
    main_memory.load_instructions_to_memory(instructions)
    


# Pass instruction list into CU for execution
execute_instructions(main_memory.mem_list)

i = 500
while i < 517:
    print('Memory address {} holds a value of {}'.format(i, main_memory.mem_list[i]))
    i += 1