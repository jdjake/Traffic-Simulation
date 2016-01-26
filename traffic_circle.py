#TODO: Add Traffic_light_rates

from collections import defaultdict
from math import pi

car_width = 2.5
car_rate = 1

class jackson_graph:
    def __init__(self, lane_number, entrances, velocity, speed, radius, entrance_rate):
        self.vertices = set(['entrance', 'exit']) | set((x,y) for x in range(lane_number) for y in range(2*entrances))

        inner_lanes = range(1,lane_number-1)
        angles = range(2*entrances + 2)

        # Define edges between vertices
        between_left = {(x,y): set([x-1, (y+1) % 2*entrances]) for x in inner_lanes for y in angles}
        between_middle = {(x,y): set([x, (y+1) % 2*entrances]) for x in inner_lanes for y in angles}
        between_right = {(x,y): set([x+1, (y+1) % 2*entrances]) for x in inner_lanes for y in angles}
        between_edges = {(x,y): between_left[x,y] | between_middle[x,y] | between_right[x,y] for x in inner_lanes for y in angles}

        inner_middle = {(0,y): set([0, (y+1) % 2*entrances]) for y in range(2*entrances)}
        inner_right = {(0,y): set([1, (y+1) % 2*entrances]) for y in range(2*entrances)}

        outer_middle = {(lane_number-1, y): set([lane_number-1, (y + 1) % 2*entrances]) for y in angles}
        outer_left = {(lane_number-1): set([lane_number-2, (y + 1) % 2*entrances]) for y in angles}
        outer_exit = {(lane_number-1) : lane_number-1, 'exit') for y in range(1,2*entrances + 2, 2)}

        # -k represents the entrance at the k'th angle.
        entrances = {-k: set([(k, lane_number-1), (k, lane_number-2)]) for k in range(0,2*entrances + 2, 2)}

        self.edges = {
            [(0, inner_edges[0] | outer_edges[0]]) +
            [(lane_number-1, inner_right[lane_number-1] | inner_middle[lane_number-1])] +
            [(x, between_left[x] | between_middle[x] | between_right[x]) for x in range(1,lane_number-1)]
        } if (lane_number > 1) else outer_middle

        # Define rates for edges
        middle_rates = {edge: 4/(3*velocity*pi*(radius + 3*edge[0][0])) for edge between_edges.items()}

        inner_middle_rates = {edge:16/(5*velocity*pi*(radius + 3*edge[0][0])) for edge in inner_middle.items()}
        inner_right_rates = {edge:4/(5*velocity*pi*(radius + 3*edge[0][0])) for edge in inner_right.items()}

        # TODO: add outer rates, and entrance/exit rates
        outer_rates = {edge:1}
        outer_exit_rates = {edge:1}

        self.rates = dict(
            list(middle_rates.items()) +
            list(inner_middle_rates.items()) +
            list(inner_right_rates.items()) +
            list(outer_rates.items()) +
            list(outer_transition_rates.items())
        )

        self.population = {vertex: 0 for vertex in self.vertices}

        # Given the speed, the maximum number of cars in a 45 degree radius such that
        # every car is at least `a second of the speed limit' away from one another.
        self.population_limit = {vertex: floor(2*pi*(radius + 3*vertex[0])/(4*(velocity + 5))) for vertex in self.vertices}

    def simulate(self, transition_number):
        # For each iteration, generate poisson distributions for
        # each node, according to the number of cars in each node,
        # and choose the action which has the minimal time. Adjust
        # the jackson graph accordingly, then rinse and repeat.
        for i in range(transition_number):
            pass