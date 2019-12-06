class Node():
    def __init__(self):
        self.parent = None
        self.children = []

    def add_child(self, other):
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
        return "Orbit --> " + self.name

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

if __name__ == '__main__':
    input_file = open('input.txt', 'r')

    with input_file as f:
        orbits = {}

        for orbit_data in f.readlines():
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

        total_orbits = 0

        for dict_orbit_name in orbits:
            dict_orbit = orbits[dict_orbit_name]

            total_orbits += dict_orbit.num_orbiting()

        print(f"The total direct and indirect orbits are {total_orbits}")