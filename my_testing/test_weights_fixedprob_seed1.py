import pyNN.spiNNaker as sim
from pyNN.random import NumpyRNG

sim.setup(timestep=1.0)
input = sim.Population(4, sim.SpikeSourceArray([0]), label="input")
pop = sim.Population(4, sim.IF_curr_exp(), label="pop")
rng = NumpyRNG(seed=1)
conn = sim.Projection(input[1:3], pop[2:4],
                      sim.FixedProbabilityConnector(0.5, rng=rng),
                      sim.StaticSynapse(weight=0.5, delay=2))
sim.run(1)
weights = conn.get(['weight', 'delay'], 'list')
sim.end()
print(weights)
