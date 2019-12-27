import functools
import operator

def createSignal(rawSignal):
    return (int(number) for number in list(rawSignal))

def createRawSignal(signal):
    return "".join(str(num) for num in signal)

def patternGenerator(position=1, base=[0,1,0,-1]):
    baseIndex = 0
    nextCount = position # Iterate over to the next value in base

    while True:
        value = base[baseIndex]
        yield value
        nextCount -= 1

        if nextCount == 0:
            baseIndex += 1
            nextCount = position

        if baseIndex == len(base):
            baseIndex = 0

def generatePattern(position, size=5000, offset=2):
    pattern = []
    count = 0
    for num in patternGenerator(position):
        pattern.append(num)
        count += 1
        if count == size + offset:
            return pattern

def truncatePattern(pattern, patternLen):
    '''
    skip the first value of our pattern
    truncate the rest down to our given patternLen
    '''
    return pattern[1:][:patternLen]

def createPattern(position, size):
    return truncatePattern(generatePattern(position, size), size)

# def transform()

def fft(rawSignal, phaseNum=1, debug=False):

    def transform(signal):
        for position in range(len(signal)):
            # pattern = createPattern(position + 1, len(signal))
            patternGen = patternGenerator(position + 1)
            next(patternGen)
            partialSums = {}

            for signalVal in signal:
                patternVal = next(patternGen)

                if patternVal == 0:
                    continue

                if not patternVal in partialSums.keys():
                    partialSums[patternVal] = 0

                partialSums[patternVal] += signalVal

            summed = functools.reduce(
                operator.add,
                [ patternMultiplier * signalMultiplier for (patternMultiplier, signalMultiplier) in partialSums.items() ]
            )

            digit = abs(summed) % 10

            if debug:
                print(f"Summed: {summed}")
                print(f"DIGIT: {digit}")

            signal[position] = digit
            # signalIndex += 1

        return signal

    def applyTransform(signal, phaseAmount, phaseCount = 0):
        if phaseCount == phaseAmount:
            if debug:
                print(signal)
            return signal
        print(signal)
        return applyTransform(transform(signal), phaseAmount, phaseCount + 1)

    return createRawSignal(applyTransform(
        list(createSignal(rawSignal)),
        phaseNum
    ))

def offsetfft(rawSignal, phaseNum=100):
    '''
    Assumes an offset given by fft within the first 7 numbers
    is greater than halfway through signal length.

    Our pattern operations act as a triangular matrix when position is high enough
    '''
    signal = list(createSignal(rawSignal))
    offset = int(rawSignal[:7])

    assert offset > len(signal) / 2

    for phase in range(phaseNum):
        print(phase)
        for index in range(len(signal) - 2, offset - 1, -1):
            digit = (signal[index] + signal[index + 1]) % 10
            signal[index] = digit

    return createRawSignal(signal[offset:])




if __name__ == "__main__":
    with open('input.txt', 'r') as f:
        data = f.read()

    testInput_1 = '12345678'
    testInput_2 = '80871224585914546619083218645595'
    testInput_3 = '19617804207202209144916044189917'
    testInput_4 = '69317163492948606335995924319873'

    output1 = fft(testInput_1, 4)
    assert output1 == '01029498'
    output2 = fft(testInput_2, 100)[:8]
    assert output2 == '24176176'
    output3 = fft(testInput_3, 100)[:8]
    assert output3 == '73745418'
    output4 = fft(testInput_4, 100)[:8]
    assert output4 == '52432133'
    print(f"Output1 --> {output1}")
    print(f"Output2 --> {output2}")
    print(f"Output3 --> {output3}")
    print(f"Output4 --> {output4}")
    # output5 = fft(data, 100, False)[:8] # Part 1
    # print(f"Output5 --> {output5}")

    # Part 2
    testInput_5 = ('03036732577212944063491565474664' * 10000)
    # testInput_6 = ('02935109699940807407585447034323' * 10000)
    # testInput_7 = ('03081770884921959731165446850517' * 10000)
    # output5 = fft( str(testInput_5), 100, True)
    # print(f"Output 5 --> {output5}")
    # output6 = fft( str(testInput_6), 100, True)
    # print(f"Output 6 --> {output6}")
    # print(output6)
    # output7 = fft( str(testInput_7), 100, True)
    # print(f"Output 7 --> {output7}")
    # print(output7)
    part2_output = offsetfft(data * 10000)
    print(part2_output)
    print(part2_output[:8])
    # offset = int(data[:7])
    # part2_output = fft( data * 10000, 100, True )

