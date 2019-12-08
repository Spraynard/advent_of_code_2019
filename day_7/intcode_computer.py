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
import traceback
from assertions import assertEquals
from enum import IntEnum
from collections import deque

# Constants
class Opcode(IntEnum):
	ADDITION=1
	MULTIPLICATION=2
	INPUT=3
	OUTPUT=4
	JUMP_IF_TRUE=5
	JUMP_IF_FALSE=6
	LESS_THAN=7
	EQUALS=8
	HALT=99


class Mode(IntEnum):
	POSITION = 0
	IMMEDIATE = 1


# Process performed when we evaluate opcode: 1
def add( value1, value2 ):
	return value1 + value2

# Process performed when we evaluate opcode: 2
def mul( value1, value2):
	return value1 * value2

def is_true( parameter ):
	return parameter != 0

def is_false( parameter ):
	return parameter == 0

def is_less_than( parameter_1, parameter_2 ):
	return parameter_1 < parameter_2

def is_equal_to( parameter_1, parameter_2 ):
	return parameter_1 == parameter_2

def build_intcode(intcode_array):
	return ",".join([str(val) for val in intcode_array])

def build_intcode_array(intcode):
	return [val for val in intcode.split(",")]

class IntcodeComputer:
	'''
	@param str instructions 	- Memory state required to run the computer.
	@param bool program_input	- Modifier for Opcode.INPUT instructions.
								  Flags whether we gain input from users or from input queue.
								  Allows for programmatic behavior of input.
	@param bool program_output 	- Modifier for Opcode.OUTPUT instructions.
								  Flags whether we output to stdout or as a return value from our API.
	@param bool persistence 	- Global Modifier.
								  Flags whether we persist changes to memory after a run of processing.
	@param bool test			- Global Modifier.
								  Flag that denotes whether or not we are testing the output of our computer.
								  If so ,then we want to compare an intcode string to another intcode string after processing.
								  If not, just signal the end of processing.
	@param bool debug 			- Output some verbose information
	'''
	def __init__(self, instructions, program_input=False, program_output=False, persistence=False, test=False, debug=False):
		self.instructions = instructions
		self.input_queue = None
		self.persistence = persistence
		self.program_input = program_input
		self.program_output = program_output
		self.debug = debug
		self.test = test
		self.instruction_pointer = 0
		self.process_count = 0

	def set_persistence(self, value):
		self.persistence = value

	def set_input_queue(self, input_items):
		self.input_queue = deque(input_items)
		return True

	# Process performed when we evaluate opcode: 3
	def get_input( self, array, value ):
		'''
		Obtains user input and puts it in the address
		denoted by value
		'''
		if self.debug:
			print(f"Input Queue: {self.input_queue}")

		user_input = input("> ") if self.program_input is False else str(self.input_queue.popleft())

		if 0 <= value < len(array):
			array[value] = user_input

		return array

	def do_output( self, array, value):
		'''
		Outputs the given value
		'''
		if self.program_output:
			return value

		print(">> {value}".format(value=value))
		return True


	def get_parameter_modes(self, parameter_modes_string ):
		'''
		Method used to abstract obtaining parameter modes from a parameter modes string.
		Returns a length three tuple containing each of the parameter modes for the current instruction.
		'''
		mode_1 = parameter_modes_string[-1:]
		mode_2 = parameter_modes_string[-2:-1]
		mode_3 = parameter_modes_string[-3:-2]

		return ( int(mode_1) if mode_1 else Mode.POSITION, int(mode_2) if mode_2 else Mode.POSITION, int(mode_3) if mode_3 else Mode.POSITION )

	def perform_mathematic_instruction(self, eval_fn, array, pointer, modes):
		'''
		Currently handles all the operations required
		for add and multiply procedures to work
		'''
		mode_1, mode_2, mode_3 = modes
		parameter_1 = int(array[pointer + 1])
		parameter_2 = int(array[pointer + 2])

		# Parameter 3
		group_store_location = int(array[pointer + 3])

		val_1 = parameter_1 if mode_1 else int(array[parameter_1])
		val_2 = parameter_2 if mode_2 else int(array[parameter_2])
		# print(f"evaluating Value 1: {val_1} and Value 2: {val_2}")
		evaluated = eval_fn(val_1, val_2)

		if mode_3 == Mode.IMMEDIATE:
			raise Exception("perform_mathematic_instruction(): Mode three is in immediate. Not really sure what to do with that.")

		# Assign the evaluated value to the group_store_location
		if 0 <= group_store_location < len(array):
			array[group_store_location] = str(evaluated)

		return True

	def perform_io_instruction(self, eval_fn, array, pointer, modes ):
		'''
		input/output based instructions. This means we will either take in input
		or give out output, or both.
		'''


	def perform_input_instruction(self, eval_fn, array, pointer ):
		param = int(array[pointer + 1])
		return eval_fn(array, param)

	def perform_print_instruction(self, eval_fn, array, pointer, modes ):
		mode_1 = modes[0]

		param = int(array[pointer + 1])
		value = param if mode_1 else int(array[param])
		'''
		Return the evaluated function
		'''
		return eval_fn(array, value)

	def perform_jump_instruction(self, eval_fn, array, pointer, modes):
		'''
		For either of the jump instructions. If we get a truthy value from our
		eval_fn, then we can use that as the `if-false` `if-true` portion of the
		the instruction
		'''
		mode_1, mode_2 = modes[:2]

		param_1 = int(array[pointer + 1])
		param_2 = int(array[pointer + 2])

		value_1 = param_1 if mode_1 else int(array[param_1])
		value_2 = param_2 if mode_2 else int(array[param_2])

		# If our jump-if function does not denote that we should
		# jump, then tell our main process function not to jump
		# by returning none
		if not eval_fn( value_1 ):
			value_2 = None

		return value_2


	def perform_comparative_instruction(self, eval_fn, array, pointer, modes):
		'''
		Compares two values and then stores a zero or a one (depending on the return of the eval_fn) in the
		address given by the third value
		'''
		mode_1, mode_2 = modes[:2]

		param_1 = int(array[pointer + 1])
		param_2 = int(array[pointer + 2])
		param_3 = int(array[pointer + 3])

		value_1 = param_1 if mode_1 else int(array[param_1])
		value_2 = param_2 if mode_2 else int(array[param_2])
		value_3 = param_3 # Guaranteed to be an address to store the value at

		array[value_3] = '0'

		if eval_fn(value_1, value_2):
			array[value_3] = '1'

		return True

	def perform_instruction( self, opcode, eval_fn, array, pointer, modes ):
		'''
		Procedure that basically acts as a controller for all instructions that are available within the system.
		Based on the opcode, we will direct our other input to other procedures that perform the specific operation we want
		'''
		if opcode == Opcode.ADDITION or opcode == Opcode.MULTIPLICATION:
			return self.perform_mathematic_instruction(eval_fn, array, pointer, modes)
		elif opcode == Opcode.INPUT:
			return self.perform_input_instruction(eval_fn, array, pointer)
		elif opcode == Opcode.OUTPUT:
			return self.perform_print_instruction(eval_fn, array, pointer, modes)
		elif opcode == Opcode.JUMP_IF_FALSE or opcode == Opcode.JUMP_IF_TRUE:
			return self.perform_jump_instruction(eval_fn, array, pointer, modes)
		elif opcode == Opcode.LESS_THAN or opcode == Opcode.EQUALS:
			return self.perform_comparative_instruction(eval_fn, array, pointer, modes)
		else:
			raise Exception(f"perform_instruction(): Unknown Instruction Opcode Given: {opcode}")



	def process_intcode(self):
		'''
		Take in an intcode string and return the processed output
		as another intcode string
		'''
		# Defining our opcode group specific variables
		intcode_array = [val for val in self.instructions.split(",")]

		if self.debug:
			if self.persistence:
				print("Intcode Array")
				print(intcode_array)
		while True:
			instruction_options = str(intcode_array[self.instruction_pointer])
			# From 0 to 3 parameter modes given.
			parameter_modes = instruction_options[:-2]
			# Casting opcode to an int will remove the leading zero if necessary.
			opcode = Opcode(int(instruction_options[-2:]))
			if self.debug:
				print(f"Opcode: {opcode}")
				print(intcode_array)
# 				print('''
# ============================================================
# Opcode: {opcode}
# Intcode Array: {intcode_array}
# ============================================================
# 	'''.format(opcode=opcode,intcode_array=intcode_array))

			# Evaluate our instruction opcodes
			if opcode == Opcode.ADDITION:
				opcode_eval_function = add
				instruction_values = 4
			elif opcode == Opcode.MULTIPLICATION:
				opcode_eval_function = mul
				instruction_values = 4
			elif opcode == Opcode.INPUT:
				opcode_eval_function = self.get_input
				instruction_values = 2
			elif opcode == Opcode.OUTPUT:
				opcode_eval_function = self.do_output
				instruction_values = 2
			elif opcode == Opcode.JUMP_IF_TRUE:
				opcode_eval_function = is_true
				instruction_values = 3
			elif opcode == Opcode.JUMP_IF_FALSE:
				opcode_eval_function = is_false
				instruction_values = 3
			elif opcode == Opcode.LESS_THAN:
				opcode_eval_function = is_less_than
				instruction_values = 4
			elif opcode == Opcode.EQUALS:
				opcode_eval_function = is_equal_to
				instruction_values = 4
			elif opcode == Opcode.HALT: # Halts processing of our intcode string

				if self.test and not self.debug:
					return build_intcode(intcode_array)

				return None

			instruction_output = self.perform_instruction( opcode, opcode_eval_function, intcode_array, self.instruction_pointer, self.get_parameter_modes(parameter_modes) )

			# This is in order to harvest the output from an opcode print.


			# Generally, at the end of our instruction we will direct our instruction pointer to point at an opcode
			# "instruction values" ahead of the current instruction.
			instruction_pointer_interrim_value = self.instruction_pointer + instruction_values

			# Case for when we are hijacking general instruction pointer direction with the output of our instruction.
			if (opcode == Opcode.JUMP_IF_FALSE or opcode == Opcode.JUMP_IF_TRUE) and instruction_output != None:
				instruction_pointer_interrim_value = instruction_output

			# Move our pointer up as many positions as instruction values
			self.instruction_pointer = instruction_pointer_interrim_value

			if self.program_output and opcode == Opcode.OUTPUT:

				if self.persistence:
					self.instructions = build_intcode(intcode_array)

				return instruction_output

			self.process_count += 1


if __name__ == '__main__':
	# Run some tests before we get to the meat and potatoes.

	''' Testing if Generics Work '''
	assertEquals(4, add(2, 2))
	assertEquals(8, mul(4,2))
	assertEquals(True, is_true(20))
	assertEquals(False, is_true(0))
	assertEquals(True, is_false(0))
	assertEquals(False, is_false(1))
	assertEquals(True, is_less_than(1, 2))
	assertEquals(False, is_less_than(100, 5))
	assertEquals(True, is_equal_to(2, 2))
	assertEquals(False, is_equal_to(50, 69))

	test1 = IntcodeComputer('', True)
	test1.set_input_queue([0])
	assertEquals(
		"3,12,6,12,15,1,13,14,13,4,13,99,0,0,1,9",
		",".join(test1.get_input(
			[val for val in "3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9".split(",")],
			12
		))
	)

	''' Blackbox testing '''
	test2 = IntcodeComputer("1,0,0,0,99", False, False, False, True)
	assertEquals("2,0,0,0,99", test2.process_intcode())
	test3 = IntcodeComputer("2,3,0,3,99", False, False, False, True)
	assertEquals("2,3,0,6,99", test3.process_intcode())
	test4 = IntcodeComputer("2,4,4,5,99,0", False, False, False, True)
	assertEquals("2,4,4,5,99,9801", test4.process_intcode())
	test5 = IntcodeComputer("1,1,1,4,99,5,6,0,99", False, False, False, True)
	assertEquals("30,1,1,4,2,5,6,0,99", test5.process_intcode())