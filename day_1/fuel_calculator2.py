from math import floor

# Calculate fuel from mass and the necessary fuel needed to carry our fuel
def calculate_fuel( mass ):
 
    fuel_needed = floor(mass/3) - 2
    
    if fuel_needed <= 0:
        return 0
    return fuel_needed + calculate_fuel(fuel_needed)


if __name__ == '__main__':
    input_file = open('input.txt', 'r')
    total_fuel = 0
    test = calculate_fuel(1969)

    if test == 966:
        print("First Is Okay")
    else:
        print(f"First is not okay: {test}")

    for mass in input_file:
        total_fuel += calculate_fuel(int(mass))

    print(f'Total Fuel Required: {total_fuel}')
