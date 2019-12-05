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

Once you have a working computer, the first step is to restore the gravity assist program (your puzzle input) to the "1202 program alarm" state it had just before the last computer caught fire. To do this, before running the program, replace position 1 with the value 12 and replace position 2 with the value 2. What value is left at position 0 after the program halts?
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
    opcode, group_pos_1, group_pos_2, group_store_location = (None, None, None, None)
    opcode_position = 0 # Position of our current opcode
    opcode_eval_function = None
    intcode_array = [int(val) for val in intcode.split(",")]

    while not opcode == 99:
        opcode = intcode_array[opcode_position]

        # Evaluate our opcodes
        if opcode == 1:
            opcode_eval_function = add
        elif opcode == 2:
            opcode_eval_function = mul
        elif opcode == 99: # Halts processing of our intcode string
            continue
        
        group_pos_1 = intcode_array[opcode_position + 1]
        group_pos_2 = intcode_array[opcode_position + 2]
        group_store_location = intcode_array[opcode_position + 3]

        # value at group_pos_1
        if 0 <= group_pos_1 <= (len(intcode_array) - 1):
            val_group_pos_1 = intcode_array[group_pos_1]

        if 0 <= group_pos_2 <= (len(intcode_array) - 1):
            val_group_pos_2 = intcode_array[group_pos_2]

        evaluated = opcode_eval_function(val_group_pos_1, val_group_pos_2)

        # Assign the evaluated value to the group_store_location
        if 0 <= group_store_location <= (len(intcode_array) - 1):
            intcode_array[group_store_location] = evaluated

        # Move our pointer up four positions to consider the next opcode group
        opcode_position += 4
    
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

        '''
        Transform our input_intcode as specified in the instructions:
            Replace position 1 with the value 12
            Replace position 2 with the value 2
        '''

        pre_run_intcode_array = [int(val) for val in input_intcode.split(",")]
        pre_run_intcode_array[1] = 12
        pre_run_intcode_array[2] = 2

        processed_intcode = process_intcode(",".join([str(val) for val in pre_run_intcode_array]))

        '''
        What value is left at position 0 after the program halts?
        '''
        print(processed_intcode)
