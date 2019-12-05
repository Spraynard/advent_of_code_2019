'''

Need to guess a password based on the following facts:
    1. It is a six-digit number.
    2. The value is within the range given in puzzle input
    3. Two adjacent digits are the same
    4. Going from left to right, the digits never decrease.
        They only ever increase or stay the same.
'''
def number_len( number ):
    return len(str(number))

def contains_two_adjacent_similar_digits( number ):
    similar_digit_flag = False
    for i in range(0, number_len(number) - 1):
        first, second = (int(str(number)[i]), int(str(number)[i+1]))

        if first == second: 
            # Flag that there are similar digits
            similar_digit_flag = True

    return similar_digit_flag

def contains_two_adjacent_similar_digits_non_group( number ):
    number_of_digits = number_len(number)
    i = 0
    while i < number_of_digits:
        j = i + 1
        digits = [ int(str(number)[i]) ]

        # Now look forward and append all of the numbers if they are the same.
        # Break out if not.
        while j < number_of_digits:
            current_number = int(str(number)[j])
            if current_number == digits[0]:
                digits += [current_number]
                j += 1
            else:
                break

        if len(digits) == 2:
            return True
        else:
            # increase by the differnce of i and j
            increase_by = abs(i - j) - 1
            i = i + increase_by
        i += 1
    return False



def only_ever_increases_from_left_to_right( number ):
    digit_flag = True
    for i in range(0, number_len(number) - 1):
        first, second = (int(str(number)[i]), int(str(number)[i+1]))

        if not first <= second:
            digit_flag = False

    return digit_flag

if __name__ == '__main__':
    range_file = open('input.txt', 'r')

    with range_file:
        input_range = range_file.read()
        lower, upper = [int(boundary) for boundary in input_range.split("-")]

        all_possible = [pw for pw in range(lower, upper + 1)]
        filtered_by_two_adjacent_digits = [pw for pw in all_possible if contains_two_adjacent_similar_digits_non_group(pw)]
        filtered_by_only_increasing_numbers = [pw for pw in filtered_by_two_adjacent_digits if only_ever_increases_from_left_to_right(pw)]

        print(filtered_by_only_increasing_numbers)
        ## All of these passwords should fit the criteria.
        print("Possible Passwords: " + str(len(filtered_by_only_increasing_numbers)))
