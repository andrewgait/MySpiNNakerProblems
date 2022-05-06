import pyNN.spiNNaker as sim
from spinn_front_end_common.utilities import globals_variables

sim.setup(timestep=1.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp(), 2)
pop1 = sim.Population(6, sim.IF_curr_exp(), label="pop_1")
pop2 = sim.Population(6, sim.IF_curr_exp(), label="pop_2")
pop1view = pop1[0:4]
pop2view = pop2[2:6]
sim.Projection(pop1view, pop2view, sim.OneToOneConnector())

graph = globals_variables.get_simulator()._application_graph
print(graph)

sim.end()
