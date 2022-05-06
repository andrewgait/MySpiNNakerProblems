from spinn_front_end_common.utilities import globals_variables
import pyNN.spiNNaker as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=1.0)

n1 = 14
n2 = 17
runtime = 100
sim.set_number_of_neurons_per_core(sim.IF_curr_exp(), 10)

pop1 = sim.Population(n1, sim.IF_curr_exp(), label="pop1")
pop2 = sim.Population(n2, sim.IF_curr_exp(), label="pop2")

weights = 1.0
delays = 1.0

proj1 = sim.Projection(pop1, pop2, sim.OneToOneConnector(),
                       sim.StaticSynapse(weight=weights, delay=delays))
# proj2 = sim.Projection(pop1[6:12], pop2[9:16], sim.OneToOneConnector(),
#                        sim.StaticSynapse(weight=weights, delay=delays),
#                        label='check')

sim.run(runtime)

# is there a way of getting the (number of edges in the) graph here?
graph = globals_variables.get_simulator()._machine_graph
labelled_edges = [edge for edge in graph.edges if (
    edge.label=='machine_edge_forcheck')]
print(labelled_edges)
print(len(labelled_edges))

print(proj1.get(['weight', 'delay'], 'list'))
# print(proj2.get(['weight', 'delay'], 'list'))

sim.end()
