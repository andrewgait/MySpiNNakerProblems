import pyNN.spiNNaker as sim

sim.setup(timestep=1.0)
simtime = 10
n_neurons = 6
pop_1 = sim.Population(n_neurons, sim.IF_curr_exp(), label="pop_1")
# pop_2 = sim.Population(n_neurons, sim.IF_curr_exp(), label="pop_2")
# proj = sim.Projection(pop_1, pop_2, sim.OneToOneConnector())
pop_1.record("all")
# pop_2.record("all")
sim.run(simtime)

sim.end()