from math import floor

def calculate_fuel( mass ):
    return floor(mass / 3) - 2

if __name__ == '__main__':
    input_file = open('input.txt', 'r')
    total_fuel = 0

    for mass in input_file:
        total_fuel += calculate_fuel(int(mass))

    print(f'Total Fuel Required: {total_fuel}')
