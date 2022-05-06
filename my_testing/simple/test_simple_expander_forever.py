import pyNN.spiNNaker as sim

sim.setup(timestep=1.0)

pop_1 = sim.Population(4, sim.IF_curr_exp(), label="pop_1")
input = sim.Population(4, sim.SpikeSourceArray(spike_times=[0]), label="input")

delays = sim.RandomDistribution(
    "normal_clipped", mu=20, sigma=1, low=1, high=6)

input_proj = sim.Projection(input, pop_1, sim.AllToAllConnector(),
                            synapse_type=sim.StaticSynapse(
                                weight=5, delay=delays))

simtime = 10
sim.run(simtime)

sim.end()
