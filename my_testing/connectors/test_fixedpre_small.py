import pyNN.spiNNaker as sim

sim.setup(timestep=1.0)
n_neurons = 25
pop1 = sim.Population(n_neurons, sim.IF_curr_exp(), label="pop_1")
pop2 = sim.Population(n_neurons, sim.IF_curr_exp(), label="pop_2")
sim.Projection(pop1, pop2, sim.FixedNumberPreConnector(n_neurons/2),
                            synapse_type=sim.StaticSynapse(weight=5, delay=1))
simtime = 10
sim.run(simtime)
sim.end()