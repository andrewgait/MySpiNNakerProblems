import pyNN.spiNNaker as sim
from spinn_front_end_common.utilities import globals_variables

sim.setup(timestep=1.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp(), 2)
pop1 = sim.Population(10, sim.IF_curr_exp(), label="pop_1")
pop2 = sim.Population(10, sim.IF_curr_exp(), label="pop_2")
pop1view = pop1[0:4]
pop2view = pop2[2,5,6,8]

fromlist = [[0,2],[1,5],[2,6],[1,8],[2,5]]
# proj = sim.Projection(pop1view, pop2view, sim.FromListConnector(fromlist))
proj = sim.Projection(pop1view, pop2view, sim.FixedProbabilityConnector(0.5))

graph = globals_variables.get_simulator()._application_graph
print(graph)

sim.run(1000)

print(proj.get(["weight", "delay"], "list"))

sim.end()
