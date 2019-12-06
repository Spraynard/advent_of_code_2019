class Node():
    def __init__(self):
        self.parent = None
        self.children = None

    def add_child(self, other):
        if self.children is None:
            self.children = []

        self.children += [other]

    def set_parent(self, other):
        self.parent = other

class Orbit(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return self.name

    def print_orbit(self):
        '''
        Prints the name of the orbit and its children
        '''
        print("=" * 20)
        print("{name} Parent: {parent} Children: {children}".format(name=self.name, parent=self.parent, children=[str(child) for child in self.children] if self.children else '[]'))
        print("=" * 20)
        print("\n")

    def add_orbiter(self, other):
        '''
        Add in an orbiter that orbits around this orbit
        '''
        return self.add_child(other)

    def set_orbitee(self, other):
        '''
        Set the Orbit in which this orbit is an orbiter
        '''
        return self.set_parent(other)

    def num_orbiting(self, count=0):
        '''
        Find out the total of orbits that we directly and indirectly orbit.
        '''
        if not self.parent:
            return count

        return self.parent.num_orbiting(count + 1)

def build_all_orbits( data_file ):
    '''
    Takes in orbit_data and builds a dictionary of all of
    the orbits.

    The map of orbits can be build by starting at COM.
    '''
    orbits = {}

    for orbit_data in data_file.readlines():
        orbit_data = orbit_data.replace("\n", "")
        orbit_name, orbiter_name = orbit_data.split(")")

        if not orbit_name in orbits:
            orbits[orbit_name] = Orbit(orbit_name)

        if not orbiter_name in orbits:
            orbits[orbiter_name] = Orbit(orbiter_name)

        orbit = orbits[orbit_name]
        orbiter = orbits[orbiter_name]

        orbit.add_orbiter(orbiter)
        orbiter.set_orbitee(orbit)

    return orbits

def find_santa( current_location, already_traveled=[], transfers=0, level=0 ):
    # current_location.print_orbit()
    # print([str(traveled) for traveled in already_traveled] if already_traveled else "Haven't Traveled")

    if current_location is None:
        return

    if already_traveled and current_location in already_traveled:
        return

    already_traveled += [current_location]
    # print("Transfers: " + str(transfers))
    if current_location.name == 'SAN':
        print("Level" + str(level))
        print("\t" * (level % 10) + current_location.name)
        print("We got Santa")
        return transfers - 1

    if current_location.children is None:
        return


    for location in current_location.children:
        possible_transfers = find_santa( location, already_traveled, transfers + 1, level + 1)
        # print(possible_transfers)
    # This is where we truly exit.
    if possible_transfers:
        print(possible_transfers)
        return possible_transfers
    # print("Movin on up")

    return find_santa( current_location.parent, already_traveled, transfers + 1, level)


if __name__ == '__main__':
    input_file = open('input.txt', 'r')

    with input_file as f:
        orbits = build_all_orbits(f)

    my_own_orbit = orbits['YOU']
    try:
        # print("Entry")
        transfers_to_find_santa = find_santa(my_own_orbit.parent)
    except RecursionError:
        print("Oh no too much recursion")
        exit()

    print(f"Minimum Transfers Needed: {transfers_to_find_santa}")



