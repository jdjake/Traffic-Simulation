import simpy
import copy
import random
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from math import pi, inf as infinity

# TODO: When entrances are initialized, they should be initialized to
# simpy so they may begin producing cars.

class Node():
    def __init__(self, exit_time, max_capacity, name = ""):
        """
            exit_time (positive, floating point number):
                The average time between a car entering and exiting
                the node.
            max_capacity (positive integer):
                The maximum number of cars which can be placed in a node.
            name (string, optional):
                A distinct name for a node in the traffic graph.
        """

        self.name = name
        self.exit_time = exit_time
        self.connected_nodes = {}
        self.max_capacity = max_capacity
        self.current_capacity = 0

    def connect(self, node, transition_probability):
        self.connected_nodes[node] = transition_probability

    def verify_probabilities(self):
        print([(x.name, self.connected_nodes[x]) for x in self.connected_nodes.keys()])
        all_positive = all(self.connected_nodes[x] >= 0 for x in self.connected_nodes.keys())
        total_probability = sum(self.connected_nodes[x] for x in self.connected_nodes.keys())

        return all_positive and (total_probability == 1)

    def can_move(self):
        return self.current_capacity < self.max_capacity

    def move_car_in(self):
        assert(self.current_capacity < self.max_capacity)
        self.current_capacity += 1

    def move_car_out(self):
        assert(self.current_capacity > 0)
        self.current_capacity -= 1

class EntranceNode(Node):
    def __init__(self, exit_time, max_capacity, name = ""):
        """
            exit_time (positive, floating point number):
                The average time between a car entering and exiting
                the node.
            max_capacity (positive integer):
                The maximum number of cars which can be placed in a node.
            name (string, optional):
                A distinct name for a node in the traffic graph.
        """

        self.name = name
        self.exit_time = exit_time
        self.connected_nodes = {}
        self.max_capacity = max_capacity
        self.current_capacity = 0

        env.process(self.run(env))

    def run(self, env):
        while (True):
            if random.choice([False,True]):
                print("A New little baby car!")
                Car(self, env)
                yield env.timeout(5)

class ExitNode():
    def __init__(self, name = ""):
        self.name = name



class TrafficCircle():
    def __init__(self, radius, angular_node_frequency,
                 speed_limit, entrance_spacing, env, start_radius = 1):
        """
            radius (positive integer):
                The number of lanes in the traffic circle.
            angular_node_frequency (positive integer):
                The number of nodes in a complete rotation of the traffic
                circle. Increasing the frequency will likely result in a more
                accurate simulation, up to a point, but having the frequency
                too large will result in integer rounding errors (since
                at least one car must be able to fit in one node, and if a
                node is too thin, no cars will be able to fit into the node).
            speed_limit (positive floating-point number):
                The average speed a car travels.
            entrance_spacing (non-negative integer):
                The number of nodes between successive entrances in the
                traffic circle, going clockwise.
            start_radius (positive integer less than radius, optional):
                The radius at which the lanes begin (in the case of a 
                bigger traffic island)
        """

        self.start_radius = start_radius
        self.radius = radius
        self.angular_node_frequency = angular_node_frequency
        self.speed_limit = speed_limit

        self.nodes = {}
        self.entrances = {}
        self.exits = {}

        # Define nodes in the interior of the circle
        for r in range(start_radius,radius+1):
            exit_time = 2*pi*r/angular_node_frequency/speed_limit
            # Possibly want to include space between cars
            max_car_number = int(2*pi*r/angular_node_frequency/3)
            print(max_car_number)

            for k in range(0,angular_node_frequency):
                self.nodes[r,k] = Node(exit_time, max_car_number, "(%d, %d)" % (r,k))

        # Define connections which go forward in the circle.
        for r in range(start_radius, radius+1):
            for k in range(0, angular_node_frequency):
                transition_probability = 0.5 if start_radius < r < radius else 0.7
                next_node = self.nodes[r,(k+1) % angular_node_frequency]
                self.nodes[r,k].connect(next_node, transition_probability)

        # Define connections which turn right in the circle.
        for r in range(start_radius, radius):
            for k in range(0, angular_node_frequency):
                transition_probability = 0.3 if r == start_radius else 0.25
                next_node = self.nodes[r+1,(k+1) % angular_node_frequency]
                self.nodes[r,k].connect(next_node, transition_probability)

        # Define connections which turn left in the circle.
        for r in range(start_radius+1, radius+1):
            is_entrance = 0
            for k in range(0, angular_node_frequency):
                if (r == radius):
                    transition_probability = 0.15 if is_entrance == 0 else 0.3
                else:
                    transition_probability = 0.25

                next_node = self.nodes[r-1,(k+1) % angular_node_frequency]

                self.nodes[r,k].connect(next_node, transition_probability)

                is_entrance = (is_entrance + 1) % (entrance_spacing + 1)

        is_entrance = 0
        for k in range(0, angular_node_frequency):
            if (is_entrance == 0):
                new_entrance = EntranceNode(0.5, infinity, "entrance")
                new_entrance.connect(self.nodes[radius, k], 1)

                self.entrances[k] = new_entrance

                new_exit = ExitNode("exit %d" % k)
                self.nodes[radius, k].connect(new_exit, 0.15)

                self.exits[k] = new_exit

            is_entrance = (is_entrance + 1) % (entrance_spacing + 1)

        #for r in range(start_radius, radius+1):
        #    for k in range(0, angular_node_frequency):
        #        print(r, k, self.nodes[r,k].verify_probabilities())

class Car():
    def __init__(self, entrance, env):
        """
            entrance (Node):
                the entrance where the Car begins.
        """

        self.current_node = entrance
        self.current_node.move_car_in()

        self.env = env
        env.process(self.try_moving(env))

    def try_moving(self, env):
        while (True):
            print("Trying to Move")
            if random.choice([False,True]):
                print("Moving")
                not_ended = self.move_node()
                if not not_ended:
                    print("Bye")
                    return

            yield env.timeout(5)

    def move_node(self):
        to_choose = list(self.current_node.connected_nodes.keys())
        probabilities = [self.current_node.connected_nodes[x] for x in to_choose]

        print("Choosing from ", [x.name for x in to_choose])
        next_node = np.random.choice(to_choose, p = probabilities)
        print("Now in %s" % next_node.name)

        # Check if next_node is exit -- if so, shut down the car
        if type(next_node) is ExitNode:
            # TODO -- Kick car out of simulation, shut it down
            return False

        # Check if able to move to next node, and if so, move to the next node.
        elif next_node.can_move():
            self.current_node.move_car_out()
            self.current_node = next_node
            self.current_node.move_car_in()

            return True

            # DETERMINE WAITING TIME, AND WORK OUT IF SIMPY CAN STOP CAR
            # FROM BEING RUN FOR A SPECIFIED AMOUNT OF TIME.

        else:
            # TODO -- Collision: Run for cover! IF YOU CAN DELAY CAR IN
            # SIMPY, THEN DELAY CAR
            print("CRASH!")

            return True

def draw_graph(env, traffic_circle):
    while(True):
        print("I am drawing a graph")

        G = nx.DiGraph()

#        for node in traffic_circle.nodes:
#            G.add_node(node.name)

#        for entrance in traffic_circle.entrances:
#            G.add_node(entrance.name)

#        for exit in traffic_circle.exits:
#            G.add_node(exit.name)

        labels = {}
        for r in range(traffic_circle.start_radius, traffic_circle.radius + 1):
            for k in range(0,traffic_circle.angular_node_frequency):
                G.add_node('[%d,%d]' % (r,k), capacity=traffic_circle.nodes[r,k].current_capacity)
                labels['[%d,%d]' % (r,k)] = '%d/%d' % (traffic_circle.nodes[r,k].current_capacity, traffic_circle.nodes[r,k].max_capacity)
                G.add_edge('[%d,%d]' % (r,k), '[%d,%d]' % (r,(k + 1) % traffic_circle.angular_node_frequency))

                if (r > start_radius):
                    G.add_edge('[%d,%d]' % (r,k), '[%d,%d]' % (r-1, k % traffic_circle.angular_node_frequency))

                if (r < radius):
                    G.add_edge('[%d,%d]' % (r,k), '[%d,%d]' % (r+1, k % traffic_circle.angular_node_frequency))

        nx.draw(G, labels=labels, node_size = 3000)
        plt.show()

        yield env.timeout(5)

radius = 4
start_radius = 2
angular_node_frequency = 5
speed_limit = 10
entrance_spacing = 2

env = simpy.Environment()

x = TrafficCircle(radius, angular_node_frequency,
                  speed_limit, entrance_spacing,
                  env, start_radius = start_radius)

env.process(draw_graph(env, x))

env.run(until = 1000)

# TODO -- Setup entrances and cars to be simpy actors, and use random distribution
# to determine movement rates.

"""
class Car():
    def __init__(self, entrance):
        self.node = entrance

class Car():
    def __init__(self, env, name, bcs, driving_time, charge_duration):
        self.env = env
        self.action = env.process(self.run())
        self.name = name
        self.bcs = bcs
        self.driving_time = driving_time
        self.charge_duration = charge_duration

    def run(self):
        print("Start Driving at %d" % env.now)
        yield self.env.timeout(self.driving_time)

        try:
            print("Start Parking at %d" % env.now)

            with bcs.request() as req:
                yield req

                print("%s starting to charge at %s" % (self.name, self.env.now))
                yield self.env.process(self.charge())
                print("%s leaving the bcs at %s" % (self.name, self.env.now))

        except simpy.Interrupt:
            print("Was interrupted. Hope the battery is full enough...")

    def charge(self):
        yield self.env.timeout(self.charge_duration)

env = simpy.Environment()
bcs = simpy.Resource(env, capacity = 2)

for i in range(4): car = Car(env, "Car %d" % i, bcs, i, 5)

env.run(until = 50)
"""