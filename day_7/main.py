from intcode_computer import IntcodeComputer
from assertions import assertEquals
import uuid
import itertools

def get_computer_output( computer, instruction_1, instruction_2 = 0):
    '''
    Need to take in a phase setting and provide it and an
    input and an output to our intcode computer.
    '''
    if not isinstance(instruction_1, int) or not isinstance(instruction_2, int):
        type_1 = type(instruction_1)
        type_2 = type(instruction_2)
        raise TypeError(
f"Instruction_1: {instruction_1} - {type_1} and Instruction_2: {instruction_2} - {type_2} must be of type integer"
        )

    if computer.set_input_queue([instruction_1, instruction_2]):
        return computer.process_intcode()

def process_phase_sequence(computer, sequence, previous = 0):
    '''
    Tail recursive function that takes in a phase sequence and runs subsequent computer programs with the
    output from the previous computer program's run sequence.
    '''
    first_phase = sequence[:1][0]
    rest_phases = sequence[1:]

    if len(sequence) is 1:
        return get_computer_output(computer, first_phase, previous)

    return process_phase_sequence(
        computer,
        rest_phases,
        int(get_computer_output(computer, first_phase, previous))
    )

def process_amplifiers( amplifiers, previous_amplifier_output = 0):
    amp = amplifiers[:1][0]
    rest_amps = amplifiers[1:]

    if len(amplifiers) == 1:
        return amp.get_computer_output(previous_amplifier_output)

    computer_output = amp.get_computer_output(previous_amplifier_output)

    if computer_output is None:
        return None

    return process_amplifiers(
        rest_amps,
        computer_output
    )

def feedback_loop_sequence( amplifiers ):
    def feedback_loop(previous, current=0, count=0):
        if current is None:
            return previous

        return feedback_loop(
            current,
            process_amplifiers(amplifiers , current),
            count + 1
        )

    return feedback_loop(0)

def generate_phase_sequences( min_phase_setting, max_phase_setting, phase_sequence_len = 5 ):
    '''
    Generates all phase sequence permutations that are possible with the given minimum and maximum phases
    '''
    return itertools.permutations(range(min_phase_setting, max_phase_setting + 1), phase_sequence_len )

def get_max_phase_sequence_output( computer_factory, print_at=None ):
    '''
    Builds all possible phase setting permutations and runs them through our phase
    '''
    phase_sequence_outputs = []

    count = 0
    for phase_sequence in generate_phase_sequences(0, 4):
        amplifiers = [Amplifier(computer_factory(), phase) for phase in phase_sequence]
        phase_sequence_data = tuple([process_amplifiers(amplifiers), phase_sequence])

        # For debugging purposes. Tell it the value in which you want to print the phase_sequence_output
        if phase_sequence_data[0] == print_at:
            print(phase_sequence_outputs)

        phase_sequence_outputs += [phase_sequence_data[0]]
        count += 1

    max_phase_sequence_output = max(phase_sequence_outputs)

    return max_phase_sequence_output

def get_max_feedback_loop_output( computer_factory ):
    feedback_loop_outputs = []
    for phase_sequence in generate_phase_sequences(5, 9):

        amplifiers = [Amplifier(computer_factory('persist'), phase) for phase in phase_sequence]
        feedback_loop_outputs += [ feedback_loop_sequence(amplifiers) ]

    return max(feedback_loop_outputs)

class Amplifier():
    def __init__(self, computer, phase):
        self.computer = computer

        if not isinstance(phase, int):
            raise Exception("You must provide an integer for the phase amount of this amplifier")

        self.phase = phase


    def get_computer_output(self, input_instruction = 0):
        '''
        Need to take in a phase setting and provide it and an
        input and an output to our intcode computer.
        '''
        if not isinstance(input_instruction, int):
            instruction_type = type(input_instruction)
            raise TypeError(
    f"Instruction: {input_instruction} - {instruction_type} must be of type integer"
            )
        input_queue = [ input_instruction ]

        if not self.computer.process_count:
            input_queue = [self.phase] + input_queue
        if self.computer.set_input_queue(input_queue):
            return self.computer.process_intcode()

def computer_factory(instructions, params={}, type="default"):

    try:
        debug = params['debug']
    except KeyError:
        debug = False

    try:
        test = params['test']
    except KeyError:
        test = False

    if type == "persist":
        return AmplifierController( instructions, test, True, debug )
    else:
        return AmplifierController( instructions, test, False, debug )

def partial_computer_factory(instructions, params={}):
    return lambda comp_type='default': computer_factory(instructions, params, comp_type )

class AmplifierController(IntcodeComputer):
    def __init__(self, instructions, test=False, persist=False, debug=False):
        super().__init__(instructions, True, True, persist, test, debug)
        self.name = str(uuid.uuid4())

if __name__ == '__main__':
    with open('ex_1.txt') as f:
        instructions = f.read()
        amplifiers = [Amplifier(computer_factory(instructions, { 'test' : True }), phase) for phase in [4,3,2,1,0]]
        assertEquals(43210, process_amplifiers(amplifiers))
        partial = partial_computer_factory(instructions, { 'test' : True })
        assertEquals(43210, get_max_phase_sequence_output(partial))

    with open('ex_2.txt') as f:
        instructions = f.read()
        amplifiers = [Amplifier(IntcodeComputer(instructions, True, True, False, True), phase) for phase in [0,1,2,3,4]]
        assertEquals(54321, process_amplifiers(amplifiers))
        partial = partial_computer_factory(instructions, { 'test' : True })
        assertEquals(54321, get_max_phase_sequence_output(partial))

    with open('ex_3.txt') as f:
        instructions = f.read()
        amplifiers = [Amplifier(IntcodeComputer(instructions, True, True, False, True), phase) for phase in [1,0,4,3,2]]
        assertEquals(65210, process_amplifiers(amplifiers))
        partial = partial_computer_factory(instructions, { 'test' : True })
        assertEquals(65210, get_max_phase_sequence_output(partial))

    with open('ex_4.txt') as f:
        print("Processing ex:4")
        instructions = f.read()
        computer = IntcodeComputer(f.read(), True, True,True,True)
        factory = partial_computer_factory(instructions)#{ 'test' : True, 'debug' : True })

        amplifiers = [Amplifier(factory('persist'), phase) for phase in [9,8,7,6,5]]
        # exit()
        assertEquals(139629729, feedback_loop_sequence(amplifiers))
        assertEquals(139629729, get_max_feedback_loop_output(factory))

    with open('ex_5.txt') as f:
        instructions = f.read()
        factory = partial_computer_factory(instructions)
        assertEquals(18216, get_max_feedback_loop_output(factory))

    with open('input.txt') as f:
        factory = partial_computer_factory(f.read())
        print("Max Output")
        print(get_max_feedback_loop_output(factory))

