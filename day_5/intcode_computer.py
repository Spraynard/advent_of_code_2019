'''
Intcode program is a list of integers separated by commas.

 Integer Position 0 --> opcode
 Either 1, 2, or 99. Indicates what to do.

99 	- 	Exit. Program is finished and should immediately halt.

1  	-  	Add. adds together numbers read from two positions and stores the result
      	in a third position. The three integers *immediately after* the opcode tell
      	you these three positions. The first two indicate the *positions* from which
      	you should read the input values. The third indicates the *position* at which
      	the *output* should be stored.

2  	-  	Multiply. Works like opcode 1, except it multiplies instead of adds.

3  	-  	Input. Takes a single integer as input and saves it to the address given by its only
      	parameter. The instruction 3,50 would take an input value and store it at
      	address 50.

4  	-  	Output. Outputs the value of its only paramester. The instruction 4,50 would output
      	the value at address 50.

5	-	jump-if-true. If the first parameter is *non-zero*, it sets the instruction pointer to the value from the second parameter.
		otherwise does nothing.

6	-	jump-if-false. If the first parameter is *zero*, it sets the instruction pointer to the value from the second parameter.
		Otherwise does nothing.

7	-	less than. If the first parameter is less than the second parameter, it stores 1 in the position given by the third parameter.
		Otherwise, it stores *0*

8	-	equals. If the first parameter is equal to the second parameter, it stores 1 in the position given by the third parameter.
		Otherwise, it stores *0*

Once done processing an opcode, move the instruction pointer forward
as many times as there are instruction values in the instruction.

This is true unless we perform certain instructions, such as that of opcode
5 and 6 (jump-if-true, jump-if-false, respectively). These instructions move the pointer
and skip over any automatic pointer increases.

PARAMETER MODES:
    * 0 - Position Mode. Denotes we interpret a parameter as the position of
          the value that we want to interpret.
    * 1 - Immediate Mode. Denotes we want to interpret the parameter as a value

Parameter modes are stored in the same value as the instruction's opcode.
The opcode is the rightmost two digits of the first value in an instruction.

Parameter modes are single digits, one per parameter, read right to left from
the opcode. The first parameter's mode is in the hundreds digit, the second is in the thousands digit, and the third parameter is in the ten-thousands digit. Any missing nodes are 0.

Example
ABCDE
 1002

DE - Two Digit Opcode,          02 == opcode 2
 C - Mode of first parameter,    0 == position mode
 B - Mode of second parameter,   1 == immediate mode
 A - Mode of third parameter,    0 == position mode,
                                      omitted due to being a leading zero.
=================================================================

Intcodes model a computer's memory. Be sure and initialize memory to the program's values when you start.

A position in memory is called an address (for example, the first value in memory is at "address 0").

Opcodes (like 1, 2, or 99) mark the beginning of an instruction. The values used immediately after an opcode, if any, are called the instruction's parameters. For example, in the instruction 1,2,3,4, 1 is the opcode; 2, 3, and 4 are the parameters. The instruction 99 contains only an opcode and has no parameters.

The address of the current instruction is called the instruction pointer; it starts at 0. After an instruction finishes, the instruction pointer increases by the number of values in the instruction; until you add more instructions to the computer, this is always 4 (1 opcode + 3 parameters) for the add and multiply instructions. (The halt instruction would increase the instruction pointer by 1, but it halts the program instead.)
'''
# Constants
OPCODE_ADDITION=1
OPCODE_MULTIPLICATION=2
OPCODE_INPUT=3
OPCODE_PRINT=4
OPCODE_JUMP_IF_TRUE=5
OPCODE_JUMP_IF_FALSE=6
OPCODE_LESS_THAN=7
OPCODE_EQUALS=8

PARAMETER_MODE_POSITION=0
PARAMETER_MODE_IMMEDIATE=1


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

# Process performed when we evaluate opcode: 3
def get_input( array, value ):
    '''
    Obtains user input and puts it in the address
    denoted by value
    '''
    user_input = input("> ")

    if 0 <= value < len(array):
        array[value] = user_input

    return True

def do_output( array, value):
    print(">> {value}".format(value=value))
    return True

def get_parameter_modes( parameter_modes_string ):
    mode_1 = parameter_modes_string[-1:]
    mode_2 = parameter_modes_string[-2:-1]
    mode_3 = parameter_modes_string[-3:-2]

    return (
            int(mode_1) if mode_1 else PARAMETER_MODE_POSITION,
            int(mode_2) if mode_2 else PARAMETER_MODE_POSITION,
            int(mode_3) if mode_3 else PARAMETER_MODE_POSITION
            )

def perform_mathematic_instruction( eval_fn, array, pointer, modes):
    '''
    Currently handles all the operations required
    for add and multiply procedures to work
    '''
    mode_1, mode_2, mode_3 = modes
    parameter_1 = int(array[pointer + 1])
    parameter_2 = int(array[pointer + 2])
    val_1, val_2 = (None, None)

    # Parameter 3
    group_store_location = int(array[pointer + 3])

    if mode_1 == PARAMETER_MODE_IMMEDIATE:
        val_1 = parameter_1
    elif 0 <= parameter_1 < len(array):
        val_1 = int(array[parameter_1])

    if mode_2 == PARAMETER_MODE_IMMEDIATE:
        val_2 = parameter_2
    elif 0 <= parameter_2 < len(array):
        val_2 = int(array[parameter_2])

    if val_1 == None or val_2 == None:
        raise Exception("perform_mathematic_instruction(): One of your values is not defined. Value_1: {val_1} | Value_2: {val_2}".format(val_1=val_1,val_2=val_2))

    evaluated = eval_fn(val_1, val_2)

    if mode_3 == 1:
        raise Exception("perform_mathematic_instruction(): Mode three is in immediate. Not really sure what to do with that.")

    # Assign the evaluated value to the group_store_location
    if 0 <= group_store_location <= (len(array) - 1):
        array[group_store_location] = str(evaluated)

    return True

def perform_io_instruction( eval_fn, array, pointer, modes ):
    '''
    input/output based instructions. This means we will either take in input
    or give out output, or both.
    '''
    mode_1, mode_2, mode_3 = modes

    param = int(array[pointer + 1])

    if int(mode_1) == PARAMETER_MODE_IMMEDIATE:
        value = param
    elif 0 <= param  <= (len(array) - 1):
        value = int(array[param])
    '''
    Return the evaluated function and the value as I need the value to be able
    to store an input value
    '''
    return eval_fn(array, value)

def perform_instruction( opcode, eval_fn, array, pointer, modes ):
    if opcode == OPCODE_ADDITION or opcode == OPCODE_MULTIPLICATION:
        return perform_mathematic_instruction(eval_fn, array, pointer, modes)
    elif opcode == OPCODE_INPUT or opcode == OPCODE_PRINT:
        return perform_io_instruction(eval_fn, array, pointer, modes)
    else:
        raise Exception("perform_instruction(): Unknown Instruction Opcode")


def process_intcode( intcode ):
    '''
    Take in an intcode string and return the processed output
    as another intcode string
    '''

    # Defining our opcode group specific variables
    instruction_pointer = 0 # Position of our current opcode
    intcode_array = [val for val in intcode.split(",")]

    while True:
        instruction_options = str(intcode_array[instruction_pointer])
        # From 0 to 3 parameter modes given.
        parameter_modes = instruction_options[:-2]
        # Casting opcode to an int will remove the leading zero if necessary.
        opcode = int(instruction_options[-2:])
        # Evaluate our instruction opcodes
        if opcode == OPCODE_ADDITION:
            opcode_eval_function = add
            instruction_values = 4
        elif opcode == OPCODE_MULTIPLICATION:
            opcode_eval_function = mul
            instruction_values = 4
        elif opcode == OPCODE_INPUT:
            opcode_eval_function = get_input
            instruction_values = 2
        elif opcode == OPCODE_PRINT:
            opcode_eval_function = do_output
            instruction_values = 2
		elif opcode == OPCODE_JUMP_IF_TRUE:
			opcode_eval_function = is_true
			instruction_values = 3 # not like it matters
		elif opcode == OPCODE_JUMP_IF_FALSE:
			opcode_eval_function = is_false
			instruction_values = 3 # not like it matters
		elif opcode == OPCODE_LESS_THAN:
			opcode_eval_function = is_less_than
			instruction_values = 4
		elif opcode == OPCODE_EQUALS:
			opcode_eval_funtion = is_equal_to
			instruction_values = 4
        elif opcode == 99: # Halts processing of our intcode string
            break

        try:
            instruction_value = perform_instruction( opcode, opcode_eval_function, intcode_array, instruction_pointer, get_parameter_modes(parameter_modes) )
        except Exception as e:
            print("Error Occurred")
            print(e)

        # Move our pointer up as many positions as instruction values
        instruction_pointer += instruction_values

    return ",".join([str(val) for val in intcode_array])

if __name__ == '__main__':
    # Run some tests before we get to the meat and potatoes.
	assertEquals("2,0,0,0,99", process_intcode("1,0,0,0,99"))
	assertEquals("2,3,0,6,99", process_intcode("2,3,0,3,99"))
	assertEquals("2,4,4,5,99,9801", process_intcode("2,4,4,5,99,0"))
	assertEquals("30,1,1,4,2,5,6,0,99", process_intcode("1,1,1,4,99,5,6,0,99"))

	input_file = open('input.txt','r')

	with input_file:
		input_intcode = input_file.read()
		process_intcode(input_intcode)