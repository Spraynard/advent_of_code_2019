'''
Intcode program is a list of integers separated by commas.

 Integer Position 0 --> opcode
 Either 1, 2, or 99. Indicates what to do.

99 - Program is finished and should immediately halt.
1  -  adds together numbers read from two positions and stores the result
      in a third position. The three integers *immediately after* the opcode tell
      you these three positions. The first two indicate the *positions* from which
      you should read the input values. The third indicates the *position* at which
      the *output* should be stored.
2  -  Works like opcode 1, except it multiplies instead of adds.

Once done processing an opcode, move to the next one by stepping
forward 4 positions
=================================================================

Intcodes model a computer's memory. Be sure and initialize memory to the program's values when you start.

A position in memory is called an address (for example, the first value in memory is at "address 0").

Opcodes (like 1, 2, or 99) mark the beginning of an instruction. The values used immediately after an opcode, if any, are called the instruction's parameters. For example, in the instruction 1,2,3,4, 1 is the opcode; 2, 3, and 4 are the parameters. The instruction 99 contains only an opcode and has no parameters.

The address of the current instruction is called the instruction pointer; it starts at 0. After an instruction finishes, the instruction pointer increases by the number of values in the instruction; until you add more instructions to the computer, this is always 4 (1 opcode + 3 parameters) for the add and multiply instructions. (The halt instruction would increase the instruction pointer by 1, but it halts the program instead.)
'''
import sys

def assertEquals( target, guess ):
    '''
    Assert that the guess equals the value of the target
    '''

    if not guess == target:
        print('''
Unsuccessful...

Guess: {guess}
Target: {target}
'''.format( guess=guess, target=target))
        return False
    print("Test is good")
    return True 

# Process performed when we evaluate opcode: 1
def add( value1, value2 ):
    return value1 + value2

# Process performed when we evaluate opcode: 2
def mul( value1, value2):
    return value1 * value2

def process_intcode( intcode ):
    '''
    Take in an intcode string and return the processed output
    as another intcode string
    '''

    # Defining our opcode group specific variables
    instruction_pointer = 0 # Position of our current opcode
    intcode_array = [int(val) for val in intcode.split(",")]

    while True:
        opcode = intcode_array[instruction_pointer]
        
        # Evaluate our instruction opcodes
        if opcode == 1:
            opcode_eval_function = add
            instruction_values = 4
        elif opcode == 2:
            opcode_eval_function = mul
            instruction_values = 4
        elif opcode == 99: # Halts processing of our intcode string
            break
        # Address of first num in memory
        instruction_parameter_1 = intcode_array[instruction_pointer + 1]

        # Address of second num in memory
        instruction_parameter_2 = intcode_array[instruction_pointer + 2]

        # Address of memory storage
        group_store_location = intcode_array[instruction_pointer + 3]

        # value at instruction_parameter_1
        if 0 <= instruction_parameter_1 <= (len(intcode_array) - 1):
            val_1 = intcode_array[instruction_parameter_1]

        if 0 <= instruction_parameter_2 <= (len(intcode_array) - 1):
            val_2 = intcode_array[instruction_parameter_2]

        evaluated = opcode_eval_function(val_1, val_2)

        # Assign the evaluated value to the group_store_location
        if 0 <= group_store_location <= (len(intcode_array) - 1):
            intcode_array[group_store_location] = evaluated

        # Move our pointer up four positions to consider the next opcode group
        instruction_pointer += instruction_values
    
    return ",".join([str(val) for val in intcode_array])

if __name__ == '__main__':
    # Run some tests before we get to the meat and potatoes.
    assertEquals("2,0,0,0,99", process_intcode("1,0,0,0,99"))
    assertEquals("2,3,0,6,99", process_intcode("2,3,0,3,99"))
    assertEquals("2,4,4,5,99,9801", process_intcode("2,4,4,5,99,0"))
    assertEquals("30,1,1,4,2,5,6,0,99", process_intcode("1,1,1,4,99,5,6,0,99"))

    input_intcode_file = open('input.txt', 'r')

    with input_intcode_file:
        input_intcode = input_intcode_file.read()
        verb = 0
        noun = 0
        output = 0

        while True:
            initialized = [int(val) for val in input_intcode.split(",")]
            initialized[1] = noun
            initialized[2] = verb

            processed_intcode = process_intcode(",".join([str(val) for val in initialized]))
            output = [int(val) for val in processed_intcode.split(",")][0]
            print(output)
            if output == 19690720:
                break;

            verb += 1

            if verb == 100:
                verb = 0
                noun += 1


    '''
    What are the verb and noun values that produce the output 19690720
    '''
    answer = 100 * noun + verb
    print(f"Noun: {noun} Verb: {verb}")
    print(f"100 * noun + verb = {answer}")
